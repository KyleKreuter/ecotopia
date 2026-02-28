import type { GameState } from '../types/game';
import { INITIAL_GAME_STATE } from './mockData';

const API_BASE = '/api/game';
const USE_MOCK = true;

/** Simulates network delay for realistic mock behavior. */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Returns a clamped random delta for resource bars. */
function randomDelta(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function clamp(value: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, value));
}

/**
 * Mock speech submission: shifts resources randomly and rotates citizen dialogue
 * to simulate backend AI processing.
 */
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

export async function getGameState(): Promise<GameState> {
  if (USE_MOCK) {
    await delay(200);
    return { ...INITIAL_GAME_STATE };
  }
  const res = await fetch(`${API_BASE}/state`);
  return res.json() as Promise<GameState>;
}

export async function submitSpeech(
  speech: string,
  currentState: GameState
): Promise<GameState> {
  if (USE_MOCK) {
    return mockSubmitSpeech(currentState, speech);
  }
  const res = await fetch(`${API_BASE}/speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ speech }),
  });
  return res.json() as Promise<GameState>;
}

export async function startNewGame(): Promise<GameState> {
  if (USE_MOCK) {
    await delay(300);
    return { ...INITIAL_GAME_STATE };
  }
  const res = await fetch(`${API_BASE}/new`, { method: 'POST' });
  return res.json() as Promise<GameState>;
}
