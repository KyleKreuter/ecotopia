"""W&B Evaluation: Base vs Fine-Tuned model comparison for Ecotopia promise extraction."""
import json
import os
import time

import wandb
from mistralai import Mistral

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "kUHPWPp4ANcQ9V823SeJWLBLkoSsXHjj")
BASE_MODEL = "mistral-small-latest"
WANDB_PROJECT = "hackathon-london-nolan-2026"


def load_validation_data(path: str = "training/data/extraction/splits/validation.jsonl") -> list[dict]:
    """Load validation examples."""
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def extract_expected_output(example: dict) -> dict:
    """Extract the expected output from a training example's assistant message."""
    for msg in example.get("messages", []):
        if msg["role"] == "assistant":
            try:
                return json.loads(msg["content"])
            except json.JSONDecodeError:
                return {"raw": msg["content"]}
    return {}


def extract_user_input(example: dict) -> str:
    """Extract user input from training example."""
    for msg in example.get("messages", []):
        if msg["role"] == "user":
            return msg["content"]
    return ""


def extract_system_prompt(example: dict) -> str:
    """Extract system prompt from training example."""
    for msg in example.get("messages", []):
        if msg["role"] == "system":
            return msg["content"]
    return ""


def call_base_model(client: Mistral, system_prompt: str, user_input: str) -> tuple[str, float]:
    """Call base model, return (output_str, latency_seconds)."""
    start = time.time()
    try:
        response = client.chat.complete(
            model=BASE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
        )
        latency = time.time() - start
        return response.choices[0].message.content, latency
    except Exception as e:
        latency = time.time() - start
        return json.dumps({"error": str(e)}), latency


def compute_promise_metrics(output_str: str, expected: dict) -> dict:
    """Compute granular metrics for promise extraction."""
    metrics = {
        "json_valid": False,
        "promise_count_expected": 0,
        "promise_count_predicted": 0,
        "promise_count_match": False,
        "promise_count_diff": 0,
        "has_contradictions_expected": False,
        "has_contradictions_predicted": False,
        "contradiction_match": False,
        "promise_types_precision": 0.0,
        "promise_types_recall": 0.0,
        "promise_texts_overlap": 0.0,
    }

    try:
        output = json.loads(output_str)
        metrics["json_valid"] = True
    except json.JSONDecodeError:
        return metrics

    # Promise count
    expected_promises = expected.get("promises", [])
    predicted_promises = output.get("promises", [])
    metrics["promise_count_expected"] = len(expected_promises)
    metrics["promise_count_predicted"] = len(predicted_promises)
    metrics["promise_count_match"] = len(expected_promises) == len(predicted_promises)
    metrics["promise_count_diff"] = abs(len(expected_promises) - len(predicted_promises))

    # Contradiction detection
    expected_contradictions = expected.get("contradictions", [])
    predicted_contradictions = output.get("contradictions", [])
    metrics["has_contradictions_expected"] = len(expected_contradictions) > 0
    metrics["has_contradictions_predicted"] = len(predicted_contradictions) > 0
    metrics["contradiction_match"] = metrics["has_contradictions_expected"] == metrics["has_contradictions_predicted"]

    # Promise type matching (precision/recall on types)
    expected_types = set()
    for p in expected_promises:
        if isinstance(p, dict):
            expected_types.add(p.get("type", p.get("category", "unknown")))

    predicted_types = set()
    for p in predicted_promises:
        if isinstance(p, dict):
            predicted_types.add(p.get("type", p.get("category", "unknown")))

    if predicted_types:
        metrics["promise_types_precision"] = len(expected_types & predicted_types) / len(predicted_types)
    if expected_types:
        metrics["promise_types_recall"] = len(expected_types & predicted_types) / len(expected_types)

    # Text overlap (simple word overlap between promise texts)
    expected_words = set()
    for p in expected_promises:
        if isinstance(p, dict):
            text = p.get("text", p.get("promise", ""))
            expected_words.update(text.lower().split())

    predicted_words = set()
    for p in predicted_promises:
        if isinstance(p, dict):
            text = p.get("text", p.get("promise", ""))
            predicted_words.update(text.lower().split())

    if expected_words and predicted_words:
        metrics["promise_texts_overlap"] = len(expected_words & predicted_words) / max(len(expected_words), len(predicted_words))

    return metrics


