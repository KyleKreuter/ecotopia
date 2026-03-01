# Ecotopia

Political eco-simulation game. You are the mayor of a city facing ecological collapse: 7 rounds, tile-based grid, three resource bars (ecology, economy, research). Deliver free-text speeches, watch AI extract your promises, and face citizen reactions powered by fine-tuned Mistral models.

**Team:** Nolan Cacheux, Kyle Kreuter
**Built at:** Mistral Hackathon London 2026 (48 hours)

## What It Does

Ecotopia puts you in charge of a dying city through 7 rounds of ecological crisis. Each round, you enact policies on a tile-based grid (close a coal plant, fund research, build infrastructure) and deliver a free-text speech to your citizens. Fine-tuned models extract promises from your words and track them across rounds. Citizens react based on their personality, profession, and memory of your past speeches. Broken promises erode trust; honesty builds it.

## Architecture

**Play now:** [ecotopia.nolancacheux.com](https://ecotopia.nolancacheux.com) *(HF endpoints may be paused outside demo/hackathon — credits-based)*

```
Speech → FT-Extract (12B) → Contradiction Detection → FT-Citizens (8B) → ElevenLabs TTS → UI
```

| Stage | Description |
|-------|-------------|
| Speech Input | Player types a free-text speech |
| FT-Extract | Fine-tuned Mistral Nemo 12B extracts promises with deadlines and detects contradictions (JSON) |
| Game Engine | Deterministic state updates: ecology, economy, research scores |
| FT-Citizens | Fine-tuned Ministral 8B generates citizen reactions, dialogues, and approval deltas |
| TTS | ElevenLabs gives each citizen a unique voice (10 voice profiles) |
| UI | Phaser 3 pixel art frontend with tile grid, citizen sprites, and speech bubbles |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Phaser 3, TypeScript, Vite, Pixel Art |
| Backend | Spring Boot 3.5, Spring AI, PostgreSQL |
| AI Models | Fine-tuned Mistral via QLoRA on HuggingFace Inference Endpoints |
| TTS | ElevenLabs Turbo v2.5 (unique voice per citizen) |
| Monitoring | Weights & Biases (training metrics + evaluation) |

## Fine-Tuned Models

| Model | Task | Base | HuggingFace |
|-------|------|------|-------------|
| ecotopia-extract-ministral-8b | Promise extraction | Ministral 8B Instruct | [LoRA](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b) / [Merged](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-8b-merged) |
| ecotopia-extract-nemo-12b | Promise extraction | Mistral Nemo 12B | [LoRA](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-nemo-12b) |
| ecotopia-citizens-ministral-8b | Citizen reactions | Ministral 8B Instruct | [LoRA](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b) / [Merged](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-8b-merged) |
| ecotopia-citizens-small-22b | Citizen reactions | Mistral Small 22B | [LoRA](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-small-22b) / [Merged](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-24b-merged) |

**Datasets:**
- [ecotopia-extraction-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-extraction-dataset) (300 examples)
- [ecotopia-citizens-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-citizens-dataset) (390 examples)

## Setup

### Prerequisites
- Java 21+
- Docker (for PostgreSQL)
- Node.js 18+ (for frontend)

### Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# 2. Start database
cd backend && docker compose up -d

# 3. Start backend (port 7777)
cd backend && ./mvnw spring-boot:run

# 4. Start frontend (port 5173)
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173` in your browser.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EXTRACTION_ENDPOINT` | Yes | HuggingFace endpoint URL for 8B extraction model |
| `CITIZEN_ENDPOINT` | Yes | HuggingFace endpoint URL for 24B citizen model |
| `HF_TOKEN` | Yes | HuggingFace API token (for endpoint auth) |
| `ELEVENLABS_API_KEY` | No | ElevenLabs API key (enables citizen voice TTS) |
| `DB_USERNAME` | No | PostgreSQL username (default: ecotopia) |
| `DB_PASSWORD` | No | PostgreSQL password (default: ecotopia) |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/games` | Create a new game |
| GET | `/api/games/{id}` | Get game state (resources, citizens, tiles) |
| POST | `/api/games/{id}/speech` | Submit speech (triggers AI extraction + reactions + TTS) |
| POST | `/api/games/{id}/end-round` | End current round, advance to next |
| GET | `/api/games/{id}/promises` | List all tracked promises |
| POST | `/api/games/{id}/tiles/{tileId}/action` | Execute tile action |

### Speech Response Format

```json
{
  "extractedPromises": [
    {"id": 1, "text": "build wind farms", "deadline": 3, "status": "ACTIVE"}
  ],
  "contradictions": [
    {"description": "Promises forests while building coal plants", "severity": "high"}
  ],
  "citizenReactions": [
    {
      "citizenName": "Karl",
      "dialogue": "Wind farms won't replace factory jobs.",
      "tone": "suspicious",
      "approvalDelta": -3,
      "audioBase64": "base64_encoded_mp3..."
    }
  ]
}
```

### HuggingFace Endpoints

Both fine-tuned models are deployed on HuggingFace Inference Endpoints with NF4 4-bit quantization via custom `handler.py`. Endpoints scale to zero after 15 minutes of inactivity.

**Cold start warning:** First request after idle takes ~5 minutes. The backend retries automatically (10x with 30s delay).

## W&B Report

Full training metrics, evaluation benchmarks, and model comparisons:

[Ecotopia: Fine-Tuning Mistral for Political Simulation (W&B)](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NzA3OA)

[PDF Report](report/ecotopia-finetuning-report.pdf)

## License

MIT
