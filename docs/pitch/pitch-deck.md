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
- AI citizens react dynamically

## Slide 4: Live Demo

- [Show the game running]
- Type a speech -> see promises extracted -> citizens react
- Show contradiction detection
- Show dynamic citizen spawning

## Slide 5: Architecture

- Pipeline: Speech -> FT-Extract -> FT-Citizens -> Game State
- Frontend: React + TypeScript
- Backend: Spring Boot (Java)
- AI: 2 fine-tuned Ministral 8B models
- Tracing: W&B Weave on every call

## Slide 6: Fine-Tuning Story

- WHY fine-tune? Base model gets 10% type precision, FT gets 100%
- 540 hand-crafted training examples
- TRL SFT + QLoRA (4-bit) on HF Jobs
- Total cost: $2
- 85%+ token accuracy

## Slide 7: Results

- Table: Base vs FT comparison
- Promise Count: 87.5% -> 100%
- Contradiction Detection: 82.5% -> 100%
- Type Precision: 10% -> 100%
- "Specialized small models beat large base models on domain tasks"

## Slide 8: W&B Integration

- Training metrics tracked in W&B Models
- Every Mistral call traced with W&B Weave
- Evaluation dashboard comparing base vs FT
- Full report with findings

## Slide 9: What We Learned

- Fine-tuning is about schema conformance, not intelligence
- QLoRA makes 8B models trainable on a single A10G in minutes
- La Plateforme FT was blocked -> pivoted to HF Jobs in 30 min
- Game works with base models, FT makes it 10x better

## Slide 10: Thank You

- Links: GitHub, HuggingFace org, W&B project
- Try it: [demo URL]
