import type { CitizenReactionResponse } from '../types/backend.ts';

/** Displays citizen reactions after a speech with optional TTS audio playback. */
export class ReactionPanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'reaction-panel';
    parent.appendChild(this.el);
  }

  show(reactions: CitizenReactionResponse[]): void {
    if (!reactions || reactions.length === 0) {
      this.el.innerHTML = '';
      return;
    }

    this.el.innerHTML = `
      <h3>Citizen Reactions</h3>
      ${reactions.map((r) => this.renderReaction(r)).join('')}
    `;
    this.el.classList.add('visible');

    // Auto-play first audio after a short delay
    if (reactions.some((r) => r.audioBase64)) {
      setTimeout(() => this.playAudioSequence(reactions, 0), 500);
    }
  }

  hide(): void {
    this.el.classList.remove('visible');
    this.el.innerHTML = '';
  }

  private renderReaction(r: CitizenReactionResponse): string {
    const deltaClass = r.approvalDelta >= 0 ? 'positive' : 'negative';
    const deltaStr = r.approvalDelta >= 0 ? `+${r.approvalDelta}` : `${r.approvalDelta}`;
    const hasAudio = r.audioBase64 ? '🔊' : '';

    const avatarKey = r.citizenName.toLowerCase();
    return `
      <div class="reaction-entry reaction-${r.tone}">
        <div class="reaction-header">
          <img class="citizen-avatar" src="/assets/character/${avatarKey}.png" alt="${r.citizenName}" width="32" height="32">
          <span class="reaction-name">${r.citizenName} ${hasAudio}</span>
          <span class="reaction-delta ${deltaClass}">${deltaStr}</span>
        </div>
        <p class="reaction-dialogue">"${r.dialogue}"</p>
      </div>
    `;
  }

  private playAudioSequence(reactions: CitizenReactionResponse[], index: number): void {
    if (index >= reactions.length) return;

    const r = reactions[index];
    if (r.audioBase64) {
      const audio = new Audio(`data:audio/mpeg;base64,${r.audioBase64}`);
      audio.onended = () => this.playAudioSequence(reactions, index + 1);
      audio.onerror = () => this.playAudioSequence(reactions, index + 1);
      audio.play().catch(() => this.playAudioSequence(reactions, index + 1));
    } else {
      this.playAudioSequence(reactions, index + 1);
    }
  }

  destroy(): void {
    this.el.remove();
  }
}
