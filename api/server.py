"""Ecotopia API server with Weave tracing for Mistral calls."""
import json
import os

import weave
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from mistralai import Mistral
from pydantic import BaseModel

from api.tts import text_to_speech

weave.init("ecotopia-hackathon")

app = FastAPI(title="Ecotopia API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", ""))

EXTRACTION_MODEL = os.environ.get("EXTRACTION_MODEL", "mistral-small-latest")
CITIZENS_MODEL = os.environ.get("CITIZENS_MODEL", "mistral-small-latest")


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{name}.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return f"You are an AI for the Ecotopia game. Task: {name}"


class SpeechRequest(BaseModel):
    """Request body for the speech endpoint."""

    speech: str
    game_state: dict


class ActionRequest(BaseModel):
    """Request body for build/demolish actions."""

    action_type: str
    x: int
    y: int
    tile_type: str
    game_state: dict


class GameState(BaseModel):
    """Simplified game state representation."""

    round_number: int = 1
    ecology: int = 50
    economy: int = 50
    research: int = 50
    promises: list = []
    citizens: list = []


@weave.op
def extract_promises(speech: str, game_context: str) -> dict:
    """Extract promises and contradictions from mayor speech."""
    response = client.chat.complete(
        model=EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": load_prompt("extraction")},
            {
                "role": "user",
                "content": f"Game context:\n{game_context}\n\nMayor's speech:\n{speech}",
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"promises": [], "contradictions": [], "raw": content}


@weave.op
def generate_reactions(
    promises: list, contradictions: list, game_context: str
) -> dict:
    """Generate citizen reactions to promises."""
    response = client.chat.complete(
        model=CITIZENS_MODEL,
        messages=[
            {"role": "system", "content": load_prompt("citizens")},
            {
                "role": "user",
                "content": (
                    f"Promises: {json.dumps(promises)}\n"
                    f"Contradictions: {json.dumps(contradictions)}\n"
                    f"Game context: {game_context}"
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"reactions": [], "dynamic_citizens": [], "raw": content}


@weave.op
def process_turn(speech: str, game_state: dict) -> dict:
    """Full turn pipeline: extract promises then generate citizen reactions."""
    game_context = json.dumps(game_state, indent=2)
    extraction = extract_promises(speech, game_context)
    promises = extraction.get("promises", [])
    contradictions = extraction.get("contradictions", [])
    reactions = generate_reactions(promises, contradictions, game_context)
    return {
        "extraction": extraction,
        "reactions": reactions,
    }


@app.post("/api/game/speech")
async def submit_speech(req: SpeechRequest) -> dict:
    """Process a player's speech through the AI pipeline."""
    try:
        result = process_turn(req.speech, req.game_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TTSRequest(BaseModel):
    """Request body for TTS endpoint."""

    citizen_name: str = "default"
    text: str


@app.post("/api/tts")
async def generate_speech(req: TTSRequest) -> FileResponse:
    """Generate speech audio for a citizen's dialogue."""
    try:
        path = text_to_speech(req.text, req.citizen_name)
        return FileResponse(path, media_type="audio/mpeg")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health() -> dict:
    """Return service health and model configuration."""
    return {
        "status": "ok",
        "extraction_model": EXTRACTION_MODEL,
        "citizens_model": CITIZENS_MODEL,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
