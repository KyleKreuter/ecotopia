import { api } from '../services/api.ts';
import { eventBus, GameEvents } from './EventBus.ts';
import type {
  GameStateResponse,
  SpeechResponse,
  TileActionType,
} from '../types/backend.ts';

class GameStateManager {
  private state: GameStateResponse | null = null;
  private _speechResponse: SpeechResponse | null = null;

  get gameState(): GameStateResponse | null {
    return this.state;
  }

  get gameId(): number | null {
    return this.state?.id ?? null;
  }

  get speechResponse(): SpeechResponse | null {
    return this._speechResponse;
  }

  async createGame(): Promise<void> {
    this.state = await api.createGame();
    this._speechResponse = null;
    eventBus.emit(GameEvents.STATE_CHANGED, this.state);
  }

  async getTileActions(x: number, y: number): Promise<string[]> {
    if (!this.state) return [];
    const res = await api.getTileActions(this.state.id, x, y);
    eventBus.emit(GameEvents.ACTIONS_LOADED, { x, y, actions: res.availableActions });
    return res.availableActions;
  }

  async executeAction(x: number, y: number, action: TileActionType): Promise<void> {
    if (!this.state) return;
    const oldState = this.state;
    this.state = await api.executeAction(this.state.id, x, y, action);
    eventBus.emit(GameEvents.ACTION_EXECUTED, { x, y, action, oldState });
    eventBus.emit(GameEvents.STATE_CHANGED, this.state);

    if (this.state.currentRoundInfo.remainingActions === 0) {
      eventBus.emit(GameEvents.PHASE_CHANGED, 'speech');
    }
  }

  async submitSpeech(text: string): Promise<void> {
    if (!this.state) return;
    this._speechResponse = await api.submitSpeech(this.state.id, text);
    eventBus.emit(GameEvents.SPEECH_RESPONSE, this._speechResponse);
  }

  async endRound(): Promise<void> {
    if (!this.state) return;
    const oldRound = this.state.currentRound;
    this.state = await api.endRound(this.state.id);
    this._speechResponse = null;
    eventBus.emit(GameEvents.ROUND_ENDED, { oldRound, newRound: this.state.currentRound });
    eventBus.emit(GameEvents.STATE_CHANGED, this.state);

    if (this.state.status !== 'IN_PROGRESS') {
      eventBus.emit(GameEvents.GAME_OVER, this.state);
    } else {
      eventBus.emit(GameEvents.PHASE_CHANGED, 'action');
    }
  }
}

export const gameState = new GameStateManager();
