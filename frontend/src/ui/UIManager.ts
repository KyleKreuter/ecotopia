import type { GameStateResponse, SpeechResponse } from '../types/backend.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';
import { ResourcePanel } from './ResourcePanel.ts';
import { SpeechPanel } from './SpeechPanel.ts';
import { PromisePanel } from './PromisePanel.ts';
import { ContradictionAlert } from './ContradictionAlert.ts';

export class UIManager {
  private overlay: HTMLElement;
  private resourcePanel: ResourcePanel;
  private speechPanel: SpeechPanel;
  private promisePanel: PromisePanel;
  private contradictionAlert: ContradictionAlert;

  constructor() {
    this.overlay = document.getElementById('ui-overlay')!;

    this.resourcePanel = new ResourcePanel(this.overlay);
    this.speechPanel = new SpeechPanel(this.overlay);
    this.promisePanel = new PromisePanel(this.overlay);
    this.contradictionAlert = new ContradictionAlert(this.overlay);

    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    eventBus.on(GameEvents.PHASE_CHANGED, (phase: unknown) => {
      if (phase === 'speech') {
        this.speechPanel.show();
      } else {
        this.speechPanel.hide();
      }
    });

    eventBus.on(GameEvents.SPEECH_RESPONSE, (response: unknown) => {
      const r = response as SpeechResponse;
      if (r.contradictions.length > 0) {
        this.contradictionAlert.show(r.contradictions);
      }
      this.speechPanel.showEndRound();
    });
  }

  updateAll(state: GameStateResponse): void {
    this.resourcePanel.update(state);
    this.promisePanel.update(state.promises);
  }

  destroy(): void {
    this.resourcePanel.destroy();
    this.speechPanel.destroy();
    this.promisePanel.destroy();
    this.contradictionAlert.destroy();
  }
}
