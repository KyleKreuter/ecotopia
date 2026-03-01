import type { GameStateResponse } from '../types/backend.ts';

export class ResourcePanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'resource-panel';
    this.el.innerHTML = `
      <div class="round-info">Round <span class="round-num">1</span>/7</div>
      <div class="resources">
        <div class="resource-bar ecology">
          <span class="bar-label">ECO</span>
          <div class="bar-track"><div class="bar-fill" style="width: 50%"></div></div>
          <span class="bar-value">50</span>
        </div>
        <div class="resource-bar economy">
          <span class="bar-label">ECON</span>
          <div class="bar-track"><div class="bar-fill" style="width: 50%"></div></div>
          <span class="bar-value">50</span>
        </div>
        <div class="resource-bar research">
          <span class="bar-label">RES</span>
          <div class="bar-track"><div class="bar-fill" style="width: 50%"></div></div>
          <span class="bar-value">50</span>
        </div>
      </div>
      <div class="actions-info">Actions: <span class="actions-num">2</span></div>
    `;
    parent.appendChild(this.el);
  }

  update(state: GameStateResponse): void {
    const roundEl = this.el.querySelector('.round-num');
    if (roundEl) roundEl.textContent = String(state.currentRound);

    const actionsEl = this.el.querySelector('.actions-num');
    if (actionsEl) actionsEl.textContent = String(state.currentRoundInfo.remainingActions);

    this.updateBar('ecology', state.resources.ecology);
    this.updateBar('economy', state.resources.economy);
    this.updateBar('research', state.resources.research);
  }

  private updateBar(type: string, value: number): void {
    const bar = this.el.querySelector(`.resource-bar.${type}`);
    if (!bar) return;
    const fill = bar.querySelector('.bar-fill') as HTMLElement;
    const valEl = bar.querySelector('.bar-value');
    if (fill) fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
    if (valEl) valEl.textContent = String(value);
  }

  destroy(): void {
    this.el.remove();
  }
}
