import type { CitizenReactionResponse, CitizenResponse } from '../types/backend.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';
import { getPortraitPath } from './portraits.ts';

export class ReactionPopup {
  private el: HTMLElement;
  private reactions: CitizenReactionResponse[] = [];
  private citizens: CitizenResponse[] = [];
  private currentIndex = 0;

  constructor(parent: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'reaction-popup';
    parent.appendChild(this.el);
  }

  show(reactions: CitizenReactionResponse[], citizens: CitizenResponse[]): void {
    this.reactions = reactions;
    this.citizens = citizens;
    this.currentIndex = 0;

    if (reactions.length === 0) {
      eventBus.emit(GameEvents.REACTIONS_DONE);
      return;
    }

    this.render();
    this.el.classList.add('visible');
  }

  hide(): void {
    this.el.classList.remove('visible');
  }

  private render(): void {
    const reaction = this.reactions[this.currentIndex];
    const citizen = this.citizens.find(
      (c) => c.name.toLowerCase() === reaction.citizenName.toLowerCase()
    );
    const total = this.reactions.length;
    const isFirst = this.currentIndex === 0;
    const isLast = this.currentIndex === total - 1;

    const approval = citizen?.approval ?? 0;
    const delta = reaction.approvalDelta;
    const deltaClass = delta >= 0 ? 'positive' : 'negative';
    const deltaText = delta >= 0 ? `+${delta}` : `${delta}`;
    const portraitSrc = getPortraitPath(reaction.citizenName);

    this.el.innerHTML = `
      <div class="reaction-modal">
        <div class="reaction-header">
          <span>Citizen Reactions</span>
          <span class="reaction-page">${this.currentIndex + 1} / ${total}</span>
        </div>
        <div class="reaction-body">
          <div class="reaction-left">
            <img class="reaction-portrait" src="${portraitSrc}"
                 alt="${reaction.citizenName}"
                 onerror="this.style.display='none'" />
            <div class="reaction-name">${reaction.citizenName}</div>
            <div class="reaction-profession">${citizen?.profession ?? ''}</div>
            <div class="reaction-approval-section">
              <div class="reaction-approval-label">Approval:</div>
              <div class="reaction-bar-track">
                <div class="reaction-bar-fill" style="width:${Math.max(0, Math.min(100, approval))}%"></div>
              </div>
              <div class="reaction-approval-value">${approval}</div>
              <div class="approval-delta ${deltaClass}">(${deltaText})</div>
            </div>
          </div>
          <div class="reaction-right">
            <div class="reaction-dialogue">"${reaction.dialogue}"</div>
          </div>
        </div>
        <div class="reaction-nav">
          ${isFirst ? '' : '<button class="pixel-btn reaction-back">Back</button>'}
          <button class="pixel-btn reaction-next">${isLast ? 'End Round' : 'Next'}</button>
        </div>
      </div>
    `;

    const backBtn = this.el.querySelector('.reaction-back');
    const nextBtn = this.el.querySelector('.reaction-next')!;

    backBtn?.addEventListener('click', () => {
      this.currentIndex--;
      this.render();
    });

    nextBtn.addEventListener('click', () => {
      if (isLast) {
        this.hide();
        eventBus.emit(GameEvents.REACTIONS_DONE);
      } else {
        this.currentIndex++;
        this.render();
      }
    });
  }

  destroy(): void {
    this.el.remove();
  }
}
