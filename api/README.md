# Ecotopia API

FastAPI backend wrapping Mistral API calls with Weights & Biases Weave tracing.

## Setup

```bash
pip install -r requirements.txt
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | Yes | - | Mistral API key |
| `WANDB_API_KEY` | Yes | - | W&B API key for Weave tracing |
| `EXTRACTION_MODEL` | No | `mistral-small-latest` | Model for promise extraction |
| `CITIZENS_MODEL` | No | `mistral-small-latest` | Model for citizen reactions |

## Run

```bash
cd ecotopia
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

Or directly:

```bash
python api/server.py
```

## Endpoints

### `GET /api/health`

Returns service status and model config.

### `POST /api/game/speech`

Process a mayor speech through the AI pipeline (extract promises, detect contradictions, generate citizen reactions).

Request body:

```json
{
  "speech": "I promise to build more parks and invest in renewable energy!",
  "game_state": {
    "round_number": 1,
    "ecology": 50,
    "economy": 50,
    "research": 50,
    "promises": [],
    "citizens": []
  }
}
```

Response contains `extraction` (promises + contradictions) and `reactions` (citizen responses).

## Tracing

All Mistral calls are traced via W&B Weave under the project `ecotopia-hackathon`. View traces at https://wandb.ai.
