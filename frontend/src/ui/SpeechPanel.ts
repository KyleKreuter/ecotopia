import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

export class SpeechPanel {
  private static readonly MAX_CHARS = 500;

  private el: HTMLElement;
  private textarea!: HTMLTextAreaElement;
  private submitBtn!: HTMLButtonElement;
  private endRoundBtn!: HTMLButtonElement;
  private contextHint!: HTMLDivElement;
  private charCount!: HTMLDivElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'speech-panel';
    this.el.innerHTML = `
      <div class="speech-modal">
        <h3>Deliver Your Speech</h3>
        <div class="speech-context"></div>
        <textarea placeholder="Address your citizens..." maxlength="${SpeechPanel.MAX_CHARS}"></textarea>
        <div class="speech-charcount">0 / ${SpeechPanel.MAX_CHARS} characters</div>
        <div class="speech-actions">
          <button class="pixel-btn speech-submit">Deliver Speech</button>
          <button class="pixel-btn warning end-round" style="display:none">End Round</button>
        </div>
      </div>
    `;
    parent.appendChild(this.el);

    this.textarea = this.el.querySelector('textarea')!;
    this.submitBtn = this.el.querySelector('.speech-submit')!;
    this.endRoundBtn = this.el.querySelector('.end-round')!;
    this.contextHint = this.el.querySelector('.speech-context')!;
    this.charCount = this.el.querySelector('.speech-charcount')!;

    this.submitBtn.addEventListener('click', () => this.handleSubmit());
    this.endRoundBtn.addEventListener('click', () => this.handleEndRound());
    this.textarea.addEventListener('input', () => this.updateCharCount());
  }

  private async handleSubmit(): Promise<void> {
    const text = this.textarea.value.trim();
    if (!text) return;

    this.submitBtn.disabled = true;
    this.submitBtn.innerHTML = '<span class="loading-spinner"></span> Speaking';

    try {
      await gameState.submitSpeech(text);
      this.submitBtn.textContent = 'Speech Delivered!';
    } catch (err) {
      this.submitBtn.textContent = 'Error - Retry';
      this.submitBtn.disabled = false;
      const msg = err instanceof Error ? err.message : 'Speech failed';
      eventBus.emit(GameEvents.ERROR, msg);
    }
  }

  private async handleEndRound(): Promise<void> {
    this.endRoundBtn.disabled = true;
    this.endRoundBtn.textContent = 'Ending...';

    try {
      await gameState.endRound();
      this.hide();
    } catch (err) {
      this.endRoundBtn.disabled = false;
      this.endRoundBtn.textContent = 'End Round';
      const msg = err instanceof Error ? err.message : 'End round failed';
      eventBus.emit(GameEvents.ERROR, msg);
    }
  }

  private updateCharCount(): void {
    const len = this.textarea.value.length;
    this.charCount.textContent = `${len} / ${SpeechPanel.MAX_CHARS} characters`;
  }

  private populateContext(): void {
    const state = gameState.gameState;
    if (!state) {
      this.contextHint.style.display = 'none';
      return;
    }

    const { resources, citizens, promises, currentRound } = state;
    const activePromises = promises.filter(p => p.status === 'active').length;
    const citizenLines = citizens
      .map(c => `${c.name} (${c.profession}) — ${c.approval}% approval`)
      .join('<br>');

    this.contextHint.style.display = 'block';
    this.contextHint.innerHTML = [
      `<strong>Round ${currentRound}</strong>`,
      `Ecology ${resources.ecology}% / Economy ${resources.economy}% / Research ${resources.research}%`,
      citizenLines,
      `${activePromises} active promise${activePromises !== 1 ? 's' : ''}`,
    ].join('<br>');
  }

  show(): void {
    this.el.classList.add('visible');
    this.textarea.value = '';
    this.submitBtn.disabled = false;
    this.submitBtn.textContent = 'Deliver Speech';
    this.endRoundBtn.style.display = 'none';
    this.updateCharCount();
    this.populateContext();
    requestAnimationFrame(() => this.textarea.focus());
  }

  showEndRound(): void {
    this.endRoundBtn.style.display = 'inline-block';
    this.endRoundBtn.disabled = false;
    this.endRoundBtn.textContent = 'End Round';
  }

  hide(): void {
    this.el.classList.remove('visible');
  }

  destroy(): void {
    this.el.remove();
  }
}
