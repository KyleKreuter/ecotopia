"""Generate training data using AWS Bedrock Mistral models.

Demonstrates AWS Bedrock integration for the hackathon AWS sponsor prize.
Uses Mistral Large on Bedrock to generate high-quality training examples.
"""
import json
import os
from pathlib import Path

import boto3


def get_bedrock_client():
    """Create Bedrock runtime client."""
    return boto3.client(
        "bedrock-runtime",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def call_mistral_bedrock(client, prompt: str, system: str = "") -> str:
    """Call Mistral Large via AWS Bedrock."""
    messages = []
    if system:
        messages.append({
            "role": "user",
            "content": f"[System instruction: {system}]\n\n{prompt}",
        })
    else:
        messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.8,
    })

    response = client.invoke_model(
        modelId="mistral.mistral-large-2407-v1:0",
        body=body,
        contentType="application/json",
    )

    result = json.loads(response["body"].read())
    return result["choices"][0]["message"]["content"]


def generate_extraction_examples(client, count: int = 20) -> list[dict]:
    """Generate promise extraction training examples via Bedrock."""
    system = (
        "You are a data generator for a political simulation game called Ecotopia. "
        "Generate a realistic mayor's speech and the expected JSON extraction output. "
        "The output must contain: promises (array of {text, type, impact, deadline}) "
        "and contradictions (array of {promise1, promise2, explanation}). "
        "Types: ecology, economy, research. Impact: positive, negative. "
        "Deadline: short_term, medium_term, long_term."
    )

    examples = []
    scenarios = [
        "a mayor promising green energy investments",
        "a mayor cutting environmental regulations for economic growth",
        "a mayor making contradictory promises about taxes and spending",
        "a mayor focused on research and innovation",
        "a mayor promising everything to everyone (populist speech)",
        "a mayor giving a vague speech with no clear promises",
        "a mayor addressing a water crisis with specific actions",
        "a mayor responding to citizen protests about pollution",
        "a mayor proposing a new industrial zone near a nature reserve",
        "a mayor announcing education reforms with green curriculum",
    ]

    for i in range(min(count, len(scenarios))):
        prompt = f"""Generate a training example for scenario: {scenarios[i]}

Return ONLY valid JSON in this exact format:
{{
  "messages": [
    {{"role": "system", "content": "Extract promises from the mayor's speech as JSON."}},
    {{"role": "user", "content": "<the mayor's speech>"}},
    {{"role": "assistant", "content": "<JSON with promises and contradictions>"}}
  ]
}}"""

        try:
            result = call_mistral_bedrock(client, prompt, system)
            parsed = json.loads(result)
            if "messages" in parsed:
                examples.append(parsed)
                print(f"Generated example {i+1}/{count}: {scenarios[i][:50]}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed example {i+1}: {e}")

    return examples


def generate_citizens_examples(client, count: int = 20) -> list[dict]:
    """Generate citizen reaction training examples via Bedrock."""
    system = (
        "You are a data generator for a political simulation game called Ecotopia. "
        "Generate citizen reaction training data. Given promises, generate realistic "
        "citizen dialogues. Citizens have names, types (environmentalist, business_owner, "
        "student, worker, scientist), and react based on their archetype."
    )

    examples = []
    promise_sets = [
        "build solar panels on all public buildings",
        "cut corporate taxes by 20% to attract investment",
        "fund a new university research center for climate science",
        "ban single-use plastics within 2 years",
        "build a new highway through the nature reserve",
        "implement universal basic income pilot program",
        "close the coal power plant and replace with wind farms",
        "deregulate housing to allow more construction",
        "create a citizen science program for air quality monitoring",
        "privatize the water treatment facility",
    ]

    for i in range(min(count, len(promise_sets))):
        prompt = f"""Generate a training example for citizen reactions to this promise: "{promise_sets[i]}"

Return ONLY valid JSON in this exact format:
{{
  "messages": [
    {{"role": "system", "content": "Generate citizen reactions to the mayor's promises."}},
    {{"role": "user", "content": "<promises and game context>"}},
    {{"role": "assistant", "content": "<JSON with reactions array>"}}
  ]
}}"""

        try:
            result = call_mistral_bedrock(client, prompt, system)
            parsed = json.loads(result)
            if "messages" in parsed:
                examples.append(parsed)
                print(f"Generated citizen example {i+1}/{count}: {promise_sets[i][:50]}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed citizen example {i+1}: {e}")

    return examples


def main():
    """Generate training data using AWS Bedrock."""
    print("Connecting to AWS Bedrock...")
    client = get_bedrock_client()

    output_dir = Path("training/data/bedrock_generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nGenerating extraction examples...")
    extraction = generate_extraction_examples(client, count=10)
    with open(output_dir / "extraction_bedrock.jsonl", "w") as f:
        for ex in extraction:
            f.write(json.dumps(ex) + "\n")
    print(f"Saved {len(extraction)} extraction examples")

    print("\nGenerating citizens examples...")
    citizens = generate_citizens_examples(client, count=10)
    with open(output_dir / "citizens_bedrock.jsonl", "w") as f:
        for ex in citizens:
            f.write(json.dumps(ex) + "\n")
    print(f"Saved {len(citizens)} citizens examples")

    print(f"\nTotal: {len(extraction) + len(citizens)} examples generated via AWS Bedrock")
    print(f"Output: {output_dir}/")


if __name__ == "__main__":
    main()
