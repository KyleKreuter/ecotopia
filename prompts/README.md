# Ecotopia System Prompts

This directory contains the system prompts used by the Mistral fine-tuned models (or base models with few-shot prompting) for Ecotopia's two core AI tasks.

## Overview

| Prompt | File | Model Task | When Used |
|--------|------|------------|-----------|
| Promise Extraction | `extraction.txt` | Extract promises from player speech, detect contradictions with actions | Every time the player submits a speech via `POST /api/game/speech` |
| Citizen Simulation | `citizens.txt` | Generate citizen dialogue reactions, spawn dynamic citizens | After extraction, within the same `POST /api/game/speech` pipeline |

## Pipeline Flow

```
Player submits speech
    |
    v
[extraction.txt] --> promises[], contradictions[]
    |
    v
[citizens.txt] --> citizen_reactions[], new_dynamic_citizens[]
    |
    v
Backend updates GameState, returns full response to frontend
```

The backend calls these sequentially: extraction first (to get promises and contradictions), then citizens (which needs the extraction output as input).

## extraction.txt

**Purpose:** Parse player speech to identify promises (explicit and implicit) and detect contradictions between words and actions.

### Input Schema

```json
{
  "round": 3,
  "player_speech": "I will protect the forest!",
  "actions_this_round": [
    { "type": "BUILD", "detail": "solar_farm_south" }
  ],
  "actions_history": [
    { "round": 1, "type": "BUILD", "detail": "house_center" }
  ],
  "previous_promises": [
    {
      "text": "No more factories",
      "type": "implicit",
      "status": "active",
      "round_made": 2
    }
  ],
  "active_citizens": ["Elena", "Karl"],
  "dynamic_citizens": ["Yara"],
  "game_state": {
    "ecology": 65,
    "economy": 55,
    "research": 40
  }
}
```

### Output Schema

```json
{
  "promises": [
    {
      "text": "I will protect the forest",
      "type": "explicit",
      "target_citizen": null,
      "deadline_round": null,
      "confidence": 0.95
    }
  ],
  "contradictions": [
    {
      "description": "Player said X but did Y",
      "speech_quote": "exact quote from speech",
      "contradicting_action": "BUILD factory_north",
      "severity": "high"
    }
  ]
}
```

### Field Details

**promises[].type**: `"explicit"` (uses direct promise language) or `"implicit"` (implies commitment without saying "I promise").

**promises[].confidence**: Float 0.0-1.0. Explicit promises score 0.85+, implicit ones 0.5-0.85.

**promises[].target_citizen**: Set only if the player addresses a citizen by name.

**promises[].deadline_round**: Set only if the player mentions a specific round or timeframe.

**contradictions[].severity**: `"low"` (minor inconsistency), `"medium"` (clear conflict), `"high"` (undeniable broken promise).

## citizens.txt

**Purpose:** Simulate citizen reactions to the player's promises, contradictions, and actions. Optionally spawn new dynamic citizens when game conditions trigger it.

### Input Schema

```json
{
  "round": 5,
  "promises_extracted": ["Expand the solar grid by round 5"],
  "contradictions": [
    {
      "description": "Promised forest protection, built coal plant",
      "severity": "high"
    }
  ],
  "game_state": {
    "ecology": 28,
    "economy": 70,
    "research": 35
  },
  "active_citizens": [
    {
      "name": "Elena",
      "role": "ecologist",
      "personality": "passionate about nature",
      "approval": 40
    }
  ],
  "dynamic_citizens": [],
  "actions_this_round": ["Built coal_plant at (1,4)"],
  "previous_speeches": ["The forest is sacred."]
}
```

### Output Schema

```json
{
  "citizen_reactions": [
    {
      "citizen_name": "Elena",
      "dialogue": "You promised to protect the forest...",
      "tone": "angry",
      "approval_delta": -14,
      "references_promise": true
    }
  ],
  "new_dynamic_citizens": [
    {
      "name": "Yara",
      "role": "displaced farmer",
      "personality": "quiet, stubborn",
      "initial_approval": 35,
      "dialogue": "Where do we go now?",
      "tone": "desperate"
    }
  ],
  "summary": "Round 5: Elena furious about broken promise. Yara spawned due to low ecology."
}
```

### Field Details

**citizen_reactions[].approval_delta**: Integer from -15 to +15. Most reactions are moderate (-5 to +5); extreme values reserved for major betrayals or fulfilled promises.

**citizen_reactions[].tone**: One of `angry`, `hopeful`, `sarcastic`, `desperate`, `grateful`, `suspicious`, `neutral`.

**citizen_reactions[].references_promise**: True if the citizen's dialogue references a specific promise.

**new_dynamic_citizens[].initial_approval**: Integer 40-60. New citizens start wary, not committed.

### Dynamic Citizen Spawn Triggers

| Condition | Example Citizens |
|-----------|-----------------|
| ecology < 30 | Environmental refugees, wildlife advocates |
| economy < 30 | Unemployed workers, struggling merchants |
| ecology or economy > 90 | Journalists, investors, tourists |
| research > 80 | Scientists, tech entrepreneurs |
| 3+ broken promises | Protest leaders, whistleblowers |

Maximum 2 dynamic citizens spawned per round.

## Usage Notes

- Both prompts expect and return raw JSON only (no markdown fencing, no commentary).
- The prompts include inline few-shot examples for use with base models. For fine-tuned models, the few-shot examples are redundant but harmless.
- The backend should validate the JSON output and handle malformed responses gracefully (retry once, then use empty defaults).
