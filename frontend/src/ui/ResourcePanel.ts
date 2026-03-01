import type { GameStateResponse } from '../types/backend.ts';

export class ResourcePanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'resource-panel';
    this.el.innerHTML = `
      <div class="panel-header">Resources</div>
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
      <div class="tech-tree">
        <span class="tech-label">TECH</span>
        <div class="tech-track">
          <div class="tech-fill" style="width: 5%"></div>
          <div class="tech-marker solar" style="left: 40%"><span class="tech-icon solar">S</span></div>
          <div class="tech-marker fusion" style="left: 80%"><span class="tech-icon fusion">F</span></div>
        </div>
      </div>
    <div class="sidebar-divider"></div>
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

    // Update tech tree
    const techFill = this.el.querySelector('.tech-fill') as HTMLElement;
    if (techFill) techFill.style.width = `${state.resources.research}%`;
    const solarMarker = this.el.querySelector('.tech-marker.solar') as HTMLElement;
    if (solarMarker) solarMarker.classList.toggle('unlocked', state.resources.research >= 40);
    const fusionMarker = this.el.querySelector('.tech-marker.fusion') as HTMLElement;
    if (fusionMarker) fusionMarker.classList.toggle('unlocked', state.resources.research >= 80);

    // Color code resource bars based on danger
    this.updateBarDanger('ecology', state.resources.ecology);
    this.updateBarDanger('economy', state.resources.economy);
  }

  private updateBar(type: string, value: number): void {
    const bar = this.el.querySelector(`.resource-bar.${type}`);
    if (!bar) return;
    const fill = bar.querySelector('.bar-fill') as HTMLElement;
    const valEl = bar.querySelector('.bar-value');
    if (fill) fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
    if (valEl) valEl.textContent = String(value);
  }

  private updateBarDanger(type: string, value: number): void {
    const bar = this.el.querySelector(`.resource-bar.${type}`) as HTMLElement;
    if (!bar) return;
    bar.classList.toggle('danger', value < 25);
    bar.classList.toggle('warning', value >= 25 && value < 40);
  }

  destroy(): void {
    this.el.remove();
  }
}