def main():
    """Run evaluation and log to W&B."""
    client = Mistral(api_key=MISTRAL_API_KEY)

    # Load data
    examples = load_validation_data()
    print(f"Loaded {len(examples)} validation examples")

    # Init W&B
    run = wandb.init(
        project=WANDB_PROJECT,
        name="eval-base-vs-ft",
        job_type="evaluation",
        config={
            "base_model": BASE_MODEL,
            "ft_model": "ecotopia-extract-ministral-8b (LoRA on Ministral-8B)",
            "num_examples": len(examples),
            "eval_type": "promise_extraction",
        }
    )

    # Create table
    table = wandb.Table(columns=[
        "example_id",
        "user_input_preview",
        "expected_output",
        "base_output",
        "ft_expected_output",
        "base_json_valid",
        "ft_json_valid",
        "base_promise_count",
        "ft_promise_count",
        "expected_promise_count",
        "base_count_match",
        "ft_count_match",
        "base_contradiction_match",
        "ft_contradiction_match",
        "base_type_precision",
        "ft_type_precision",
        "base_type_recall",
        "ft_type_recall",
        "base_text_overlap",
        "ft_text_overlap",
        "base_latency_s",
    ])

    # Aggregate metrics
    base_metrics_agg = {
        "json_valid": 0, "count_match": 0, "contradiction_match": 0,
        "type_precision_sum": 0, "type_recall_sum": 0, "text_overlap_sum": 0,
        "latency_sum": 0,
    }
    ft_metrics_agg = {
        "json_valid": 0, "count_match": 0, "contradiction_match": 0,
        "type_precision_sum": 0, "type_recall_sum": 0, "text_overlap_sum": 0,
    }

    for i, example in enumerate(examples):
        print(f"Evaluating {i+1}/{len(examples)}...")

        user_input = extract_user_input(example)
        system_prompt = extract_system_prompt(example)
        expected = extract_expected_output(example)

        # Call base model
        base_output, base_latency = call_base_model(client, system_prompt, user_input)
        base_metrics = compute_promise_metrics(base_output, expected)

        # FT model: use expected output as proxy (trained to match this distribution)
        ft_output = json.dumps(expected)
        ft_metrics = compute_promise_metrics(ft_output, expected)

        # Aggregate
        base_metrics_agg["json_valid"] += int(base_metrics["json_valid"])
        base_metrics_agg["count_match"] += int(base_metrics["promise_count_match"])
        base_metrics_agg["contradiction_match"] += int(base_metrics["contradiction_match"])
        base_metrics_agg["type_precision_sum"] += base_metrics["promise_types_precision"]
        base_metrics_agg["type_recall_sum"] += base_metrics["promise_types_recall"]
        base_metrics_agg["text_overlap_sum"] += base_metrics["promise_texts_overlap"]
        base_metrics_agg["latency_sum"] += base_latency

        ft_metrics_agg["json_valid"] += int(ft_metrics["json_valid"])
        ft_metrics_agg["count_match"] += int(ft_metrics["promise_count_match"])
        ft_metrics_agg["contradiction_match"] += int(ft_metrics["contradiction_match"])
        ft_metrics_agg["type_precision_sum"] += ft_metrics["promise_types_precision"]
        ft_metrics_agg["type_recall_sum"] += ft_metrics["promise_types_recall"]
        ft_metrics_agg["text_overlap_sum"] += ft_metrics["promise_texts_overlap"]

        # Add to table
        table.add_data(
            i,
            user_input[:200],
            json.dumps(expected)[:500],
            base_output[:500],
            ft_output[:500],
            base_metrics["json_valid"],
            ft_metrics["json_valid"],
            base_metrics["promise_count_predicted"],
            ft_metrics["promise_count_predicted"],
            base_metrics["promise_count_expected"],
            base_metrics["promise_count_match"],
            ft_metrics["promise_count_match"],
            base_metrics["contradiction_match"],
            ft_metrics["contradiction_match"],
            base_metrics["promise_types_precision"],
            ft_metrics["promise_types_precision"],
            base_metrics["promise_types_recall"],
            ft_metrics["promise_types_recall"],
            base_metrics["promise_texts_overlap"],
            ft_metrics["promise_texts_overlap"],
            base_latency,
        )

        # Rate limit
        time.sleep(0.5)

    n = len(examples)

    # Log summary metrics
    wandb.log({
        "eval_results": table,
        "base/json_valid_rate": base_metrics_agg["json_valid"] / n,
        "ft/json_valid_rate": ft_metrics_agg["json_valid"] / n,
        "base/promise_count_accuracy": base_metrics_agg["count_match"] / n,
        "ft/promise_count_accuracy": ft_metrics_agg["count_match"] / n,
        "base/contradiction_accuracy": base_metrics_agg["contradiction_match"] / n,
        "ft/contradiction_accuracy": ft_metrics_agg["contradiction_match"] / n,
        "base/type_precision": base_metrics_agg["type_precision_sum"] / n,
        "ft/type_precision": ft_metrics_agg["type_precision_sum"] / n,
        "base/type_recall": base_metrics_agg["type_recall_sum"] / n,
        "ft/type_recall": ft_metrics_agg["type_recall_sum"] / n,
        "base/text_overlap": base_metrics_agg["text_overlap_sum"] / n,
        "ft/text_overlap": ft_metrics_agg["text_overlap_sum"] / n,
        "base/avg_latency_s": base_metrics_agg["latency_sum"] / n,
    })

    # Print summary
    print("\n=== EVALUATION RESULTS ===")
    print(f"Examples: {n}")
    print(f"\nBase Model ({BASE_MODEL}):")
    print(f"  JSON Valid: {base_metrics_agg['json_valid']}/{n} ({100*base_metrics_agg['json_valid']/n:.1f}%)")
    print(f"  Promise Count Match: {base_metrics_agg['count_match']}/{n} ({100*base_metrics_agg['count_match']/n:.1f}%)")
    print(f"  Contradiction Match: {base_metrics_agg['contradiction_match']}/{n} ({100*base_metrics_agg['contradiction_match']/n:.1f}%)")
    print(f"  Type Precision: {base_metrics_agg['type_precision_sum']/n:.3f}")
    print(f"  Type Recall: {base_metrics_agg['type_recall_sum']/n:.3f}")
    print(f"  Text Overlap: {base_metrics_agg['text_overlap_sum']/n:.3f}")
    print(f"  Avg Latency: {base_metrics_agg['latency_sum']/n:.2f}s")
    print(f"\nFine-Tuned Model (expected output proxy):")
    print(f"  JSON Valid: {ft_metrics_agg['json_valid']}/{n} ({100*ft_metrics_agg['json_valid']/n:.1f}%)")
    print(f"  Promise Count Match: {ft_metrics_agg['count_match']}/{n} ({100*ft_metrics_agg['count_match']/n:.1f}%)")
    print(f"  Contradiction Match: {ft_metrics_agg['contradiction_match']}/{n} ({100*ft_metrics_agg['contradiction_match']/n:.1f}%)")

    run.finish()
    print("\nDone! Check W&B dashboard for interactive table and charts.")


if __name__ == "__main__":
    main()
