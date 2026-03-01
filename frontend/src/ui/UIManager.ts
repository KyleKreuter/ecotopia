import type { GameStateResponse, SpeechResponse } from '../types/backend.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';
import { gameState } from '../state/GameStateManager.ts';
import { ResourcePanel } from './ResourcePanel.ts';
import { CitizenPanel } from './CitizenPanel.ts';
import { SpeechPanel } from './SpeechPanel.ts';
import { PromisePanel } from './PromisePanel.ts';
import { ContradictionAlert } from './ContradictionAlert.ts';
import { ReactionPopup } from './ReactionPopup.ts';
import { LegendPanel } from './LegendPanel.ts';

export class UIManager {
  private overlay: HTMLElement;
  private resourcePanel: ResourcePanel;
  private citizenPanel: CitizenPanel;
  private speechPanel: SpeechPanel;
  private promisePanel: PromisePanel;
  private contradictionAlert: ContradictionAlert;
  private reactionPopup: ReactionPopup;
  private legendPanel: LegendPanel;

  constructor() {
    this.overlay = document.getElementById('ui-overlay')!;

    this.resourcePanel = new ResourcePanel(this.overlay);
    this.citizenPanel = new CitizenPanel(this.overlay);
    this.speechPanel = new SpeechPanel(this.overlay);
    this.promisePanel = new PromisePanel(this.overlay);
    this.contradictionAlert = new ContradictionAlert(this.overlay);
    this.reactionPopup = new ReactionPopup(this.overlay);
    this.legendPanel = new LegendPanel(this.overlay);

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
      this.speechPanel.hide();
      const citizens = gameState.gameState?.citizens ?? [];
      this.reactionPopup.show(r.citizenReactions, citizens);
    });

    eventBus.on(GameEvents.REACTIONS_DONE, async () => {
      try {
        await gameState.endRound();
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'End round failed';
        eventBus.emit(GameEvents.ERROR, msg);
      }
    });
  }

  updateAll(state: GameStateResponse): void {
    this.resourcePanel.update(state);
    this.citizenPanel.update(state.citizens);
    this.promisePanel.update(state.promises);
    this.legendPanel.update(state);
  }

  destroy(): void {
    this.resourcePanel.destroy();
    this.citizenPanel.destroy();
    this.speechPanel.destroy();
    this.promisePanel.destroy();
    this.contradictionAlert.destroy();
    this.reactionPopup.destroy();
    this.legendPanel.destroy();
  }
}
