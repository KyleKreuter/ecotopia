"""Generate training data for Ecotopia fine-tuning using AWS Bedrock Mistral Large.

Generates extraction (promise + contradiction detection) and citizens (dialogue + reactions)
training examples across easy, medium, and hard difficulty levels.

Usage:
    python bedrock_data_gen.py --type extraction --count 100 --difficulty hard
    python bedrock_data_gen.py --type citizens --count 50 --difficulty hard
    python bedrock_data_gen.py --type all --count 150  # 100 extraction + 50 citizens
"""
import argparse
import json
import os
import random
import re
import time
from pathlib import Path

import boto3

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
MODEL_ID = "mistral.mistral-large-2402-v1:0"
DATA_DIR = Path(__file__).parent / "data"

EXTRACTION_SYSTEM = (
    "You are Ecotopia's promise extraction and contradiction detection engine. "
    "Extract all promises from the player's speech (explicit and implicit). "
    "Detect contradictions between words and actions. "
    "Rules: Explicit promises use 'I promise', 'I guarantee', 'I will', 'You have my word'. "
    "Implicit promises are statements implying commitment ('The forest stays', 'No more factories'). "
    "Extract target_citizen if promise is directed at someone. "
    "Extract deadline_round if mentioned. "
    "NOT a promise: opinions, descriptions, questions. "
    "Confidence 0.0-1.0. For contradictions: compare speech with actions, severity low/medium/high. "
    "Always respond with valid JSON only."
)

CITIZENS_SYSTEM = (
    "You are Ecotopia's citizen reaction engine. Given extracted promises and current game state, "
    "generate realistic citizen reactions. Each citizen has a personality, mood, and trust level. "
    "Generate dialogue and trust changes. Core citizens: Karl (worker, economy-focused), "
    "Mia (environmentalist, ecology-focused), Sarah (opposition leader, critical). "
    "Dynamic citizens can be spawned based on events."
)

EXTRACTION_CATEGORIES = {
    "easy": [
        "single explicit promise with clear type and impact",
        "two promises with no contradictions",
        "simple ecology promise with positive impact",
        "simple economy promise with clear deadline",
    ],
    "medium": [
        "implicit promise requiring inference",
        "multiple promises with one obvious contradiction",
        "mixed ecology and economy promises",
        "promise with ambiguous deadline",
    ],
    "hard": [
        "subtle contradiction between ecology and economy promises",
        "5+ promises in a single speech with mixed impacts",
        "ambiguous language where extraction is tricky",
        "negative promises (cutting budgets, closing facilities)",
        "conditional promises (if X then Y)",
        "round-specific deadlines (by round 3, by round 5)",
        "sarcastic or ironic speech that implies promises",
        "very short speech (1-2 sentences) with multiple implications",
        "promises directed at specific citizens",
        "speech with hidden negative impacts behind positive framing",
        "contradicting previous round promises",
        "promises about research that conflict with economy goals",
        "vague promises that are hard to classify",
        "promises mixing all 3 types (ecology, economy, research)",
        "speech with no actual promises despite sounding promising",
    ],
}

CITIZENS_CATEGORIES = {
    "easy": [
        "Karl reacts positively to economy promise",
        "Mia reacts positively to ecology promise",
        "Sarah criticizes a vague promise",
    ],
    "medium": [
        "Karl and Mia have opposing reactions",
        "Sarah agrees with one promise but criticizes another",
        "citizens react to contradictions in promises",
    ],
    "hard": [
        "conflicting reactions between Karl (wants economy) and Mia (wants ecology)",
        "dynamic citizen spawning triggered by extreme promises",
        "maximum 5 citizens reacting simultaneously",
        "citizens reacting to broken promises from previous rounds",
        "Sarah (opposition) finding something to actually agree with",
        "Karl and Mia both angry at same promise for different reasons",
        "extreme game states (environment < 20 or economy < 20)",
        "all citizens suspicious after repeated lies",
        "dynamic citizen spawned mid-game changing dynamics",
        "mixed reactions where some citizens hopeful and others furious",
    ],
}


def get_client() -> boto3.client:
    """Create Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=REGION)


def call_mistral(client: boto3.client, prompt: str, max_retries: int = 5) -> str:
    """Call Mistral Large via Bedrock with exponential backoff."""
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.8,
    })
    for attempt in range(max_retries):
        try:
            resp = client.invoke_model(
                modelId=MODEL_ID, body=body, contentType="application/json"
            )
            result = json.loads(resp["body"].read())
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            wait = (attempt + 1) * 5
            print(f"  Retry {attempt + 1}/{max_retries} ({type(e).__name__}), waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Bedrock call failed after {max_retries} retries")


def extract_json_from_text(text: str) -> dict:
    """Extract JSON object from LLM response text."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    raise json.JSONDecodeError("No JSON found in response", text, 0)


def fix_deadlines(data: dict) -> dict:
    """Ensure all deadlines use round-based format."""
    mapping = {
        "short_term": "by_round_3",
        "medium_term": "by_round_5",
        "long_term": "by_end_of_game",
    }
    for promise in data.get("promises", []):
        deadline = promise.get("deadline", "")
        if deadline in mapping:
            promise["deadline"] = mapping[deadline]
    return data


