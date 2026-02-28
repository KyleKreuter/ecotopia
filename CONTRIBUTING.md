# Contributing to Ecotopia

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Mistral AI API key

### Clone and install

```bash
git clone https://github.com/KyleKreuter/ecotopia.git
cd ecotopia

# API dependencies
pip install fastapi uvicorn mistralai weave pydantic python-dotenv

# Frontend
cd frontend
npm install
cd ..

# Training (optional)
pip install trl transformers datasets peft accelerate bitsandbytes torch \
    huggingface_hub wandb mistralai
```

## Required Environment Variables

| Variable           | Required | Description                            |
|--------------------|----------|----------------------------------------|
| `MISTRAL_API_KEY`  | Yes      | Mistral AI API key                     |
| `WANDB_API_KEY`    | No       | Weights & Biases for Weave tracing     |
| `EXTRACTION_MODEL` | No       | Override extraction model (default: `mistral-small-latest`) |
| `CITIZENS_MODEL`   | No       | Override citizens model (default: `mistral-small-latest`)   |
| `HF_TOKEN`         | No       | HuggingFace token (for training jobs)  |

Export them or use a `.env` file:

```bash
export MISTRAL_API_KEY="your-key-here"
export WANDB_API_KEY="your-key-here"
```

## Running the Project

### API Server

```bash
cd api
MISTRAL_API_KEY=<key> uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The API is then available at `http://localhost:8000`. Check health:

```bash
curl http://localhost:8000/api/health
```

### Frontend

```bash
cd frontend
npm run dev
```

Opens at `http://localhost:5173` (Vite default).

### Training

Fine-tuning jobs run on HuggingFace infrastructure:

```bash
# Extraction model (HF Jobs)
hf jobs uv run --flavor a10g-small training/hf_finetune_extraction.py

# Citizens model (HF Jobs)
hf jobs uv run --flavor a10g-small training/hf_finetune_citizens.py

# Mistral API fine-tuning
python training/launch_extraction_ft.py
python training/launch_citizens_ft.py

# Evaluate models
python training/evaluate_models.py --task extraction \
    --models ft:<model_id>,base:mistral-large-latest
```

## Git Workflow

1. **Never push directly to `master`.**
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes with small, focused commits.
4. Push and open a PR against `master`.
5. Get at least one review before merging.

### Branch naming

- `feat/` -- new features
- `fix/` -- bug fixes
- `docs/` -- documentation only
- `refactor/` -- code restructuring
- `chore/` -- tooling, CI, dependencies

### Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add citizen spawning based on policy decisions
fix: handle empty speech input gracefully
docs: update API contract with curl examples
refactor: extract prompt loading into shared util
```

## Code Standards

- **Python:** Type hints on all functions. Google-style docstrings on public
  classes and functions. No unused imports or dead code.
- **TypeScript/React:** Strict mode. Functional components with hooks.
- **Formatting:** Use `ruff` for Python linting/formatting, `prettier` for
  TypeScript.
- **No hardcoded secrets.** Use environment variables.
- **Max 500 lines per file.** Split into modules when approaching the limit.
- **Tests:** Add tests for new functionality. Run `python training/test_finetuning.py`
  for training validation.

## Project Structure

```
ecotopia/
  api/            -- FastAPI server (Mistral AI calls, Weave tracing)
  frontend/       -- React game UI
  training/       -- Fine-tuning scripts, data, evaluation
    data/
      extraction/ -- Promise extraction training data (JSONL)
      citizens/   -- Citizen dialogue training data (JSONL)
  prompts/        -- System prompt templates for Mistral calls
  docs/           -- API contract, fine-tuning results
```
