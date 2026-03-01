import Phaser from 'phaser';
import {
  TILE_SIZE, TILE_TYPES, MULTI_TILE_SIZES,
  TILE_ASSETS, initTileSize,
} from '../config.ts';
import { WATER_TRANSITION_ASSETS } from '../objects/WaterTransitions.ts';

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' });
  }

  preload(): void {
    for (const [key, path] of Object.entries(TILE_ASSETS)) {
      this.load.image(`svg_${key}`, path);
    }
    for (const [key, path] of Object.entries(WATER_TRANSITION_ASSETS)) {
      this.load.image(key, path);
    }

    this.load.audio('soundtrack', [
      'soundtrack/Drifting Memories.ogg',
      'soundtrack/Drifting Memories.mp3',
    ]);

    const characters = ['karl', 'mia', 'sarah', 'bernd', 'henning', 'kerstin', 'lena', 'oleg', 'pavel', 'yuki'];
    for (const name of characters) {
      this.load.image(`char_${name}`, `/assets/character/${name}.png`);
    }
  }

  async create(): Promise<void> {
    const { width, height } = this.scale;
    initTileSize(width, height);

    await this.loadFont();
    this.generateFallbackTextures();
    this.generateCursorTexture();
    this.generateClickRingTexture();
    this.scene.start('TitleScene');
  }

  private async loadFont(): Promise<void> {
    const font = new FontFace('BitPotionExt', 'url(/font/BitPotionExt.ttf)');
    try {
      const loaded = await font.load();
      document.fonts.add(loaded);
    } catch {
      console.warn('Failed to load BitPotionExt font, falling back to monospace');
    }
  }

  /** Generate colored rectangle fallbacks for tiles without SVG assets */
  private generateFallbackTextures(): void {
    for (const [key, config] of Object.entries(TILE_TYPES)) {
      const multiSize = MULTI_TILE_SIZES[key];
      const w = multiSize ? multiSize.w * TILE_SIZE : TILE_SIZE;
      const h = multiSize ? multiSize.h * TILE_SIZE : TILE_SIZE;

      const gfx = this.add.graphics();
      gfx.fillStyle(config.color, 1);
      gfx.fillRect(0, 0, w, h);
      gfx.lineStyle(1, 0x000000, 0.4);
      gfx.strokeRect(0, 0, w, h);

      const texKey = multiSize ? `tile_multi_${key}` : `tile_${key}`;
      gfx.generateTexture(texKey, w, h);
      gfx.destroy();
    }
  }

  private generateClickRingTexture(): void {
    const radius = 12;
    const size = radius * 2 + 4;
    const gfx = this.add.graphics();
    gfx.lineStyle(2, 0x000000, 1);
    gfx.strokeCircle(size / 2, size / 2, radius);
    gfx.generateTexture('click_ring', size, size);
    gfx.destroy();
  }

  private generateCursorTexture(): void {
    const gfx = this.add.graphics();
    gfx.lineStyle(2, 0x000000, 1);
    gfx.strokeRect(0, 0, TILE_SIZE, TILE_SIZE);
    gfx.generateTexture('tile_cursor', TILE_SIZE, TILE_SIZE);
    gfx.destroy();
  }
}
