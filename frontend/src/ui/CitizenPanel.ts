import type { CitizenResponse } from '../types/backend.ts';
import { getPortraitPath } from './portraits.ts';

export class CitizenPanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'citizen-panel';
    parent.appendChild(this.el);
  }

  update(citizens: CitizenResponse[]): void {
    const core = citizens.filter((c) => c.citizenType === 'CORE');
    const dynamic = citizens.filter((c) => c.citizenType === 'DYNAMIC');

    let html = '<div class="citizen-panel-title">Citizens</div>';
    html += core.map((c) => this.renderCitizen(c)).join('');

    if (dynamic.length > 0) {
      html += '<div class="citizen-separator"></div>';
      html += dynamic.map((c) => this.renderCitizen(c, true)).join('');
    }

    this.el.innerHTML = html;
  }

  private renderCitizen(c: CitizenResponse, isDynamic = false): string {
    const pct = Math.max(0, Math.min(100, c.approval));
    const cls = pct < 25 ? ' critical' : '';
    const portraitSrc = getPortraitPath(c.name);
    const roundsBadge =
      isDynamic && c.remainingRounds != null
        ? ` <span class="citizen-rounds">${c.remainingRounds}r</span>`
        : '';
    const tooltipText = c.personality ? c.personality.split('.')[0] + '.' : '';

    return `
      <div class="citizen-entry${cls}" title="${this.escapeAttr(tooltipText)}">
        <img class="citizen-portrait"
             src="${portraitSrc}"
             alt="${c.name}"
             onerror="this.style.visibility='hidden'" />
        <div class="citizen-info">
          <div class="citizen-header">
            <span class="citizen-name">${c.name}${roundsBadge}</span>
            <span class="citizen-value">${c.approval}</span>
          </div>
          <div class="citizen-profession">${c.profession}</div>
          <div class="citizen-bar-track">
            <div class="citizen-bar-fill" style="width: ${pct}%"></div>
          </div>
        </div>
      </div>
    `;
  }

  private escapeAttr(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  destroy(): void {
    this.el.remove();
  }
}
