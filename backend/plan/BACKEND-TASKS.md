# Ecotopia — Backend Task Plan

> Derived from `docs/GAME.md`. This document describes all backend components that need to be built.

---

## Phase 1: Domain Model & Entities ✅

### 1.1 Game Session
- [x] `Game` Entity — Game session with ID, current round (1-7), status (RUNNING, WON, LOST), result rank (BRONZE, SILVER, GOLD), timestamps
- [x] `GameRound` Entity — Round with number, player speech text, remaining actions (max 2), AI reactions

### 1.2 Grid System
- [x] `Tile` Entity — Position (x/y), TileType, state (healthy/sick/dead), pollution level, age (rounds since state change), reference to Game
- [x] `TileType` Enum — HEALTHY_FOREST, SICK_FOREST, CLEAN_RIVER, POLLUTED_RIVER, FARMLAND, DEAD_FARMLAND, WASTELAND, FACTORY, CLEAN_FACTORY, OIL_REFINERY, COAL_PLANT, RESIDENTIAL, CITY_CENTER, RESEARCH_CENTER, SOLAR_FIELD, FUSION_REACTOR
- [x] `TileActionType` Enum — DEMOLISH, BUILD_FACTORY, BUILD_SOLAR, BUILD_RESEARCH_CENTER, BUILD_FUSION, PLANT_FOREST, UPGRADE_CARBON_CAPTURE, REPLACE_WITH_SOLAR, CLEAR_FARMLAND
- [x] Start map generation (fixed 10x10 map per Game Design)

### 1.3 Resources
- [x] `GameResources` (Embeddable or Entity) — Ecology (start 45%), Economy (start 65%), Research (start 5%)
- [x] Define thresholds: < 20% Ecology = Eco-collapse, < 20% Economy = Famine

### 1.4 Citizen System
- [x] `Citizen` Entity — Name, type (CORE/DYNAMIC), profession, age, personality, approval value (0-100%), opening speech, remaining rounds (for dynamic citizens)
- [x] Core citizen definitions: Karl (factory worker), Mia (climate activist), Sarah (opposition politician)
- [x] Starting approval: Karl 60%, Mia 35%, Sarah 25% (estimated, balance during gameplay)

### 1.5 Promises
- [x] `Promise` Entity — Text, round of promise, optional deadline, status (ACTIVE, KEPT, BROKEN), reference to citizen (optional), reference to Game

---

## Phase 2: Game Logic / Services ✅

### 2.1 Grid & Tile Actions
- [x] `TileActionService` — Calculate available actions per tile (depending on TileType + research level)
- [x] `TileActionService` — Execute action, apply resource effects, decrement action counter
- [x] Implement action rules (see Game.md: deforest, demolish factory, carbon capture, etc.)
- [x] Check research prerequisites (Solar at 40%, Fusion at 80%)

### 2.2 Passive Grid Changes
- [x] `PollutionService` — Pollution spread per round
  - Factories: range 1
  - Oil refinery & coal plant: range 2
  - Effects: river -> polluted, forest -> sick, farm -> dead
- [x] Degradation: Sick forest that stays sick for 2 rounds -> wasteland
- [x] Regeneration: Polluted river heals after 2 rounds without pollution source
- [x] Newly planted forest needs 2 rounds until full effect

### 2.3 Resource Calculation
- [x] `GameService.recalculateResources()` — Recalculate ecology/economy/research at end of round
- [x] Game-over check: Ecology < 20%, Economy < 20%, all core citizens < 25% approval

### 2.4 Tech Tree
- [x] Integrated into `TileActionService.getAvailableActions()` — checks research level
- [x] Milestone 40%: Unlock solar
- [x] Milestone 80%: Unlock fusion

### 2.5 Citizen Logic
- [x] `CitizenService` — Spawn dynamic citizens, calculate approval
- [x] Dynamic citizen lifecycle: Spawn on certain actions, max 2 dynamic at once (max 5 total), automatic removal after 2-3 rounds
- [x] Solidarity mechanic: Karl reacts to worker spawns, Mia to environment spawns
- [x] Core citizen reaction to dynamic citizens (approval adjustment)

### 2.6 Spawn Rules for Dynamic Citizens
- [x] Oil refinery demolished -> Oleg (drill worker, 54)
- [x] Coal plant demolished -> Kerstin (power plant worker, single mother)
- [x] Forest deforested -> Forester Bernd
- [x] Farmland destroyed -> Farmer Henning
- [x] Solar field built -> Lena (technician)
- [x] Research center built -> Dr. Yuki (PhD student)
- [x] Fusion reactor built -> Pavel (engineer)
- [x] Double spawns on replacement (e.g., refinery -> solar = Oleg + Lena)

