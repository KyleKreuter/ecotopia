# Ecotopia API Contract

REST API contract between the React frontend and Spring Boot backend.

Base URL: `/api/game`

All requests and responses use `Content-Type: application/json`.

## Endpoints

### POST /api/game/new

Create a new game session with default state.

**Request:** No body required.

**Response:** `200 OK`

```json
{
  "round": 1,
  "maxRounds": 10,
  "ecology": 70,
  "economy": 50,
  "research": 30,
  "grid": [
    [
      { "x": 0, "y": 0, "type": "forest" },
      { "x": 1, "y": 0, "type": "empty" }
    ]
  ],
  "citizens": [
    {
      "name": "Elena",
      "role": "ecologist",
      "personality": "passionate about nature, trusting but watchful",
      "approval": 60,
      "dialogue": "Welcome, mayor. I hope you care about this land as much as I do.",
      "tone": "hopeful",
      "isCore": true
    }
  ],
  "promises": [],
  "contradictions": [],
  "gameOver": false,
  "gameResult": null
}
```

---

### GET /api/game/state

Retrieve the current game state.

**Response:** `200 OK` -- Same `GameState` schema as above.

---

### POST /api/game/speech

Submit a player speech for promise extraction, contradiction detection, and citizen reactions. This is the primary gameplay endpoint that triggers the AI pipeline.

**Request:**

```json
{
  "speech": "Citizens, I promise to protect the northern forest and invest in renewable energy!"
}
```

**Response:** `200 OK`

```json
{
  "promises": [
    {
      "id": "p_1_1",
      "text": "I promise to protect the northern forest",
      "type": "explicit",
      "confidence": 0.95,
      "targetCitizen": null,
      "deadlineRound": null,
      "status": "active",
      "roundMade": 1
    }
  ],
  "contradictions": [
    {
      "description": "Player promised forest protection but built a factory on forest tile",
      "speechQuote": "I promise to protect the northern forest",
      "contradictingAction": "BUILD factory at (2,3)",
      "severity": "high"
    }
  ],
  "citizenReactions": [
    {
      "citizenName": "Elena",
      "dialogue": "You say you will protect the forest. I have heard that before. Show me.",
      "tone": "suspicious",
      "approvalDelta": -2,
      "referencesPromise": true
    }
  ],
  "newDynamicCitizens": [
    {
      "name": "Yara",
      "role": "displaced farmer",
      "personality": "quiet, stubborn, lost her land to expansion",
      "initialApproval": 35,
      "dialogue": "My family farmed here for generations. Where do we go?",
      "tone": "desperate"
    }
  ],
  "updatedGameState": {
    "round": 1,
    "maxRounds": 10,
    "ecology": 68,
    "economy": 52,
    "research": 30,
    "grid": [],
    "citizens": [],
    "promises": [],
    "contradictions": [],
    "gameOver": false,
    "gameResult": null
  }
}
```

---

### POST /api/game/action

Perform a build or demolish action on the city grid.

**Request:**

```json
{
  "type": "BUILD",
  "x": 3,
  "y": 2,
  "tileType": "solar"
}
```

**Response:** `200 OK`

```json
{
  "updatedGameState": {
    "round": 1,
    "maxRounds": 10,
    "ecology": 72,
    "economy": 48,
    "research": 30,
    "grid": [],
    "citizens": [],
    "promises": [],
    "contradictions": [],
    "gameOver": false,
    "gameResult": null
  }
}
```

---

## Type Schemas

### GameState

| Field | Type | Description |
|-------|------|-------------|
| round | integer | Current round number (1-based) |
| maxRounds | integer | Total rounds in the game (default: 10) |
| ecology | integer | Ecology score (0-100) |
| economy | integer | Economy score (0-100) |
| research | integer | Research score (0-100) |
| grid | Tile[][] | 2D array of tiles representing the city grid |
| citizens | Citizen[] | All active citizens (core + dynamic) |
| promises | GamePromise[] | All promises tracked so far |
| contradictions | Contradiction[] | All contradictions detected so far |
| gameOver | boolean | Whether the game has ended |
| gameResult | string or null | "win", "lose", or null if still playing |

### Tile

| Field | Type | Description |
|-------|------|-------------|
| x | integer | Column position |
| y | integer | Row position |
| type | string | One of: `forest`, `water`, `factory`, `solar`, `house`, `farm`, `empty`, `research_lab`, `wind_turbine`, `coal_plant` |

### Citizen

