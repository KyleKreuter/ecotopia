"""Run Weave evaluations for Ecotopia extraction and citizens tasks.

Uses W&B Weave framework to evaluate Mistral Large on extraction (promise parsing)
and citizens (reaction generation) validation datasets with structured scorers.
"""

import asyncio
import json
import os
import re
import time

import httpx
import weave

DATA_DIR = "/root/clawd/hackathon-workspace/ecotopia/training/data"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-large-latest"


def strip_markdown_json(text: str) -> str:
    """Strip markdown code fences from JSON responses."""
    text = text.strip()
    m = re.match(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def call_mistral(messages: list[dict]) -> str:
    """Call Mistral API and return the response text."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")

    resp = httpx.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": MISTRAL_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return strip_markdown_json(content)


def load_jsonl(path: str) -> list[dict]:
    """Load a JSONL file."""
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# Extraction scorers and dataset

class ExtractionScorer(weave.Scorer):
    """Scorer for extraction evaluation: JSON validity, promise count, type precision, contradictions."""

    @weave.op()
    def score(self, output: dict, expected: str) -> dict:
        """Score extraction output against expected JSON."""
        response = output.get("response", "")
        results = {}

        try:
            pred = json.loads(response)
            results["json_valid"] = True
        except (json.JSONDecodeError, ValueError):
            return {"json_valid": False, "promise_count_match": False, "type_precision": 0.0, "contradiction_detection": False}

        try:
            exp = json.loads(expected)
        except (json.JSONDecodeError, ValueError):
            return {"json_valid": True, "promise_count_match": False, "type_precision": 0.0, "contradiction_detection": False}

        pred_promises = pred.get("promises", [])
        exp_promises = exp.get("promises", [])
        results["promise_count_match"] = len(pred_promises) == len(exp_promises)

        if exp_promises:
            pred_types = sorted(p.get("type", "") for p in pred_promises)
            exp_types = sorted(p.get("type", "") for p in exp_promises)
            matches = sum(1 for p, e in zip(pred_types, exp_types) if p == e)
            results["type_precision"] = matches / len(exp_types)
        else:
            results["type_precision"] = 1.0

        results["contradiction_detection"] = (len(pred.get("contradictions", [])) > 0) == (len(exp.get("contradictions", [])) > 0)

        return results


class CitizensScorer(weave.Scorer):
    """Scorer for citizens evaluation: JSON validity, reactions presence, schema compliance."""

    @weave.op()
    def score(self, output: dict, expected: str) -> dict:
        """Score citizens output against expected schema."""
        response = output.get("response", "")
        try:
            data = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return {"json_valid": False, "has_reactions": False, "schema_compliance": False}

        reactions = data.get("citizen_reactions", [])
        has_reactions = len(reactions) > 0

        schema_ok = False
        if has_reactions:
            r = reactions[0]
            schema_ok = all(k in r for k in ["citizen_name", "dialogue", "tone", "approval_delta"])

        return {"json_valid": True, "has_reactions": has_reactions, "schema_compliance": schema_ok}


def build_extraction_dataset() -> list[dict]:
    """Load all extraction test data."""
    dataset = []
    for difficulty in ["test_easy", "test_medium", "test_hard"]:
        path = f"{DATA_DIR}/extraction/{difficulty}.jsonl"
        for item in load_jsonl(path):
            msgs = item["messages"]
            dataset.append({
                "system_prompt": msgs[0]["content"],
                "user_prompt": msgs[1]["content"],
                "expected": msgs[2]["content"],
            })
    return dataset


def build_citizens_dataset() -> list[dict]:
    """Load citizens validation data (first 15 examples)."""
    dataset = []
    path = f"{DATA_DIR}/citizens/splits/validation.jsonl"
    for item in load_jsonl(path)[:15]:
        msgs = item["messages"]
        dataset.append({
            "system_prompt": msgs[0]["content"],
            "user_prompt": msgs[1]["content"],
            "expected": msgs[2]["content"],
        })
    return dataset


async def run_extraction_eval():
    """Run extraction evaluation with Weave."""
    dataset = build_extraction_dataset()
    print(f"Extraction dataset: {len(dataset)} examples")

    @weave.op()
    async def predict(system_prompt: str, user_prompt: str) -> dict:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response = call_mistral(messages)
        time.sleep(0.5)
        return {"response": response}

    evaluation = weave.Evaluation(
        name="Extraction: Mistral Large (base)",
        dataset=dataset,
        scorers=[ExtractionScorer()],
    )
    results = await evaluation.evaluate(predict)
    print(f"Extraction results: {results}")
    return results


async def run_citizens_eval():
    """Run citizens evaluation with Weave."""
    dataset = build_citizens_dataset()
    print(f"Citizens dataset: {len(dataset)} examples")

    @weave.op()
    async def predict(system_prompt: str, user_prompt: str) -> dict:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response = call_mistral(messages)
        time.sleep(0.5)
        return {"response": response}

    evaluation = weave.Evaluation(
        name="Citizens: Mistral Large (base)",
        dataset=dataset,
        scorers=[CitizensScorer()],
    )
    results = await evaluation.evaluate(predict)
    print(f"Citizens results: {results}")
    return results


async def main():
    """Run both extraction and citizens Weave evaluations."""
    weave.init("nolancacheux/hackathon-london-nolan-2026")

    print("=" * 60)
    print("Running Extraction evaluation...")
    print("=" * 60)
    ext_results = await run_extraction_eval()

    print("=" * 60)
    print("Running Citizens evaluation...")
    print("=" * 60)
    cit_results = await run_citizens_eval()

    print("\n" + "=" * 60)
    print("ALL DONE")
    print(f"Extraction: {ext_results}")
    print(f"Citizens: {cit_results}")


if __name__ == "__main__":
    asyncio.run(main())