---

## Phase 3: AI Integration (Mistral AI via Spring AI)

### 3.1 Speech Processing
- [ ] `SpeechService` — Accept player speech, build context (round history, citizens, promises, actions), send to Mistral AI

### 3.2 Promise Extraction
- [ ] `PromiseService` — AI prompt that extracts promises from free text
  - Explicit: "I promise...", "I guarantee..."
  - Implicit: "The forest stays", "No more factories"
  - Citizen-related: "Oleg, I'll find you a job"
  - Extract deadlines when mentioned

### 3.3 Contradiction Detection
- [ ] `ContradictionService` — Compare current actions vs. previous statements
- [ ] Detect broken promises and update status

### 3.4 Generate Citizen Reactions
- [ ] AI generates in-character reactions for each citizen (core + dynamic)
- [ ] Context: personality, approval, past interactions, current actions
- [ ] Sarah quotes the player verbatim on broken promises

### 3.5 Create Dynamic Citizens
- [ ] AI generates: name, profession, age, personality, opening speech
- [ ] Everything must be contextually relevant to the triggering action
- [ ] Generate interactions between dynamic citizens (e.g., Oleg meets Lena)

### 3.6 Prompt Engineering
- [ ] Design system prompts for each AI call
- [ ] Context management: Entire game history must fit into the prompt (round history, all speeches, all promises)
- [ ] Structured output: Parse AI responses as JSON (approval changes, new promises, citizen texts)

---

## Phase 4: REST API ✅

### 4.1 Game Controller
- [x] `POST /api/games` — Start new game (initialize start map + core citizens + resources)
- [x] `GET /api/games/{id}` — Retrieve complete game state (grid, resources, citizens, promises, round)
- [x] `DELETE /api/games/{id}` — End/delete game

### 4.2 Tile Controller
- [x] `GET /api/games/{id}/tiles/{x}/{y}/actions` — Available actions for a tile (depending on type + research)
- [x] `POST /api/games/{id}/tiles/{x}/{y}/actions` — Execute tile action (validate: max 2 per round, prerequisites)

### 4.3 Speech Controller
- [x] `POST /api/games/{id}/speech` — Placeholder (returns empty reactions, Phase 3 will add AI)

### 4.4 Round Controller
- [x] `POST /api/games/{id}/end-round` — End round -> passive changes, promise check, game-over/victory check
- [x] `GET /api/games/{id}/promises` — Retrieve active promises

### 4.5 DTOs & Response Models
- [x] Request/response DTOs for all endpoints (11 Java records)
- [x] Game state DTO (complete for frontend rendering)
- [x] GameMapper utility class for entity-to-DTO conversion
- [x] Error handling & validation (GlobalExceptionHandler)

---

## Phase 5: Victory & Game Over ✅

- [x] Victory condition: Round 7 completed without game-over
- [x] Rank calculation:
  - Bronze (Survivor): Both > 45%
  - Silver (Reformer): Both > 65%
  - Gold (Ecotopia): Both > 80%, Research > 75%
- [x] Game-over conditions:
  - Eco-collapse: Ecology < 20%
  - Famine: Economy < 20%
  - Voted out: All three core citizens < 25% approval
- [ ] Provide end screen data (rank, statistics, final citizen words)

---

## Phase 6: Infrastructure & Quality

- [x] PostgreSQL via Docker Compose (`backend/docker-compose.yml`)
- [x] Exception handling (GlobalExceptionHandler)
- [x] CORS configuration for frontend (WebConfig)
- [x] Application properties (DB, Mistral AI key, etc.)
- [ ] Flyway migrations (currently using `ddl-auto: update`)
- [ ] Unit tests for game logic (grid, resources, pollution, tech tree)
- [ ] Integration tests for AI calls
- [ ] API tests for all endpoints

---

## Recommended Order

```
Phase 1 (Domain) ✅ -> Phase 2 (Logic) ✅ -> Phase 4 (API) ✅ -> Phase 3 (AI) -> Phase 5 ✅ -> Phase 6 (Infra)
```

AI integration (Phase 3) intentionally after the API, so the core mechanics can be tested without AI first (using mock reactions).
