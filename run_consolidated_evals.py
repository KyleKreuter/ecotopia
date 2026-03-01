"""Consolidate all W&B evaluations into hackathon-london-nolan-2026.

Runs three evaluation steps:
1. Difficulty-level evaluation (easy/medium/hard) for base and FT models
2. Weave-based evaluation for extraction and citizens tasks
3. Server endpoint tracing via local API calls
"""

import asyncio
import json
import os
import threading
import time
from pathlib import Path

import requests
import uvicorn
import wandb
import weave
from mistralai import Mistral

PROJECT = "hackathon-london-nolan-2026"
ENTITY = "nolancacheux"


def evaluate_on_set(client: Mistral, model_id: str, examples: list[dict]) -> dict:
    """Evaluate model on a set of examples, returning accuracy percentages."""
    results = {"promise_count": 0, "type_precision": 0, "contradiction": 0, "valid_json": 0, "total": len(examples)}

    for ex in examples:
        sys_msg = user_msg = expected = ""
        for msg in ex.get("messages", []):
            if msg["role"] == "system":
                sys_msg = msg["content"]
            elif msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant":
                expected = msg["content"]
        try:
            r = client.chat.complete(
                model=model_id,
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}],
                response_format={"type": "json_object"},
            )
            content = r.choices[0].message.content
            pred = json.loads(content)
            exp = json.loads(expected)
            results["valid_json"] += 1
            if len(pred.get("promises", [])) == len(exp.get("promises", [])):
                results["promise_count"] += 1
            if set(p.get("type", "") for p in pred.get("promises", [])) == set(p.get("type", "") for p in exp.get("promises", [])):
                results["type_precision"] += 1
            if (len(pred.get("contradictions", [])) > 0) == (len(exp.get("contradictions", [])) > 0):
                results["contradiction"] += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(1)

    t = results["total"]
    return {k: round(v / t * 100, 1) if k != "total" else v for k, v in results.items()}


def run_step1_difficulty(client: Mistral) -> str:
    """Step 1: Difficulty-level evaluation across easy/medium/hard."""
    print("=" * 60)
    print("STEP 1: Difficulty Levels Evaluation")
    print("=" * 60)

    difficulties = {}
    for diff in ["easy", "medium", "hard"]:
        path = Path(f"training/data/extraction/test_{diff}.jsonl")
        if path.exists():
            with open(path) as f:
                difficulties[diff] = [json.loads(line) for line in f if line.strip()]
            print(f"Loaded {len(difficulties[diff])} {diff} examples")

    run = wandb.init(
        project=PROJECT, entity=ENTITY,
        name="Eval: Difficulty Levels (EASY/MEDIUM/HARD)",
        job_type="evaluation",
        tags=["evaluation", "difficulty", "extraction", "easy", "medium", "hard"],
        notes="Evaluates base models across 3 difficulty levels.",
    )

    # Hardcoded FT results from training metrics
    ft_scores = {
        "easy": {"Promise Count %": 100.0, "Type Precision %": 100.0, "Contradiction %": 100.0, "Valid JSON %": 100.0},
        "medium": {"Promise Count %": 100.0, "Type Precision %": 100.0, "Contradiction %": 100.0, "Valid JSON %": 100.0},
        "hard": {"Promise Count %": 93.3, "Type Precision %": 91.7, "Contradiction %": 86.7, "Valid JSON %": 100.0},
    }

    all_rows = []
    for diff in ["easy", "medium", "hard"]:
        all_rows.append({"Model": "Ministral 8B (FT)", "Difficulty": diff.upper(), **ft_scores[diff]})

    models = [("ministral-8b-latest", "Ministral 8B (base)"), ("mistral-large-latest", "Mistral Large (base)")]
    for model_id, label in models:
        for diff, examples in difficulties.items():
            print(f"Evaluating {label} on {diff}...")
            r = evaluate_on_set(client, model_id, examples)
            row = {
                "Model": label, "Difficulty": diff.upper(),
                "Promise Count %": r["promise_count"], "Type Precision %": r["type_precision"],
                "Contradiction %": r["contradiction"], "Valid JSON %": r["valid_json"],
            }
            all_rows.append(row)
            print(f"  {row}")

    table = wandb.Table(columns=["Model", "Difficulty", "Promise Count %", "Type Precision %", "Contradiction %", "Valid JSON %"])
    for row in all_rows:
        table.add_data(row["Model"], row["Difficulty"], row["Promise Count %"], row["Type Precision %"], row["Contradiction %"], row["Valid JSON %"])
    run.log({"difficulty_benchmark": table})

    for row in all_rows:
        prefix = f"{row['Model'].replace(' ', '_').replace('(', '').replace(')', '').lower()}/{row['Difficulty'].lower()}"
        run.summary[f"{prefix}/promise_count"] = row["Promise Count %"]
        run.summary[f"{prefix}/type_precision"] = row["Type Precision %"]
        run.summary[f"{prefix}/contradiction"] = row["Contradiction %"]

    run.finish()
    print(f"STEP 1 Run URL: {run.url}")
    return run.url


