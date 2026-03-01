import Phaser from 'phaser';
import {
  TILE_SIZE, TILE_TYPES, MULTI_TILE_SIZES,
  TILE_ASSETS, initTileSize,
} from '../config.ts';
import { WATER_TRANSITION_ASSETS } from '../objects/WaterTransitions.ts';
import { CITY_TEXTURE_KEYS } from '../objects/CityTransitions.ts';

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

  }

  async create(): Promise<void> {
    const { width, height } = this.scale;
    initTileSize(width, height);

    await this.loadFont();
    this.generateFallbackTextures();
    this.generateCityTextures();
    this.generateCursorTexture();
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

  /** Generate 12 city-border overlay textures (thin dark lines at edges) */
  private generateCityTextures(): void {
    const BORDER_COLOR = 0x4B4340;
    const BORDER_ALPHA = 0.85;
    const LINE_W = Math.max(1, Math.round(TILE_SIZE * 0.04));

    for (const key of CITY_TEXTURE_KEYS) {
      const gfx = this.add.graphics();
      const ts = TILE_SIZE;

      gfx.fillStyle(BORDER_COLOR, BORDER_ALPHA);

      if (key.includes('_edge_')) {
        const dir = key.slice(-1);
        if (dir === 'n') gfx.fillRect(0, 0, ts, LINE_W);
        else if (dir === 's') gfx.fillRect(0, ts - LINE_W, ts, LINE_W);
        else if (dir === 'w') gfx.fillRect(0, 0, LINE_W, ts);
        else if (dir === 'e') gfx.fillRect(ts - LINE_W, 0, LINE_W, ts);
      } else if (key.includes('_inner_')) {
        const corner = key.slice(-2);
        // Two lines meeting at a corner
        if (corner.includes('n')) gfx.fillRect(0, 0, ts, LINE_W);
        else gfx.fillRect(0, ts - LINE_W, ts, LINE_W);
        if (corner.includes('w')) gfx.fillRect(0, 0, LINE_W, ts);
        else gfx.fillRect(ts - LINE_W, 0, LINE_W, ts);
      } else {
        // Outer corner — small L-shaped notch
        const corner = key.slice(-2);
        const notch = Math.max(2, Math.round(TILE_SIZE * 0.08));
        if (corner === 'ne') {
          gfx.fillRect(ts - notch, 0, notch, LINE_W);
          gfx.fillRect(ts - LINE_W, 0, LINE_W, notch);
        } else if (corner === 'nw') {
          gfx.fillRect(0, 0, notch, LINE_W);
          gfx.fillRect(0, 0, LINE_W, notch);
        } else if (corner === 'se') {
          gfx.fillRect(ts - notch, ts - LINE_W, notch, LINE_W);
          gfx.fillRect(ts - LINE_W, ts - notch, LINE_W, notch);
        } else if (corner === 'sw') {
          gfx.fillRect(0, ts - LINE_W, notch, LINE_W);
          gfx.fillRect(0, ts - notch, LINE_W, notch);
        }
      }

      gfx.generateTexture(key, ts, ts);
      gfx.destroy();
    }
  }

  private generateCursorTexture(): void {
    const gfx = this.add.graphics();
    gfx.lineStyle(2, 0x000000, 1);
    gfx.strokeRect(0, 0, TILE_SIZE, TILE_SIZE);
    gfx.generateTexture('tile_cursor', TILE_SIZE, TILE_SIZE);
    gfx.destroy();
  }
}
