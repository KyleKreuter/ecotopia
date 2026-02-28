"""Minimal fine-tuning test: upload tiny dataset, create job, check status.

Usage:
    MISTRAL_API_KEY=<key> python3 training/test_finetuning.py
"""

import json
import os
import sys
import tempfile

from mistralai import Mistral


def main() -> None:
    """Try to create a minimal fine-tuning job to diagnose API access."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("ERROR: Set MISTRAL_API_KEY env var")
        sys.exit(1)

    client = Mistral(api_key=api_key)

    # Step 1: Create minimal JSONL (10 lines, simplest possible)
    print("--- Step 1: Create minimal dataset ---")
    examples = []
    for i in range(10):
        examples.append(json.dumps({
            "messages": [
                {"role": "user", "content": f"Say hello {i}"},
                {"role": "assistant", "content": f"Hello {i}!"},
            ]
        }))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(examples) + "\n")
        tmp_path = f.name
    print(f"Created {tmp_path} with {len(examples)} lines")

    # Step 2: Upload
    print("\n--- Step 2: Upload file ---")
    with open(tmp_path, "rb") as f:
        uploaded = client.files.upload(
            file={"file_name": "test_ft.jsonl", "content": f},
            purpose="fine-tune",
        )
    print(f"Upload OK: id={uploaded.id}, sample_type={uploaded.sample_type}")

    # Step 3: Check available FT models
    print("\n--- Step 3: Check FT models endpoint ---")
    import httpx
    r = httpx.get(
        "https://api.mistral.ai/v1/fine_tuning/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=15,
    )
    models_data = r.json()
    available = models_data.get("data", [])
    print(f"Available FT models: {len(available)}")
    for m in available:
        print(f"  - {m.get('id', m)}")

    if not available:
        print("\nNo FT models available for this account.")
        print("This means fine-tuning is NOT enabled on your workspace.")
        print("Fix: go to admin.mistral.ai > Workspaces > upgrade plan")

    # Step 4: Try creating FT job anyway
    print("\n--- Step 4: Try creating FT job ---")
    models_to_try = ["open-mistral-nemo", "ministral-8b-latest", "mistral-small-latest"]
    for model in models_to_try:
        try:
            job = client.fine_tuning.jobs.create(
                model=model,
                training_files=[{"file_id": uploaded.id, "weight": 1}],
                suffix="test",
                hyperparameters={"training_steps": 1},
                auto_start=False,
            )
            print(f"  {model}: OK! job_id={job.id}, status={job.status}")
            # Cancel immediately
            client.fine_tuning.jobs.cancel(job_id=job.id)
            print(f"  Cancelled test job {job.id}")
            break
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200]
            print(f"  {model}: FAIL - {error_msg}")

    # Cleanup
    os.unlink(tmp_path)
    print("\nDone.")


if __name__ == "__main__":
    main()
