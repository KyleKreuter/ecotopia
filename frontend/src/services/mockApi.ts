import type {
  GameStateResponse,
  TileActionResponse,
  TileActionType,
  SpeechResponse,
  PromiseResponse,
  CitizenResponse,
  TileResponse,
} from '../types/backend.ts';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function delay(ms = 200): Promise<void> {
  return new Promise((r) => setTimeout(r, ms + Math.random() * 200));
}

function rand(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function clamp(v: number, lo = 0, hi = 100): number {
  return Math.max(lo, Math.min(hi, v));
}

/** Manhattan distance between two grid positions */
function manhattan(ax: number, ay: number, bx: number, by: number): number {
  return Math.abs(ax - bx) + Math.abs(ay - by);
}

let nextId = 1;

// ---------------------------------------------------------------------------
// In-memory store
// ---------------------------------------------------------------------------

const games = new Map<number, GameStateResponse>();

// ---------------------------------------------------------------------------
// Bytemap loader — same .map format as backend
// ---------------------------------------------------------------------------

const HEX_TO_TILE: Record<string, string> = {
  '0': 'HEALTHY_FOREST',
  '1': 'SICK_FOREST',
  '2': 'CLEAN_RIVER',
  '3': 'POLLUTED_RIVER',
  '4': 'FARMLAND',
  '5': 'DEAD_FARMLAND',
  '6': 'WASTELAND',
  '7': 'FACTORY',
  '8': 'CLEAN_FACTORY',
  '9': 'OIL_REFINERY',
  'A': 'COAL_PLANT',
  'B': 'CITY_INNER',
  'C': 'CITY_OUTER',
  'D': 'RESEARCH_CENTER',
  'E': 'SOLAR_FIELD',
  'F': 'FUSION_REACTOR',
};

let cachedStartMap: TileResponse[] | null = null;

async function loadBytemap(path: string): Promise<TileResponse[]> {
  if (cachedStartMap) return cachedStartMap.map((t) => ({ ...t, roundsInCurrentState: 0 }));

  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load map: ${path}`);
  const text = await res.text();

  const lines = text
    .split('\n')
    .filter((l) => l.trim() !== '' && !l.startsWith('#'));

  const tiles: TileResponse[] = [];
  for (let y = 0; y < lines.length; y++) {
    const line = lines[y].trim().toUpperCase();
    for (let x = 0; x < line.length; x++) {
      const tileType = HEX_TO_TILE[line[x]];
      if (!tileType) throw new Error(`Invalid tile char '${line[x]}' at (${x},${y})`);
      tiles.push({ x, y, tileType, roundsInCurrentState: 0 });
    }
  }

  cachedStartMap = tiles;
  return tiles.map((t) => ({ ...t }));
}

// ---------------------------------------------------------------------------
// Citizens — 3 fixed CORE citizens (matching backend)
// ---------------------------------------------------------------------------

function generateCitizens(): CitizenResponse[] {
  return [
    {
      id: nextId++,
      name: 'Karl',
      citizenType: 'CORE',
      profession: 'Factory Worker',
      age: 48,
      personality: 'Pragmatic blue-collar worker who values economic stability and jobs.',
      approval: 60,
      openingSpeech: 'I have worked in the factory for 25 years. Do not forget us workers when you make your grand plans.',
      remainingRounds: null,
    },
    {
      id: nextId++,
      name: 'Mia',
      citizenType: 'CORE',
      profession: 'Climate Activist',
      age: 24,
      personality: 'Passionate and uncompromising on environmental issues.',
      approval: 35,
      openingSpeech: 'The planet is burning and you want to talk about economy? Act now or step aside.',
      remainingRounds: null,
    },
    {
      id: nextId++,
      name: 'Sarah',
      citizenType: 'CORE',
      profession: 'Opposition Politician',
      age: 42,
      personality: 'Skeptical and always looking for contradictions in policy.',
      approval: 25,
      openingSpeech: 'I will be watching every decision you make. The people deserve accountability.',
      remainingRounds: null,
    },
  ];
}

// ---------------------------------------------------------------------------
// createGame
// ---------------------------------------------------------------------------

async function buildGameState(id: number): Promise<GameStateResponse> {
  const now = new Date().toISOString();
  return {
    id,
    currentRound: 1,
    status: 'RUNNING',
    resultRank: null,
    defeatReason: null,
    resources: { ecology: 40, economy: 70, research: 5 },
    tiles: await loadBytemap('/maps/start.map'),
    citizens: generateCitizens(),
    promises: [],
    currentRoundInfo: { roundNumber: 1, remainingActions: 2, speechText: null },
    createdAt: now,
    updatedAt: now,
  };
}

// ---------------------------------------------------------------------------
// Tile-action logic — with research gating
// ---------------------------------------------------------------------------

const ACTIONS_BY_TYPE: Record<string, TileActionType[]> = {
  HEALTHY_FOREST: ['DEMOLISH', 'BUILD_RESEARCH_CENTER'],
  SICK_FOREST: ['DEMOLISH', 'BUILD_RESEARCH_CENTER'],
  CLEAN_RIVER: [],
  POLLUTED_RIVER: [],
  FARMLAND: ['CLEAR_FARMLAND'],
  DEAD_FARMLAND: [],
  WASTELAND: ['PLANT_FOREST', 'BUILD_FACTORY', 'BUILD_SOLAR', 'BUILD_RESEARCH_CENTER', 'BUILD_FUSION'],
  FACTORY: ['DEMOLISH', 'UPGRADE_CARBON_CAPTURE', 'REPLACE_WITH_SOLAR'],
  CLEAN_FACTORY: ['DEMOLISH'],
  OIL_REFINERY: ['DEMOLISH', 'REPLACE_WITH_SOLAR'],
  COAL_PLANT: ['DEMOLISH', 'REPLACE_WITH_SOLAR'],
  CITY_INNER: [],
  CITY_OUTER: [],
  RESEARCH_CENTER: ['DEMOLISH'],
  SOLAR_FIELD: ['DEMOLISH'],
  FUSION_REACTOR: ['DEMOLISH'],
};

/** Actions that require a minimum research level */
const RESEARCH_GATES: Partial<Record<TileActionType, { minResearch: number; tileTypes?: string[] }>> = {
  BUILD_SOLAR: { minResearch: 40, tileTypes: ['WASTELAND'] },
  BUILD_FUSION: { minResearch: 80, tileTypes: ['WASTELAND'] },
  UPGRADE_CARBON_CAPTURE: { minResearch: 35, tileTypes: ['FACTORY'] },
  REPLACE_WITH_SOLAR: { minResearch: 40, tileTypes: ['FACTORY', 'OIL_REFINERY', 'COAL_PLANT'] },
};

function getAvailableActions(tileType: string, research: number): TileActionType[] {
  const base = ACTIONS_BY_TYPE[tileType] ?? [];
  return base.filter((action) => {
    const gate = RESEARCH_GATES[action];
    if (!gate) return true;
    if (gate.tileTypes && !gate.tileTypes.includes(tileType)) return true;
    return research >= gate.minResearch;
  });
}

// ---------------------------------------------------------------------------
// Context-dependent action effects (matching backend)
// ---------------------------------------------------------------------------

interface ResourceDelta {
  ecology: number;
  economy: number;
  research: number;
  newType: string;
}

function getActionEffect(action: TileActionType, tileType: string): ResourceDelta | null {
  switch (action) {
    case 'DEMOLISH':
      if (tileType === 'HEALTHY_FOREST' || tileType === 'SICK_FOREST')
        return { ecology: -3, economy: +1, research: 0, newType: 'WASTELAND' };
      if (tileType === 'FACTORY')
        return { ecology: +2, economy: -4, research: 0, newType: 'WASTELAND' };
      if (tileType === 'OIL_REFINERY')
        return { ecology: +4, economy: -5, research: 0, newType: 'WASTELAND' };
      if (tileType === 'COAL_PLANT')
        return { ecology: +3, economy: -4, research: 0, newType: 'WASTELAND' };
      return { ecology: 0, economy: 0, research: 0, newType: 'WASTELAND' };

    case 'BUILD_RESEARCH_CENTER':
      if (tileType === 'HEALTHY_FOREST' || tileType === 'SICK_FOREST')
        return { ecology: -2, economy: -2, research: +5, newType: 'RESEARCH_CENTER' };
      return { ecology: 0, economy: -2, research: +5, newType: 'RESEARCH_CENTER' };

    case 'BUILD_FACTORY':
      return { ecology: -3, economy: +4, research: 0, newType: 'FACTORY' };

    case 'BUILD_SOLAR':
      return { ecology: +2, economy: +3, research: 0, newType: 'SOLAR_FIELD' };

    case 'BUILD_FUSION':
      return { ecology: +3, economy: +8, research: 0, newType: 'FUSION_REACTOR' };

    case 'PLANT_FOREST':
      return { ecology: +2, economy: 0, research: 0, newType: 'HEALTHY_FOREST' };

    case 'CLEAR_FARMLAND':
      return { ecology: 0, economy: 0, research: 0, newType: 'WASTELAND' };

    case 'UPGRADE_CARBON_CAPTURE':
      return { ecology: +3, economy: -1, research: 0, newType: 'CLEAN_FACTORY' };

    case 'REPLACE_WITH_SOLAR':
      if (tileType === 'FACTORY')
        return { ecology: +4, economy: -1, research: 0, newType: 'SOLAR_FIELD' };
      if (tileType === 'OIL_REFINERY')
        return { ecology: +5, economy: -2, research: 0, newType: 'SOLAR_FIELD' };
      if (tileType === 'COAL_PLANT')
        return { ecology: +4, economy: -1, research: 0, newType: 'SOLAR_FIELD' };
      return null;

    default:
      return null;
  }
}

// ---------------------------------------------------------------------------
// Citizen spawning on actions (max 5 total citizens)
// ---------------------------------------------------------------------------

interface DynamicCitizenDef {
  name: string;
  profession: string;
  age: number;
  approval: number;
  rounds: number;
  personality: string;
  openingSpeech: string;
  solidarityGroup: 'worker' | 'environment' | 'positive';
}

const CITIZEN_SPAWNS: Record<string, DynamicCitizenDef | ((tileType: string) => DynamicCitizenDef | DynamicCitizenDef[] | null)> = {
  'DEMOLISH:OIL_REFINERY': {
    name: 'Oleg', profession: 'Drill Worker', age: 54, approval: 15, rounds: 3,
    personality: 'Bitter about losing his livelihood.', openingSpeech: 'You destroyed my workplace. Where am I supposed to go now?',
    solidarityGroup: 'worker',
  },
  'DEMOLISH:COAL_PLANT': {
    name: 'Kerstin', profession: 'Power Plant Worker', age: 38, approval: 20, rounds: 2,
    personality: 'Worried about her family after the plant closure.', openingSpeech: 'My children depend on this job. What is your plan for us?',
    solidarityGroup: 'worker',
  },
  'DEMOLISH:HEALTHY_FOREST': {
    name: 'Bernd', profession: 'Forester', age: 61, approval: 25, rounds: 2,
    personality: 'Lifelong guardian of the forest.', openingSpeech: 'That forest was my life. You cannot just bulldoze nature.',
    solidarityGroup: 'environment',
  },
  'CLEAR_FARMLAND:FARMLAND': {
    name: 'Henning', profession: 'Farmer', age: 55, approval: 20, rounds: 2,
    personality: 'Traditional farmer who lost his land.', openingSpeech: 'My family has farmed this land for generations. This is a disgrace.',
    solidarityGroup: 'worker',
  },
  'BUILD_SOLAR': {
    name: 'Lena', profession: 'Solar Technician', age: 28, approval: 65, rounds: 2,
    personality: 'Enthusiastic about renewable energy.', openingSpeech: 'Finally! Clean energy for our community. I am ready to get to work.',
    solidarityGroup: 'positive',
  },
  'BUILD_RESEARCH_CENTER': {
    name: 'Dr. Yuki', profession: 'PhD Student', age: 29, approval: 70, rounds: 2,
    personality: 'Excited about research opportunities.', openingSpeech: 'A new research center! The possibilities are endless.',
    solidarityGroup: 'positive',
  },
  'BUILD_FUSION': {
    name: 'Pavel', profession: 'Fusion Engineer', age: 45, approval: 60, rounds: 3,
    personality: 'Visionary engineer who believes in fusion power.', openingSpeech: 'Fusion is the future. You have made a bold and wise choice.',
    solidarityGroup: 'positive',
  },
};

function applySolidarityEffects(group: 'worker' | 'environment' | 'positive', citizens: CitizenResponse[]): void {
  const karl = citizens.find((c) => c.name === 'Karl');
  const mia = citizens.find((c) => c.name === 'Mia');
  const sarah = citizens.find((c) => c.name === 'Sarah');

  switch (group) {
    case 'worker':
      if (karl) karl.approval = clamp(karl.approval - 5);
      if (sarah) sarah.approval = clamp(sarah.approval + 3);
      break;
    case 'environment':
      if (mia) mia.approval = clamp(mia.approval - 3);
      break;
    case 'positive':
      if (mia) mia.approval = clamp(mia.approval + 3);
      if (karl) karl.approval = clamp(karl.approval + 2);
      break;
  }
}

function spawnCitizens(action: TileActionType, tileType: string, g: GameStateResponse): void {
  if (g.citizens.length >= 5) return;

  // REPLACE_WITH_SOLAR spawns demolish citizen + Lena
  if (action === 'REPLACE_WITH_SOLAR') {
    const demolishKey = `DEMOLISH:${tileType}`;
    const demolishDef = CITIZEN_SPAWNS[demolishKey];
    if (demolishDef && typeof demolishDef === 'object' && 'name' in demolishDef) {
      if (g.citizens.length < 5) {
        g.citizens.push({
          id: nextId++, name: demolishDef.name, citizenType: 'DYNAMIC',
          profession: demolishDef.profession, age: demolishDef.age,
          personality: demolishDef.personality, approval: demolishDef.approval,
          openingSpeech: demolishDef.openingSpeech, remainingRounds: demolishDef.rounds,
        });
        applySolidarityEffects(demolishDef.solidarityGroup, g.citizens);
      }
    }
    // Also spawn Lena
    const lenaDef = CITIZEN_SPAWNS['BUILD_SOLAR'] as DynamicCitizenDef;
    if (g.citizens.length < 5) {
      g.citizens.push({
        id: nextId++, name: lenaDef.name, citizenType: 'DYNAMIC',
        profession: lenaDef.profession, age: lenaDef.age,
        personality: lenaDef.personality, approval: lenaDef.approval,
        openingSpeech: lenaDef.openingSpeech, remainingRounds: lenaDef.rounds,
      });
      applySolidarityEffects(lenaDef.solidarityGroup, g.citizens);
    }
    return;
  }

  // Context-specific key first, then action-only key
  const contextKey = `${action}:${tileType}`;
  const def = CITIZEN_SPAWNS[contextKey] ?? CITIZEN_SPAWNS[action];
  if (!def || typeof def === 'function') return;

  g.citizens.push({
    id: nextId++, name: def.name, citizenType: 'DYNAMIC',
    profession: def.profession, age: def.age,
    personality: def.personality, approval: def.approval,
    openingSpeech: def.openingSpeech, remainingRounds: def.rounds,
  });
  applySolidarityEffects(def.solidarityGroup, g.citizens);
}

// ---------------------------------------------------------------------------
// End-round: deterministic resource recalculation from grid
// ---------------------------------------------------------------------------

const ECOLOGY_CONTRIB: Record<string, number> = {
  HEALTHY_FOREST: +2, SICK_FOREST: +1, CLEAN_RIVER: +1, SOLAR_FIELD: +2,
  FUSION_REACTOR: +3, CLEAN_FACTORY: +1, FACTORY: -3, OIL_REFINERY: -5,
  COAL_PLANT: -4, POLLUTED_RIVER: -1, DEAD_FARMLAND: -1,
};

const ECONOMY_CONTRIB: Record<string, number> = {
  FACTORY: +3, CLEAN_FACTORY: +2, OIL_REFINERY: +5, COAL_PLANT: +4,
  FARMLAND: +1, SOLAR_FIELD: +3, FUSION_REACTOR: +8, RESEARCH_CENTER: -2,
  CITY_INNER: +2, CITY_OUTER: +1,
};

const RESEARCH_CONTRIB: Record<string, number> = {
  RESEARCH_CENTER: +5,
};

function recalculateResources(tiles: TileResponse[]): { ecology: number; economy: number; research: number } {
  let ecology = 0, economy = 0, research = 0;
  for (const t of tiles) {
    ecology += ECOLOGY_CONTRIB[t.tileType] ?? 0;
    economy += ECONOMY_CONTRIB[t.tileType] ?? 0;
    research += RESEARCH_CONTRIB[t.tileType] ?? 0;
  }
  return {
    ecology: clamp(ecology),
    economy: clamp(economy),
    research: clamp(research),
  };
}

// ---------------------------------------------------------------------------
// Pollution tick
// ---------------------------------------------------------------------------

const POLLUTION_SOURCES: Record<string, number> = {
  FACTORY: 1,
  OIL_REFINERY: 2,
  COAL_PLANT: 2,
};

const POLLUTION_TARGETS: Record<string, string> = {
  CLEAN_RIVER: 'POLLUTED_RIVER',
  HEALTHY_FOREST: 'SICK_FOREST',
  FARMLAND: 'DEAD_FARMLAND',
};

function pollutionTick(tiles: TileResponse[]): void {
  // 1. Spread: pollution sources affect nearby tiles
  const sources = tiles.filter((t) => POLLUTION_SOURCES[t.tileType] !== undefined);
  for (const src of sources) {
    const range = POLLUTION_SOURCES[src.tileType];
    for (const target of tiles) {
      if (manhattan(src.x, src.y, target.x, target.y) <= range) {
        const newType = POLLUTION_TARGETS[target.tileType];
        if (newType) {
          target.tileType = newType;
          target.roundsInCurrentState = 0;
        }
      }
    }
  }

  // 2. Degradation: SICK_FOREST with roundsInCurrentState >= 2 → WASTELAND
  for (const t of tiles) {
    if (t.tileType === 'SICK_FOREST' && t.roundsInCurrentState >= 2) {
      t.tileType = 'WASTELAND';
      t.roundsInCurrentState = 0;
    }
  }

  // 3. Regeneration: POLLUTED_RIVER without active pollution source in range → count up, at >= 2 → CLEAN_RIVER
  for (const t of tiles) {
    if (t.tileType !== 'POLLUTED_RIVER') continue;
    const hasSource = sources.some(
      (src) => manhattan(src.x, src.y, t.x, t.y) <= POLLUTION_SOURCES[src.tileType],
    );
    if (!hasSource) {
      t.roundsInCurrentState++;
      if (t.roundsInCurrentState >= 2) {
        t.tileType = 'CLEAN_RIVER';
        t.roundsInCurrentState = 0;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Game-over conditions (matching backend)
// ---------------------------------------------------------------------------

function checkGameOver(g: GameStateResponse): { defeated: boolean; reason: string | null } {
  if (g.resources.ecology < 20) return { defeated: true, reason: 'ECOLOGICAL_COLLAPSE' };
  if (g.resources.economy < 20) return { defeated: true, reason: 'ECONOMIC_COLLAPSE' };

  const coreCitizens = g.citizens.filter((c) => c.citizenType === 'CORE');
  if (coreCitizens.length > 0 && coreCitizens.every((c) => c.approval < 25)) {
    return { defeated: true, reason: 'VOTED_OUT' };
  }

  return { defeated: false, reason: null };
}

// ---------------------------------------------------------------------------
// Victory ranks (matching backend)
// ---------------------------------------------------------------------------

function computeRank(g: GameStateResponse): string {
  const { ecology, economy, research } = g.resources;
  if (ecology > 80 && economy > 80 && research > 75) return 'GOLD';
  if (ecology > 65 && economy > 65) return 'SILVER';
  return 'BRONZE';
}

// ---------------------------------------------------------------------------
// Speech mock data — CORE citizen templates
// ---------------------------------------------------------------------------

const REACTION_TEMPLATES: Record<string, { dialogues: string[]; tones: string[] }> = {
  Karl: {
    dialogues: [
      'As long as the factories keep running, I can live with that.',
      'Jobs first, everything else second. That is my motto.',
      'I have a family to feed. Do not forget the working people.',
    ],
    tones: ['pragmatic', 'concerned', 'cautious'],
  },
  Mia: {
    dialogues: [
      'Talk is cheap — I am watching your actions closely.',
      'Finally, someone who listens to the planet!',
      'Every compromise with nature is a loss we cannot afford.',
    ],
    tones: ['fierce', 'excited', 'warning'],
  },
  Sarah: {
    dialogues: [
      'Interesting promises. Let us see if you actually deliver.',
      'The opposition is taking notes. Do not disappoint.',
      'Your words sound nice, but the numbers tell a different story.',
    ],
    tones: ['skeptical', 'sharp', 'analytical'],
  },
};

const DYNAMIC_REACTION_TEMPLATES: { dialogues: string[]; tones: string[] } = {
  dialogues: [
    'I will remember what you did here.',
    'This directly affects my livelihood.',
    'I hope you know what you are doing.',
  ],
  tones: ['emotional', 'concerned', 'hopeful'],
};

const CONTRADICTION_TEMPLATES = [
  {
    description: 'You promised to protect forests but demolished one this round.',
    speechQuote: 'I will protect the green spaces',
    contradictingAction: 'DEMOLISH on FOREST tile',
    severity: 'MAJOR',
  },
  {
    description: 'Your speech mentions sustainability but you built a factory.',
    speechQuote: 'Sustainability is my priority',
    contradictingAction: 'BUILD_FACTORY action',
    severity: 'MINOR',
  },
  {
    description: 'You spoke about clean energy but cleared farmland for development.',
    speechQuote: 'Clean energy for all',
    contradictingAction: 'CLEAR_FARMLAND action',
    severity: 'MODERATE',
  },
];

// ---------------------------------------------------------------------------
// Public mock API
// ---------------------------------------------------------------------------

export const mockApi = {
  async createGame(): Promise<GameStateResponse> {
    await delay();
    const id = nextId++;
    const game = await buildGameState(id);
    games.set(id, game);
    return structuredClone(game);
  },

  async getGame(id: number): Promise<GameStateResponse> {
    await delay();
    const g = games.get(id);
    if (!g) throw new Error(`Mock: game ${id} not found`);
    return structuredClone(g);
  },

  async deleteGame(id: number): Promise<void> {
    await delay();
    games.delete(id);
  },

  async getTileActions(gameId: number, x: number, y: number): Promise<TileActionResponse> {
    await delay();
    const g = games.get(gameId);
    if (!g) throw new Error(`Mock: game ${gameId} not found`);
    const tile = g.tiles.find((t) => t.x === x && t.y === y);
    if (!tile) return { availableActions: [] };
    const actions = getAvailableActions(tile.tileType, g.resources.research);
    return { availableActions: [...actions] };
  },

  async executeAction(
    gameId: number,
    x: number,
    y: number,
    action: TileActionType,
  ): Promise<GameStateResponse> {
    await delay();
    const g = games.get(gameId);
    if (!g) throw new Error(`Mock: game ${gameId} not found`);

    const tile = g.tiles.find((t) => t.x === x && t.y === y);
    if (!tile) throw new Error(`Mock: tile ${x},${y} not found`);

    const previousType = tile.tileType;
    const effect = getActionEffect(action, previousType);
    if (effect) {
      tile.tileType = effect.newType;
      tile.roundsInCurrentState = 0;
      g.resources.ecology = clamp(g.resources.ecology + effect.ecology);
      g.resources.economy = clamp(g.resources.economy + effect.economy);
      g.resources.research = clamp(g.resources.research + effect.research);
    }

    // Spawn dynamic citizens based on action + previous tile type
    spawnCitizens(action, previousType, g);

    g.currentRoundInfo.remainingActions = Math.max(
      0,
      g.currentRoundInfo.remainingActions - 1,
    );
    g.updatedAt = new Date().toISOString();
    return structuredClone(g);
  },

  async submitSpeech(gameId: number, text: string): Promise<SpeechResponse> {
    await delay(300);
    const g = games.get(gameId);
    if (!g) throw new Error(`Mock: game ${gameId} not found`);

    g.currentRoundInfo.speechText = text;

    // 2-4 citizen reactions
    const reactionCount = rand(2, Math.min(4, g.citizens.length));
    const shuffled = [...g.citizens].sort(() => Math.random() - 0.5);
    const citizenReactions = shuffled.slice(0, reactionCount).map((c) => {
      const templates = REACTION_TEMPLATES[c.name] ?? DYNAMIC_REACTION_TEMPLATES;
      const delta = rand(-8, 10);
      c.approval = clamp(c.approval + delta);
      return {
        citizenName: c.name,
        dialogue: pick(templates.dialogues),
        tone: pick(templates.tones),
        approvalDelta: delta,
      };
    });

    // 30% chance of contradiction
    const contradictions =
      Math.random() < 0.3 ? [pick(CONTRADICTION_TEMPLATES)] : [];

    // 1 extracted promise
    const promise: PromiseResponse = {
      id: nextId++,
      text: text.length > 60 ? text.slice(0, 60) + '...' : text,
      roundMade: g.currentRound,
      deadline: g.currentRound + rand(1, 3),
      status: 'PENDING',
      citizenName: pick(g.citizens).name,
    };
    g.promises.push(promise);

    g.updatedAt = new Date().toISOString();
    return { extractedPromises: [promise], contradictions, citizenReactions };
  },

  async endRound(gameId: number): Promise<GameStateResponse> {
    await delay();
    const g = games.get(gameId);
    if (!g) throw new Error(`Mock: game ${gameId} not found`);

    g.currentRound += 1;

    // Increment roundsInCurrentState for all tiles
    for (const t of g.tiles) {
      t.roundsInCurrentState++;
    }

    // Pollution tick (spread, degradation, regeneration)
    pollutionTick(g.tiles);

    // Deterministic resource recalculation from grid state
    g.resources = recalculateResources(g.tiles);

    // Citizen lifecycle: decrement remainingRounds for DYNAMIC citizens, remove expired
    g.citizens = g.citizens.filter((c) => {
      if (c.citizenType !== 'DYNAMIC' || c.remainingRounds === null) return true;
      c.remainingRounds--;
      return c.remainingRounds > 0;
    });

    // Game over check
    const { defeated, reason } = checkGameOver(g);
    if (defeated) {
      g.status = 'WON';
      g.defeatReason = reason;
      g.resultRank = 'BRONZE';
    } else if (g.currentRound > 7) {
      g.status = 'WON';
      g.resultRank = computeRank(g);
    } else {
      g.currentRoundInfo = {
        roundNumber: g.currentRound,
        remainingActions: 2,
        speechText: null,
      };
    }

    g.updatedAt = new Date().toISOString();
    return structuredClone(g);
  },

  async getPromises(gameId: number): Promise<PromiseResponse[]> {
    await delay();
    const g = games.get(gameId);
    if (!g) throw new Error(`Mock: game ${gameId} not found`);
    return structuredClone(g.promises);
  },
};
