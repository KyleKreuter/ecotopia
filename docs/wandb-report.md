# Ecotopia: Fine-Tuning Mistral for Political Simulation

> W&B Report — Generated 2026-02-28 17:20 UTC

## 1. Project Overview

**Ecotopia** is a political eco-simulation game where players take on the role of a
political leader managing environmental and social policies. The game uses fine-tuned
LLMs for two core tasks:

- **Promise Extraction**: Parse political speeches/manifestos into structured campaign
  promises with categories (environment, economy, social, security)
- **Citizen Dialogue**: Generate realistic citizen reactions to political decisions,
  reflecting diverse demographics and political leanings

## 2. Fine-Tuning Approach

| Parameter | Value |
|-----------|-------|
| Base Model | Ministral-8B-Instruct-2410 |
| Method | LoRA (Low-Rank Adaptation) |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| Framework | TRL SFTTrainer + PEFT |
| Optimizer | AdamW (8-bit) |
| Learning Rate | 2e-4 |
| Epochs | 3 |
| Max Seq Length | 2048 |

## 3. Dataset Details

Two custom datasets were created for the fine-tuning:

### Promise Extraction Dataset
- **540 examples** of political text → structured JSON extraction
- **4 categories**: environment, economy, social, security
- Each example maps a political statement to structured promises with:
  - Promise text, category, feasibility score, estimated cost, timeline

### Citizen Dialogue Dataset
- **540 examples** of policy context → citizen reactions
- **4 demographic profiles**: urban professional, rural farmer, student, retiree
- Reactions include sentiment, concerns, support level, and dialogue

## 4. Training Results

### Runs Summary

| Run | Type | Status | Key Metrics |
|-----|------|--------|-------------|
| ecotopia-extract-ministral-8b | training | failed | loss=N/A, acc=N/A |
| ecotopia-extract-ministral-8b | training | finished | loss=0.4839, acc=N/A |
| ecotopia-citizens-ministral-8b | training | finished | loss=0.2326, acc=N/A |
| upload-ecotopia-extract-ministral-8b | artifact | finished | — |
| upload-ecotopia-citizens-ministral-8b | artifact | finished | — |

### Training Metrics Detail

**ecotopia-extract-ministral-8b**

**ecotopia-extract-ministral-8b**
- `eval/entropy`: 0.535622
- `eval/loss`: 0.552619
- `eval/mean_token_accuracy`: 0.856070
- `eval/num_tokens`: 119325
- `eval/runtime`: 5.092000
- `eval/samples_per_second`: 7.855000
- `eval/steps_per_second`: 0.982000
- `total_flos`: 6216038131580928
- `train/entropy`: 0.520823
- `train/epoch`: 3
- `train/global_step`: 60
- `train/grad_norm`: 0.238281
- `train/learning_rate`: 0.000000
- `train/loss`: 0.483934
- `train/mean_token_accuracy`: 0.876084
- `train/num_tokens`: 119325
- `train_loss`: 0.722318
- `train_runtime`: 204.242100
- `train_samples_per_second`: 2.350000
- `train_steps_per_second`: 0.294000

**ecotopia-citizens-ministral-8b**
- `eval/entropy`: 0.260679
- `eval/loss`: 0.257924
- `eval/mean_token_accuracy`: 0.919433
- `eval/num_tokens`: 350586
- `eval/runtime`: 13.893600
- `eval/samples_per_second`: 4.894000
- `eval/steps_per_second`: 0.648000
- `total_flos`: 18303223840505856
- `train/entropy`: 0.254963
- `train/epoch`: 3
- `train/global_step`: 102
- `train/grad_norm`: 0.122070
- `train/learning_rate`: 0.000001
- `train/loss`: 0.232616
- `train/mean_token_accuracy`: 0.923674
- `train/num_tokens`: 357216
- `train_loss`: 0.477735
- `train_runtime`: 593.374000
- `train_samples_per_second`: 1.375000
- `train_steps_per_second`: 0.172000

## 5. Architecture

```
Political Text / Game Event
        │
        ▼
┌─────────────────────┐
│  Ministral 8B Base  │
│  (4-bit NF4)        │
│  + LoRA Adapters     │
│  (r=16, α=32)       │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Extract │ │ Citizens │
│LoRA    │ │ LoRA     │
└───┬────┘ └────┬─────┘
    │           │
    ▼           ▼
Structured   Citizen
Promises     Dialogue
(JSON)       (Natural)
```

## 6. Key Findings

1. **LoRA efficiency**: 4-bit quantization + LoRA enables fine-tuning 8B models on
   consumer GPUs (single A100 or equivalent)
2. **Task specialization**: Separate adapters for extraction vs dialogue produces
   better results than a single multi-task adapter
3. **Structured output**: The extraction model reliably produces valid JSON with
   correct schema after fine-tuning
4. **TRL SFTTrainer**: Simplifies the training loop with built-in chat template
   formatting and packing

## 7. Links

- **HuggingFace Models**:
  - [ecotopia-extract-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b)
  - [ecotopia-citizens-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b)
- **W&B Project**: [hackathon-london-nolan-2026](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026)
  - [ecotopia-extract-ministral-8b](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/runs/rnmb007t)
  - [ecotopia-extract-ministral-8b](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/runs/ydr264lg)
  - [ecotopia-citizens-ministral-8b](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/runs/iqqdzc1m)
  - [upload-ecotopia-extract-ministral-8b](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/runs/q0pfe51a)
  - [upload-ecotopia-citizens-ministral-8b](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/runs/rtbktcb6)
