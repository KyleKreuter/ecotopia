"""Evaluate extraction models across difficulty levels (EASY/MEDIUM/HARD).

Runs base Mistral models on test sets of varying difficulty and logs
results to W&B with a comparison table.
"""

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
METRIC_KEYS = ["valid_json", "promise_count", "type_precision", "contradiction"]
TABLE_COLUMNS = ["Model", "Difficulty", "Promise Count %", "Type Precision %", "Contradiction %", "Valid JSON %"]


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


def evaluate_example(predicted: dict | None, expected: dict) -> dict[str, float]:
    """Score a single prediction against expected output."""
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


def evaluate_model(client: Mistral, model: str, examples: list[dict]) -> dict[str, float]:
    """Evaluate a model on a set of examples, returning percentage scores."""
    scores = {k: [] for k in METRIC_KEYS}

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
        raise ValueError("MISTRAL_API_KEY environment variable not set")

    client = Mistral(api_key=api_key)
    wandb.init(project="ecotopia-extraction", name="difficulty-eval")

    rows = []
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

    table = wandb.Table(
        columns=TABLE_COLUMNS,
        data=[[r[c] for c in TABLE_COLUMNS] for r in rows],
    )
    wandb.log({"difficulty_eval": table})

    print("\n" + "=" * 90)
    print(f"{'Model':<35} {'Difficulty':<12} {'Promise%':>10} {'Type%':>10} {'Contra%':>10} {'JSON%':>10}")
    print("=" * 90)
    for r in rows:
        print(f"{r['Model']:<35} {r['Difficulty']:<12} {r['Promise Count %']:>10.1f} "
              f"{r['Type Precision %']:>10.1f} {r['Contradiction %']:>10.1f} {r['Valid JSON %']:>10.1f}")
    print("=" * 90)

    wandb.finish()


if __name__ == "__main__":
    main()
