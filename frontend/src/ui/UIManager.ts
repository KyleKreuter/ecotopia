import type { GameStateResponse, SpeechResponse } from '../types/backend.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';
import { ResourcePanel } from './ResourcePanel.ts';
import { CitizenPanel } from './CitizenPanel.ts';
import { SpeechPanel } from './SpeechPanel.ts';
import { PromisePanel } from './PromisePanel.ts';
import { ContradictionAlert } from './ContradictionAlert.ts';
import { ReactionPanel } from './ReactionPanel.ts';
import { TutorialOverlay } from './TutorialOverlay.ts';
import { gameState } from '../state/GameStateManager.ts';

export class UIManager {
  private overlay: HTMLElement;
  private resourcePanel: ResourcePanel;
  private citizenPanel: CitizenPanel;
  private speechPanel: SpeechPanel;
  private promisePanel: PromisePanel;
  private contradictionAlert: ContradictionAlert;
  private reactionPanel: ReactionPanel;
  private tutorial: TutorialOverlay | null = null;

  constructor() {
    this.overlay = document.getElementById('ui-overlay')!;

    this.resourcePanel = new ResourcePanel(this.overlay);
    this.citizenPanel = new CitizenPanel(this.overlay);
    this.speechPanel = new SpeechPanel(this.overlay);
    this.promisePanel = new PromisePanel(this.overlay);
    this.contradictionAlert = new ContradictionAlert(this.overlay);
    this.reactionPanel = new ReactionPanel(this.overlay);

    this.setupEventListeners();

    if (gameState.getState().currentRound === 1) {
      this.tutorial = new TutorialOverlay(this.overlay, () => {
        this.tutorial = null;
      });
    }
  }

  private setupEventListeners(): void {
    eventBus.on(GameEvents.PHASE_CHANGED, (phase: unknown) => {
      if (phase === 'speech') {
        this.speechPanel.show();
        this.reactionPanel.hide();
      } else {
        this.speechPanel.hide();
        this.reactionPanel.hide();
      }
    });

    eventBus.on(GameEvents.SPEECH_RESPONSE, (response: unknown) => {
      const r = response as SpeechResponse;
      if (r.contradictions.length > 0) {
        this.contradictionAlert.show(r.contradictions);
      }
      if (r.citizenReactions.length > 0) {
        this.reactionPanel.show(r.citizenReactions);
      }
      this.speechPanel.showEndRound();
    });
  }

  updateAll(state: GameStateResponse): void {
    this.resourcePanel.update(state);
    this.citizenPanel.update(state.citizens);
    this.promisePanel.update(state.promises);
  }

  destroy(): void {
    this.resourcePanel.destroy();
    this.citizenPanel.destroy();
    this.speechPanel.destroy();
    this.promisePanel.destroy();
    this.contradictionAlert.destroy();
    this.reactionPanel.destroy();
  }
}
