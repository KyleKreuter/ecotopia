# Ecotopia API Contract

REST API contract for the Ecotopia game server (FastAPI + Mistral AI).

Base URL: `http://localhost:8000`

All requests and responses use `Content-Type: application/json`.

## Observability

Every Mistral AI call is traced via [Weave](https://wandb.me/weave) under the
project `ecotopia-hackathon`. Set `WANDB_API_KEY` to enable dashboard access.
Traced operations:

- `extract_promises` -- promise extraction from mayor speech
- `generate_reactions` -- citizen reaction generation
- `process_turn` -- full turn orchestration (calls both above)

## Endpoints

### POST /api/game/speech

Process a player's speech through the AI pipeline: extract promises and
contradictions, then generate citizen reactions.

**Request body** (`SpeechRequest`):

| Field        | Type   | Required | Description                           |
|--------------|--------|----------|---------------------------------------|
| `speech`     | string | yes      | The mayor's speech text               |
| `game_state` | object | yes      | Current game state (round, metrics, citizens, promises) |

```json
{
  "speech": "Citizens, I promise to protect the northern forest and invest in renewable energy!",
  "game_state": {
    "round_number": 1,
    "ecology": 50,
    "economy": 50,
    "research": 50,
    "promises": [],
    "citizens": [
      {
        "name": "Elena",
        "role": "ecologist",
        "approval": 60
      }
    ]
  }
}
```

**Response** `200 OK`:

```json
{
  "extraction": {
    "promises": [
      {
        "text": "protect the northern forest",
        "type": "explicit",
        "confidence": 0.95,
        "category": "ecology"
      }
    ],
    "contradictions": []
  },
  "reactions": {
    "reactions": [
      {
        "citizen": "Elena",
        "dialogue": "Finally, someone who cares about our forests!",
        "tone": "hopeful",
        "approval_change": 10
      }
    ],
    "dynamic_citizens": []
  }
}
```

**Error** `500`:

```json
{
  "detail": "Error message from Mistral or processing pipeline"
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/game/speech \
  -H "Content-Type: application/json" \
  -d '{
    "speech": "I will build a new factory and create jobs for everyone!",
    "game_state": {
      "round_number": 2,
      "ecology": 45,
      "economy": 55,
      "research": 50,
      "promises": [],
      "citizens": []
    }
  }'
```

---

### GET /api/health

Return service health status and active model configuration.

**Response** `200 OK`:

```json
{
  "status": "ok",
  "extraction_model": "mistral-small-latest",
  "citizens_model": "mistral-small-latest"
}
```

**curl example:**

```bash
curl http://localhost:8000/api/health
```

---

## Pydantic Models

### SpeechRequest

```python
class SpeechRequest(BaseModel):
    speech: str
    game_state: dict
```

### ActionRequest

```python
class ActionRequest(BaseModel):
    action_type: str
    x: int
    y: int
    tile_type: str
    game_state: dict
```

### GameState

```python
class GameState(BaseModel):
    round_number: int = 1
    ecology: int = 50
    economy: int = 50
    research: int = 50
    promises: list = []
    citizens: list = []
```

## Environment Variables

| Variable           | Default                | Description                              |
|--------------------|------------------------|------------------------------------------|
| `MISTRAL_API_KEY`  | (empty)                | Mistral AI API key (required)            |
| `EXTRACTION_MODEL` | `mistral-small-latest` | Model for promise extraction             |
| `CITIZENS_MODEL`   | `mistral-small-latest` | Model for citizen reaction generation    |
| `WANDB_API_KEY`    | (unset)                | Weights & Biases key for Weave tracing   |

## CORS

All origins are allowed (`*`). This is intended for hackathon/development use.
