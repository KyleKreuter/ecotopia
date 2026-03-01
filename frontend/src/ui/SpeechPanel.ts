import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

export class SpeechPanel {
  private el: HTMLElement;
  private textarea!: HTMLTextAreaElement;
  private submitBtn!: HTMLButtonElement;
  private endRoundBtn!: HTMLButtonElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'speech-panel';
    this.el.innerHTML = `
      <h3>📢 Deliver Your Speech</h3>
      <textarea placeholder="Address your citizens..."></textarea>
      <div class="speech-actions">
        <button class="pixel-btn speech-submit">Deliver Speech</button>
        <button class="pixel-btn warning end-round" style="display:none">End Round</button>
      </div>
    `;
    parent.appendChild(this.el);

    this.textarea = this.el.querySelector('textarea')!;
    this.submitBtn = this.el.querySelector('.speech-submit')!;
    this.endRoundBtn = this.el.querySelector('.end-round')!;

    this.submitBtn.addEventListener('click', () => this.handleSubmit());
    this.endRoundBtn.addEventListener('click', () => this.handleEndRound());
  }

  private async handleSubmit(): Promise<void> {
    const text = this.textarea.value.trim();
    if (!text) return;

    this.submitBtn.disabled = true;
    this.submitBtn.textContent = 'Speaking...';

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

  show(): void {
    this.el.classList.add('visible');
    this.textarea.value = '';
    this.submitBtn.disabled = false;
    this.submitBtn.textContent = 'Deliver Speech';
    this.endRoundBtn.style.display = 'none';
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
