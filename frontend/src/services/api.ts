import type {
  GameStateResponse,
  TileActionResponse,
  TileActionType,
  SpeechResponse,
  PromiseResponse,
} from '../types/backend.ts';
import { mockApi } from './mockApi.ts';

const BASE = '/api/games';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

const realApi = {
  createGame(): Promise<GameStateResponse> {
    return request<GameStateResponse>(BASE, { method: 'POST' });
  },

  getGame(id: number): Promise<GameStateResponse> {
    return request<GameStateResponse>(`${BASE}/${id}`);
  },

  deleteGame(id: number): Promise<void> {
    return request<void>(`${BASE}/${id}`, { method: 'DELETE' });
  },

  getTileActions(gameId: number, x: number, y: number): Promise<TileActionResponse> {
    return request<TileActionResponse>(`${BASE}/${gameId}/tiles/${x}/${y}/actions`);
  },

  executeAction(gameId: number, x: number, y: number, action: TileActionType): Promise<GameStateResponse> {
    return request<GameStateResponse>(`${BASE}/${gameId}/tiles/${x}/${y}/actions`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  },

  submitSpeech(gameId: number, text: string): Promise<SpeechResponse> {
    return request<SpeechResponse>(`${BASE}/${gameId}/speech`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  },

  endRound(gameId: number): Promise<GameStateResponse> {
    return request<GameStateResponse>(`${BASE}/${gameId}/end-round`, { method: 'POST' });
  },

  getPromises(gameId: number): Promise<PromiseResponse[]> {
    return request<PromiseResponse[]>(`${BASE}/${gameId}/promises`);
  },
};

const IS_DEMO = import.meta.env.VITE_DEMO_MODE === 'true';
export const api = IS_DEMO ? mockApi : realApi;
