"""Launch fine-tuning jobs for Ecotopia's promise extraction model.

Merges JSONL batches, splits train/validation, uploads to Mistral,
and creates SFT jobs for Ministral 8B and Mistral Nemo 12B.
"""

import json
import os
import random
import sys
import time
from pathlib import Path

from mistralai import Mistral

DATA_DIR = Path(__file__).parent / "data" / "extraction"
OUTPUT_DIR = Path(__file__).parent / "data" / "extraction" / "splits"

BATCH_FILES = [
    "batch1_explicit_promises.jsonl",
    "batch2_implicit_and_none.jsonl",
    "batch3_contradictions.jsonl",
    "batch4_edge_cases.jsonl",
]

MODELS = [
    "ministral-8b-latest",
    "open-mistral-nemo",
]

TRAIN_RATIO = 0.8
RANDOM_SEED = 42


def load_and_merge(data_dir: Path) -> list[dict]:
    """Load all batch JSONL files and merge into a single list."""
    examples = []
    for filename in BATCH_FILES:
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"WARNING: {filepath} not found, skipping")
            continue
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    examples.append(json.loads(line))
        print(f"Loaded {filepath.name}")
    return examples


def split_dataset(
    examples: list[dict], train_ratio: float, seed: int
) -> tuple[list[dict], list[dict]]:
    """Shuffle and split into train/validation sets."""
    random.seed(seed)
    shuffled = examples.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * train_ratio)
    return shuffled[:split_idx], shuffled[split_idx:]


def write_jsonl(examples: list[dict], filepath: Path) -> None:
    """Write examples to a JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"Wrote {len(examples)} examples to {filepath}")


def upload_file(client: Mistral, filepath: Path) -> str:
    """Upload a JSONL file to Mistral and return the file ID."""
    with open(filepath, "rb") as f:
        uploaded = client.files.upload(
            file={"file_name": filepath.name, "content": f},
            purpose="fine-tune",
        )
    print(f"Uploaded {filepath.name} -> {uploaded.id}")
    return uploaded.id


def create_ft_job(
    client: Mistral,
    model: str,
    train_file_id: str,
    val_file_id: str,
    suffix: str,
) -> str:
    """Create a fine-tuning job and return the job ID."""
    job = client.fine_tuning.jobs.create(
        model=model,
        training_files=[{"file_id": train_file_id, "weight": 1}],
        validation_files=[val_file_id],
        suffix=suffix,
        hyperparameters={
            "training_steps": 100,
            "learning_rate": 1e-4,
        },
        auto_start=True,
        integrations=[],
    )
    print(f"Created FT job: {job.id} (model: {model}, suffix: {suffix})")
    return job.id


def main() -> None:
    """Merge, split, upload, and launch fine-tuning jobs."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("MISTRAL_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
        if not api_key:
            print("ERROR: MISTRAL_API_KEY not set")
            sys.exit(1)

    # Step 1: Merge all batches
    print("\n--- Step 1: Merge batches ---")
    examples = load_and_merge(DATA_DIR)
    print(f"Total examples: {len(examples)}")

    # Step 2: Split train/validation
    print("\n--- Step 2: Split dataset ---")
    train, val = split_dataset(examples, TRAIN_RATIO, RANDOM_SEED)
    print(f"Train: {len(train)}, Validation: {len(val)}")

    train_path = OUTPUT_DIR / "train.jsonl"
    val_path = OUTPUT_DIR / "validation.jsonl"
    write_jsonl(train, train_path)
    write_jsonl(val, val_path)

    # Step 3: Upload to Mistral
    print("\n--- Step 3: Upload files ---")
    client = Mistral(api_key=api_key)
    train_file_id = upload_file(client, train_path)
    val_file_id = upload_file(client, val_path)

    # Step 4: Launch FT jobs
    print("\n--- Step 4: Launch fine-tuning jobs ---")
    job_ids = []
    for model in MODELS:
        short_name = "8b" if "8b" in model else "nemo"
        suffix = f"eco_extract_{short_name}"
        job_id = create_ft_job(client, model, train_file_id, val_file_id, suffix)
        job_ids.append({"model": model, "job_id": job_id, "suffix": suffix})
        time.sleep(2)

    # Summary
    print("\n--- Summary ---")
    print(f"Train file: {train_file_id}")
    print(f"Validation file: {val_file_id}")
    for job in job_ids:
        print(f"  {job['model']}: job_id={job['job_id']}")
    print("\nMonitor at: https://console.mistral.ai/build/fine-tuning")

    # Save job info
    info_path = OUTPUT_DIR / "ft_jobs.json"
    with open(info_path, "w") as f:
        json.dump(
            {
                "train_file_id": train_file_id,
                "val_file_id": val_file_id,
                "jobs": job_ids,
            },
            f,
            indent=2,
        )
    print(f"Job info saved to {info_path}")


if __name__ == "__main__":
    main()
