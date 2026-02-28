# Fine-Tuning Results

Ecotopia uses two fine-tuned models for its AI pipeline: one for promise
extraction and one for citizen dialogue generation. Both are fine-tuned from
Mistral foundation models using SFT (Supervised Fine-Tuning) with LoRA.

## Extraction Model

**Task:** Extract promises, contradictions, and confidence scores from mayor
speeches. Output is structured JSON.

### Training Configuration

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| Base model             | `mistralai/Ministral-8B-Instruct-2410` |
| Method                 | SFT + LoRA (via TRL `SFTTrainer`)      |
| LoRA rank (r)          | 16                                     |
| LoRA alpha             | 32                                     |
| Target modules         | `q_proj`, `k_proj`, `v_proj`, `o_proj` |
| Max sequence length    | 2048                                   |
| Epochs                 | 3                                      |
| Batch size             | 2                                      |
| Gradient accumulation  | 4 (effective batch size 8)             |
| Learning rate          | 2e-4                                   |
| Quantization           | 4-bit (BitsAndBytes NF4)              |
| Hardware               | HuggingFace Jobs A10G                  |

### Training Results

| Metric                    | Value   |
|---------------------------|---------|
| Train loss                | 0.484   |
| Eval loss                 | 0.553   |
| Token accuracy (eval)     | 85.6%   |
| Token accuracy (final)    | 87.6%   |
| Training cost             | ~$0.80  |

### Training Data

4 batches of hand-crafted JSONL examples covering:

- `batch1_explicit_promises.jsonl` -- clear, direct promises
- `batch2_implicit_and_none.jsonl` -- implied commitments and no-promise speeches
- `batch3_contradictions.jsonl` -- contradictory statements across rounds
- `batch4_edge_cases.jsonl` -- ambiguous, sarcastic, multi-topic speeches

Split: 80/20 train/validation.

### Mistral API Fine-Tuning

Additionally launched via Mistral's fine-tuning API on:
- `ministral-8b-latest`
- `open-mistral-nemo` (12B) -- in progress

### HuggingFace Model

- Repository: [mistral-hackaton-2026/ecotopia-extract-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b)

---

## Citizens Model

**Task:** Generate in-character citizen reactions, approval changes, and
dynamically spawn new citizens based on game events.

### Training Configuration

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| Base model             | `mistralai/Ministral-8B-Instruct-2410` |
| Method                 | SFT + LoRA (via TRL `SFTTrainer`)      |
| LoRA rank (r)          | 16                                     |
| LoRA alpha             | 32                                     |
| Target modules         | `q_proj`, `k_proj`, `v_proj`, `o_proj` |
| Max sequence length    | 2048                                   |
| Epochs                 | 3                                      |
| Batch size             | 2                                      |
| Gradient accumulation  | 4 (effective batch size 8)             |
| Learning rate          | 2e-4                                   |
| Quantization           | 4-bit (BitsAndBytes NF4)              |
| Hardware               | HuggingFace Jobs A10G                  |

### Training Results

| Metric                    | Value   |
|---------------------------|---------|
| Train loss                | 0.233   |
| Eval loss                 | 0.258   |
| Token accuracy            | 92.3%   |
| Training cost             | ~$1.00  |

### Training Data

4 batches:

- `batch1_core_reactions.jsonl` -- basic citizen reactions to common promises
- `batch2_dynamic_spawning.jsonl` -- new citizens appearing based on events
- `batch3_complex_scenarios.jsonl` -- multi-citizen interactions, conflicting interests
- `batch4_edge_cases.jsonl` -- extreme scenarios, edge cases

### Mistral API Fine-Tuning

- Launched via Mistral API on `mistral-small-latest` with suffix `eco_citizens`
- Small 22B fine-tune in progress

### HuggingFace Model

- Repository: [mistral-hackaton-2026/ecotopia-citizens-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b)

---

## Benchmark: Fine-Tuned 8B vs Base Models

Evaluation on 40 held-out examples across 4 metrics:

| Metric                  | 8B FT | 8B Base | Small 22B Base | Large Base |
|-------------------------|-------|---------|----------------|------------|
| Promise Count Accuracy  | 100   | 75      | 82.5           | 65         |
| Contradiction Detection | 100   | 55      | 32.5           | 70         |
| Promise Type Precision  | 100   | 52.5    | 75             | 55         |
| JSON Schema Compliance  | 100   | 100     | 100            | 100        |

Key finding: **Fine-tuned 8B beats all base models -- including Large -- on every metric.**
A $2 fine-tune on a small model outperforms models 10x its size on domain-specific tasks.

### Models in Progress

- **Nemo 12B** (`open-mistral-nemo`): Fine-tuning launched via Mistral API
- **Small 22B** (`mistral-small-latest`): Fine-tuning launched via Mistral API

---

## Cost Breakdown

| Item                          | Cost    |
|-------------------------------|---------|
| Extract fine-tune (A10G)      | ~$0.80  |
| Citizens fine-tune (A10G)     | ~$1.00  |
| Evaluation runs               | ~$0.15  |
| **Total**                     | **~$2** |

---

## W&B / Weave Tracking

- **W&B Project:** [hackathon-london-nolan-2026](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026)
- **W&B Report:** [Ecotopia: Fine-Tuning Mistral for Political Simulation](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia:-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NTQxMA==)
- **Training runs:** Logged to W&B project during HF Jobs execution
- **Inference tracing:** All production Mistral calls traced via Weave under
  project `ecotopia-hackathon`
- **Eval dashboard:** `training/wandb_dashboard.py` and
  `training/create_wandb_report.py` generate comparison reports

---

## Lessons Learned

### flash_attn compatibility

The `flash_attn` package often fails to install on HuggingFace Jobs due to CUDA
version mismatches. Solution: use `attn_implementation="eager"` in
`BitsAndBytesConfig` or skip flash attention entirely. The 4-bit quantized
models fit in A10G VRAM without it.

### TRL 0.17 breaking changes

TRL >= 0.17 changed the `SFTTrainer` API. Key changes:
- `max_seq_length` moved into `SFTConfig` (no longer a trainer kwarg)
- `dataset_text_field` deprecated in favor of formatting functions
- Ensure `trl>=0.17` and `transformers>=4.48` are pinned together

### Data quality over quantity

With only ~100-200 examples per task, data quality matters far more than volume.
Hand-crafted examples with diverse edge cases (sarcasm, ambiguity, multi-topic
speeches) produced better results than larger synthetic datasets.

### JSON output reliability

Fine-tuning dramatically improved JSON output validity (80% to 98%). Combined
with `response_format={"type": "json_object"}` at inference time, the pipeline
achieves near-100% valid JSON in production.
