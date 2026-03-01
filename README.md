# Ecotopia

Political eco-simulation game. You are the mayor of a city facing ecological collapse: 7 rounds, tile-based grid, three resource bars (ecology, economy, research). Deliver free-text speeches, watch AI extract your promises, and face citizen reactions powered by fine-tuned Mistral models.

**Team:** Nolan Cacheux, Kyle Kreuter
**Built at:** Mistral Hackathon London 2026 (48 hours)

## What It Does

Ecotopia puts you in charge of a dying city through 7 rounds of ecological crisis. Each round, you enact policies on a tile-based grid (close a coal plant, fund research, build infrastructure) and deliver a free-text speech to your citizens. Fine-tuned models extract promises from your words and track them across rounds. Citizens react based on their personality, profession, and memory of your past speeches. Broken promises erode trust; honesty builds it.

## Architecture

```
Speech → FT-Extract (8B/12B) → Game Engine → FT-Citizens (24B) → TTS → UI
```

| Stage | Description |
|-------|-------------|
| Speech Input | Player types a free-text speech |
| FT-Extract | Fine-tuned Ministral 8B/Nemo 12B extracts promises and contradictions (JSON) |
| Game Engine | Deterministic state updates: ecology, economy, research scores |
| FT-Citizens | Fine-tuned Mistral Small 22B generates citizen reactions and approval changes |
| TTS | ElevenLabs gives each citizen a unique voice |
| UI | React frontend with speech bubbles, animations, updated game state |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite |
| Backend | Spring Boot, Spring AI (Mistral integration) |
| AI Models | Fine-tuned Mistral via LoRA/QLoRA on HuggingFace |
| TTS | ElevenLabs (unique voice per citizen) |
| Monitoring | Weights & Biases (training metrics + Weave tracing) |

## Fine-Tuned Models

| Model | Task | HuggingFace |
|-------|------|-------------|
| ecotopia-extract-ministral-8b | Promise extraction (8B LoRA) | [Link](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b) |
| ecotopia-extract-nemo-12b | Promise extraction (12B) | [Link](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-nemo-12b) |
| ecotopia-citizens-small-22b | Citizen reactions (22B) | [Link](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-small-22b) |

**Datasets:**
- [ecotopia-extraction-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-extraction-dataset)
- [ecotopia-citizens-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-citizens-dataset)

## Run Locally

```bash
# Frontend
cd frontend && npm install && npm run dev

# API server (FastAPI + Weave tracing)
cd api && pip install -r requirements.txt && python server.py

# Backend (Spring Boot)
cd backend && ./mvnw spring-boot:run
```

Open `http://localhost:5173` in your browser.

## Inference Endpoints (HuggingFace)

Both fine-tuned models are deployed on HuggingFace Inference Endpoints using TGI (Text Generation Inference) with LoRA adapters. Endpoints scale to zero when idle.

| Model | Endpoint |
|-------|----------|
| 8B Extract | `https://xsam38gf1zpvndtj.us-east-1.aws.endpoints.huggingface.cloud` |
| 24B Citizens | `https://q574xtmjmyojmv8q.us-east-1.aws.endpoints.huggingface.cloud` |

The endpoints expose an OpenAI-compatible API. Example usage:

```bash
curl https://xsam38gf1zpvndtj.us-east-1.aws.endpoints.huggingface.cloud/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $HF_TOKEN" \
  -d '{
    "model": "tgi",
    "messages": [{"role": "user", "content": "Extract promises from this speech..."}],
    "max_tokens": 512
  }'
```

## W&B Report

Full training metrics, evaluation benchmarks, and Weave traces:

[Ecotopia: Fine-Tuning Mistral for Political Simulation](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia:-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NzA3OA==)

## License

MIT
