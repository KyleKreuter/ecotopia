import type { ContradictionResponse } from '../types/backend.ts';

/** Eye-catching alert banner for detected contradictions. */
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
        <div class="contradiction-icon">⚠</div>
        <div class="contradiction-content">
          <strong class="contradiction-title">Contradiction Detected</strong>
          <span class="contradiction-desc">${c.description}</span>
          <span class="contradiction-quote">
            "${c.speechQuote}" vs ${c.contradictingAction}
          </span>
        </div>
      `;
      this.parent.appendChild(alert);

      setTimeout(() => {
        alert.classList.add('fade-out');
        setTimeout(() => alert.remove(), 600);
      }, 5000);
    }
  }

  destroy(): void {
    this.parent.querySelectorAll('.contradiction-alert').forEach((el) => el.remove());
  }
}