def generate_extraction_example(client: boto3.client, category: str) -> dict | None:
    """Generate one extraction training example via Bedrock."""
    prompt = f"""Generate a training example for a political simulation game called Ecotopia.
The player is the mayor of a city on the edge of ecological collapse. The game has 7 rounds (each = 5 years).

Category: {category}

Generate:
1. A realistic mayor's speech (the user input)
2. The expected JSON extraction output

The output JSON format:
{{"promises": [{{"text": "promise text", "type": "ecology|economy|research", "impact": "positive|negative", "deadline": "immediate|by_round_3|by_round_5|by_end_of_game"}}], "contradictions": [{{"promise1": "text", "promise2": "text", "explanation": "why contradictory"}}]}}

Return JSON with two keys: "speech" (string) and "extraction" (object).
Use ONLY these deadlines: immediate, by_round_3, by_round_5, by_end_of_game."""

    try:
        response = call_mistral(client, prompt)
        parsed = extract_json_from_text(response)
        speech = parsed.get("speech", "")
        extraction = fix_deadlines(parsed.get("extraction", {}))
        if not speech or "promises" not in extraction:
            return None
        return {
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": speech},
                {"role": "assistant", "content": json.dumps(extraction)},
            ]
        }
    except Exception as e:
        print(f"  Failed to generate: {e}")
        return None


def generate_citizens_example(client: boto3.client, category: str) -> dict | None:
    """Generate one citizens reaction training example via Bedrock."""
    game_state = {
        "round": random.randint(1, 7),
        "environment": random.randint(15, 85),
        "economy": random.randint(15, 85),
        "happiness": random.randint(15, 85),
    }

    prompt = f"""Generate a training example for citizen reactions in Ecotopia (political simulation).
Game state: round {game_state['round']}, env={game_state['environment']}, economy={game_state['economy']}, happiness={game_state['happiness']}

Category: {category}

Generate:
1. User input: extracted promises + game state as JSON
2. Expected citizen reactions

Reactions format:
{{"reactions": [{{"name": "citizen_name", "type": "worker|environmentalist|opposition|journalist|economist", "mood": "angry|happy|suspicious|neutral|hopeful|disappointed", "dialogue": "realistic dialogue", "trust_change": -20 to +20}}]}}

Core citizens: Karl (worker), Mia (environmentalist), Sarah (opposition). Dynamic citizens can be spawned.
Return JSON with two keys: "input" (object) and "reactions" (object)."""

    try:
        response = call_mistral(client, prompt)
        parsed = extract_json_from_text(response)
        user_input = parsed.get("input", {})
        reactions = parsed.get("reactions", {})
        if not user_input or not reactions.get("reactions"):
            return None
        return {
            "messages": [
                {"role": "system", "content": CITIZENS_SYSTEM},
                {"role": "user", "content": json.dumps(user_input)},
                {"role": "assistant", "content": json.dumps(reactions)},
            ]
        }
    except Exception as e:
        print(f"  Failed to generate: {e}")
        return None


def generate_batch(
    client: boto3.client,
    gen_type: str,
    count: int,
    difficulty: str,
    output_path: Path,
) -> int:
    """Generate a batch of training examples."""
    categories = (
        EXTRACTION_CATEGORIES[difficulty]
        if gen_type == "extraction"
        else CITIZENS_CATEGORIES[difficulty]
    )
    gen_fn = generate_extraction_example if gen_type == "extraction" else generate_citizens_example

    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated = 0

    with open(output_path, "w") as f:
        for i in range(count):
            category = categories[i % len(categories)]
            print(f"  [{i + 1}/{count}] {category[:60]}...")
            example = gen_fn(client, category)
            if example:
                f.write(json.dumps(example) + "\n")
                f.flush()
                generated += 1
            time.sleep(3)

    print(f"Generated {generated}/{count} {gen_type} examples -> {output_path}")
    return generated


def main() -> None:
    """Entry point for data generation."""
    parser = argparse.ArgumentParser(description="Generate Ecotopia training data via Bedrock")
    parser.add_argument("--type", choices=["extraction", "citizens", "all"], default="all")
    parser.add_argument("--count", type=int, default=150, help="Total examples (for 'all': 2/3 extraction, 1/3 citizens)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="hard")
    args = parser.parse_args()

    client = get_client()
    print(f"Using Bedrock Mistral Large ({MODEL_ID}) in {REGION}")

    if args.type in ("extraction", "all"):
        ext_count = args.count if args.type == "extraction" else int(args.count * 2 / 3)
        out = DATA_DIR / "extraction" / f"batch_bedrock_{args.difficulty}.jsonl"
        generate_batch(client, "extraction", ext_count, args.difficulty, out)

    if args.type in ("citizens", "all"):
        cit_count = args.count if args.type == "citizens" else args.count - int(args.count * 2 / 3)
        out = DATA_DIR / "citizens" / f"batch_bedrock_{args.difficulty}.jsonl"
        generate_batch(client, "citizens", cit_count, args.difficulty, out)

    print("Done!")


if __name__ == "__main__":
    main()
