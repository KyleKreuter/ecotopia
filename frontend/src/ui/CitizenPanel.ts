import type { CitizenResponse } from '../types/backend.ts';

export class CitizenPanel {
  private el: HTMLElement;
  private listEl!: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'citizen-panel';
    this.el.innerHTML = '<div class="panel-header">Citizens</div><div class="citizen-list"></div>';
    parent.appendChild(this.el);
    this.listEl = this.el.querySelector('.citizen-list')!;
  }

  update(citizens: CitizenResponse[]): void {
    const core = citizens.filter((c) => c.citizenType === 'CORE');
    const dynamic = citizens.filter((c) => c.citizenType === 'DYNAMIC');

    this.listEl.innerHTML = core
      .map((c) => this.renderCitizen(c))
      .concat(dynamic.map((c) => this.renderCitizen(c, true)))
      .join('');
  }

  /** Extract the base name for avatar lookup (handles prefixes like "Dr."). */
  private avatarKey(name: string): string {
    const parts = name.toLowerCase().split(/[\s.]+/).filter(Boolean);
    return parts[parts.length - 1];
  }

  /** Briefly add 'reacting' class to a citizen's avatar to trigger shake animation. */
  triggerReaction(citizenName: string): void {
    const avatarKey = this.avatarKey(citizenName);
    const img = this.el.querySelector(
      `img.citizen-avatar[alt="${citizenName}"]`,
    ) as HTMLElement | null;
    if (!img) return;
    img.classList.add('reacting');
    setTimeout(() => img.classList.remove('reacting'), 1000);
  }

  private renderCitizen(c: CitizenResponse, isDynamic = false): string {
    const pct = Math.max(0, Math.min(100, c.approval));
    const label = isDynamic ? `${c.name} (${c.remainingRounds}r)` : c.name;
    const cls = pct < 25 ? ' critical' : '';
    const approvalColor = pct >= 60 ? '#2ecc71' : pct >= 35 ? '#f39c12' : '#e74c3c';
    const profession = c.profession || '';
    const personality = c.personality ? c.personality.split('.')[0] + '.' : '';

    const avatarKey = this.avatarKey(c.name);
    return `
      <div class="citizen-entry${cls}">
        <img class="citizen-avatar" src="/assets/character/${avatarKey}.png" alt="${c.name}" width="48" height="48" onerror="this.style.display='none'">
        <div class="citizen-info">
          <div class="citizen-header">
            <span class="citizen-name">${label}</span>
            <span class="citizen-value" style="color:${approvalColor}">${c.approval}%</span>
          </div>
          <div class="citizen-profession">${profession}${c.age ? ', ' + c.age : ''}</div>
          <div class="citizen-bar-track"><div class="citizen-bar-fill" style="width: ${pct}%; background: ${approvalColor}"></div></div>
          ${personality ? `<div class="citizen-personality">${personality}</div>` : ''}
        </div>
      </div>
    `;
  }

  destroy(): void {
    this.el.remove();
  }
}
