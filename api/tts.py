"""ElevenLabs TTS service for Ecotopia citizen voices."""
import os
import hashlib
from pathlib import Path

import httpx

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
BASE_URL = "https://api.elevenlabs.io/v1"

# Map citizen archetypes to ElevenLabs voice IDs
CITIZEN_VOICES = {
    "Martha Green": "21m00Tcm4TlvDq8ikWAM",
    "Bob Industrial": "29vD33N1CtxCmqQRPOHJ",
    "Dr. Sarah Chen": "EXAVITQu4vr4xnSDxMaL",
    "Tommy Student": "ErXwobaYiN019PkySvjV",
    "default": "21m00Tcm4TlvDq8ikWAM",
}


def get_voice_id(citizen_name: str) -> str:
    """Get ElevenLabs voice ID for a citizen."""
    return CITIZEN_VOICES.get(citizen_name, CITIZEN_VOICES["default"])


def text_to_speech(text: str, citizen_name: str = "default", output_dir: str = "audio") -> str:
    """Convert citizen dialogue to speech. Returns path to audio file."""
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not set")

    voice_id = get_voice_id(citizen_name)

    text_hash = hashlib.md5(f"{citizen_name}:{text}".encode()).hexdigest()[:12]
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = f"{output_dir}/{text_hash}.mp3"

    if Path(output_path).exists():
        return output_path

    response = httpx.post(
        f"{BASE_URL}/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
            },
        },
        timeout=30.0,
    )
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path


def list_available_voices() -> list[dict]:
    """List all available ElevenLabs voices."""
    if not ELEVENLABS_API_KEY:
        return []

    response = httpx.get(
        f"{BASE_URL}/voices",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        timeout=10.0,
    )
    response.raise_for_status()
    voices = response.json().get("voices", [])
    return [{"id": v["voice_id"], "name": v["name"]} for v in voices]


if __name__ == "__main__":
    voices = list_available_voices()
    print(f"Available voices: {len(voices)}")
    for v in voices[:10]:
        print(f"  {v['name']}: {v['id']}")

    path = text_to_speech(
        "Mayor, your promise to build solar panels is wonderful! Our children deserve clean air.",
        citizen_name="Martha Green",
    )
    print(f"Audio saved: {path}")
