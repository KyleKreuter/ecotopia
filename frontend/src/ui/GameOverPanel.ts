import type { GameStateResponse } from '../types/backend.ts';

/** Rank display metadata. */
const RANK_INFO: Record<string, { title: string; description: string }> = {
  BRONZE: { title: 'Survivor', description: 'Your city endured, but barely.' },
  SILVER: { title: 'Reformer', description: 'You built a better future for your citizens.' },
  GOLD: { title: 'Ecotopia', description: 'A perfect balance of nature, economy, and progress!' },
};

/** Defeat reason display text. */
const DEFEAT_REASONS: Record<string, string> = {
  ECOLOGICAL_COLLAPSE: "Your city's ecosystem collapsed",
  ECONOMIC_COLLAPSE: 'Famine struck your city',
  VOTED_OUT: 'Citizens voted you out',
};

/** Build an HTML bar for a resource value (0-100). */
function resourceBar(label: string, value: number, color: string): string {
  const pct = Math.max(0, Math.min(100, value));
  return `
    <div class="go-resource">
      <span class="go-resource-label">${label}</span>
      <div class="go-bar-track">
        <div class="go-bar-fill" style="width:${pct}%;background:${color}"></div>
      </div>
      <span class="go-resource-val">${value}</span>
    </div>`;
}

export class GameOverPanel {
  private el: HTMLElement;

  constructor(state: GameStateResponse, onPlayAgain: () => void) {
    this.el = document.createElement('div');
    this.el.className = 'gameover-panel';

    const isVictory = state.status === 'WON' || state.status === 'VICTORY' || state.resultRank !== null;
    const icon = isVictory ? '🏆' : '💀';
    const heading = isVictory ? 'Victory!' : 'Game Over';

    // Rank or defeat reason subtitle
    let subtitle = '';
    if (isVictory && state.resultRank) {
      const info = RANK_INFO[state.resultRank] ?? { title: state.resultRank, description: '' };
      subtitle = `<div class="go-rank">${info.title}</div><div class="go-rank-desc">${info.description}</div>`;
    } else if (!isVictory && state.defeatReason) {
      const reason = DEFEAT_REASONS[state.defeatReason] ?? state.defeatReason;
      subtitle = `<div class="go-reason">${reason}</div>`;
    }

    // Resource bars
    const { ecology, economy, research } = state.resources;
    const bars = [
      resourceBar('Ecology', ecology, '#4ade80'),
      resourceBar('Economy', economy, '#facc15'),
      resourceBar('Research', research, '#60a5fa'),
    ].join('');

    // Citizen approvals
    const approvals = state.citizens.map(c =>
      `<span class="go-citizen" title="${c.citizenType}">${c.name}: ${c.approval}%</span>`
    ).join('');

    this.el.innerHTML = `
      <div class="go-icon">${icon}</div>
      <div class="result-title">${heading}</div>
      ${subtitle}
      <div class="go-round">Round ${state.currentRound} / 7</div>
      <div class="go-bars">${bars}</div>
      ${approvals ? `<div class="go-approvals"><div class="go-approvals-title">Citizen Approvals</div>${approvals}</div>` : ''}
      <button class="pixel-btn play-again">Play Again</button>
    `;

    document.getElementById('ui-overlay')?.appendChild(this.el);
    this.el.querySelector('.play-again')?.addEventListener('click', onPlayAgain);
  }

  destroy(): void {
    this.el.remove();
  }
}
