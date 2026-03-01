import type { ContradictionResponse } from '../types/backend.ts';

export class ContradictionAlert {
  private parent: HTMLElement;

  constructor(parent: HTMLElement) {
    this.parent = parent;
  }

  show(contradictions: ContradictionResponse[]): void {
    for (const c of contradictions) {
      const alert = document.createElement('div');
      alert.className = 'contradiction-alert';
      alert.innerHTML = `
        <strong>Contradiction Detected</strong><br/>
        <span style="margin-top:4px;display:block">${c.description}</span>
        <span style="font-size:7px;color:#666;display:block;margin-top:4px">
          "${c.speechQuote}" vs ${c.contradictingAction}
        </span>
      `;
      this.parent.appendChild(alert);

      setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.3s';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    }
  }

  destroy(): void {
    this.parent.querySelectorAll('.contradiction-alert').forEach((el) => el.remove());
  }
}
