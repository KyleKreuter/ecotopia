import Phaser from 'phaser';
import { TILE_SIZE } from '../config.ts';
import type { OverlaySpec } from './WaterTransitions.ts';

export class TileSprite extends Phaser.GameObjects.Container {
  public gridX: number;
  public gridY: number;
  public tileType: string;

  private bg: Phaser.GameObjects.Image;
  private waterOverlays: Phaser.GameObjects.Image[] = [];

  constructor(scene: Phaser.Scene, gridX: number, gridY: number, tileType: string) {
    const px = gridX * TILE_SIZE;
    const py = gridY * TILE_SIZE;
    super(scene, px, py);

    this.gridX = gridX;
    this.gridY = gridY;
    this.tileType = tileType;

    // Create the background image (will be configured by applyTexture)
    this.bg = scene.add.image(TILE_SIZE / 2, TILE_SIZE / 2, '__DEFAULT');
    this.bg.setDisplaySize(TILE_SIZE, TILE_SIZE);
    this.add(this.bg);

    this.applyTexture(tileType);

    this.setSize(TILE_SIZE, TILE_SIZE);
    this.setInteractive(new Phaser.Geom.Rectangle(0, 0, TILE_SIZE, TILE_SIZE), Phaser.Geom.Rectangle.Contains);

    scene.add.existing(this);
  }

  setTileType(newType: string): void {
    if (newType === this.tileType) return;
    this.tileType = newType;

    this.applyTexture(newType);
    this.clearWaterOverlays();
  }

  flash(duration = 300): void {
    this.scene.tweens.add({
      targets: this.bg,
      alpha: { from: 0.3, to: 1 },
      duration,
      ease: 'Cubic.easeOut',
    });
  }

  setHiddenByMultiTile(hidden: boolean): void {
    this.bg.setVisible(!hidden);
  }

  clearWaterOverlays(): void {
    for (const ov of this.waterOverlays) ov.destroy();
    this.waterOverlays = [];
  }

  applyWaterOverlays(specs: OverlaySpec[]): void {
    this.clearWaterOverlays();
    const POLLUTED_TINT = 0x99AA77;

    for (const spec of specs) {
      if (!this.scene.textures.exists(spec.key)) continue;

      const img = this.scene.add.image(TILE_SIZE / 2, TILE_SIZE / 2, spec.key);
      img.setDisplaySize(TILE_SIZE, TILE_SIZE);

      if (spec.tintPolluted) {
        img.setTint(POLLUTED_TINT);
      }

      this.add(img);
      this.waterOverlays.push(img);
    }
  }

  private applyTexture(type: string): void {
    const svgKey = `svg_${type}`;

    if (this.scene.textures.exists(svgKey)) {
      this.bg.setTexture(svgKey);
      this.bg.setDisplaySize(TILE_SIZE, TILE_SIZE);
      this.bg.clearTint();
    } else {
      // Fallback to generated color rect
      const texKey = `tile_${type}`;
      const key = this.scene.textures.exists(texKey) ? texKey : 'tile_EMPTY';
      this.bg.setTexture(key);
      this.bg.setDisplaySize(TILE_SIZE, TILE_SIZE);
      this.bg.clearTint();
    }
  }
}
