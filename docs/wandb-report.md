# Ecotopia: Fine-Tuning Mistral for Political Simulation

**Nolan Cacheux, Kyle Kreuter**

W&B Report: https://wandb.ai/nolancacheux/hackathon-london-nolan-2026

## 1. Project Overview

Ecotopia is a political simulation game. The player is mayor of a city facing ecological collapse: 7 rounds (5 years each), a tile-based city grid, and three resource bars (ecology, economy, research). Each round, the player gives a speech with promises that directly affect citizens and resources.

We fine-tuned **small Mistral models** to handle two structured JSON tasks in the game pipeline:

- **FT-Extract**: Takes the player's raw speech text and outputs structured JSON with every promise identified, its category (ecology/economy/research), whether it helps or hurts that resource, a deadline in game rounds, and any contradictions between promises. This feeds directly into the game engine to update resource bars.
- **FT-Citizens**: Takes the extracted promises plus the current game state (resource levels, citizen trust scores, round number) and generates dynamic citizen reactions. Each citizen has a name, archetype (environmentalist, industrialist, scientist...), a mood, spoken dialogue, and a trust delta that shifts their relationship with the player.

## 2. Technical Approach

### QLoRA + SFT

- **LoRA**: Trainable matrices (rank=16, alpha=32) injected alongside frozen weights. Only ~0.5% of parameters trained.
- **QLoRA**: Base model quantized to 4-bit NF4, then LoRA applied. Fits a 24B model on a single 48GB GPU.
- **SFT**: 690 input/output pairs generated via AWS Bedrock (Mistral Large). Under 10 minutes training per model.

### Training Data

- Extraction: 300 examples (270 train / 30 val), three difficulty levels
- Citizens: 390 examples (351 train / 39 val), diverse scenarios and citizen types

## 3. Models

### FT-Extract

- **Ministral 8B**: LoRA r=16, alpha=32, 3 epochs, A10G 24GB
- **Mistral Nemo 12B**: Same config, L40S 48GB

### FT-Citizens

- **Mistral Small 24B**: QLoRA 4-bit, r=16, alpha=32, 3 epochs, L40S 48GB. 351 examples.

## 4. Evaluation Results

### Promise Extraction (45 test examples)

Both fine-tuned models beat Large on **promise count (+30%)** and **contradiction detection (+5%)**, at half the latency.

### Citizen Reactions (39 validation examples)

Large returns markdown-wrapped JSON with wrong field names (**0% compliance**). The 24B FT gets **100%**.

## 5. Key Findings

- Small fine-tuned models beat Large on both tasks for structured output
- 24B FT: **100% schema compliance** vs 0% for Large on citizen reactions
- 8B/12B FT: **+30% promise count**, +5% contradiction detection vs Large
- QLoRA fits 24B on a single 48GB GPU, trains in under 10 minutes
- 690 Bedrock-generated examples are enough for strong task specialization

## 6. Resources

- Models: [ecotopia-extract-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b) (30.7MB LoRA)
- Models: [ecotopia-extract-nemo-12b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-nemo-12b) (39.4MB LoRA)
- Models: [ecotopia-citizens-small-22b](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-small-22b) (69.8MB LoRA)
- Datasets: [ecotopia-extraction-data](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-extraction-data) (300 examples)
- Datasets: [ecotopia-citizens-data](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-citizens-data) (390 examples)
