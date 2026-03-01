import type { GameStateResponse } from '../types/backend.ts';

export class GameOverPanel {
  private el: HTMLElement;

  constructor(state: GameStateResponse, onPlayAgain: () => void) {
    this.el = document.createElement('div');
    this.el.className = 'gameover-panel';

    const isVictory = state.status === 'VICTORY' || state.resultRank !== null;
    const titleText = isVictory ? 'VICTORY' : 'DEFEAT';

    const rankText = state.resultRank
      ? `${state.resultRank} Rank`
      : '';

    const reasonText = state.defeatReason ?? '';

    this.el.innerHTML = `
      <div class="result-title">${titleText}</div>
      ${rankText ? `<div class="result-rank">${rankText}</div>` : ''}
      ${reasonText ? `<div class="result-rank">${reasonText}</div>` : ''}
      <div class="result-stats">
        Round ${state.currentRound} / 7<br/>
        Ecology: ${state.resources.ecology} | Economy: ${state.resources.economy} | Research: ${state.resources.research}<br/>
        Citizens: ${state.citizens.length}
      </div>
      <button class="pixel-btn play-again">Play Again</button>
    `;

    document.getElementById('ui-overlay')?.appendChild(this.el);

    this.el.querySelector('.play-again')?.addEventListener('click', onPlayAgain);
  }

  destroy(): void {
    this.el.remove();
  }
}
