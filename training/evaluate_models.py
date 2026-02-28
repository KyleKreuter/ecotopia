"""Evaluate fine-tuned vs base models on Ecotopia extraction tasks.

Runs inference on held-out validation examples, computes precision/recall/F1
for promise extraction and contradiction detection, and logs everything to W&B.

Usage:
    python training/evaluate_models.py --task extraction \
        --models ft:ft_model_id_1,ft:ft_model_id_2,base:mistral-large-latest
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import wandb
from dotenv import load_dotenv
from mistralai import Mistral

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

PRICE_PER_MILLION = {
    "ministral-8b-latest": {"input": 0.1, "output": 0.1},
    "open-mistral-nemo": {"input": 0.15, "output": 0.15},
    "mistral-large-latest": {"input": 2.0, "output": 6.0},
}

DEFAULT_PRICE = {"input": 1.0, "output": 3.0}


@dataclass
class EvalResult:
    """Aggregated evaluation result for a single model."""

    model_id: str
    total_examples: int = 0
    valid_json_count: int = 0
    promise_tp: int = 0
    promise_fp: int = 0
    promise_fn: int = 0
    contradiction_tp: int = 0
    contradiction_fp: int = 0
    contradiction_fn: int = 0
    confidence_errors: list[float] = field(default_factory=list)
    latencies: list[float] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    predictions: list[dict] = field(default_factory=list)

    @property
    def json_validity_rate(self) -> float:
        """Fraction of responses that parsed as valid JSON."""
        if self.total_examples == 0:
            return 0.0
        return self.valid_json_count / self.total_examples

    @property
    def avg_latency(self) -> float:
        """Mean response time in seconds."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    @property
    def confidence_mae(self) -> float:
        """Mean absolute error of confidence scores."""
        if not self.confidence_errors:
            return 0.0
        return sum(self.confidence_errors) / len(self.confidence_errors)

    def _prf(self, tp: int, fp: int, fn: int) -> dict[str, float]:
        """Compute precision, recall, and F1 from raw counts."""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}

    @property
    def promise_metrics(self) -> dict[str, float]:
        """Precision, recall, F1 for promise extraction."""
        return self._prf(self.promise_tp, self.promise_fp, self.promise_fn)

    @property
    def contradiction_metrics(self) -> dict[str, float]:
        """Precision, recall, F1 for contradiction detection."""
        return self._prf(self.contradiction_tp, self.contradiction_fp, self.contradiction_fn)

    def estimated_cost(self) -> float:
        """Estimated API cost in USD."""
        base_model = self.model_id.split(":")[-1] if ":" in self.model_id else self.model_id
        prices = PRICE_PER_MILLION.get(base_model, DEFAULT_PRICE)
        return (
            self.input_tokens * prices["input"] / 1_000_000
            + self.output_tokens * prices["output"] / 1_000_000
        )

    def summary(self) -> dict:
        """Full metrics dictionary for logging."""
        pm = self.promise_metrics
        cm = self.contradiction_metrics
        return {
            "model": self.model_id,
            "json_validity_rate": round(self.json_validity_rate, 4),
            "promise_precision": round(pm["precision"], 4),
            "promise_recall": round(pm["recall"], 4),
            "promise_f1": round(pm["f1"], 4),
            "contradiction_precision": round(cm["precision"], 4),
            "contradiction_recall": round(cm["recall"], 4),
            "contradiction_f1": round(cm["f1"], 4),
            "confidence_mae": round(self.confidence_mae, 4),
            "avg_latency_s": round(self.avg_latency, 3),
            "total_examples": self.total_examples,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost_usd": round(self.estimated_cost(), 6),
        }


