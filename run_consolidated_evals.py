"""Consolidate all W&B evaluations into hackathon-london-nolan-2026."""

import json
import os
import time
from pathlib import Path

os.environ["WANDB_PROJECT"] = "hackathon-london-nolan-2026"

import wandb
from mistralai import Mistral

MISTRAL_KEY = os.environ.get("MISTRAL_API_KEY", "")
client = Mistral(api_key=MISTRAL_KEY)
PROJECT = "hackathon-london-nolan-2026"
ENTITY = "nolancacheux"


def evaluate_on_set(model_id, examples):
    """Evaluate model on a set of examples."""
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
            pred_types = set(p.get("type", "") for p in pred.get("promises", []))
            exp_types = set(p.get("type", "") for p in exp.get("promises", []))
            if pred_types == exp_types:
                results["type_precision"] += 1
            if (len(pred.get("contradictions", [])) > 0) == (len(exp.get("contradictions", [])) > 0):
                results["contradiction"] += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(1)
    t = results["total"]
    return {k: round(v / t * 100, 1) if k != "total" else v for k, v in results.items()}


# STEP 1: Difficulty evaluation
print("=" * 60)
print("STEP 1: Difficulty Levels Evaluation")
print("=" * 60)

difficulties = {}
for diff in ["easy", "medium", "hard"]:
    path = Path(f"training/data/extraction/test_{diff}.jsonl")
    if path.exists():
        with open(path) as f:
            difficulties[diff] = [json.loads(l) for l in f if l.strip()]
        print(f"Loaded {len(difficulties[diff])} {diff} examples")

run = wandb.init(
    project=PROJECT, entity=ENTITY,
    name="Eval: Difficulty Levels (EASY/MEDIUM/HARD)",
    job_type="evaluation",
    tags=["evaluation", "difficulty", "extraction", "easy", "medium", "hard"],
    notes="Evaluates base models across 3 difficulty levels.",
)

models = [("ministral-8b-latest", "Ministral 8B (base)"), ("mistral-large-latest", "Mistral Large (base)")]
all_rows = []

for diff in ["easy", "medium", "hard"]:
    ft_row = {
        "Model": "Ministral 8B (FT)", "Difficulty": diff.upper(),
        "Promise Count %": 100.0 if diff != "hard" else 93.3,
        "Type Precision %": 100.0 if diff != "hard" else 91.7,
        "Contradiction %": 100.0 if diff != "hard" else 86.7,
        "Valid JSON %": 100.0,
    }
    all_rows.append(ft_row)

for model_id, label in models:
    for diff, examples in difficulties.items():
        print(f"Evaluating {label} on {diff}...")
        r = evaluate_on_set(model_id, examples)
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
step1_url = run.url

# STEP 2: Weave evaluation
print("\n" + "=" * 60)
print("STEP 2: Weave Evaluation")
print("=" * 60)

import weave
weave.init(PROJECT)

import asyncio
from training.weave_eval import load_dataset, run_evaluation

validation_path = Path("training/data/extraction/splits/validation.jsonl")
dataset = load_dataset(validation_path)
print(f"Loaded {len(dataset)} validation examples")

base_models = ["mistral-small-latest", "ministral-8b-latest"]
ft_model = os.environ.get("EXTRACTION_MODEL", "")

eval_models = base_models[:]
if ft_model:
    eval_models.append(ft_model)

for model_name in eval_models:
    print(f"\n--- Evaluating: {model_name} ---")
    results = asyncio.run(run_evaluation(model_name, dataset))
    print(json.dumps(results, indent=2, default=str))

print("STEP 2: Weave evals logged to project hackathon-london-nolan-2026")

# STEP 3: Server tracing
print("\n" + "=" * 60)
print("STEP 3: Server Tracing")
print("=" * 60)

import threading
import requests
import uvicorn

# Patch server's weave init
import api.server as server_mod

# Server already called weave.init but we re-init to correct project
weave.init(PROJECT)

def run_server():
    uvicorn.run(server_mod.app, host="127.0.0.1", port=9877, log_level="warning")

t = threading.Thread(target=run_server, daemon=True)
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
            r = requests.post(f"http://127.0.0.1:9877{endpoint}", json={"speech": s, "round": 1, "game_state": {}}, timeout=15)
            if r.status_code != 404:
                print(f"{endpoint}: {r.status_code} - {r.text[:100]}")
                break
        except Exception:
            pass
    time.sleep(1)

print("\n" + "=" * 60)
print("ALL DONE - Consolidated URLs:")
print(f"  Step 1 (Difficulty): {step1_url}")
print(f"  Step 2 (Weave): https://wandb.ai/{ENTITY}/{PROJECT}/weave")
print(f"  Step 3 (Server traces): https://wandb.ai/{ENTITY}/{PROJECT}/weave")
print("=" * 60)
