type EditState = 'loading' | 'editable' | 'locked';

const OFFSET_X = 12;
const OFFSET_Y = 12;

export class TileTooltip {
  private el: HTMLDivElement;

  constructor() {
    this.el = document.createElement('div');
    this.el.className = 'tile-tooltip';
    this.el.style.display = 'none';
    document.getElementById('ui-overlay')?.appendChild(this.el);
  }

  show(screenX: number, screenY: number, label: string, editState: EditState): void {
    const icon = editState === 'loading' ? '…'
      : editState === 'editable' ? '✎'
      : '✕';

    this.el.innerHTML = `<span class="edit-icon">${icon}</span> ${label}`;
    this.el.className = `tile-tooltip ${editState}`;
    this.el.style.display = 'block';

    // Position with clamping
    const rect = this.el.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    let x = screenX + OFFSET_X;
    let y = screenY + OFFSET_Y;

    if (x + rect.width > vw) x = screenX - OFFSET_X - rect.width;
    if (y + rect.height > vh) y = screenY - OFFSET_Y - rect.height;

    this.el.style.left = `${Math.max(0, x)}px`;
    this.el.style.top = `${Math.max(0, y)}px`;
  }

  hide(): void {
    this.el.style.display = 'none';
  }

  destroy(): void {
    this.el.remove();
  }
}
