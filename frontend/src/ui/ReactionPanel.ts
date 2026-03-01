import type { CitizenReactionResponse } from '../types/backend.ts';

/** Displays citizen reactions after a speech with optional TTS audio playback. */
export class ReactionPanel {
  private el: HTMLElement;
  private currentAudio: HTMLAudioElement | null = null;
  private playingIndex: number = -1;

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

    const visible = reactions.slice(0, 5);

    this.el.innerHTML = `
      <h3>Citizen Reactions</h3>
      <div class="reaction-cards">
        ${visible.map((r, i) => this.renderReaction(r, i)).join('')}
      </div>
    `;
    this.el.classList.add('visible');

    if (reactions.some((r) => r.audioBase64)) {
      setTimeout(() => this.playAudioSequence(reactions, 0), 500);
    }
  }

  hide(): void {
    this.currentAudio?.pause();
    this.currentAudio = null;
    this.playingIndex = -1;
    this.el.classList.remove('visible');
    this.el.innerHTML = '';
  }

  private renderReaction(r: CitizenReactionResponse, index: number): string {
    const deltaClass = r.approvalDelta >= 0 ? 'positive' : 'negative';
    const deltaStr = r.approvalDelta >= 0 ? `+${r.approvalDelta}` : `${r.approvalDelta}`;
    const hasAudio = r.audioBase64
      ? `<span class="audio-icon" data-index="${index}">&#9835;</span>`
      : '';

    const parts = r.citizenName.toLowerCase().split(/[\s.]+/).filter(Boolean);
    const avatarKey = parts[parts.length - 1];
    const glowClass = r.approvalDelta >= 0 ? 'positive' : 'negative';

    const toneColors: Record<string, string> = {
      angry: '#e74c3c',
      suspicious: '#f39c12',
      hopeful: '#2ecc71',
      sarcastic: '#9b59b6',
    };
    const toneLabels: Record<string, string> = {
      angry: 'Angry',
      suspicious: 'Suspicious',
      hopeful: 'Hopeful',
      sarcastic: 'Sarcastic',
    };
    const dotColor = toneColors[r.tone] || '#888';
    const toneLabel = toneLabels[r.tone] || r.tone;

    return `
      <div class="reaction-card reaction-${r.tone}" style="animation-delay: ${index * 0.12}s">
        <div class="reaction-card-header">
          <img class="citizen-avatar reacting ${glowClass}"
               src="/assets/character/${avatarKey}.png"
               alt="${r.citizenName}" width="48" height="48">
          <div class="reaction-card-info">
            <span class="reaction-name">${r.citizenName} ${hasAudio}</span>
            <span class="reaction-tone" style="color:${dotColor}">
              <span class="reaction-tone-dot" style="background:${dotColor}"></span>
              ${toneLabel}
            </span>
          </div>
          <span class="reaction-delta ${deltaClass}">${deltaStr}</span>
        </div>
        <p class="reaction-dialogue">\u201C${r.dialogue}\u201D</p>
      </div>
    `;
  }

  private playAudioSequence(reactions: CitizenReactionResponse[], index: number): void {
    if (index >= reactions.length) {
      this.playingIndex = -1;
      this.updatePlayingIcon(-1);
      return;
    }

    const r = reactions[index];
    if (r.audioBase64) {
      this.playingIndex = index;
      this.updatePlayingIcon(index);
      const audio = new Audio(`data:audio/mpeg;base64,${r.audioBase64}`);
      this.currentAudio = audio;
      audio.onended = () => {
        this.currentAudio = null;
        this.playAudioSequence(reactions, index + 1);
      };
      audio.onerror = () => {
        this.currentAudio = null;
        this.playAudioSequence(reactions, index + 1);
      };
      audio.play().catch(() => {
        this.currentAudio = null;
        this.playAudioSequence(reactions, index + 1);
      });
    } else {
      this.playAudioSequence(reactions, index + 1);
    }
  }

  private updatePlayingIcon(activeIndex: number): void {
    this.el.querySelectorAll('.audio-icon').forEach((icon) => {
      const el = icon as HTMLElement;
      const idx = parseInt(el.dataset.index || '-1', 10);
      el.classList.toggle('playing', idx === activeIndex);
    });
  }

  destroy(): void {
    this.currentAudio?.pause();
    this.el.remove();
  }
}
