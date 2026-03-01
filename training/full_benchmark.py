"""Full benchmark: base models on extraction task.

Evaluates Ministral 8B, Mistral Small, Mistral Large on validation set.
Logs all results to W&B with comparison tables and summary metrics.
"""

import json
import os
import time
from pathlib import Path

import wandb
from mistralai import Mistral

MODELS = [
    ("ministral-8b-latest", "Ministral 8B (base)"),
    ("mistral-small-latest", "Mistral Small 22B (base)"),
    ("mistral-large-latest", "Mistral Large (base)"),
]
METRIC_KEYS = ["promise_count_correct", "type_precision", "contradiction_correct", "valid_json"]


def evaluate_extraction(client: Mistral, model_id: str, label: str, examples: list[dict]) -> dict:
    """Evaluate a model on extraction task, returning counts and percentages."""
    results = {
        "model": label,
        "promise_count_correct": 0,
        "type_precision": 0,
        "contradiction_correct": 0,
        "valid_json": 0,
        "total": len(examples),
        "errors": 0,
        "latencies": [],
    }

    for i, ex in enumerate(examples):
        system_msg = user_msg = expected = ""
        for msg in ex.get("messages", []):
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant":
                expected = msg["content"]

        try:
            start = time.time()
            response = client.chat.complete(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )
            results["latencies"].append(time.time() - start)

            content = response.choices[0].message.content
            try:
                pred = json.loads(content)
                results["valid_json"] += 1

                exp = json.loads(expected)

                if len(pred.get("promises", [])) == len(exp.get("promises", [])):
                    results["promise_count_correct"] += 1

                if set(p.get("type", "") for p in pred.get("promises", [])) == set(p.get("type", "") for p in exp.get("promises", [])):
                    results["type_precision"] += 1

                if (len(pred.get("contradictions", [])) > 0) == (len(exp.get("contradictions", [])) > 0):
                    results["contradiction_correct"] += 1
            except json.JSONDecodeError:
                pass

            time.sleep(0.3)
            if (i + 1) % 10 == 0:
                print(f"  {label}: {i+1}/{len(examples)}")

        except Exception as e:
            results["errors"] += 1
            print(f"  Error on example {i}: {e}")
            time.sleep(1)

    total = results["total"]
    results["promise_count_pct"] = results["promise_count_correct"] / total * 100 if total else 0
    results["type_precision_pct"] = results["type_precision"] / total * 100 if total else 0
    results["contradiction_pct"] = results["contradiction_correct"] / total * 100 if total else 0
    results["valid_json_pct"] = results["valid_json"] / total * 100 if total else 0
    results["avg_latency"] = sum(results["latencies"]) / len(results["latencies"]) if results["latencies"] else 0

    return results


def main():
    """Run full benchmark across all models and log to W&B."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")

    client = Mistral(api_key=api_key)

    val_path = Path("training/data/extraction/splits/validation.jsonl")
    examples = []
    with open(val_path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    print(f"Loaded {len(examples)} extraction validation examples")

    run = wandb.init(
        project="hackathon-london-nolan-2026",
        name="full-benchmark-extraction",
        job_type="evaluation",
        tags=["benchmark", "extraction", "comparison"],
    )

    all_results = []
    for model_id, label in MODELS:
        print(f"\nEvaluating {label}...")
        result = evaluate_extraction(client, model_id, label, examples)
        all_results.append(result)
        print(f"  Promise count: {result['promise_count_pct']:.1f}%")
        print(f"  Type precision: {result['type_precision_pct']:.1f}%")
        print(f"  Contradiction: {result['contradiction_pct']:.1f}%")
        print(f"  Valid JSON: {result['valid_json_pct']:.1f}%")
        print(f"  Avg latency: {result['avg_latency']:.3f}s")

    table = wandb.Table(
        columns=["Model", "Promise Count %", "Type Precision %",
                 "Contradiction %", "Valid JSON %", "Avg Latency (s)", "Errors"],
    )
    for r in all_results:
        table.add_data(
            r["model"],
            round(r["promise_count_pct"], 1),
            round(r["type_precision_pct"], 1),
            round(r["contradiction_pct"], 1),
            round(r["valid_json_pct"], 1),
            round(r["avg_latency"], 3),
            r["errors"],
        )
    run.log({"extraction_benchmark": table})

    for r in all_results:
        prefix = r["model"].replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").lower()
        run.summary[f"{prefix}/promise_count"] = r["promise_count_pct"]
        run.summary[f"{prefix}/type_precision"] = r["type_precision_pct"]
        run.summary[f"{prefix}/contradiction"] = r["contradiction_pct"]
        run.summary[f"{prefix}/valid_json"] = r["valid_json_pct"]

    run.finish()
    print(f"\nW&B run: {run.url}")


if __name__ == "__main__":
    main()
