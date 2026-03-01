import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

/** Speech panel where the player addresses their citizens. */
export class SpeechPanel {
  private static readonly MAX_CHARS = 500;

  private el: HTMLElement;
  private textarea!: HTMLTextAreaElement;
  private submitBtn!: HTMLButtonElement;
  private endRoundBtn!: HTMLButtonElement;
  private contextHint!: HTMLDivElement;
  private charCount!: HTMLDivElement;
  private errorDiv!: HTMLDivElement;

  /** Extract base name for avatar (handles "Dr. Yuki" -> "yuki"). */
  private avatarKey(name: string): string {
    const parts = name.toLowerCase().split(/[\s.]+/).filter(Boolean);
    return parts[parts.length - 1];
  }

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'speech-panel';
    this.el.innerHTML = `
      <div class="speech-modal">
        <h3>🎙️ Deliver Your Speech</h3>
        <div class="speech-context"></div>
        <textarea placeholder="Address your citizens..." maxlength="${SpeechPanel.MAX_CHARS}"></textarea>
        <div class="speech-charcount">0 / ${SpeechPanel.MAX_CHARS} characters</div>
        <div class="speech-error" style="display:none">
          <span class="speech-error-msg"></span>
          <button class="pixel-btn danger speech-retry">Retry</button>
        </div>
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
    this.errorDiv = this.el.querySelector('.speech-error')!;

    this.submitBtn.addEventListener('click', () => this.handleSubmit());
    this.endRoundBtn.addEventListener('click', () => this.handleEndRound());
    this.textarea.addEventListener('input', () => this.updateCharCount());
    this.el.querySelector('.speech-retry')!.addEventListener('click', () => this.handleSubmit());
  }

  private async handleSubmit(): Promise<void> {
    const text = this.textarea.value.trim();
    if (!text) return;

    this.submitBtn.disabled = true;
    this.submitBtn.textContent = 'Analyzing speech...';
    this.submitBtn.classList.add('loading');
    this.errorDiv.style.display = 'none';

    try {
      await gameState.submitSpeech(text);
      this.submitBtn.textContent = 'Speech Delivered';
      this.submitBtn.classList.remove('loading');
      this.submitBtn.classList.add('success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Speech failed';
      this.submitBtn.textContent = 'Deliver Speech';
      this.submitBtn.disabled = false;
      this.submitBtn.classList.remove('loading');
      this.errorDiv.style.display = 'flex';
      this.errorDiv.querySelector('.speech-error-msg')!.textContent = msg;
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
    const ratio = len / SpeechPanel.MAX_CHARS;
    this.charCount.textContent = `${len} / ${SpeechPanel.MAX_CHARS} characters`;
    this.charCount.classList.toggle('warn', ratio > 0.7 && ratio <= 0.9);
    this.charCount.classList.toggle('over', ratio > 0.9);
  }

  private populateContext(): void {
    const state = gameState.gameState;
    if (!state) {
      this.contextHint.style.display = 'none';
      return;
    }

    const { resources, citizens, promises, currentRound } = state;
    const activePromises = promises.filter(p => p.status === 'active').length;

    const resourceBars = [
      { label: 'ECO', value: resources.ecology, cls: 'eco' },
      { label: 'ECON', value: resources.economy, cls: 'econ' },
      { label: 'RES', value: resources.research, cls: 'res' },
    ].map(r => `
      <div class="ctx-resource">
        <span class="ctx-resource-label">${r.label}</span>
        <div class="ctx-bar-track"><div class="ctx-bar-fill ctx-${r.cls}" style="width:${r.value}%"></div></div>
        <span class="ctx-resource-val">${r.value}</span>
      </div>
    `).join('');

    const citizenCards = citizens.map(c => {
      const key = this.avatarKey(c.name);
      const approvalColor = c.approval >= 60 ? '#2ecc71' : c.approval >= 35 ? '#f39c12' : '#e74c3c';
      return `
        <div class="ctx-citizen">
          <img class="ctx-citizen-avatar" src="/assets/character/${key}.png" alt="${c.name}" width="24" height="24" onerror="this.style.display='none'">
          <span class="ctx-citizen-name">${c.name}</span>
          <span class="ctx-citizen-approval" style="color:${approvalColor}">${c.approval}%</span>
        </div>
      `;
    }).join('');

    this.contextHint.style.display = 'block';
    this.contextHint.innerHTML = `
      <div class="ctx-header">Round ${currentRound} / 7</div>
      <div class="ctx-resources">${resourceBars}</div>
      <div class="ctx-citizens">${citizenCards}</div>
      ${activePromises > 0 ? `<div class="ctx-promises">${activePromises} active promise${activePromises !== 1 ? 's' : ''}</div>` : ''}
    `;
  }

  show(): void {
    this.el.classList.add('visible');
    this.textarea.value = '';
    this.submitBtn.disabled = false;
    this.submitBtn.textContent = 'Deliver Speech';
    this.submitBtn.classList.remove('success', 'loading');
    this.endRoundBtn.style.display = 'none';
    this.errorDiv.style.display = 'none';
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
