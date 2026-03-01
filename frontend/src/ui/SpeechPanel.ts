import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

/** Speech panel where the player addresses their citizens. */
export class SpeechPanel {
  private static readonly MAX_CHARS = 500;
  private el: HTMLElement;
  private textarea!: HTMLTextAreaElement;
  private submitBtn!: HTMLButtonElement;
  private endRoundBtn!: HTMLButtonElement;
  private charCount!: HTMLDivElement;

  private avatarKey(name: string): string {
    const parts = name.toLowerCase().split(/[\s.]+/).filter(Boolean);
    return parts[parts.length - 1];
  }

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'speech-panel';
    this.el.innerHTML = `
      <div class="speech-modal">
        <h3>Deliver Your Speech</h3>
        <div class="speech-context-bar"></div>
        <textarea placeholder="Address your citizens..." maxlength="${SpeechPanel.MAX_CHARS}"></textarea>
        <div class="speech-footer">
          <span class="speech-charcount">0 / ${SpeechPanel.MAX_CHARS}</span>
          <div class="speech-actions">
            <button class="pixel-btn speech-submit">Deliver Speech</button>
            <button class="pixel-btn warning end-round" style="display:none">End Round</button>
          </div>
        </div>
      </div>
    `;
    parent.appendChild(this.el);

    this.textarea = this.el.querySelector('textarea')!;
    this.submitBtn = this.el.querySelector('.speech-submit')!;
    this.endRoundBtn = this.el.querySelector('.end-round')!;
    this.charCount = this.el.querySelector('.speech-charcount')!;

    this.submitBtn.addEventListener('click', () => this.handleSubmit());
    this.endRoundBtn.addEventListener('click', () => this.handleEndRound());
    this.textarea.addEventListener('input', () => this.updateCharCount());
  }

  private async handleSubmit(): Promise<void> {
    const text = this.textarea.value.trim();
    if (!text) return;
    this.submitBtn.disabled = true;
    this.submitBtn.textContent = 'Analyzing...';

    try {
      await gameState.submitSpeech(text);
      this.submitBtn.textContent = 'Delivered';
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Speech failed';
      this.submitBtn.textContent = 'Retry';
      this.submitBtn.disabled = false;
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
    this.charCount.textContent = `${this.textarea.value.length} / ${SpeechPanel.MAX_CHARS}`;
  }

  private buildContext(): string {
    const state = gameState.gameState;
    if (!state) return '';
    const { resources, citizens, currentRound } = state;
    const citizenChips = citizens.map(c => {
      const key = this.avatarKey(c.name);
      const color = c.approval >= 60 ? '#2ecc71' : c.approval >= 35 ? '#f39c12' : '#e74c3c';
      return `<span style="display:inline-flex;align-items:center;gap:3px;background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:4px;margin:2px">
        <img src="/assets/character/${key}.png" width="20" height="20" style="image-rendering:pixelated;border-radius:3px" onerror="this.style.display='none'">
        <span>${c.name}</span>
        <span style="color:${color};font-weight:bold">${c.approval}%</span>
      </span>`;
    }).join(' ');

    return `<div style="display:flex;gap:16px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
      <span style="color:#fff">Round ${currentRound}/7</span>
      <span style="color:#2ecc71">ECO ${resources.ecology}</span>
      <span style="color:#f39c12">ECON ${resources.economy}</span>
      <span style="color:#3498db">RES ${resources.research}</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:4px">${citizenChips}</div>`;
  }

  show(): void {
    this.el.classList.add('visible');
    this.textarea.value = '';
    this.submitBtn.disabled = false;
    this.submitBtn.textContent = 'Deliver Speech';
    this.endRoundBtn.style.display = 'none';
    this.updateCharCount();
    const ctx = this.el.querySelector('.speech-context-bar')!;
    ctx.innerHTML = this.buildContext();
    requestAnimationFrame(() => this.textarea.focus());
  }

  showEndRound(): void {
    this.endRoundBtn.style.display = 'inline-block';
    this.endRoundBtn.disabled = false;
    this.endRoundBtn.textContent = 'End Round';
  }

  hide(): void { this.el.classList.remove('visible'); }
  destroy(): void { this.el.remove(); }
}
