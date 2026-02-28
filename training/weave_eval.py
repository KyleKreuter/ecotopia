"""Weave evaluation: compare base vs fine-tuned Mistral on promise extraction."""

import asyncio
import json
import os
import time
from pathlib import Path

import weave
from mistralai import Mistral
from weave import Evaluation

VALIDATION_PATH = (
    Path(__file__).parent / "data" / "extraction" / "splits" / "validation.jsonl"
)


def _build_client() -> Mistral:
    """Create a Mistral client from env."""
    return Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))


# Scorers

@weave.op
def json_validity_scorer(output: dict) -> dict:
    """Check whether the model output is valid JSON (already parsed)."""
    try:
        if isinstance(output, str):
            json.loads(output)
        return {"json_valid": True}
    except (json.JSONDecodeError, TypeError):
        return {"json_valid": False}


@weave.op
def promise_count_scorer(output: dict, expected: str) -> dict:
    """Compare the number of extracted promises against ground truth."""
    try:
        out = output if isinstance(output, dict) else json.loads(output)
        exp = json.loads(expected) if isinstance(expected, str) else expected
        out_count = len(out.get("promises", []))
        exp_count = len(exp.get("promises", []))
        return {
            "count_match": out_count == exp_count,
            "count_diff": abs(out_count - exp_count),
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {"count_match": False, "count_diff": -1}


@weave.op
def contradiction_scorer(output: dict, expected: str) -> dict:
    """Check contradiction detection accuracy."""
    try:
        out = output if isinstance(output, dict) else json.loads(output)
        exp = json.loads(expected) if isinstance(expected, str) else expected
        out_contradictions = set()
        for p in out.get("promises", []):
            if p.get("contradicts"):
                out_contradictions.add(p.get("id", ""))
        exp_contradictions = set()
        for p in exp.get("promises", []):
            if p.get("contradicts"):
                exp_contradictions.add(p.get("id", ""))
        if not exp_contradictions and not out_contradictions:
            return {"contradiction_precision": 1.0, "contradiction_recall": 1.0}
        precision = (
            len(out_contradictions & exp_contradictions) / len(out_contradictions)
            if out_contradictions
            else 0.0
        )
        recall = (
            len(out_contradictions & exp_contradictions) / len(exp_contradictions)
            if exp_contradictions
            else 0.0
        )
        return {"contradiction_precision": precision, "contradiction_recall": recall}
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {"contradiction_precision": 0.0, "contradiction_recall": 0.0}


@weave.op
def latency_scorer(output: dict, _latency_ms: float = 0.0) -> dict:
    """Pass-through scorer that records latency injected by the model wrapper."""
    return {"latency_ms": _latency_ms}


def load_dataset(path: Path, limit: int = 0) -> list[dict]:
    """Load validation JSONL into a list of dicts with 'input' and 'expected' keys."""
    if not path.exists():
        raise FileNotFoundError(f"Validation file not found: {path}")
    dataset = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            messages = row.get("messages", [])
            user_msg = ""
            assistant_msg = ""
            for m in messages:
                if m["role"] == "user":
                    user_msg = m["content"]
                elif m["role"] == "assistant":
                    assistant_msg = m["content"]
            dataset.append({"input": user_msg, "expected": assistant_msg})
            if 0 < limit <= len(dataset):
                break
    return dataset


def make_model_fn(model_name: str):
    """Create a weave-traced extraction function for a specific model."""
    client = _build_client()
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_path = prompts_dir / "extraction.txt"
    system_prompt = (
        prompt_path.read_text(encoding="utf-8")
        if prompt_path.exists()
        else "Extract promises from the mayor's speech as JSON."
    )

    @weave.op
    def predict(input: str) -> dict:
        """Run extraction with a specific model and measure latency."""
        t0 = time.perf_counter()
        response = client.chat.complete(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input},
            ],
            response_format={"type": "json_object"},
        )
        elapsed = (time.perf_counter() - t0) * 1000
        raw = response.choices[0].message.content
        parsed = json.loads(raw) if isinstance(raw, str) else raw
        parsed["_latency_ms"] = elapsed
        return parsed

    predict.__name__ = f"extract_{model_name.replace('-', '_').replace(':', '_')}"
    return predict


async def run_evaluation(
    model_name: str,
    dataset: list[dict],
) -> dict:
    """Run a Weave Evaluation for a single model."""
    predict_fn = make_model_fn(model_name)
    evaluation = Evaluation(
        name=f"ecotopia-eval-{model_name}",
        dataset=dataset,
        scorers=[
            json_validity_scorer,
            promise_count_scorer,
            contradiction_scorer,
        ],
    )
    results = await evaluation.evaluate(predict_fn)
    return results


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate base vs fine-tuned Mistral on promise extraction"
    )
    parser.add_argument(
        "--base-model",
        default="mistral-small-latest",
        help="Base model name (default: mistral-small-latest)",
    )
    parser.add_argument(
        "--ft-model",
        default=os.environ.get("EXTRACTION_MODEL", ""),
        help="Fine-tuned model name (env EXTRACTION_MODEL or flag)",
    )
    parser.add_argument(
        "--validation-path",
        default=str(VALIDATION_PATH),
        help="Path to validation JSONL",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max examples to evaluate (0 = all)",
    )
    args = parser.parse_args()

    weave.init("ecotopia-hackathon")

    dataset = load_dataset(Path(args.validation_path), limit=args.limit)
    print(f"Loaded {len(dataset)} validation examples")

    models = [args.base_model]
    if args.ft_model:
        models.append(args.ft_model)
    else:
        print("No fine-tuned model specified; evaluating base model only.")

    for model_name in models:
        print(f"\n--- Evaluating: {model_name} ---")
        results = asyncio.run(run_evaluation(model_name, dataset))
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
