import type { PromiseResponse } from '../types/backend.ts';

export class PromisePanel {
  private el: HTMLElement;
  private list!: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'promise-panel';
    this.el.innerHTML = '<h3>Promises</h3><div class="promise-list"></div>';
    parent.appendChild(this.el);
    this.list = this.el.querySelector('.promise-list')!;
  }

  update(promises: PromiseResponse[]): void {
    if (promises.length === 0) {
      this.el.classList.remove('visible');
      return;
    }

    this.el.classList.add('visible');
    this.list.innerHTML = '';

    for (const p of promises) {
      const statusClass = p.status.toLowerCase();
      const item = document.createElement('div');
      item.className = `promise-item ${statusClass}`;
      item.textContent = `R${p.roundMade}: ${p.text}`;
      if (p.deadline) {
        item.textContent += ` (by R${p.deadline})`;
      }
      this.list.appendChild(item);
    }
  }

  destroy(): void {
    this.el.remove();
  }
}
