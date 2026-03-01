#!/usr/bin/env python3
"""Evaluate extraction models on the expanded test sets (145 examples).

Tests base models via Mistral API and the fine-tuned model via HF Inference Endpoint.
Prints a comparison table to stdout — no W&B required.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from mistralai import Mistral

DATA_DIR = Path(__file__).parent / "data" / "extraction"
DIFFICULTIES = ["easy", "medium", "hard"]
METRIC_KEYS = ["valid_json", "promise_count", "type_precision", "contradiction"]

SYSTEM_PROMPT = (
    "Extract promises from the mayor's speech as structured JSON. "
    "Return a JSON object with 'promises' (array of {text, type, impact, deadline}) "
    "and 'contradictions' (array of {promise1, promise2, explanation}). "
    "Types: ecology, economy, research. Impact: positive, negative. "
    "Deadline: immediate, by_round_3, by_round_5, by_end_of_game."
)


def load_test_set(difficulty: str) -> list[dict]:
    path = DATA_DIR / f"test_{difficulty}.jsonl"
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def parse_json_safe(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def evaluate_example(predicted: dict | None, expected: dict) -> dict[str, float]:
    if predicted is None:
        return {k: 0.0 for k in METRIC_KEYS}

    exp_promises = expected.get("promises", [])
    pred_promises = predicted.get("promises", [])

    promise_count = 1.0 if len(pred_promises) == len(exp_promises) else 0.0

    if not exp_promises:
        type_precision = 1.0 if not pred_promises else 0.0
    else:
        exp_types = sorted(p.get("type", "") for p in exp_promises)
        pred_types = sorted(p.get("type", "") for p in pred_promises)
        matches = sum(1 for e, p in zip(exp_types, pred_types) if e == p)
        type_precision = matches / len(exp_types)

    has_exp = len(expected.get("contradictions", [])) > 0
    has_pred = len(predicted.get("contradictions", [])) > 0
    contradiction = 1.0 if has_exp == has_pred else 0.0

    return {
        "valid_json": 1.0,
        "promise_count": promise_count,
        "type_precision": type_precision,
        "contradiction": contradiction,
    }


# ── Mistral API inference ──────────────────────────────────────────

def infer_mistral(client: Mistral, model: str, user_content: str) -> str | None:
    try:
        resp = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"    [API error: {e}]")
        return None


# ── HuggingFace Inference Endpoint ─────────────────────────────────

def infer_hf_endpoint(endpoint_url: str, hf_token: str, user_content: str) -> str | None:
    url = endpoint_url.rstrip("/") + "/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "tgi",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.01,
        "max_tokens": 1024,
        "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"    [HF endpoint error: {e}]")
        return None


# ── Evaluation loop ────────────────────────────────────────────────

def evaluate_examples(examples: list[dict], infer_fn) -> dict[str, float]:
    scores = {k: [] for k in METRIC_KEYS}
    for i, ex in enumerate(examples):
        user_content = ex["messages"][1]["content"]
        expected = json.loads(ex["messages"][2]["content"])

        raw = infer_fn(user_content)
        predicted = parse_json_safe(raw) if raw else None
        result = evaluate_example(predicted, expected)
        for k, v in result.items():
            scores[k].append(v)

        # Progress dot every 5 examples
        if (i + 1) % 5 == 0:
            print(f"    {i + 1}/{len(examples)}", flush=True)

    return {k: sum(v) / len(v) * 100 for k, v in scores.items()}


def print_table(rows: list[dict]):
    print()
    print("=" * 100)
    print(f"{'Model':<40} {'Diff':<8} {'#Ex':>4} {'Promise%':>10} {'Type%':>10} {'Contra%':>10} {'JSON%':>8}")
    print("=" * 100)
    for r in rows:
        print(
            f"{r['model']:<40} {r['diff']:<8} {r['n']:>4} "
            f"{r['promise_count']:>10.1f} {r['type_precision']:>10.1f} "
            f"{r['contradiction']:>10.1f} {r['valid_json']:>8.1f}"
        )
    print("=" * 100)

    # Aggregated per model
    models = sorted(set(r["model"] for r in rows))
    print()
    print("AGGREGATED (weighted by example count):")
    print("-" * 80)
    print(f"{'Model':<40} {'Promise%':>10} {'Type%':>10} {'Contra%':>10} {'JSON%':>8}")
    print("-" * 80)
    for model in models:
        model_rows = [r for r in rows if r["model"] == model]
        total_n = sum(r["n"] for r in model_rows)
        agg = {}
        for metric in METRIC_KEYS:
            agg[metric] = sum(r[metric] * r["n"] for r in model_rows) / total_n
        print(
            f"{model:<40} {agg['promise_count']:>10.1f} {agg['type_precision']:>10.1f} "
            f"{agg['contradiction']:>10.1f} {agg['valid_json']:>8.1f}"
        )
    print("-" * 80)


def main():
    mistral_key = os.environ.get("MISTRAL_API_KEY", "")
    hf_token = os.environ.get("HF_TOKEN", "")
    extraction_endpoint = os.environ.get("EXTRACTION_ENDPOINT", "")

    if not mistral_key:
        print("ERROR: MISTRAL_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = Mistral(api_key=mistral_key)

    # Define models to test
    models = []

    # Fine-tuned model via HF endpoint
    if extraction_endpoint and hf_token:
        models.append({
            "name": "8B-finetune (HF endpoint)",
            "infer": lambda uc: infer_hf_endpoint(extraction_endpoint, hf_token, uc),
        })
    else:
        print("WARN: EXTRACTION_ENDPOINT or HF_TOKEN not set, skipping fine-tuned model\n")

    # Base models via Mistral API
    for model_id in ["ministral-8b-latest", "mistral-small-latest", "mistral-large-latest"]:
        models.append({
            "name": model_id,
            "infer": lambda uc, m=model_id: infer_mistral(client, m, uc),
        })

    # Load test data
    test_sets = {}
    for diff in DIFFICULTIES:
        test_sets[diff] = load_test_set(diff)
        print(f"Loaded test_{diff}.jsonl: {len(test_sets[diff])} examples")
    total = sum(len(v) for v in test_sets.values())
    print(f"Total: {total} test examples\n")

    # Evaluate
    rows = []
    for model_info in models:
        name = model_info["name"]
        infer = model_info["infer"]
        for diff in DIFFICULTIES:
            examples = test_sets[diff]
            print(f"Evaluating {name} on {diff.upper()} ({len(examples)} examples)...")
            t0 = time.time()
            scores = evaluate_examples(examples, infer)
            elapsed = time.time() - t0
            print(f"  Done in {elapsed:.1f}s")
            rows.append({
                "model": name,
                "diff": diff.upper(),
                "n": len(examples),
                **scores,
            })

    print_table(rows)

    # Save results to JSON
    out_path = Path(__file__).parent / "eval_expanded_results.json"
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()