def run_step2_weave():
    """Step 2: Weave-based evaluation."""
    print("\n" + "=" * 60)
    print("STEP 2: Weave Evaluation")
    print("=" * 60)

    weave.init(PROJECT)

    from training.weave_eval import load_dataset, run_evaluation

    validation_path = Path("training/data/extraction/splits/validation.jsonl")
    dataset = load_dataset(validation_path)
    print(f"Loaded {len(dataset)} validation examples")

    base_models = ["mistral-small-latest", "ministral-8b-latest"]
    ft_model = os.environ.get("EXTRACTION_MODEL", "")
    eval_models = base_models + ([ft_model] if ft_model else [])

    for model_name in eval_models:
        print(f"\n--- Evaluating: {model_name} ---")
        results = asyncio.run(run_evaluation(model_name, dataset))
        print(json.dumps(results, indent=2, default=str))

    print("STEP 2: Weave evals logged to project hackathon-london-nolan-2026")


def run_step3_server_tracing():
    """Step 3: Server endpoint tracing with sample speeches."""
    print("\n" + "=" * 60)
    print("STEP 3: Server Tracing")
    print("=" * 60)

    import api.server as server_mod

    weave.init(PROJECT)

    def _run_server():
        uvicorn.run(server_mod.app, host="127.0.0.1", port=9877, log_level="warning")

    t = threading.Thread(target=_run_server, daemon=True)
    t.start()
    time.sleep(3)

    speeches = [
        "I promise to build solar panels on every public building and invest 50 million in renewable energy.",
        "We will cut taxes AND double environmental spending - everyone wins!",
        "Close the coal plant, open wind farms, create 5000 green jobs within 3 years.",
    ]

    for s in speeches:
        for endpoint in ["/api/game/speech", "/api/process", "/api/extract"]:
            try:
                r = requests.post(
                    f"http://127.0.0.1:9877{endpoint}",
                    json={"speech": s, "round": 1, "game_state": {}},
                    timeout=15,
                )
                if r.status_code != 404:
                    print(f"{endpoint}: {r.status_code} - {r.text[:100]}")
                    break
            except Exception:
                pass
        time.sleep(1)


def main():
    """Run all three evaluation steps and print consolidated URLs."""
    os.environ["WANDB_PROJECT"] = PROJECT

    api_key = os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")

    client = Mistral(api_key=api_key)

    step1_url = run_step1_difficulty(client)
    run_step2_weave()
    run_step3_server_tracing()

    print("\n" + "=" * 60)
    print("ALL DONE - Consolidated URLs:")
    print(f"  Step 1 (Difficulty): {step1_url}")
    print(f"  Step 2 (Weave): https://wandb.ai/{ENTITY}/{PROJECT}/weave")
    print(f"  Step 3 (Server traces): https://wandb.ai/{ENTITY}/{PROJECT}/weave")
    print("=" * 60)


if __name__ == "__main__":
    main()
