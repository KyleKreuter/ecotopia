# Ecotopia — Fine-Tuning Plan

## Architecture: 2 Specialized Pipelines

```
Player speech + game state
        │
        ▼
  ┌──────────────┐
  │  FT-Extract  │  Promise extraction + contradiction detection
  └──────┬───────┘
         │ promises + contradictions (JSON)
         ▼
  ┌──────────────┐
  │ FT-Citizens  │  Citizen dialogue + spawning + interactions
  └──────┬───────┘
         │ reactions + spawns + approval deltas (JSON)
         ▼
    Backend applies changes (rule-based)
```

## FT-Extract: Promise Extraction + Contradiction Detection

| Model | API name | Fine-tuned? | Role |
|---|---|---|---|
| Ministral 8B | `ministral-8b-latest` | Yes SFT | Small specialist |
| Mistral Nemo 12B | `open-mistral-nemo` | Yes SFT | Medium specialist |
| Mistral Large 3 | `mistral-large-latest` | No Base | Benchmark |

**Dataset:** 200 examples in `training/data/extraction/`
- 25 explicit promises
- 55 implicit + no promise + ambivalent
- 60 contradictions (clear, subtle, none)
- 60 edge cases (toxic, long, mixed lang, game-over, self-contradicting)

## FT-Citizens: Citizen Dialogue + Dynamic Spawning

| Model | API name | Fine-tuned? | Role |
|---|---|---|---|
| Mistral Small 24B | `mistral-small-latest` | Yes SFT | Production (in-game) |
| Mistral Large 3 | `mistral-large-latest` | No Base | Benchmark |

**Dataset:** ~340 examples (to be generated)

## W&B Evaluation Story

- **Extraction:** "Can a fine-tuned 8B/12B beat raw Large 3 on structured extraction?"
- **Citizens:** "Can a fine-tuned Small 24B match raw Large 3 on creative roleplay?"
- **Pipeline:** "Specialized small models > one large generalist, at 5x lower cost"

## Budget

| Item | Cost |
|---|---|
| FT: Ministral 8B (extraction) | ~$4 |
| FT: Nemo 12B (extraction) | ~$5 |
| FT: Small 24B (citizens) | ~$12 |
| Data gen + eval | ~$5 |
| **Total** | **~$26** |
| **Available** | **$35** ($15 Mistral + $20 HF) |
