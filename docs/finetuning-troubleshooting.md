# Fine-Tuning Troubleshooting

## "Model not available" Error

### Error Message

```
Model not available for this type of fine-tuning (completion). Available model(s):
```

The "Available model(s):" list is empty.

### Root Cause

The Mistral workspace is not provisioned for fine-tuning. Calling `GET /v1/fine_tuning/models` returns an empty list, which means no models are available for FT on the current plan/workspace.

This is NOT a data format issue.

### What We Tried

- All model name variants: `mistral-small-latest`, `open-mistral-nemo`, `ministral-8b-latest`, full version strings
- All format variations: `completion` vs `instruct` sample types
- Both available API keys
- Verified data format is correct (see below)

### Data Format (Confirmed Correct)

Our JSONL files use `sample_type: "instruct"` with a `messages` array containing `system`, `user`, and `assistant` roles:

```json
{
  "sample_type": "instruct",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

This matches the Mistral fine-tuning documentation exactly.

### Solution

Fine-tuning must be activated on the Mistral workspace:

1. Check your billing/plan at https://console.mistral.ai
2. Ensure the workspace has fine-tuning enabled (may require a paid plan)
3. Contact Mistral support if the plan should include FT but `/v1/fine_tuning/models` returns empty

### How to Run (Once Fixed)

```bash
# Extraction model (2 jobs: Ministral 8B + Mistral Nemo)
MISTRAL_API_KEY=<key> python3 training/launch_extraction_ft.py

# Citizens model (1 job: mistral-small-latest)
MISTRAL_API_KEY=<key> python3 training/launch_citizens_ft.py
```

### Verifying FT Access

Quick check to see if your workspace has FT models available:

```bash
curl -s https://api.mistral.ai/v1/fine_tuning/models \
  -H "Authorization: Bearer $MISTRAL_API_KEY" | python3 -m json.tool
```

If the response contains an empty `data` array, FT is not enabled on the workspace.

### Monitor Jobs

Once jobs are running, monitor progress at:
https://console.mistral.ai/build/fine-tuning
