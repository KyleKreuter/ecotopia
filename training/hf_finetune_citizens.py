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
"""Fine-tune Ministral 8B on Ecotopia citizens dialogue data using TRL SFT + LoRA.

Runs as a HuggingFace Job via: hf jobs uv run --flavor a10g-small hf_finetune_citizens.py
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

BASE_MODEL = "mistralai/Ministral-8B-Instruct-2410"
OUTPUT_DIR = "./ecotopia-citizens-ministral-8b"
HF_REPO = "mistral-hackaton-2026/ecotopia-citizens-ministral-8b"
MAX_SEQ_LENGTH = 2048
NUM_EPOCHS = 3
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
LORA_R = 16
LORA_ALPHA = 32


def load_data() -> tuple[Dataset, Dataset]:
    """Load citizens training data from HF or local."""
    data_dir = Path("/root/clawd/ecotopia/training/data/citizens")

    if not data_dir.exists():
        api = HfApi()
        for f in ["batch1_core_reactions.jsonl", "batch2_dynamic_spawning.jsonl",
                   "batch3_complex_scenarios.jsonl", "batch4_edge_cases.jsonl"]:
            api.hf_hub_download(
                repo_id="mistral-hackaton-2026/ecotopia-citizens-data",
                filename=f,
                local_dir="./data/citizens",
                repo_type="dataset",
            )
        data_dir = Path("./data/citizens")

    examples = []
    for f in sorted(data_dir.glob("batch*.jsonl")):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    examples.append(json.loads(line))

    # 80/20 split
    import random
    random.seed(42)
    random.shuffle(examples)
    split = int(len(examples) * 0.8)

    train_ds = Dataset.from_list(examples[:split])
    val_ds = Dataset.from_list(examples[split:])
    return train_ds, val_ds


def main() -> None:
    """Fine-tune Ministral 8B with LoRA on citizens data."""
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
        dtype=torch.bfloat16,
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
        wandb.init(project=wandb_project, name="ecotopia-citizens-ministral-8b")

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
        run_name="ecotopia-citizens-ministral-8b",
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
