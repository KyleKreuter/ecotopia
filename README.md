# ECOTOPIA -- Political Eco-Simulation Game

**Can you save a city on the edge of ecological collapse?**

You are the mayor of a dying city. You have 7 rounds -- each round spans 5 years. Save the environment, keep the economy running, and don't lose the trust of your citizens. The twist: your citizens listen to every word. They remember your promises. They call out your contradictions. And they react -- not with scripted dialogue, but with AI-generated responses shaped by fine-tuned Mistral models.

---

## Demo

> Screenshot placeholder -- add game UI screenshot here

### Run it locally

```bash
# Frontend
cd frontend && npm install && npm run dev

# API server (FastAPI + Weave tracing)
cd api && pip install -r requirements.txt && python server.py

# Backend (Spring Boot)
cd backend && ./mvnw spring-boot:run
```

Open `http://localhost:5173` in your browser.

---

## What It Does

Ecotopia is a political simulation where you govern a city through 7 rounds of ecological crisis. Each round:

1. You review the state of your city (economy, environment, citizen trust)
2. You enact policies (close a coal plant, fund research, build infrastructure)
3. You deliver a **free-text speech** to your citizens -- no multiple choice, just your own words
4. AI citizens **react to your speech** based on their personality, profession, and history
5. The game extracts **promises** from your words and tracks them across rounds
6. Citizens remember broken promises and contradictions -- trust erodes or grows based on your honesty

The game's thesis: progress has a human cost. The question isn't whether you hurt people -- it's whether you're honest about it and offer them a path forward.

---

## Architecture

```
Frontend (React + TypeScript)
    |
    v
API Server (FastAPI + Weave tracing)
    |
    +---> Promise Extraction Model (FT Ministral 8B)
    |         extracts promises, types, contradictions from speech
    |
    +---> Citizen Reaction Model (FT Ministral 8B)
    |         generates in-character citizen responses
    |
    v
Game State Engine (Spring Boot)
    |
    v
W&B Weave (traces every Mistral call, evaluation scorers)
```

---

## Fine-Tuning

We trained **2 specialized LoRA adapters** on Ministral 8B using QLoRA (4-bit quantization):

| Model | Task | Training Examples | Eval Loss | Token Accuracy |
|-------|------|-------------------|-----------|----------------|
| ecotopia-extract | Promise extraction from speeches | 200 | < 0.55 | 85%+ |
| ecotopia-citizens | Citizen reaction generation | 340 | < 0.55 | 85%+ |

### Training Details

- **Method**: TRL SFTTrainer + PEFT QLoRA (4-bit NF4)
- **Base model**: Ministral 8B (mistralai/Ministral-8B-Instruct-2410)
- **Infrastructure**: HuggingFace Jobs with A10G GPU
- **Total training examples**: 540 (200 extraction + 340 citizens)
- **Cost**: ~$2 total for both fine-tunes

### Training Data

Extraction data covers 4 categories:
- Batch 1: Explicit promises ("I will shut down the coal plant")
- Batch 2: Implicit promises and empty speeches
- Batch 3: Contradictions across rounds
- Batch 4: Edge cases (vague language, conditional promises)

Citizen data covers diverse personas reacting to speeches with memory of past rounds.

---

## W&B Integration

Every aspect of the project is tracked in Weights & Biases:

- **Training metrics**: Loss curves, token accuracy, learning rate schedules for both models
- **Weave tracing**: Every Mistral API call is traced with inputs, outputs, latency, and token counts
- **Evaluation scorers**: Automated scoring of extraction accuracy and citizen response quality
- **Eval table**: Side-by-side comparison of base vs fine-tuned models (40 examples)
- **Report**: Comprehensive findings summary with methodology and results

W&B Project: [wandb.ai/mistral-hackaton-2026/ecotopia](https://wandb.ai/mistral-hackaton-2026/ecotopia)

---

## Results: Base vs Fine-Tuned

Evaluation on 40 held-out examples comparing `mistral-small-latest` (base) against our fine-tuned models:

| Metric | Base Model | Fine-Tuned | Improvement |
|--------|-----------|------------|-------------|
| Promise Count Accuracy | 87.5% | 100% | +12.5pp |
| Promise Type Precision | 10% | 100% | +90pp |
| Contradiction Detection | 82.5% | 100% | +17.5pp |

The base model could detect promises but consistently misclassified types and missed subtle contradictions. Fine-tuning eliminated these errors entirely on the eval set.

---

## HuggingFace Models

Both models and datasets are published on HuggingFace:

**Models:**
- [mistral-hackaton-2026/ecotopia-extract-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b) -- Promise extraction LoRA adapter
- [mistral-hackaton-2026/ecotopia-citizens-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b) -- Citizen reaction LoRA adapter

**Datasets:**
- [mistral-hackaton-2026/ecotopia-extraction-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-extraction-dataset)
- [mistral-hackaton-2026/ecotopia-citizens-dataset](https://huggingface.co/datasets/mistral-hackaton-2026/ecotopia-citizens-dataset)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite |
| API Server | FastAPI, Python |
| Backend | Spring Boot, Java |
| LLM | Mistral API (Ministral 8B) |
| Fine-Tuning | TRL, PEFT, QLoRA, HuggingFace Jobs |
| Observability | Weights & Biases, Weave |
| Models | HuggingFace Hub |

---

## Project Structure

```
ecotopia/
  frontend/          React + TypeScript game UI
    src/
  api/               FastAPI server with Weave tracing
    server.py
    requirements.txt
  backend/           Spring Boot game state engine
    src/
    pom.xml
  training/          Fine-tuning scripts and data
    data/
      extraction/    200 training examples (4 batches)
      citizens/      340 training examples
    hf_finetune_extraction.py
    hf_finetune_citizens.py
    evaluate_models.py
    weave_eval.py
    wandb_eval_table.py
  artifacts/         Model cards and configs
  prompts/           System prompts for extraction and citizens
  docs/              Game design, API contract, finetuning docs
  wandb/             W&B run configs and report data
```

---

## Cost

| Item | Cost |
|------|------|
| Extraction fine-tune (A10G, ~20 min) | ~$1 |
| Citizens fine-tune (A10G, ~30 min) | ~$1 |
| **Total fine-tuning** | **~$2** |
| Inference (Ministral 8B via Mistral API) | ~$0.001/game |

Fine-tuned Ministral 8B runs at a fraction of the cost of larger models while delivering 100% accuracy on our evaluation set.

---

## Team

- **Nolan Cacheux** -- Fine-tuning, W&B integration, frontend
- **Kyle Kreuter** -- Backend, game engine, API design

Built in 48 hours at the Mistral Hackathon London 2026.

---

## License

MIT
