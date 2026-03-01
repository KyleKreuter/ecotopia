type Listener = (...args: unknown[]) => void;

export const GameEvents = {
  STATE_CHANGED: 'state_changed',
  PHASE_CHANGED: 'phase_changed',
  TILE_SELECTED: 'tile_selected',
  TILE_DESELECTED: 'tile_deselected',
  ACTIONS_LOADED: 'actions_loaded',
  ACTION_EXECUTED: 'action_executed',
  SPEECH_SUBMITTED: 'speech_submitted',
  SPEECH_RESPONSE: 'speech_response',
  ROUND_ENDED: 'round_ended',
  GAME_OVER: 'game_over',
  ERROR: 'error',
} as const;

class EventBus {
  private listeners = new Map<string, Set<Listener>>();

  on(event: string, listener: Listener): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }

  off(event: string, listener: Listener): void {
    this.listeners.get(event)?.delete(listener);
  }

  emit(event: string, ...args: unknown[]): void {
    this.listeners.get(event)?.forEach((fn) => fn(...args));
  }

  clear(): void {
    this.listeners.clear();
  }
}

export const eventBus = new EventBus();
