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
"""Fine-tune Mistral Small 22B on Ecotopia citizens dialogue data using TRL SFT + QLoRA.

Runs as a HuggingFace Job via: hf jobs uv run --flavor a10g-large hf_finetune_citizens_small.py
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

BASE_MODEL = "mistralai/Mistral-Small-Instruct-2409"
OUTPUT_DIR = "./ecotopia-citizens-small-22b"
HF_REPO = "mistral-hackaton-2026/ecotopia-citizens-small-22b"
MAX_SEQ_LENGTH = 2048
NUM_EPOCHS = 3
BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 8
LEARNING_RATE = 2e-4
LORA_R = 16
LORA_ALPHA = 32


def load_data() -> tuple[Dataset, Dataset]:
    """Load citizens training data from HF dataset splits."""
    api = HfApi()
    train_path = api.hf_hub_download(
        repo_id="mistral-hackaton-2026/ecotopia-citizens-data",
        filename="train.jsonl",
        repo_type="dataset",
    )
    val_path = api.hf_hub_download(
        repo_id="mistral-hackaton-2026/ecotopia-citizens-data",
        filename="validation.jsonl",
        repo_type="dataset",
    )

    def read_jsonl(path: str) -> list[dict]:
        examples = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        return examples

    train_ds = Dataset.from_list(read_jsonl(train_path))
    val_ds = Dataset.from_list(read_jsonl(val_path))
    return train_ds, val_ds


def main() -> None:
    """Fine-tune Mistral Small 22B with QLoRA on citizens data."""
    print(f"Fine-tuning {BASE_MODEL} for Ecotopia citizens")

    train_ds, val_ds = load_data()
    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}")

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
        wandb.init(project=wandb_project, name="ecotopia-citizens-small-22b")

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
        max_seq_length=MAX_SEQ_LENGTH,
        report_to="wandb" if use_wandb else "none",
        run_name="ecotopia-citizens-small-22b",
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
