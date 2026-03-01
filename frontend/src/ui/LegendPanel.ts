import type { GameStateResponse } from '../types/backend.ts';

interface LegendEntry {
  label: string;
  asset: string;
  threshold: number;
  resource: 'research';
}

const TECH_MILESTONES: LegendEntry[] = [
  { label: 'Carbon Capture', asset: 'carbon_capture', threshold: 35, resource: 'research' },
  { label: 'Solar Field',    asset: 'solar_field',     threshold: 40, resource: 'research' },
  { label: 'Fusion Reactor', asset: 'fusion_reactor',  threshold: 80, resource: 'research' },
];

export class LegendPanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'legend-panel';
    this.el.innerHTML = this.buildHTML(0);
    parent.appendChild(this.el);
  }

  private buildHTML(research: number): string {
    const rows = TECH_MILESTONES.map(m => {
      const unlocked = research >= m.threshold;
      const cls = unlocked ? 'legend-entry unlocked' : 'legend-entry locked';
      return `
        <div class="${cls}">
          <img class="legend-icon" src="/assets/tiles/${m.asset}.png" alt="${m.label}" />
          <div class="legend-info">
            <span class="legend-label">${m.label}</span>
            <span class="legend-threshold">${unlocked ? 'Unlocked' : `RES ${m.threshold}%`}</span>
          </div>
        </div>`;
    }).join('');

    return `<h3 class="legend-title">Tech Tree</h3>${rows}`;
  }

  update(state: GameStateResponse): void {
    this.el.innerHTML = this.buildHTML(state.resources.research);
  }

  destroy(): void {
    this.el.remove();
  }
}
