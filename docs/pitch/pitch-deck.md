# Ecotopia - Pitch Deck Outline

## Slide 1: Title

- ECOTOPIA
- "Can you save a city on the edge of ecological collapse?"
- Team: Nolan Cacheux + Kyle Kreuter
- Mistral Worldwide Hackathon London 2026

## Slide 2: The Problem

- Climate policy is complex - tradeoffs between ecology, economy, research
- Politicians make promises they can't keep
- Citizens react differently to the same policies
- How do you teach people about these tradeoffs?

## Slide 3: Our Solution

- A political simulation game powered by Mistral AI
- You are the mayor. 7 rounds. Each round = 5 years.
- Free-text speeches (no pre-written options)
- AI extracts your promises and tracks them
- AI citizens react dynamically with unique voices (ElevenLabs TTS)

## Slide 4: Live Demo

- [Show the game running]
- Type a speech -> see promises extracted -> citizens react (with voice)
- Show contradiction detection
- Show dynamic citizen spawning

## Slide 5: Architecture

- Pipeline: Speech -> FT-Extract -> Rule Engine -> FT-Citizens -> TTS -> UI
- Frontend: React + TypeScript (speech bubbles, animations)
- Backend: FastAPI (Python) with Weave tracing on every call
- AI: 2 fine-tuned Ministral 8B models
- TTS: ElevenLabs (unique voice per citizen)
- Data gen: AWS Bedrock for synthetic training examples
- Tracing: W&B Weave on every Mistral call

## Slide 6: Fine-Tuning Story

- WHY fine-tune? Base models fail on domain-specific tasks
- 540 hand-crafted training examples + 18 via AWS Bedrock
- TRL SFT + QLoRA (4-bit) on HF Jobs
- Total cost: ~$2 ($0.80 extract + $1.00 citizens + $0.15 eval)
- Extract model: 85.6% token accuracy (87.6% final)
- Citizens model: 92.3% token accuracy

## Slide 7: Benchmark Results

| Metric                  | 8B FT | 8B Base | Small 22B Base | Large Base |
|-------------------------|-------|---------|----------------|------------|
| Promise Count Accuracy  | 100   | 75      | 82.5           | 65         |
| Contradiction Detection | 100   | 55      | 32.5           | 70         |
| Promise Type Precision  | 100   | 52.5    | 75             | 55         |
| JSON Schema Compliance  | 100   | 100     | 100            | 100        |

"Fine-tuned 8B beats Large on all metrics. $2 beats $0."

## Slide 8: W&B Integration

- Training metrics tracked in W&B Models
- Every Mistral call traced with W&B Weave
- Evaluation dashboard comparing base vs FT vs Large
- Nemo 12B and Small 22B fine-tunes in progress

## Slide 9: What We Learned

- Fine-tuning is about schema conformance, not intelligence
- QLoRA makes 8B models trainable on a single A10G in minutes
- La Plateforme FT was blocked -> pivoted to HF Jobs in 30 min
- A $2 fine-tune beats models costing 10x more on domain tasks
- ElevenLabs TTS transforms the experience (citizens feel alive)

## Slide 10: Thank You

- Links: GitHub, HuggingFace org, W&B project
- Try it: [demo URL]
