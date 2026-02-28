"""Quick test: run promise extraction on a base Mistral model (no fine-tuning needed).

Usage:
    MISTRAL_API_KEY=<key> python3 training/test_base_model.py
"""

import json
import os
import sys
import time

from mistralai import Mistral

SYSTEM_PROMPT = (
    "You are Ecotopia's promise extraction and contradiction detection engine. "
    "Extract all promises from the player's speech (explicit and implicit). "
    "Detect contradictions between words and actions. "
    "Rules: Explicit promises use 'I promise', 'I guarantee', 'I will', 'You have my word'. "
    "Implicit promises are statements implying commitment ('The forest stays', 'No more factories'). "
    "Extract target_citizen if promise is directed at someone. "
    "Extract deadline_round if mentioned. "
    "NOT a promise: opinions, descriptions, questions. "
    "Confidence 0.0-1.0. "
    "For contradictions: compare speech with actions, severity low/medium/high. "
    "Always respond with valid JSON only."
)

TEST_INPUT = json.dumps({
    "round": 2,
    "player_speech": (
        "Citizens, I promise to shut down the coal plant by round 4. "
        "Oleg, I guarantee you will have a new job in the solar sector. "
        "The forest stays -- no one touches it."
    ),
    "actions_this_round": [
        {"type": "BUILD", "detail": "solar_farm_east"},
        {"type": "DEMOLISH", "detail": "old_warehouse"},
    ],
    "actions_history": [
        {"round": 1, "actions": [{"type": "BUILD", "detail": "factory_north"}]},
    ],
    "previous_promises": [
        {"text": "I will protect the environment", "round": 1},
    ],
    "active_citizens": ["Elena", "Oleg", "Marta"],
    "dynamic_citizens": [],
    "game_state": {"ecology": 55, "economy": 48, "research": 35},
})

MODELS = [
    "mistral-small-latest",
    "mistral-large-latest",
]


def main() -> None:
    """Test base models on a sample extraction task."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("ERROR: Set MISTRAL_API_KEY env var")
        sys.exit(1)

    client = Mistral(api_key=api_key)

    for model in MODELS:
        print(f"\n{'=' * 60}")
        print(f"Model: {model}")
        print(f"{'=' * 60}")

        start = time.time()
        try:
            response = client.chat.complete(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": TEST_INPUT},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            elapsed = time.time() - start
            content = response.choices[0].message.content
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens

            print(f"Latency: {elapsed:.2f}s")
            print(f"Tokens: {tokens_in} in / {tokens_out} out")

            # Validate JSON
            try:
                parsed = json.loads(content)
                print(f"Valid JSON: yes")
                print(f"Promises found: {len(parsed.get('promises', []))}")
                print(f"Contradictions found: {len(parsed.get('contradictions', []))}")
                print(f"\nFull response:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                print(f"Valid JSON: NO")
                print(f"Raw response: {content[:500]}")

        except Exception as e:
            elapsed = time.time() - start
            print(f"ERROR after {elapsed:.2f}s: {e}")

    print(f"\n{'=' * 60}")
    print("Test complete. If responses look good, base models work for the game.")
    print("Fine-tuning will improve accuracy and reduce cost/latency.")


if __name__ == "__main__":
    main()
