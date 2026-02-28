# ECOTOPIA -- Political Eco-Simulation Game

**Can you save a city on the edge of ecological collapse?**

You are the mayor of a dying city. You have 7 rounds -- each round spans 5 years. Save the environment, keep the economy running, and don't lose the trust of your citizens. The twist: your citizens listen to every word. They remember your promises. They call out your contradictions. And they react -- not with scripted dialogue, but with AI-generated responses shaped by fine-tuned Mistral models, each citizen speaking with their own unique voice.

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
4. AI extracts **promises** from your words and tracks them across rounds
5. AI citizens **react to your speech** based on their personality, profession, and history -- each with their own voice
6. Citizens remember broken promises and contradictions -- trust erodes or grows based on your honesty

The game's thesis: progress has a human cost. The question isn't whether you hurt people -- it's whether you're honest about it and offer them a path forward.

---

## Architecture

```
Speech -> FT-Extract -> Rule Engine -> FT-Citizens -> TTS -> UI
```

| Stage | What it does |
|-------|-------------|
| Speech Input | Player types or speaks a free-text speech |
| FT-Extract | Fine-tuned Ministral 8B extracts promises and contradictions (JSON) |
| Rule Engine | Deterministic game state updates (ecology, economy, research scores) |
| FT-Citizens | Fine-tuned Ministral 8B generates citizen reactions and approval changes |
| ElevenLabs TTS | Each citizen speaks with a unique voice |
| UI | Speech bubbles, animations, updated game state |

Every Mistral API call is traced via **W&B Weave** for full observability.

See [docs/architecture.md](docs/architecture.md) for the full system design.

---

## Fine-Tuning

We trained **2 specialized LoRA adapters** on Ministral 8B using QLoRA (4-bit quantization):

| Model | Task | Examples | Train Loss | Eval Loss | Token Accuracy |
|-------|------|----------|------------|-----------|----------------|
| FT-Extract | Promise extraction | 200 | 0.484 | 0.553 | 85.6% (87.6% final) |
| FT-Citizens | Citizen reactions | 340 | 0.233 | 0.258 | 92.3% |

Training data augmented with 18 synthetic examples via **AWS Bedrock**.

### Benchmark: Fine-Tuned 8B vs Base Models

| Metric                  | 8B FT | 8B Base | Small 22B Base | Large Base |
|-------------------------|-------|---------|----------------|------------|
| Promise Count Accuracy  | 100   | 75      | 82.5           | 65         |
| Contradiction Detection | 100   | 55      | 32.5           | 70         |
| Promise Type Precision  | 100   | 52.5    | 75             | 55         |
| JSON Schema Compliance  | 100   | 100     | 100            | 100        |

**Fine-tuned 8B beats all base models -- including Large -- on every metric.**

### Models in Progress
- Nemo 12B fine-tune via Mistral API
- Small 22B fine-tune via Mistral API

### Cost

| Item | Cost |
|------|------|
| Extract fine-tune (A10G) | ~$0.80 |
| Citizens fine-tune (A10G) | ~$1.00 |
| Evaluation runs | ~$0.15 |
| **Total** | **~$2** |

See [docs/finetuning-results.md](docs/finetuning-results.md) for detailed metrics.

---

## W&B Integration

Every aspect of the project is tracked in Weights & Biases:

- **Training metrics**: Loss curves, token accuracy, learning rate schedules
- **Weave tracing**: Every Mistral API call traced with inputs, outputs, latency, token counts
- **Evaluation scorers**: Automated scoring of extraction accuracy and citizen response quality
- **Eval table**: Side-by-side comparison of base vs fine-tuned vs Large (40 examples)
- **Report**: Comprehensive findings summary

W&B Project: [hackathon-london-nolan-2026](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026)

W&B Report: [Ecotopia: Fine-Tuning Mistral for Political Simulation](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia:-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NTQxMA==)

---

## HuggingFace Models

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
| LLM | Mistral API (Ministral 8B fine-tuned) |
| TTS | ElevenLabs (unique voice per citizen) |
| Data Generation | AWS Bedrock (synthetic training data) |
| Fine-Tuning | TRL, PEFT, QLoRA, HuggingFace Jobs |
| Tracing | W&B Weave (every Mistral call) |
| Experiment Tracking | Weights & Biases |
| Models | HuggingFace Hub |

---

## Project Structure

```
ecotopia/
  frontend/          React + TypeScript game UI (speech bubbles, animations)
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
  docs/              Architecture, results, pitch deck
  wandb/             W&B run configs and report data
```

---

## Team

- **Nolan Cacheux** -- Fine-tuning, W&B integration, frontend, TTS
- **Kyle Kreuter** -- Backend, game engine, API design

Built in 48 hours at the Mistral Hackathon London 2026.

---

## License

MIT
