"""Evaluate extraction models across difficulty levels (EASY/MEDIUM/HARD)."""

import json
import os
from pathlib import Path

import wandb
from mistralai import Mistral

DATA_DIR = Path(__file__).parent / "data" / "extraction"
DIFFICULTIES = ["easy", "medium", "hard"]
MODELS = ["ministral-8b-latest", "mistral-large-latest"]
SYSTEM_PROMPT = (
    "Extract promises from the mayor's speech as structured JSON. "
    "Return a JSON object with 'promises' (array of {text, type, impact, deadline}) "
    "and 'contradictions' (array of {promise1, promise2, explanation}). "
    "Types: ecology, economy, research. Impact: positive, negative. "
    "Deadline: short_term, medium_term, long_term."
)


def load_test_set(difficulty: str) -> list[dict]:
    """Load a JSONL test set file."""
    path = DATA_DIR / f"test_{difficulty}.jsonl"
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def parse_json_safe(text: str) -> dict | None:
    """Try to parse JSON from model output, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def evaluate_example(
    predicted: dict | None, expected: dict
) -> dict[str, float]:
    """Score a single prediction against expected output."""
    if predicted is None:
        return {"valid_json": 0, "promise_count": 0, "type_precision": 0, "contradiction": 0}

    exp_promises = expected.get("promises", [])
    pred_promises = predicted.get("promises", [])
    exp_contradictions = expected.get("contradictions", [])
    pred_contradictions = predicted.get("contradictions", [])

    # Promise count accuracy (1 if counts match)
    promise_count = 1.0 if len(pred_promises) == len(exp_promises) else 0.0

    # Type precision (fraction of correctly typed promises)
    if not exp_promises:
        type_precision = 1.0 if not pred_promises else 0.0
    else:
        exp_types = sorted(p.get("type", "") for p in exp_promises)
        pred_types = sorted(p.get("type", "") for p in pred_promises)
        matches = sum(1 for e, p in zip(exp_types, pred_types) if e == p)
        type_precision = matches / len(exp_types)

    # Contradiction detection (1 if both have or both lack contradictions)
    has_exp = len(exp_contradictions) > 0
    has_pred = len(pred_contradictions) > 0
    contradiction = 1.0 if has_exp == has_pred else 0.0

    return {
        "valid_json": 1.0,
        "promise_count": promise_count,
        "type_precision": type_precision,
        "contradiction": contradiction,
    }


def evaluate_model(client: Mistral, model: str, examples: list[dict]) -> dict[str, float]:
    """Evaluate a model on a set of examples."""
    scores = {"valid_json": [], "promise_count": [], "type_precision": [], "contradiction": []}

    for ex in examples:
        msgs = ex["messages"]
        user_content = msgs[1]["content"]
        expected = json.loads(msgs[2]["content"])

        response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        predicted = parse_json_safe(response.choices[0].message.content)
        result = evaluate_example(predicted, expected)
        for k, v in result.items():
            scores[k].append(v)

    return {k: sum(v) / len(v) * 100 for k, v in scores.items()}


def main():
    """Run difficulty-level evaluation and log to W&B."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set")

    client = Mistral(api_key=api_key)

    wandb.init(project="ecotopia-extraction", name="difficulty-eval")

    rows = []

    # Evaluate base models
    for model in MODELS:
        for difficulty in DIFFICULTIES:
            print(f"Evaluating {model} on {difficulty}...")
            examples = load_test_set(difficulty)
            scores = evaluate_model(client, model, examples)
            row = {
                "Model": model,
                "Difficulty": difficulty.upper(),
                "Promise Count %": round(scores["promise_count"], 1),
                "Type Precision %": round(scores["type_precision"], 1),
                "Contradiction %": round(scores["contradiction"], 1),
                "Valid JSON %": round(scores["valid_json"], 1),
            }
            rows.append(row)
            print(f"  → {row}")

    # Log W&B table
    table = wandb.Table(
        columns=["Model", "Difficulty", "Promise Count %", "Type Precision %", "Contradiction %", "Valid JSON %"],
        data=[[r[c] for c in ["Model", "Difficulty", "Promise Count %", "Type Precision %", "Contradiction %", "Valid JSON %"]] for r in rows],
    )
    wandb.log({"difficulty_eval": table})

    # Print summary
    print("\n" + "=" * 90)
    print(f"{'Model':<35} {'Difficulty':<12} {'Promise%':>10} {'Type%':>10} {'Contra%':>10} {'JSON%':>10}")
    print("=" * 90)
    for r in rows:
        print(f"{r['Model']:<35} {r['Difficulty']:<12} {r['Promise Count %']:>10.1f} {r['Type Precision %']:>10.1f} {r['Contradiction %']:>10.1f} {r['Valid JSON %']:>10.1f}")
    print("=" * 90)

    wandb.finish()


if __name__ == "__main__":
    main()