def word_overlap(a: str, b: str) -> float:
    """Compute word-level Jaccard-like overlap between two strings."""
    words_a = set(a.lower().strip().split())
    words_b = set(b.lower().strip().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    smaller = min(len(words_a), len(words_b))
    return len(intersection) / smaller if smaller > 0 else 0.0


def match_promises(
    predicted: list[dict], expected: list[dict], result: EvalResult
) -> None:
    """Match predicted promises against expected using fuzzy text overlap.

    Updates result.promise_tp/fp/fn and confidence_errors in place.
    """
    matched_expected: set[int] = set()

    for pred in predicted:
        pred_text = pred.get("text", "")
        best_idx = -1
        best_overlap = 0.0

        for i, exp in enumerate(expected):
            if i in matched_expected:
                continue
            overlap = word_overlap(pred_text, exp.get("text", ""))
            if overlap > best_overlap:
                best_overlap = overlap
                best_idx = i

        if best_overlap >= 0.8 and best_idx >= 0:
            result.promise_tp += 1
            matched_expected.add(best_idx)
            # Confidence calibration
            pred_conf = pred.get("confidence", 0.5)
            exp_conf = expected[best_idx].get("confidence", 0.5)
            result.confidence_errors.append(abs(pred_conf - exp_conf))
        else:
            result.promise_fp += 1

    result.promise_fn += len(expected) - len(matched_expected)


def match_contradictions(
    predicted: list[dict], expected: list[dict], result: EvalResult
) -> None:
    """Match predicted contradictions against expected by severity + description.

    Updates result.contradiction_tp/fp/fn in place.
    """
    matched_expected: set[int] = set()

    for pred in predicted:
        pred_sev = pred.get("severity", "").lower().strip()
        pred_desc = pred.get("description", "")
        best_idx = -1
        best_score = 0.0

        for i, exp in enumerate(expected):
            if i in matched_expected:
                continue
            exp_sev = exp.get("severity", "").lower().strip()
            if pred_sev != exp_sev:
                continue
            overlap = word_overlap(pred_desc, exp.get("description", ""))
            if overlap > best_score:
                best_score = overlap
                best_idx = i

        if best_score >= 0.5 and best_idx >= 0:
            result.contradiction_tp += 1
            matched_expected.add(best_idx)
        else:
            result.contradiction_fp += 1

    result.contradiction_fn += len(expected) - len(matched_expected)


def load_validation_data(task: str) -> list[dict]:
    """Load validation examples from the splits directory.

    Returns list of dicts with 'messages' key (system + user + assistant).
    """
    val_path = SCRIPT_DIR / "data" / task / "splits" / "validation.jsonl"
    if not val_path.exists():
        print(f"ERROR: Validation file not found: {val_path}", file=sys.stderr)
        sys.exit(1)

    examples = []
    with open(val_path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    print(f"Loaded {len(examples)} validation examples from {val_path}")
    return examples


def load_models_from_jobs(task: str) -> list[str]:
    """Read fine-tuned model IDs from ft_jobs.json if available."""
    jobs_path = SCRIPT_DIR / "data" / task / "splits" / "ft_jobs.json"
    if not jobs_path.exists():
        print(f"WARNING: {jobs_path} not found, no default models available", file=sys.stderr)
        return []

    with open(jobs_path) as f:
        jobs = json.load(f)

    model_ids = []
    if isinstance(jobs, list):
        for job in jobs:
            mid = job.get("fine_tuned_model") or job.get("model_id")
            if mid:
                model_ids.append(f"ft:{mid}")
    elif isinstance(jobs, dict):
        for _, job in jobs.items():
            mid = job.get("fine_tuned_model") or job.get("model_id")
            if mid:
                model_ids.append(f"ft:{mid}")

    return model_ids


def parse_model_spec(spec: str) -> tuple[str, str]:
    """Parse 'prefix:model_id' into (prefix, model_id).

    Prefix is 'ft' for fine-tuned or 'base' for base models.
    If no prefix, assumes 'ft'.
    """
    if ":" in spec:
        prefix, model_id = spec.split(":", 1)
        return prefix, model_id
    return "ft", spec


def run_inference(
    client: Mistral,
    model_id: str,
    messages: list[dict],
    max_retries: int = 3,
) -> tuple[str, float, int, int]:
    """Run inference on a single example with retries.

    Args:
        client: Mistral client instance.
        model_id: Model to query.
        messages: System + user messages (no assistant).
        max_retries: Number of retry attempts on failure.

    Returns:
        Tuple of (response_text, latency_seconds, input_tokens, output_tokens).
    """
    for attempt in range(max_retries):
        try:
            start = time.monotonic()
            response = client.chat.complete(
                model=model_id,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            latency = time.monotonic() - start

            content = response.choices[0].message.content or ""
            usage = response.usage
            return (
                content,
                latency,
                usage.prompt_tokens if usage else 0,
                usage.completion_tokens if usage else 0,
            )
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(
                f"  Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {wait}s...",
                file=sys.stderr,
            )
            time.sleep(wait)

    return "", 0.0, 0, 0


def evaluate_model(
    client: Mistral,
    model_id: str,
    examples: list[dict],
) -> EvalResult:
    """Run evaluation for a single model across all examples.

    Args:
        client: Mistral client instance.
        model_id: Model identifier to evaluate.
        examples: Validation examples with messages and expected output.

    Returns:
        Populated EvalResult with all metrics.
    """
    result = EvalResult(model_id=model_id)

    for i, example in enumerate(examples):
        result.total_examples += 1
        messages = example["messages"]

        # Separate input (system + user) from expected output (assistant)
        input_messages = [m for m in messages if m["role"] != "assistant"]
        expected_raw = next(
            (m["content"] for m in messages if m["role"] == "assistant"), "{}"
        )

        try:
            expected = json.loads(expected_raw)
        except json.JSONDecodeError:
            expected = {}

        response_text, latency, in_tokens, out_tokens = run_inference(
            client, model_id, input_messages
        )

        result.latencies.append(latency)
        result.input_tokens += in_tokens
        result.output_tokens += out_tokens

        # Parse response
        predicted = {}
        if response_text:
            try:
                predicted = json.loads(response_text)
                result.valid_json_count += 1
            except json.JSONDecodeError:
                pass

        # Match promises
        expected_promises = expected.get("promises", [])
        predicted_promises = predicted.get("promises", [])
        match_promises(predicted_promises, expected_promises, result)

        # Match contradictions
        expected_contradictions = expected.get("contradictions", [])
        predicted_contradictions = predicted.get("contradictions", [])
        match_contradictions(predicted_contradictions, expected_contradictions, result)

        # Store prediction for logging
        result.predictions.append({
            "index": i,
            "expected": expected,
            "predicted": predicted,
            "valid_json": bool(predicted),
            "latency": round(latency, 3),
        })

        if (i + 1) % 10 == 0:
            print(f"  [{model_id}] {i + 1}/{len(examples)} done")

    return result


def log_to_wandb(results: list[EvalResult], task: str) -> None:
    """Log all evaluation results to Weights & Biases.

    Creates summary metrics, comparison tables, and example predictions.
    """
    run = wandb.init(
        project="ecotopia-ft",
        name=f"{task}-eval",
        config={"task": task, "models": [r.model_id for r in results]},
    )

    # Summary metrics table
    summary_table = wandb.Table(
        columns=[
            "model", "json_validity", "promise_p", "promise_r", "promise_f1",
            "contradiction_p", "contradiction_r", "contradiction_f1",
            "confidence_mae", "avg_latency", "cost_usd",
        ]
    )
    for r in results:
        s = r.summary()
        summary_table.add_data(
            s["model"], s["json_validity_rate"],
            s["promise_precision"], s["promise_recall"], s["promise_f1"],
            s["contradiction_precision"], s["contradiction_recall"], s["contradiction_f1"],
            s["confidence_mae"], s["avg_latency_s"], s["estimated_cost_usd"],
        )
        # Log per-model scalar metrics
        prefix = r.model_id.replace(":", "_").replace("/", "_")
        wandb.log({
            f"{prefix}/promise_f1": s["promise_f1"],
            f"{prefix}/contradiction_f1": s["contradiction_f1"],
            f"{prefix}/json_validity": s["json_validity_rate"],
            f"{prefix}/avg_latency": s["avg_latency_s"],
            f"{prefix}/cost_usd": s["estimated_cost_usd"],
        })

    wandb.log({"model_comparison": summary_table})

    # Example predictions table (first 20 per model)
    pred_table = wandb.Table(
        columns=["model", "index", "expected", "predicted", "valid_json", "latency"]
    )
    for r in results:
        for p in r.predictions[:20]:
            pred_table.add_data(
                r.model_id, p["index"],
                json.dumps(p["expected"], ensure_ascii=False)[:500],
                json.dumps(p["predicted"], ensure_ascii=False)[:500],
                p["valid_json"], p["latency"],
            )
    wandb.log({"predictions": pred_table})

    # Bar charts for F1 comparison
    f1_table = wandb.Table(columns=["model", "metric", "value"])
    for r in results:
        pm = r.promise_metrics
        cm = r.contradiction_metrics
        f1_table.add_data(r.model_id, "promise_f1", pm["f1"])
        f1_table.add_data(r.model_id, "contradiction_f1", cm["f1"])
        f1_table.add_data(r.model_id, "json_validity", r.json_validity_rate)
    wandb.log({
        "f1_comparison": wandb.plot.bar(
            f1_table, "model", "value", title="Model F1 Comparison"
        )
    })

    run.finish()
    print(f"W&B run logged: {run.url}")


def print_summary(results: list[EvalResult]) -> None:
    """Print a formatted summary table to stdout."""
    header = (
        f"{'Model':<40} {'JSON%':>6} {'Prom-P':>7} {'Prom-R':>7} {'Prom-F1':>7} "
        f"{'Cont-P':>7} {'Cont-R':>7} {'Cont-F1':>7} {'MAE':>6} {'Lat(s)':>7} {'Cost$':>8}"
    )
    print("\n" + "=" * len(header))
    print("EVALUATION RESULTS")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    for r in results:
        s = r.summary()
        print(
            f"{s['model']:<40} {s['json_validity_rate']:>6.1%} "
            f"{s['promise_precision']:>7.3f} {s['promise_recall']:>7.3f} {s['promise_f1']:>7.3f} "
            f"{s['contradiction_precision']:>7.3f} {s['contradiction_recall']:>7.3f} "
            f"{s['contradiction_f1']:>7.3f} {s['confidence_mae']:>6.3f} "
            f"{s['avg_latency_s']:>7.2f} {s['estimated_cost_usd']:>8.5f}"
        )
    print("=" * len(header) + "\n")


def main() -> None:
    """Entry point: parse args, run evaluation, log results."""
    parser = argparse.ArgumentParser(
        description="Evaluate Ecotopia fine-tuned models vs baselines"
    )
    parser.add_argument(
        "--task", default="extraction",
        help="Task name matching data/<task>/splits/ directory (default: extraction)",
    )
    parser.add_argument(
        "--models", default=None,
        help="Comma-separated model specs: ft:model_id or base:model_id",
    )
    parser.add_argument(
        "--no-wandb", action="store_true",
        help="Skip W&B logging (print results only)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (default: training/eval_results.json)",
    )
    args = parser.parse_args()

    # Load environment
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("ERROR: MISTRAL_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Resolve models
    if args.models:
        model_specs = args.models.split(",")
    else:
        model_specs = load_models_from_jobs(args.task)
        # Always include base model for comparison
        model_specs.append("base:mistral-large-latest")

    if not model_specs:
        print("ERROR: No models specified and none found in ft_jobs.json", file=sys.stderr)
        sys.exit(1)

    models = [parse_model_spec(s.strip()) for s in model_specs]
    print(f"Evaluating {len(models)} model(s): {[m[1] for m in models]}")

    # Load data
    examples = load_validation_data(args.task)

    # Run evaluations
    client = Mistral(api_key=api_key)
    results: list[EvalResult] = []

    for prefix, model_id in models:
        print(f"\nEvaluating: {prefix}:{model_id}")
        result = evaluate_model(client, model_id, examples)
        results.append(result)

    # Print summary
    print_summary(results)

    # Save results JSON
    output_path = Path(args.output) if args.output else SCRIPT_DIR / "eval_results.json"
    output_data = {
        "task": args.task,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": [r.summary() for r in results],
        "predictions": {r.model_id: r.predictions for r in results},
    }
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output_path}")

    # Log to W&B
    if not args.no_wandb:
        wandb_key = os.getenv("WANDB_API_KEY")
        if not wandb_key:
            print("WARNING: WANDB_API_KEY not set, skipping W&B logging", file=sys.stderr)
        else:
            log_to_wandb(results, args.task)


if __name__ == "__main__":
    main()
