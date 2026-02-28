# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "trl>=0.17",
#   "transformers>=4.48",
#   "datasets",
#   "peft",
#   "accelerate",
#   "bitsandbytes",
#   "torch",
#   "huggingface_hub",
#   "wandb",
# ]
# ///
"""Fine-tune Mistral Nemo 12B on Ecotopia extraction data using TRL SFT + LoRA.

Runs as a HuggingFace Job via: hf jobs uv run --flavor a10g-large hf_finetune_extraction_nemo.py
"""

import json
import os
from pathlib import Path

import torch
from datasets import Dataset
from huggingface_hub import HfApi
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

# Config
BASE_MODEL = "mistralai/Mistral-Nemo-Instruct-2407"
OUTPUT_DIR = "./ecotopia-extract-nemo-12b"
HF_REPO = "mistral-hackaton-2026/ecotopia-extract-nemo-12b"
MAX_SEQ_LENGTH = 2048
NUM_EPOCHS = 3
BATCH_SIZE = 1  # Reduced for 12B on A10G
GRADIENT_ACCUMULATION = 8
LEARNING_RATE = 2e-4
LORA_R = 16
LORA_ALPHA = 32


def load_data_from_hub() -> tuple[Dataset, Dataset]:
    """Load training data from HF dataset repo or local files."""
    data_dir = Path("/root/clawd/ecotopia/training/data/extraction/splits")

    if not data_dir.exists():
        api = HfApi()
        for split in ["train", "validation"]:
            api.hf_hub_download(
                repo_id="mistral-hackaton-2026/ecotopia-extraction-data",
                filename=f"{split}.jsonl",
                local_dir="./data",
                repo_type="dataset",
            )
        data_dir = Path("./data")

    def load_jsonl(filepath: Path) -> list[dict]:
        """Load examples from a JSONL file."""
        examples = []
        with open(filepath) as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        return examples

    train_data = load_jsonl(data_dir / "train.jsonl")
    val_data = load_jsonl(data_dir / "validation.jsonl")

    train_ds = Dataset.from_list(train_data)
    val_ds = Dataset.from_list(val_data)

    return train_ds, val_ds


def main() -> None:
    """Fine-tune Mistral Nemo 12B with LoRA on extraction data."""
    print(f"Fine-tuning {BASE_MODEL} for Ecotopia extraction")
    print(f"Output: {HF_REPO}")

    train_ds, val_ds = load_data_from_hub()
    print(f"Train: {len(train_ds)} examples, Val: {len(val_ds)} examples")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
    )

    peft_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    wandb_project = os.environ.get("WANDB_PROJECT", "hackathon-london-nolan-2026")
    use_wandb = os.environ.get("WANDB_API_KEY") is not None
    if use_wandb:
        import wandb
        wandb.init(project=wandb_project, name="ecotopia-extract-nemo-12b")

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=20,
        save_strategy="steps",
        save_steps=50,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to="wandb" if use_wandb else "none",
        run_name="ecotopia-extract-nemo-12b",
        hub_model_id=HF_REPO,
        push_to_hub=True,
        hub_strategy="end",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    print("Starting training...")
    trainer.train()

    print("Saving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"Pushing to {HF_REPO}...")
    trainer.push_to_hub()

    print("Done!")


if __name__ == "__main__":
    main()
