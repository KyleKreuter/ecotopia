import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

interface TutorialStep {
  title: string;
  text: string;
  highlight?: string;
  position: 'center' | 'top' | 'bottom' | 'right';
}

const STEPS: TutorialStep[] = [
  {
    title: 'Welcome, Mayor',
    text: 'You have been elected to lead Ecotopia through an environmental crisis. Your decisions will shape the future of this town.',
    position: 'center'
  },
  {
    title: 'Your Resources',
    text: 'Keep Ecology, Economy, and Research balanced. If any resource drops to zero, your town collapses.',
    highlight: '.resource-panel',
    position: 'top'
  },
  {
    title: 'Your Citizens',
    text: 'Each citizen has their own personality and priorities. Keep their approval high or face opposition.',
    highlight: '.citizen-panel',
    position: 'right'
  },
  {
    title: 'Take Action',
    text: 'Click on map tiles to build factories, plant forests, or develop research labs. You have 2 actions per round.',
    position: 'center'
  },
  {
    title: 'Deliver Your Speech',
    text: 'After your actions, address your citizens. Make promises, explain your vision. They will react based on your words and deeds.',
    position: 'center'
  },
  {
    title: 'Good Luck',
    text: 'Survive 7 rounds. Balance progress with nature. Keep your promises. The fate of Ecotopia is in your hands.',
    position: 'center'
  }
];

export class TutorialOverlay {
  private el: HTMLElement;
  private currentStep = 0;
  private onComplete: () => void;

  constructor(parent: HTMLElement, onComplete: () => void) {
    this.onComplete = onComplete;
    this.el = document.createElement('div');
    this.el.className = 'tutorial-overlay';
    parent.appendChild(this.el);
    this.render();
  }

  private render(): void {
    const step = STEPS[this.currentStep];
    const isLast = this.currentStep === STEPS.length - 1;
    const progress = STEPS.map((_, i) =>
      `<span class="tutorial-dot${i === this.currentStep ? ' active' : ''}"></span>`
    ).join('');

    this.el.innerHTML = `
      <div class="tutorial-backdrop"></div>
      <div class="tutorial-card tutorial-${step.position}">
        <div class="tutorial-step-indicator">${this.currentStep + 1} / ${STEPS.length}</div>
        <h3 class="tutorial-title">${step.title}</h3>
        <p class="tutorial-text">${step.text}</p>
        <div class="tutorial-dots">${progress}</div>
        <div class="tutorial-actions">
          ${this.currentStep > 0 ? '<button class="pixel-btn tutorial-back">Back</button>' : ''}
          <button class="pixel-btn tutorial-next">${isLast ? 'Start Game' : 'Next'}</button>
          ${!isLast ? '<button class="tutorial-skip">Skip Tutorial</button>' : ''}
        </div>
      </div>
    `;

    if (step.highlight) {
      const highlighted = document.querySelector(step.highlight) as HTMLElement;
      if (highlighted) {
        highlighted.classList.add('tutorial-highlighted');
      }
    }

    const nextBtn = this.el.querySelector('.tutorial-next');
    nextBtn?.addEventListener('click', () => this.next());

    const backBtn = this.el.querySelector('.tutorial-back');
    backBtn?.addEventListener('click', () => this.back());

    const skipBtn = this.el.querySelector('.tutorial-skip');
    skipBtn?.addEventListener('click', () => this.complete());
  }

  private clearHighlights(): void {
    document.querySelectorAll('.tutorial-highlighted').forEach(el => {
      el.classList.remove('tutorial-highlighted');
    });
  }

  private next(): void {
    this.clearHighlights();
    if (this.currentStep >= STEPS.length - 1) {
      this.complete();
      return;
    }
    this.currentStep++;
    this.render();
  }

  private back(): void {
    this.clearHighlights();
    if (this.currentStep > 0) {
      this.currentStep--;
      this.render();
    }
  }

  private complete(): void {
    this.clearHighlights();
    this.el.remove();
    this.onComplete();
  }

  destroy(): void {
    this.clearHighlights();
    this.el.remove();
  }
}
