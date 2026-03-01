# Sponsors & Tools Used

## Mistral AI (Main Sponsor — Fine-Tuning Track)

**How we used it:**
- Fine-tuned 4 models via Mistral's fine-tuning API: Ministral 8B (extraction + citizens), Mistral Nemo 12B (extraction), Mistral Small 24B (citizens)
- QLoRA (4-bit NF4) + SFT with LoRA rank=16, alpha=32
- Training data generated using Mistral Large via AWS Bedrock
- All models hosted as HuggingFace Inference Endpoints with custom handlers

**Models fine-tuned:**
- `ecotopia-extract-ministral-8b` — Promise extraction (8B)
- `ecotopia-extract-nemo-12b` — Promise extraction (12B)
- `ecotopia-citizens-ministral-8b` — Citizen reactions (8B)
- `ecotopia-citizens-small-22b` — Citizen reactions (24B)

## Weights & Biases (Global Track Sponsor)

**How we used it:**
- Experiment tracking for all 4 fine-tuning runs (loss, token accuracy, learning rate, gradient norms)
- Evaluation logging: extraction benchmarks (valid JSON, promise count, type precision, contradiction detection) and citizen reaction benchmarks (schema compliance, has_reactions, latency)
- W&B Report summarizing all findings: training curves, bar chart comparisons, key metrics
- Comparison tables: fine-tuned 8B vs 12B vs Mistral Large (base)

**W&B Project:** [hackathon-london-nolan-2026](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026)
**W&B Report:** [Ecotopia: Fine-Tuning Mistral for Political Simulation](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NzA3OA)

## ElevenLabs

**How we used it:** Planned but not fully integrated in the final demo. The backend has an `ElevenLabsClient` that maps each citizen to a unique voice profile and generates TTS audio for citizen dialogue. The integration is implemented in code (API client, voice mapping, audio streaming) but was disabled in the live demo because we prioritized getting the fine-tuned models working on inference endpoints. The architecture supports it — each citizen reaction includes an `audioBase64` field that the frontend can play.

**What's implemented:**
- `ElevenLabsClient.java` — REST client for TTS API
- Voice mapping: 10 unique voice profiles (one per citizen archetype)
- Audio response format in the speech API

**Honest status:** Code exists, not active in demo. We did claim ElevenLabs credits but ran out of time to fully test the TTS pipeline end-to-end.

## HuggingFace

**How we used it:**
- Model hosting: all fine-tuned models uploaded to HuggingFace Hub under `mistral-hackaton-2026` organization
- Inference Endpoints: 2 dedicated GPU endpoints (Nvidia L4 + A10G) with custom `handler.py` for 4-bit quantized inference
- Dataset hosting: training data for both extraction and citizen tasks

**HF Organization:** [mistral-hackaton-2026](https://huggingface.co/mistral-hackaton-2026)

## AWS Bedrock

**How we used it:**
- Synthetic training data generation using Mistral Large
- 690 examples total (300 extraction + 390 citizen reactions)
- Three difficulty tiers for extraction data (easy/medium/hard)

## NVIDIA (On-Device Track Sponsor)

**Not used directly.** Our project is in the Fine-Tuning Track. We use GPU compute via HuggingFace Inference Endpoints (Nvidia L4 and A10G GPUs) but did not use any NVIDIA-specific SDKs or on-device tooling.

## Other Technologies

| Tool | Usage |
|------|-------|
| Spring Boot 3.5 | Backend API + game engine |
| Spring AI | LLM integration (OpenAI-compatible client for HF endpoints) |
| PostgreSQL | Game state persistence |
| Phaser 3 | Frontend game engine (TypeScript, pixel art) |
| Vite | Frontend build tool |
| Playwright | E2E testing (6 tests) |