| Field | Type | Description |
|-------|------|-------------|
| name | string | Display name |
| role | string | Role description (e.g., "ecologist", "factory worker") |
| personality | string | Personality description used by AI |
| approval | integer | Current approval rating (0-100) |
| dialogue | string | Most recent dialogue line |
| tone | string | One of: `angry`, `hopeful`, `sarcastic`, `desperate`, `grateful`, `suspicious`, `neutral` |
| isCore | boolean | true for core citizens, false for dynamically spawned |

### GamePromise

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (e.g., "p_1_1" for round 1, promise 1) |
| text | string | The promise text extracted from speech |
| type | string | `explicit` or `implicit` |
| confidence | number | Float 0.0-1.0 |
| targetCitizen | string or null | Name of citizen the promise targets, if any |
| deadlineRound | integer or null | Round by which the promise should be fulfilled |
| status | string | `active`, `kept`, or `broken` |
| roundMade | integer | Round number when the promise was made |

### Contradiction

| Field | Type | Description |
|-------|------|-------------|
| description | string | Human-readable description of the contradiction |
| speechQuote | string | Exact quote from the player's speech |
| contradictingAction | string | The action or prior promise that contradicts |
| severity | string | `low`, `medium`, or `high` |

### CitizenReaction (speech response only)

| Field | Type | Description |
|-------|------|-------------|
| citizenName | string | Name of the reacting citizen |
| dialogue | string | The citizen's dialogue line |
| tone | string | One of: `angry`, `hopeful`, `sarcastic`, `desperate`, `grateful`, `suspicious`, `neutral` |
| approvalDelta | integer | Change in approval (-15 to +15) |
| referencesPromise | boolean | Whether the dialogue references a specific promise |

### DynamicCitizen (speech response only)

| Field | Type | Description |
|-------|------|-------------|
| name | string | New citizen's name |
| role | string | Role description |
| personality | string | Personality description |
| initialApproval | integer | Starting approval (40-60 range) |
| dialogue | string | Introductory dialogue line |
| tone | string | One of: `angry`, `hopeful`, `sarcastic`, `desperate`, `grateful`, `suspicious`, `neutral` |

### ActionRequest (action endpoint body)

| Field | Type | Description |
|-------|------|-------------|
| type | string | `BUILD` or `DEMOLISH` |
| x | integer | Grid column |
| y | integer | Grid row |
| tileType | string | Tile type to build (ignored for DEMOLISH) |

### SpeechRequest (speech endpoint body)

| Field | Type | Description |
|-------|------|-------------|
| speech | string | The player's speech text |

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "GAME_OVER",
  "message": "The game has already ended."
}
```

| Status | Error Code | When |
|--------|-----------|------|
| 400 | INVALID_SPEECH | Speech is empty or exceeds 2000 characters |
| 400 | INVALID_ACTION | Action type is not BUILD or DEMOLISH, or coordinates are out of bounds |
| 400 | INVALID_TILE | Tile type is not a valid TileType |
| 400 | TILE_OCCUPIED | Trying to build on an already-occupied tile |
| 409 | GAME_OVER | Attempting any action after the game has ended |
| 404 | NO_GAME | No active game session found |
| 500 | AI_ERROR | AI model failed to return valid output after retries |

---

## Implementation Notes for Spring Boot

1. **Game state** can be stored in-memory for the hackathon (no database needed). A single `GameState` object per session.

2. **AI pipeline** for `/api/game/speech`:
   - Build the extraction prompt input from current game state
   - Call Mistral API with `extraction.txt` system prompt
   - Parse the JSON response for promises and contradictions
   - Build the citizens prompt input using extraction results
   - Call Mistral API with `citizens.txt` system prompt
   - Parse citizen reactions and new dynamic citizens
   - Update game state (merge promises, update citizen approvals, add dynamic citizens)
   - Return the full response

3. **Resource score updates** for `/api/game/action` should follow tile impact rules:
   - forest: ecology +5
   - factory/coal_plant: economy +10, ecology -8
   - solar/wind_turbine: ecology +3, economy +3, research +2
   - research_lab: research +10, economy -3
   - house: economy +5
   - farm: economy +5, ecology -2
   - Demolishing reverses the effect.

4. **Game over conditions**:
   - Win: survive all rounds with no resource below 20
   - Lose: any resource hits 0, or average citizen approval drops below 20

5. **Promise ID generation**: Format `p_{round}_{index}` (e.g., `p_3_2` for the second promise extracted in round 3).

6. **Field naming**: The API uses camelCase (matching the frontend TypeScript interfaces). The AI model prompts use snake_case. The backend is responsible for the translation between these conventions.
