"""Weave-traced Mistral API calls for Ecotopia game pipeline."""

import json
import os
from pathlib import Path

import weave
from mistralai import Mistral

weave.init("ecotopia-hackathon")

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str, fallback: str) -> str:
    """Load a prompt file or return fallback text."""
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return fallback


@weave.op
def extract_promises(speech: str, game_context: str) -> dict:
    """Extract promises from player speech using Mistral."""
    model = os.environ.get("EXTRACTION_MODEL", "mistral-small-latest")
    system_prompt = _load_prompt(
        "extraction.txt",
        "Extract promises from the mayor's speech as JSON.",
    )
    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Game context: {game_context}\n\nMayor's speech: {speech}",
            },
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw) if isinstance(raw, str) else raw


@weave.op
def generate_citizen_reactions(promises_json: str, game_context: str) -> dict:
    """Generate citizen reactions using Mistral."""
    model = os.environ.get("CITIZENS_MODEL", "mistral-small-latest")
    system_prompt = _load_prompt(
        "citizens.txt",
        "Generate citizen reactions to the mayor's promises as JSON.",
    )
    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Promises: {promises_json}\n\nGame context: {game_context}",
            },
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw) if isinstance(raw, str) else raw


@weave.op
def process_turn(speech: str, game_context: str) -> dict:
    """Full turn pipeline: extract -> react."""
    extraction = extract_promises(speech, game_context)
    extraction_str = json.dumps(extraction) if isinstance(extraction, dict) else extraction
    reactions = generate_citizen_reactions(extraction_str, game_context)
    return {"extraction": extraction, "reactions": reactions}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run a traced Ecotopia turn")
    parser.add_argument("--speech", required=True, help="Mayor speech text")
    parser.add_argument("--context", default="{}", help="Game context JSON string")
    args = parser.parse_args()

    result = process_turn(args.speech, args.context)
    print(json.dumps(result, indent=2, ensure_ascii=False))
