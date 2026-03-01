import type { CitizenResponse } from '../types/backend.ts';

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

    this.el.innerHTML = core
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

    const avatarKey = this.avatarKey(c.name);
    return `
      <div class="citizen-entry${cls}">
        <img class="citizen-avatar" src="/assets/character/${avatarKey}.png" alt="${c.name}" width="32" height="32" onerror="this.style.display='none'">
        <span class="citizen-name">${label}</span>
        <div class="citizen-bar-track"><div class="citizen-bar-fill" style="width: ${pct}%"></div></div>
        <span class="citizen-value">${c.approval}</span>
      </div>
    `;
  }

  destroy(): void {
    this.el.remove();
  }
}
