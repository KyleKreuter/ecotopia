import Phaser from 'phaser';
import { TILE_SIZE } from '../config.ts';
import type { TileGrid } from './TileGrid.ts';

export class ParticleEffects {
  private scene: Phaser.Scene;
  private grid: TileGrid;

  constructor(scene: Phaser.Scene, grid: TileGrid) {
    this.scene = scene;
    this.grid = grid;
    this.createParticleTextures();
  }

  private createParticleTextures(): void {
    if (!this.scene.textures.exists('particle')) {
      const gfx = this.scene.add.graphics();
      gfx.fillStyle(0x000000, 1);
      gfx.fillRect(0, 0, 4, 4);
      gfx.generateTexture('particle', 4, 4);
      gfx.destroy();
    }
  }

  burstAt(gridX: number, gridY: number, color: number, count = 12): void {
    const pos = this.grid.gridToScreen(gridX, gridY);
    const px = pos.x + TILE_SIZE / 2;
    const py = pos.y + TILE_SIZE / 2;

    const emitter = this.scene.add.particles(px, py, 'particle', {
      speed: { min: 30, max: 80 },
      angle: { min: 0, max: 360 },
      scale: { start: 1, end: 0 },
      lifespan: 500,
      quantity: count,
      tint: color,
      emitting: false,
    });

    emitter.explode(count);
    this.scene.time.delayedCall(600, () => emitter.destroy());
  }

  demolish(gridX: number, gridY: number): void {
    this.burstAt(gridX, gridY, 0x666666, 16);
  }

  build(gridX: number, gridY: number): void {
    this.burstAt(gridX, gridY, 0x000000, 10);
  }

  nature(gridX: number, gridY: number): void {
    this.burstAt(gridX, gridY, 0x333333, 8);
  }
}
