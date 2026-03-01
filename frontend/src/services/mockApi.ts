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

let nextId = 1;

// ---------------------------------------------------------------------------
// In-memory store
// ---------------------------------------------------------------------------

const games = new Map<number, GameStateResponse>();

// ---------------------------------------------------------------------------
// Bytemap loader — same .map format as backend
// ---------------------------------------------------------------------------

/** Hex char → TileType (matches backend TileType enum ordinal) */
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
// Citizens
// ---------------------------------------------------------------------------

function generateCitizens(): CitizenResponse[] {
  return [
    {
      id: nextId++,
      name: 'Old MacDonald',
      citizenType: 'FARMER',
      profession: 'Farmer',
      age: 58,
      personality: 'Traditional and concerned about farmland preservation.',
      approval: rand(50, 70),
      openingSpeech: 'I have been tilling this soil for decades. Whatever you decide, remember that food does not grow on solar panels.',
      remainingRounds: null,
    },
    {
      id: nextId++,
      name: 'Diana Sterling',
      citizenType: 'BUSINESS',
      profession: 'Businesswoman',
      age: 42,
      personality: 'Ambitious and focused on economic growth.',
      approval: rand(50, 70),
      openingSpeech: 'Ecotopia needs jobs. Build factories and commerce — that is how you earn my support.',
      remainingRounds: null,
    },
    {
      id: nextId++,
      name: 'Dr. Alan Voss',
      citizenType: 'SCIENTIST',
      profession: 'Scientist',
      age: 37,
      personality: 'Analytical and passionate about innovation.',
      approval: rand(50, 70),
      openingSpeech: 'Research is the key to a sustainable future. Fund the labs and I will support your vision.',
      remainingRounds: null,
    },
    {
      id: nextId++,
      name: 'Lena Marsh',
      citizenType: 'ACTIVIST',
      profession: 'Activist',
      age: 26,
      personality: 'Idealistic and uncompromising on ecology.',
      approval: rand(50, 70),
      openingSpeech: 'Every tree you cut is a promise broken. Protect nature or face the consequences.',
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
    status: 'IN_PROGRESS',
    resultRank: null,
    defeatReason: null,
    resources: { ecology: 45, economy: 65, research: 5 },
    tiles: await loadBytemap('/maps/start.map'),
    citizens: generateCitizens(),
    promises: [],
    currentRoundInfo: { roundNumber: 1, remainingActions: 2, speechText: null },
    createdAt: now,
    updatedAt: now,
  };
}

// ---------------------------------------------------------------------------
// Tile-action logic
// ---------------------------------------------------------------------------

const ACTIONS_BY_TYPE: Record<string, TileActionType[]> = {
  // Backend tile types (from bytemap)
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
  // Legacy demo tile types
  EMPTY: ['BUILD_FACTORY', 'BUILD_SOLAR', 'BUILD_RESEARCH_CENTER', 'PLANT_FOREST'],
  FOREST: ['DEMOLISH'],
  PARK: ['DEMOLISH'],
  INDUSTRIAL: ['DEMOLISH', 'REPLACE_WITH_SOLAR'],
  COMMERCIAL: ['DEMOLISH'],
  SOLAR_FARM: ['DEMOLISH'],
  WIND_FARM: ['DEMOLISH'],
  CARBON_CAPTURE: ['DEMOLISH'],
};

interface ResourceDelta {
  ecology: number;
  economy: number;
  research: number;
  newType: string;
}

const ACTION_EFFECTS: Record<string, ResourceDelta> = {
  BUILD_FACTORY:          { economy: 8,  ecology: -5, research: 0,  newType: 'FACTORY' },
  BUILD_SOLAR:            { economy: -3, ecology: 5,  research: 2,  newType: 'SOLAR_FARM' },
  BUILD_RESEARCH_CENTER:  { economy: -4, ecology: 0,  research: 8,  newType: 'RESEARCH_CENTER' },
  BUILD_FUSION:           { economy: -6, ecology: 2,  research: 10, newType: 'FUSION_REACTOR' },
  PLANT_FOREST:           { economy: -3, ecology: 6,  research: 0,  newType: 'FOREST' },
  DEMOLISH:               { economy: 3,  ecology: -2, research: 0,  newType: 'EMPTY' },
  REPLACE_WITH_SOLAR:     { economy: -2, ecology: 4,  research: 1,  newType: 'SOLAR_FARM' },
  CLEAR_FARMLAND:         { economy: 2,  ecology: -3, research: 0,  newType: 'EMPTY' },
  UPGRADE_CARBON_CAPTURE: { economy: -5, ecology: 8,  research: 3,  newType: 'CARBON_CAPTURE' },
};

// ---------------------------------------------------------------------------
// Speech mock data
// ---------------------------------------------------------------------------

const REACTION_TEMPLATES: Record<string, { dialogues: string[]; tones: string[] }> = {
  FARMER: {
    dialogues: [
      'As long as the fields are safe, I am with you.',
      'Careful now — the harvest depends on your choices.',
      'I have seen leaders come and go. Actions matter more than words.',
    ],
    tones: ['cautious', 'hopeful', 'skeptical'],
  },
  BUSINESS: {
    dialogues: [
      'Show me the numbers and you have my vote.',
      'Economic growth cannot wait. Move faster.',
      'That is a reasonable plan — if you follow through.',
    ],
    tones: ['pragmatic', 'impatient', 'approving'],
  },
  SCIENTIST: {
    dialogues: [
      'Interesting approach. The data will tell us if it works.',
      'More funding for research would make all the difference.',
      'I see potential here, but we need evidence-based decisions.',
    ],
    tones: ['analytical', 'hopeful', 'measured'],
  },
  ACTIVIST: {
    dialogues: [
      'Talk is cheap — I am watching your actions closely.',
      'Finally, someone who listens to the planet!',
      'Do not forget: every compromise with nature is a loss.',
    ],
    tones: ['fierce', 'excited', 'warning'],
  },
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
// Game-over ranking
// ---------------------------------------------------------------------------

function computeRank(g: GameStateResponse): string {
  const { ecology, economy, research } = g.resources;
  const avg = (ecology + economy + research) / 3;
  const avgApproval =
    g.citizens.reduce((s, c) => s + c.approval, 0) / g.citizens.length;
  const score = avg * 0.6 + avgApproval * 0.4;
  if (score >= 75) return 'S';
  if (score >= 60) return 'A';
  if (score >= 45) return 'B';
  if (score >= 30) return 'C';
  return 'D';
}

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
    const actions = ACTIONS_BY_TYPE[tile.tileType] ?? [];
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

    const effect = ACTION_EFFECTS[action];
    if (effect) {
      tile.tileType = effect.newType;
      tile.roundsInCurrentState = 0;
      g.resources.ecology = clamp(g.resources.ecology + effect.ecology);
      g.resources.economy = clamp(g.resources.economy + effect.economy);
      g.resources.research = clamp(g.resources.research + effect.research);
    }

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
      const templates = REACTION_TEMPLATES[c.citizenType] ?? REACTION_TEMPLATES.ACTIVIST;
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

    // Resource drift ±3
    g.resources.ecology = clamp(g.resources.ecology + rand(-3, 3));
    g.resources.economy = clamp(g.resources.economy + rand(-3, 3));
    g.resources.research = clamp(g.resources.research + rand(-3, 3));

    // Slight citizen approval drift
    for (const c of g.citizens) {
      c.approval = clamp(c.approval + rand(-2, 2));
    }

    // Game over check
    const { ecology, economy, research } = g.resources;
    if (ecology <= 0 || economy <= 0 || research <= 0) {
      g.status = 'FINISHED';
      g.defeatReason = 'A critical resource has been depleted.';
      g.resultRank = 'D';
    } else if (g.currentRound > 7) {
      g.status = 'FINISHED';
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
