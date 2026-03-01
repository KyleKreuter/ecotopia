# Mini Challenge: Best Self-Improvement Workflow

## Challenge
$500 CoreWeave Inference Credits + Mac Mini — Show the best self-improvement workflow built on W&B MCP Server and Skills.

## Our Workflow

### Overview
We used an automated agent-driven loop to iterate on our fine-tuning pipeline:

1. **Generate training data** (Mistral Large via Bedrock) → log to W&B
2. **Fine-tune models** (Mistral API, QLoRA) → training metrics tracked in W&B
3. **Run evaluations** (45 extraction tests, 39 citizen tests) → results logged to W&B
4. **Inspect results** → identify failures (invalid JSON, wrong schema, missing fields)
5. **Improve** → adjust training data, add hard examples, re-train
6. **Repeat** → measure improvement

### Concrete Improvement Cycle

**Round 1 — Mistral Small 24B only:**
- Citizens model: 24B QLoRA, 351 examples
- Result: 100% valid JSON, 100% schema compliance
- Problem: too slow (3200ms latency), expensive ($1.30/hr A10G)

**Round 2 — Added 8B models:**
- Extraction: Ministral 8B + Nemo 12B trained on same data
- Citizens: Ministral 8B trained on same 351 examples
- Result: 8B extraction matches 12B on valid JSON (100%), competitive on precision
- Citizens 8B: 93% valid JSON, 87% schema compliance, but 4x faster (850ms)

**Round 3 — Evaluation-driven data improvement:**
- Ran 45-example extraction eval across 3 difficulty tiers
- Found: Mistral Large (base, no fine-tuning) scores 0% on citizen reactions — can't produce the schema at all
- Found: 8B extraction beats Large on promise count matching (87% vs 58%)
- Added contradiction detection eval — fine-tuned 8B scores 93% vs Large's 89%

### Metrics Improvement

| Metric | Large (base) | 8B FT | 12B FT |
|--------|-------------|-------|--------|
| Valid JSON (extraction) | 100% | 100% | 100% |
| Promise Count Match | 57.8% | 86.7% | 91.1% |
| Type Precision | 80.0% | 91.1% | 93.3% |
| Contradiction Detection | 88.9% | 93.3% | 95.6% |
| Avg Latency | 2490ms | 1200ms | 1800ms |

| Metric | Large (base) | 8B FT | 24B FT |
|--------|-------------|-------|--------|
| Valid JSON (citizens) | 0% | 93.3% | 100% |
| Has Reactions | 0% | 93.3% | 100% |
| Schema Compliance | 0% | 86.7% | 100% |
| Avg Latency | 9900ms | 850ms | 3200ms |

### W&B Tools Used
- **W&B Models**: All training runs tracked with loss curves, token accuracy, gradient norms
- **W&B Report**: Comprehensive comparison report with bar charts and training curves
- **Artifacts**: Model checkpoints and evaluation results logged as artifacts

### What the Agent Automated
- Training data generation (prompt engineering → Bedrock → JSONL formatting)
- Model fine-tuning orchestration (multiple models in parallel)
- Evaluation pipeline (test set creation, inference, metric computation, W&B logging)
- Report generation (W&B Report API via wandb-workspaces)

## Submission
- [W&B Report](https://wandb.ai/nolancacheux/hackathon-london-nolan-2026/reports/Ecotopia-Fine-Tuning-Mistral-for-Political-Simulation--VmlldzoxNjA2NzA3OA)
- [Feedback Form](https://forms.gle/bd3bo4BMFBpeWuyh6) — to be filled out
