import type { GameState, Citizen, CitizenTone, TileType, GamePromise, Contradiction } from '../types/game';
import type {
  BackendGameStateResponse,
  BackendSpeechResponse,
} from '../types/backend';
import { INITIAL_GAME_STATE } from './mockData';
import {
  isMistralAvailable,
  processPlayerTurn,
  applyTurnResult,
} from './mistral';

/**
 * Resolves the active API mode:
 * - "backend" when VITE_BACKEND_URL is set (Spring Boot)
 * - "mistral" when VITE_MISTRAL_API_KEY is set
 * - "mock" otherwise (random offline simulation)
 */
type ApiMode = 'backend' | 'mistral' | 'mock';

function getBackendUrl(): string | null {
  return import.meta.env.VITE_BACKEND_URL || null;
}

function resolveMode(): ApiMode {
  if (getBackendUrl()) return 'backend';
  if (isMistralAvailable()) return 'mistral';
  return 'mock';
}

const MODE: ApiMode = resolveMode();

/** Current game ID when using backend mode. */
let currentGameId: number | null = null;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function randomDelta(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function clamp(value: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, value));
}

// Backend API helpers

async function backendFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getBackendUrl()!;
  const url = `${base.replace(/\/$/, '')}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Backend ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

/** Maps a backend tile type string to the frontend TileType enum. */
function mapTileType(bt: string): TileType {
  const mapping: Record<string, TileType> = {
    FOREST: 'forest',
    WATER: 'water',
    FACTORY: 'factory',
    SOLAR: 'solar',
    HOUSE: 'house',
    FARM: 'farm',
    EMPTY: 'empty',
    RESEARCH_LAB: 'research_lab',
    WIND_TURBINE: 'wind_turbine',
    COAL_PLANT: 'coal_plant',
  };
  return mapping[bt] ?? (bt.toLowerCase() as TileType);
}

/** Converts backend GameStateResponse to frontend GameState. */
function mapBackendState(bs: BackendGameStateResponse): GameState {
  const gridSize = 10;
  const grid: GameState['grid'] = Array.from({ length: gridSize }, () =>
    Array.from({ length: gridSize }, (_, x) => ({ x, y: 0, type: 'empty' as TileType }))
  );
  for (const t of bs.tiles) {
    if (t.y < gridSize && t.x < gridSize) {
      grid[t.y][t.x] = { x: t.x, y: t.y, type: mapTileType(t.tileType) };
    }
  }

  const citizens: Citizen[] = bs.citizens.map((c) => ({
    name: c.name,
    role: c.profession || c.citizenType,
    personality: c.personality,
    approval: c.approval,
    dialogue: c.openingSpeech || '',
    tone: 'neutral' as CitizenTone,
    isCore: c.remainingRounds === null,
  }));

  const promises: GamePromise[] = bs.promises.map((p) => ({
    id: `backend_${p.id}`,
    text: p.text,
    type: 'explicit' as const,
    confidence: 1,
    targetCitizen: p.citizenName ?? null,
    deadlineRound: p.deadline,
    status: (p.status?.toLowerCase() ?? 'active') as GamePromise['status'],
    roundMade: p.roundMade,
  }));

  const isFinished = bs.status === 'FINISHED' || bs.status === 'DEFEATED';
  const gameResult = bs.resultRank ? 'win' : bs.defeatReason ? 'lose' : null;

  return {
    round: bs.currentRound,
    maxRounds: 7,
    ecology: bs.resources.ecology,
    economy: bs.resources.economy,
    research: bs.resources.research,
    grid,
    citizens,
    promises,
    contradictions: [],
    gameOver: isFinished,
    gameResult,
  };
}

/** Applies backend SpeechResponse onto the current frontend GameState. */
function applyBackendSpeechResponse(
  currentState: GameState,
  resp: BackendSpeechResponse
): GameState {
  const newPromises: GamePromise[] = resp.extractedPromises.map((p) => ({
    id: `backend_${p.id}`,
    text: p.text,
    type: 'explicit' as const,
    confidence: 1,
    targetCitizen: p.citizenName ?? null,
    deadlineRound: p.deadline,
    status: (p.status?.toLowerCase() ?? 'active') as GamePromise['status'],
    roundMade: p.roundMade,
  }));

  const newContradictions: Contradiction[] = resp.contradictions.map((c) => ({
    description: c.description,
    speechQuote: c.speechQuote,
    contradictingAction: c.contradictingAction,
    severity: (['low', 'medium', 'high'].includes(c.severity?.toLowerCase())
      ? c.severity.toLowerCase()
      : 'medium') as Contradiction['severity'],
  }));

  const updatedCitizens = currentState.citizens.map((citizen) => {
    const reaction = resp.citizenReactions.find((r) => r.citizenName === citizen.name);
    if (!reaction) return citizen;
    return {
      ...citizen,
      approval: clamp(citizen.approval + reaction.approvalDelta, 0, 100),
      dialogue: reaction.dialogue,
      tone: (reaction.tone?.toLowerCase() ?? citizen.tone) as CitizenTone,
    };
  });

  const newRound = Math.min(currentState.round + 1, currentState.maxRounds);
  const isGameOver = newRound > currentState.maxRounds;

  return {
    ...currentState,
    round: isGameOver ? currentState.maxRounds : newRound,
    citizens: updatedCitizens,
    promises: [...currentState.promises, ...newPromises],
    contradictions: [...currentState.contradictions, ...newContradictions],
    gameOver: isGameOver,
  };
}

// Backend mode functions

async function backendCreateGame(): Promise<GameState> {
  const resp = await backendFetch<BackendGameStateResponse>('/api/games', {
    method: 'POST',
  });
  currentGameId = resp.id;
  return mapBackendState(resp);
}

async function backendGetGame(): Promise<GameState> {
  if (!currentGameId) return backendCreateGame();
  const resp = await backendFetch<BackendGameStateResponse>(
    `/api/games/${currentGameId}`
  );
  return mapBackendState(resp);
}

async function backendSubmitSpeech(
  speech: string,
  currentState: GameState
): Promise<GameState> {
  if (!currentGameId) {
    throw new Error('No active game. Call startNewGame() first.');
  }
  const resp = await backendFetch<BackendSpeechResponse>(
    `/api/games/${currentGameId}/speech`,
    { method: 'POST', body: JSON.stringify({ text: speech }) }
  );
  return applyBackendSpeechResponse(currentState, resp);
}

// Mock mode functions

async function mockSubmitSpeech(
  currentState: GameState,
  _speech: string
): Promise<GameState> {
  await delay(800);

  const newRound = Math.min(currentState.round + 1, currentState.maxRounds);
  const isGameOver = newRound > currentState.maxRounds;

  const ecology = clamp(currentState.ecology + randomDelta(-5, 10), 0, 100);
  const economy = clamp(currentState.economy + randomDelta(-8, 8), 0, 100);
  const research = clamp(currentState.research + randomDelta(0, 12), 0, 100);

  const mockResponses = [
    { name: 'Karl', dialogue: 'Actions speak louder than words, mayor.', tone: 'suspicious' as const },
    { name: 'Mia', dialogue: 'Finally some progress! But we need more.', tone: 'hopeful' as const },
    { name: 'Sarah', dialogue: 'The numbers do not lie, mayor. Where is the budget?', tone: 'angry' as const },
  ];

  const citizens = currentState.citizens.map((c) => {
    const response = mockResponses.find((r) => r.name === c.name);
    return {
      ...c,
      approval: clamp(c.approval + randomDelta(-10, 10), 0, 100),
      dialogue: response?.dialogue ?? c.dialogue,
      tone: response?.tone ?? c.tone,
    };
  });

  let gameResult = currentState.gameResult;
  if (isGameOver) {
    gameResult = ecology >= 50 && economy >= 30 ? 'win' : 'lose';
  }

  return {
    ...currentState,
    round: isGameOver ? currentState.maxRounds : newRound,
    ecology,
    economy,
    research,
    citizens,
    gameOver: isGameOver,
    gameResult,
  };
}

// Mistral mode functions

async function mistralSubmitSpeech(
  currentState: GameState,
  speech: string
): Promise<GameState> {
  const turnResult = await processPlayerTurn(speech, currentState);
  return applyTurnResult(currentState, turnResult);
}

// Public API (auto-detects mode)

export async function getGameState(): Promise<GameState> {
  if (MODE === 'backend') return backendGetGame();
  await delay(MODE === 'mock' ? 200 : 100);
  return { ...INITIAL_GAME_STATE };
}

export async function submitSpeech(
  speech: string,
  currentState: GameState
): Promise<GameState> {
  switch (MODE) {
    case 'backend':
      return backendSubmitSpeech(speech, currentState);
    case 'mistral':
      return mistralSubmitSpeech(currentState, speech);
    default:
      return mockSubmitSpeech(currentState, speech);
  }
}

export async function startNewGame(): Promise<GameState> {
  if (MODE === 'backend') return backendCreateGame();
  await delay(200);
  return { ...INITIAL_GAME_STATE };
}

/** Advances to next round via backend. Only available in backend mode. */
export async function endRound(): Promise<GameState | null> {
  if (MODE !== 'backend' || !currentGameId) return null;
  const resp = await backendFetch<BackendGameStateResponse>(
    `/api/games/${currentGameId}/end-round`,
    { method: 'POST' }
  );
  return mapBackendState(resp);
}
