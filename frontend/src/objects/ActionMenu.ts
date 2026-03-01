import Phaser from 'phaser';
import { TILE_SIZE, ACTION_LABELS } from '../config.ts';
import type { TileActionType } from '../types/backend.ts';
import type { TileGrid } from './TileGrid.ts';

export class ActionMenu {
  private scene: Phaser.Scene;
  private grid: TileGrid;
  private container: Phaser.GameObjects.Container;
  private isVisible = false;
  private onSelect: ((action: TileActionType) => void) | null = null;
  private hitArea: Phaser.Geom.Rectangle = new Phaser.Geom.Rectangle();

  constructor(scene: Phaser.Scene, grid: TileGrid) {
    this.scene = scene;
    this.grid = grid;
    this.container = scene.add.container(0, 0).setDepth(200).setVisible(false);
  }

  show(gridX: number, gridY: number, actions: string[], onSelect: (action: TileActionType) => void): void {
    this.hide();
    this.onSelect = onSelect;

    const pos = this.grid.gridToScreen(gridX, gridY);
    const px = pos.x;
    const py = pos.y + TILE_SIZE + 4;

    const itemHeight = 24;
    const menuWidth = 220;
    const menuHeight = actions.length * itemHeight + 8;

    const bg = this.scene.add.graphics();
    bg.fillStyle(0xffffff, 0.95);
    bg.fillRect(0, 0, menuWidth, menuHeight);
    bg.lineStyle(1, 0x000000, 1);
    bg.strokeRect(0, 0, menuWidth, menuHeight);
    this.container.add(bg);

    actions.forEach((action, i) => {
      const label = ACTION_LABELS[action] ?? action;
      const text = this.scene.add.text(8, 4 + i * itemHeight, label, {
        fontFamily: 'monospace',
        fontSize: '8px',
        color: '#000000',
      }).setInteractive({ useHandCursor: true });

      text.on('pointerover', () => text.setColor('#666666'));
      text.on('pointerout', () => text.setColor('#000000'));
      text.on('pointerup', () => {
        const cb = this.onSelect;
        this.hide();
        cb?.(action as TileActionType);
      });

      this.container.add(text);
    });

    let finalX = px;
    let finalY = py;
    const camWidth = this.scene.cameras.main.width;
    const camHeight = this.scene.cameras.main.height;

    if (finalX + menuWidth > camWidth) finalX = camWidth - menuWidth - 8;
    if (finalY + menuHeight > camHeight) finalY = pos.y - menuHeight - 4;

    this.container.setPosition(finalX, finalY);
    this.container.setVisible(true);
    this.isVisible = true;

    // Store hit area in screen space for contains-check
    this.hitArea.setTo(finalX, finalY, menuWidth, menuHeight);
  }

  /** Returns true if the screen point is inside the open menu */
  containsPoint(x: number, y: number): boolean {
    return this.isVisible && this.hitArea.contains(x, y);
  }

  hide(): void {
    this.container.removeAll(true);
    this.container.setVisible(false);
    this.isVisible = false;
    this.onSelect = null;
  }

  getVisible(): boolean {
    return this.isVisible;
  }
}
