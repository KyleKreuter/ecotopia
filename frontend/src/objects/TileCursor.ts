import Phaser from 'phaser';
import type { TileGrid } from './TileGrid.ts';

export class TileCursor {
  private cursor: Phaser.GameObjects.Image;
  private grid: TileGrid;
  private currentX = -1;
  private currentY = -1;

  constructor(scene: Phaser.Scene, grid: TileGrid) {
    this.grid = grid;
    this.cursor = scene.add.image(0, 0, 'tile_cursor')
      .setOrigin(0)
      .setVisible(false)
      .setDepth(100);

    scene.tweens.add({
      targets: this.cursor,
      alpha: { from: 1, to: 0.4 },
      duration: 600,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });
  }

  show(gridX: number, gridY: number): void {
    if (gridX === this.currentX && gridY === this.currentY) return;
    this.currentX = gridX;
    this.currentY = gridY;
    const pos = this.grid.gridToScreen(gridX, gridY);
    this.cursor.setPosition(pos.x, pos.y);
    this.cursor.setVisible(true);
  }

  hide(): void {
    this.cursor.setVisible(false);
    this.currentX = -1;
    this.currentY = -1;
  }

  getPosition(): { x: number; y: number } {
    return { x: this.currentX, y: this.currentY };
  }
}
