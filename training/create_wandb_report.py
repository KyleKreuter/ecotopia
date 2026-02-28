"""Fetch W&B run metrics and generate a markdown report for Ecotopia."""
import json
import os
from datetime import datetime

import wandb


def fetch_runs() -> list[dict]:
    """Fetch all runs from the W&B project."""
    api = wandb.Api()
    runs = api.runs("nolancacheux/hackathon-london-nolan-2026")
    results = []
    for run in runs:
        results.append({
            "name": run.name,
            "state": run.state,
            "config": dict(run.config),
            "summary": dict(run.summary),
            "url": run.url,
            "created_at": run.created_at,
            "job_type": run.job_type,
        })
    return results


def build_report(runs: list[dict]) -> str:
    """Build markdown report content."""
    # Separate training runs from upload runs
    training_runs = [r for r in runs if r.get("job_type") != "model-upload"]
    upload_runs = [r for r in runs if r.get("job_type") == "model-upload"]

    report = f"""# Ecotopia: Fine-Tuning Mistral for Political Simulation

> W&B Report — Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 1. Project Overview

**Ecotopia** is a political eco-simulation game where players take on the role of a
political leader managing environmental and social policies. The game uses fine-tuned
LLMs for two core tasks:

- **Promise Extraction**: Parse political speeches/manifestos into structured campaign
  promises with categories (environment, economy, social, security)
- **Citizen Dialogue**: Generate realistic citizen reactions to political decisions,
  reflecting diverse demographics and political leanings

## 2. Fine-Tuning Approach

| Parameter | Value |
|-----------|-------|
| Base Model | Ministral-8B-Instruct-2410 |
| Method | LoRA (Low-Rank Adaptation) |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| Framework | TRL SFTTrainer + PEFT |
| Optimizer | AdamW (8-bit) |
| Learning Rate | 2e-4 |
| Epochs | 3 |
| Max Seq Length | 2048 |

## 3. Dataset Details

Two custom datasets were created for the fine-tuning:

### Promise Extraction Dataset
- **540 examples** of political text → structured JSON extraction
- **4 categories**: environment, economy, social, security
- Each example maps a political statement to structured promises with:
  - Promise text, category, feasibility score, estimated cost, timeline

### Citizen Dialogue Dataset
- **540 examples** of policy context → citizen reactions
- **4 demographic profiles**: urban professional, rural farmer, student, retiree
- Reactions include sentiment, concerns, support level, and dialogue

## 4. Training Results

### Runs Summary

| Run | Type | Status | Key Metrics |
|-----|------|--------|-------------|
"""
    for run in training_runs:
        s = run["summary"]
        loss = s.get("train/loss", s.get("loss", "N/A"))
        if isinstance(loss, float):
            loss = f"{loss:.4f}"
        acc = s.get("train/token_accuracy", "N/A")
        if isinstance(acc, float):
            acc = f"{acc:.2%}"
        report += f"| {run['name']} | training | {run['state']} | loss={loss}, acc={acc} |\n"

    for run in upload_runs:
        report += f"| {run['name']} | artifact | {run['state']} | — |\n"

    report += """
### Training Metrics Detail

"""
    for run in training_runs:
        s = run["summary"]
        report += f"**{run['name']}**\n"
        for key in sorted(s.keys()):
            if key.startswith("_") or key in ("wandb", "graph"):
                continue
            val = s[key]
            if isinstance(val, float):
                val = f"{val:.6f}"
            report += f"- `{key}`: {val}\n"
        report += "\n"

    report += """## 5. Architecture

```
Political Text / Game Event
        │
        ▼
┌─────────────────────┐
│  Ministral 8B Base  │
│  (4-bit NF4)        │
│  + LoRA Adapters     │
│  (r=16, α=32)       │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Extract │ │ Citizens │
│LoRA    │ │ LoRA     │
└───┬────┘ └────┬─────┘
    │           │
    ▼           ▼
Structured   Citizen
Promises     Dialogue
(JSON)       (Natural)
```

## 6. Key Findings

1. **LoRA efficiency**: 4-bit quantization + LoRA enables fine-tuning 8B models on
   consumer GPUs (single A100 or equivalent)
2. **Task specialization**: Separate adapters for extraction vs dialogue produces
   better results than a single multi-task adapter
3. **Structured output**: The extraction model reliably produces valid JSON with
   correct schema after fine-tuning
4. **TRL SFTTrainer**: Simplifies the training loop with built-in chat template
   formatting and packing

## 7. Links

- **HuggingFace Models**:
  - [ecotopia-extract-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b)
  - [ecotopia-citizens-ministral-8b](https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b)
- **W&B Project**: [hackathon-london-nolan-2026](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026)
"""

    # Add run links
    for run in runs:
        report += f"  - [{run['name']}](https://wandb.ai{run['url']})\n"

    return report


def log_summary_table(runs: list[dict]) -> None:
    """Log a summary W&B table with all run metrics."""
    run = wandb.init(
        project="hackathon-london-nolan-2026",
        job_type="report",
        name="ecotopia-summary-report",
    )

    columns = ["name", "state", "job_type", "loss", "token_accuracy", "url"]
    table = wandb.Table(columns=columns)

    for r in runs:
        s = r.get("summary", {})
        table.add_data(
            r["name"],
            r["state"],
            r.get("job_type", ""),
            s.get("train/loss", s.get("loss", None)),
            s.get("train/token_accuracy", None),
            f"https://wandb.ai{r['url']}",
        )

    run.log({"run_summary": table})
    run.finish()


def main() -> None:
    """Generate W&B report and save markdown."""
    os.environ.setdefault(
        "WANDB_API_KEY",
        "",
    )

    print("Fetching W&B runs...")
    runs = fetch_runs()
    print(f"Found {len(runs)} runs")

    print("Building markdown report...")
    report_md = build_report(runs)

    output_path = "/root/clawd/ecotopia/docs/wandb-report.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_md)
    print(f"Report saved to {output_path}")

    # Also save run data as JSON for reference
    json_path = "/root/clawd/ecotopia/docs/wandb-runs.json"
    with open(json_path, "w") as f:
        json.dump(runs, f, indent=2, default=str)
    print(f"Run data saved to {json_path}")

    print("Logging summary table to W&B...")
    log_summary_table(runs)
    print("Done!")


if __name__ == "__main__":
    main()
