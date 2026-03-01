# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "transformers>=4.48",
#   "peft",
#   "accelerate",
#   "torch",
#   "huggingface_hub",
# ]
# ///
"""Merge LoRA adapter into base model for Ecotopia citizens 8B.

Runs as HF Job: hf jobs uv run --flavor l4x1 merge_citizens_8b.py
"""

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "mistralai/Ministral-8B-Instruct-2410"
ADAPTER_REPO = "mistral-hackaton-2026/ecotopia-citizens-ministral-8b"
OUTPUT_REPO = "mistral-hackaton-2026/ecotopia-citizens-8b-merged"


def main() -> None:
    """Merge LoRA weights into base model and push to Hub."""
    print(f"Loading base model: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    print(f"Loading adapter: {ADAPTER_REPO}")
    model = PeftModel.from_pretrained(model, ADAPTER_REPO)

    print("Merging weights...")
    model = model.merge_and_unload()

    print(f"Pushing merged model to {OUTPUT_REPO}...")
    model.push_to_hub(OUTPUT_REPO, private=False)
    tokenizer.push_to_hub(OUTPUT_REPO, private=False)
    print("Done!")


if __name__ == "__main__":
    main()
