import type { CitizenResponse, CitizenReactionResponse } from '../types/backend.ts';

export class CitizenPanel {
  private el: HTMLElement;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'citizen-panel';
    this.el.innerHTML = '<h3>Citizens</h3><div class="citizen-list"></div>';
    parent.appendChild(this.el);
  }

  update(citizens: CitizenResponse[]): void {
    const list = this.el.querySelector('.citizen-list')!;
    list.innerHTML = '';

    for (const c of citizens) {
      const card = document.createElement('div');
      card.className = 'citizen-card';
      card.dataset.citizenName = c.name;
      card.innerHTML = `
        <div class="citizen-name">${c.name}</div>
        <div class="citizen-profession">${c.profession} · ${c.citizenType}</div>
        <div class="approval-bar">
          <div class="approval-fill" style="width: ${c.approval}%"></div>
        </div>
        <div class="citizen-dialogue">${c.openingSpeech || ''}</div>
      `;
      list.appendChild(card);
    }
  }

  showReactions(reactions: CitizenReactionResponse[]): void {
    for (const r of reactions) {
      const card = this.el.querySelector(`[data-citizen-name="${r.citizenName}"]`);
      if (!card) continue;

      const dialogueEl = card.querySelector('.citizen-dialogue');
      if (dialogueEl) {
        this.typewriterEffect(dialogueEl as HTMLElement, r.dialogue);
      }

      const delta = r.approvalDelta;
      const deltaText = document.createElement('span');
      deltaText.style.cssText = 'font-size:7px;margin-left:4px;';
      deltaText.textContent = `${delta >= 0 ? '+' : ''}${delta}`;
      card.querySelector('.citizen-profession')?.appendChild(deltaText);
      setTimeout(() => deltaText.remove(), 3000);
    }
  }

  private typewriterEffect(el: HTMLElement, text: string): void {
    el.textContent = '';
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        el.textContent += text[i];
        i++;
      } else {
        clearInterval(interval);
      }
    }, 25);
  }

  destroy(): void {
    this.el.remove();
  }
}
