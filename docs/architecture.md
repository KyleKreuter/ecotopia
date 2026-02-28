# Architecture -- Ecotopia

## System Overview

Ecotopia uses a multi-stage pipeline combining fine-tuned Mistral models, a
rule-based game engine, ElevenLabs TTS for citizen voices, and Weave tracing
on every call.

```
Player (Browser)
    |
    | Speech (voice or text)
    v
+-------------------+
|   Frontend (UI)   |  React + TypeScript
+-------------------+
    |
    | POST /api/turn
    v
+-------------------+
| FastAPI Backend   |  Orchestrates game logic + Weave tracing
+-------------------+
    |
    |--- 1. FT-Extract (Ministral 8B fine-tuned)
    |       Extracts promises, types, contradictions from speech
    |
    |--- 2. Rule Engine
    |       Applies deterministic state updates (ecology, economy, research)
    |       Tracks promise fulfillment, checks win/lose conditions
    |
    |--- 3. FT-Citizens (Ministral 8B fine-tuned)
    |       Generates citizen dialogue, approval deltas, spawn events
    |
    |--- 4. ElevenLabs TTS
    |       Each citizen has a unique voice
    |       Citizen dialogue is spoken aloud in the UI
    |
    v
Updated game state + audio -> sent back to frontend
```

## Full Pipeline

```
Speech -> FT-Extract -> Rule Engine -> FT-Citizens -> TTS -> UI
```

1. **Speech Input**: Player types or speaks a free-text speech
2. **FT-Extract**: Extracts promises and detects contradictions (structured JSON)
3. **Rule Engine**: Applies deterministic game state updates based on actions and extracted promises
4. **FT-Citizens**: Generates in-character citizen reactions based on game state and extraction results
5. **ElevenLabs TTS**: Converts citizen dialogue to speech with unique voices per citizen
6. **UI**: Displays updated game state, citizen reactions with speech bubbles and animations

## Data Generation

Training data for fine-tuning was generated using two sources:

- **Hand-crafted examples**: 540 JSONL examples covering extraction and citizen dialogue
- **AWS Bedrock**: 18 additional synthetic examples generated via Bedrock for edge case coverage

## Observability

Every Mistral API call is traced via **W&B Weave**:

- Input prompts, outputs, latency, token counts
- Evaluation scorers for extraction accuracy and citizen response quality
- Training metrics logged to W&B project during HF Jobs execution
- Full eval tables comparing base vs fine-tuned vs Large models

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React, TypeScript, Vite | Game interface with speech bubbles, animations |
| Backend | Python, FastAPI | API server, game orchestration |
| ML Models | Ministral 8B (fine-tuned) | Promise extraction, citizen dialogue |
| TTS | ElevenLabs | Unique voice per citizen |
| Data Gen | AWS Bedrock | Synthetic training data generation |
| Training | HuggingFace Training Jobs | SFT training infrastructure |
| Tracing | W&B Weave | Traces every Mistral call |
| Experiment Tracking | Weights & Biases | Metrics, eval tables, reports |
| Model Hosting | HuggingFace Hub | Adapter/model storage |

## Key Design Decisions

**Why 2 models instead of 1?**
Separation of concerns: extraction is a structured NLP task, citizen dialogue is
creative generation. Smaller, focused datasets train better than one large
multi-task dataset. Each model can be evaluated and improved independently.

**Why a rule-based game engine between the two models?**
Game state updates need to be deterministic. No hallucination risk for score
calculations. Faster execution. Easier to balance gameplay.

**Why ElevenLabs TTS?**
Each citizen has a distinct personality -- giving them a unique voice makes the
game more immersive. Citizens speak their reactions aloud, making the political
simulation feel alive.

**Why Ministral 8B over 3B?**
Better at structured JSON output. Better understanding of nuanced promises and
contradictions. Still fast enough for real-time gameplay. Fine-tuned 8B beats
Large base model on all metrics.
