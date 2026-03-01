"""Run Weave evaluations for Ecotopia extraction and citizens tasks."""

import json
import os
import time
import httpx
import asyncio

# Set MISTRAL_API_KEY and WANDB_API_KEY env vars before running

import weave

DATA_DIR = "/root/clawd/hackathon-workspace/ecotopia/training/data"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-large-latest"
MISTRAL_KEY = os.environ["MISTRAL_API_KEY"]


import re


def strip_markdown_json(text: str) -> str:
    """Strip markdown code fences from JSON responses."""
    text = text.strip()
    m = re.match(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def call_mistral(messages: list[dict]) -> str:
    """Call Mistral API and return the response text."""
    resp = httpx.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {MISTRAL_KEY}", "Content-Type": "application/json"},
        json={"model": MISTRAL_MODEL, "messages": messages, "temperature": 0.3, "response_format": {"type": "json_object"}},
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return strip_markdown_json(content)


def load_jsonl(path: str) -> list[dict]:
    """Load a JSONL file."""
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# Extraction

@weave.op()
def extract_promises(system_prompt: str, user_prompt: str) -> dict:
    """Call Mistral Large for promise extraction."""
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    response = call_mistral(messages)
    time.sleep(0.5)
    return {"response": response}


@weave.op()
def extraction_valid_json(response: str, expected: str) -> dict:
    """Check if response is valid JSON."""
    try:
        json.loads(response)
        return {"json_valid": True}
    except Exception:
        return {"json_valid": False}


@weave.op()
def extraction_promise_count(response: str, expected: str) -> dict:
    """Check if promise count matches expected."""
    try:
        pred = json.loads(response)
        exp = json.loads(expected)
        pred_count = len(pred.get("promises", []))
        exp_count = len(exp.get("promises", []))
        return {"promise_count_match": pred_count == exp_count, "predicted": pred_count, "expected": exp_count}
    except Exception:
        return {"promise_count_match": False}


@weave.op()
def extraction_type_precision(response: str, expected: str) -> dict:
    """Check if promise types match."""
    try:
        pred = json.loads(response)
        exp = json.loads(expected)
        pred_types = sorted([p.get("type", "") for p in pred.get("promises", [])])
        exp_types = sorted([p.get("type", "") for p in exp.get("promises", [])])
        if not exp_types:
            return {"type_precision": 1.0}
        matches = sum(1 for p, e in zip(pred_types, exp_types) if p == e)
        return {"type_precision": matches / max(len(exp_types), 1)}
    except Exception:
        return {"type_precision": 0.0}


@weave.op()
def extraction_contradiction_detection(response: str, expected: str) -> dict:
    """Check if contradictions are detected correctly."""
    try:
        pred = json.loads(response)
        exp = json.loads(expected)
        pred_has = len(pred.get("contradictions", [])) > 0
        exp_has = len(exp.get("contradictions", [])) > 0
        return {"contradiction_detection": pred_has == exp_has}
    except Exception:
        return {"contradiction_detection": False}


# Citizens

@weave.op()
def generate_citizens(system_prompt: str, user_prompt: str) -> dict:
    """Call Mistral Large for citizen reactions."""
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    response = call_mistral(messages)
    time.sleep(0.5)
    return {"response": response}


@weave.op()
def citizens_valid_json(response: str, expected: str) -> dict:
    """Check if response is valid JSON."""
    try:
        json.loads(response)
        return {"json_valid": True}
    except Exception:
        return {"json_valid": False}


@weave.op()
def citizens_has_reactions(response: str, expected: str) -> dict:
    """Check if response has citizen reactions."""
    try:
        data = json.loads(response)
        has = len(data.get("citizen_reactions", [])) > 0
        return {"has_reactions": has}
    except Exception:
        return {"has_reactions": False}


@weave.op()
def citizens_schema_compliance(response: str, expected: str) -> dict:
    """Check if response follows expected schema."""
    try:
        data = json.loads(response)
        required_keys = {"citizen_reactions"}
        has_keys = required_keys.issubset(set(data.keys()))
        if has_keys and data["citizen_reactions"]:
            r = data["citizen_reactions"][0]
            has_fields = all(k in r for k in ["citizen_name", "dialogue", "tone", "approval_delta"])
        else:
            has_fields = False
        return {"schema_compliance": has_keys and has_fields}
    except Exception:
        return {"schema_compliance": False}


def build_extraction_dataset() -> list[dict]:
    """Load all extraction test data."""
    dataset = []
    for difficulty in ["test_easy", "test_medium", "test_hard"]:
        path = f"{DATA_DIR}/extraction/{difficulty}.jsonl"
        for item in load_jsonl(path):
            msgs = item["messages"]
            system_prompt = msgs[0]["content"]
            user_prompt = msgs[1]["content"]
            expected = msgs[2]["content"]
            dataset.append({
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "expected": expected,
            })
    return dataset


def build_citizens_dataset() -> list[dict]:
    """Load citizens validation data (first 15)."""
    dataset = []
    path = f"{DATA_DIR}/citizens/splits/validation.jsonl"
    for item in load_jsonl(path)[:15]:
        msgs = item["messages"]
        system_prompt = msgs[0]["content"]
        user_prompt = msgs[1]["content"]
        expected = msgs[2]["content"]
        dataset.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "expected": expected,
        })
    return dataset


class ExtractionScorer(weave.Scorer):
    """Scorer for extraction evaluation."""

    @weave.op()
    def score(self, output: dict, expected: str) -> dict:
        response = output.get("response", "")
        results = {}
        # valid json
        try:
            json.loads(response)
            results["json_valid"] = True
        except Exception:
            results["json_valid"] = False
            return results

        try:
            pred = json.loads(response)
            exp = json.loads(expected)
        except Exception:
            results["promise_count_match"] = False
            results["type_precision"] = 0.0
            results["contradiction_detection"] = False
            return results

        # promise count
        pred_count = len(pred.get("promises", []))
        exp_count = len(exp.get("promises", []))
        results["promise_count_match"] = pred_count == exp_count

        # type precision
        pred_types = sorted([p.get("type", "") for p in pred.get("promises", [])])
        exp_types = sorted([p.get("type", "") for p in exp.get("promises", [])])
        if exp_types:
            matches = sum(1 for p, e in zip(pred_types, exp_types) if p == e)
            results["type_precision"] = matches / len(exp_types)
        else:
            results["type_precision"] = 1.0

        # contradiction detection
        pred_has = len(pred.get("contradictions", [])) > 0
        exp_has = len(exp.get("contradictions", [])) > 0
        results["contradiction_detection"] = pred_has == exp_has

        return results


class CitizensScorer(weave.Scorer):
    """Scorer for citizens evaluation."""

    @weave.op()
    def score(self, output: dict, expected: str) -> dict:
        response = output.get("response", "")
        results = {}
        try:
            data = json.loads(response)
            results["json_valid"] = True
        except Exception:
            return {"json_valid": False, "has_reactions": False, "schema_compliance": False}

        reactions = data.get("citizen_reactions", [])
        results["has_reactions"] = len(reactions) > 0

        if reactions:
            r = reactions[0]
            results["schema_compliance"] = all(
                k in r for k in ["citizen_name", "dialogue", "tone", "approval_delta"]
            )
        else:
            results["schema_compliance"] = False

        return results


async def run_extraction_eval():
    """Run extraction evaluation."""
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
    """Run citizens evaluation."""
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
