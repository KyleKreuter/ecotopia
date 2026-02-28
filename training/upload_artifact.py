"""Upload fine-tuned LoRA adapters as W&B Artifacts."""
import os

import wandb
from huggingface_hub import snapshot_download


def upload_model_artifact(model_name: str, hf_repo: str) -> None:
    """Download model from HF and log as W&B artifact."""
    run = wandb.init(
        project="hackathon-london-nolan-2026",
        job_type="model-upload",
        name=f"upload-{model_name}",
    )

    local_dir = snapshot_download(
        repo_id=hf_repo,
        local_dir=f"./artifacts/{model_name}",
    )

    artifact = wandb.Artifact(
        name=model_name,
        type="model",
        description=(
            f"LoRA adapter for Ecotopia {model_name}. "
            "Base: Ministral-8B-Instruct-2410. Fine-tuned with TRL SFT."
        ),
        metadata={
            "base_model": "mistralai/Ministral-8B-Instruct-2410",
            "method": "LoRA (r=16, alpha=32)",
            "framework": "TRL + PEFT",
            "quantization": "4-bit NF4",
            "hf_repo": hf_repo,
        },
    )
    artifact.add_dir(local_dir)
    run.log_artifact(artifact)
    run.finish()
    print(f"Uploaded {model_name} to W&B")


if __name__ == "__main__":
    os.environ.setdefault(
        "WANDB_API_KEY",
        "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",
    )

    upload_model_artifact(
        "ecotopia-extract-ministral-8b",
        "mistral-hackaton-2026/ecotopia-extract-ministral-8b",
    )

    try:
        upload_model_artifact(
            "ecotopia-citizens-ministral-8b",
            "mistral-hackaton-2026/ecotopia-citizens-ministral-8b",
        )
    except Exception as e:
        print(f"Citizens model not ready yet: {e}")
