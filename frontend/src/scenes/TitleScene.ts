import Phaser from 'phaser';
import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

// --- Color palette ---
const BG_COLOR = 0x0A0E1A;
const BUILDING_COLORS = [0x0F1520, 0x111825, 0x131A28, 0x151D2B, 0x171F2E, 0x1A2030];
const WINDOW_COLORS = [0xFFD93D, 0xFFA500, 0xFFFBE6, 0xFFE066, 0xFFCC00];
const STREET_COLOR = 0x080B14;
const SPARKLE_COLORS = [0xFFFFFF, 0xFFFBE6, 0xFFE8A0];

// --- Layout ---
const STREET_WIDTH_MIN = 2;
const STREET_WIDTH_MAX = 4;
const BLOCK_GAP_MIN = 35;
const BLOCK_GAP_MAX = 90;

// --- Window lights ---
const WINDOW_COUNT_MIN = 250;
const WINDOW_COUNT_MAX = 450;
const WINDOW_BLINK_MIN = 2000;
const WINDOW_BLINK_MAX = 8000;

// --- Moving pixels ---
const MOVING_PIXEL_COUNT = 20;
const PIXEL_SPEED_MIN = 20;
const PIXEL_SPEED_MAX = 60;

// --- Sparkle ---
const SPARKLE_INTERVAL = 200;
const SPARKLE_DURATION = 400;

interface WindowLight {
  gfx: Phaser.GameObjects.Graphics;
  x: number;
  y: number;
  color: number;
  timer: Phaser.Time.TimerEvent;
  tween?: Phaser.Tweens.Tween;
}

interface MovingPixel {
  gfx: Phaser.GameObjects.Graphics;
  x: number;
  y: number;
  dx: number;
  dy: number;
  speed: number;
  color: number;
  road: { x: number; y: number; horizontal: boolean; length: number };
}

interface StreetSegment {
  x: number;
  y: number;
  width: number;
  height: number;
  horizontal: boolean;
}

interface BuildingBlock {
  x: number;
  y: number;
  width: number;
  height: number;
}

export class TitleScene extends Phaser.Scene {
  private windowLights: WindowLight[] = [];
  private movingPixels: MovingPixel[] = [];
  private sparkleTimer?: Phaser.Time.TimerEvent;
  private streets: StreetSegment[] = [];
  private buildings: BuildingBlock[] = [];

  private cityGraphics!: Phaser.GameObjects.Graphics;
  private overlay!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private subtitleText!: Phaser.GameObjects.Text;
  private btnText!: Phaser.GameObjects.Text;
  private versionText!: Phaser.GameObjects.Text;

  constructor() {
    super({ key: 'TitleScene' });
  }

  create(): void {
    const { width, height } = this.scale;

    this.cameras.main.setBackgroundColor(BG_COLOR);

    // Generate city
    this.generateCity(width, height);

    // Window lights
    this.createWindowLights(width, height);

    // Moving pixels on streets
    this.createMovingPixels();

    // Sparkle timer
    this.sparkleTimer = this.time.addEvent({
      delay: SPARKLE_INTERVAL,
      callback: () => this.spawnSparkle(width, height),
      loop: true,
    });

    // Overlay band
    this.overlay = this.add.graphics();
    this.overlay.setDepth(10);
    this.drawOverlay(width, height);

    // Title
    this.titleText = this.add.text(width / 2, height * 0.35, 'ECOTOPIA', {
      fontFamily: 'BitPotionExt, monospace',
      fontSize: '120px',
      color: '#FFFBF1',
      stroke: '#0A0E1A',
      strokeThickness: 6,
    }).setOrigin(0.5).setDepth(20);

    this.subtitleText = this.add.text(width / 2, height * 0.35 + 70, 'A Political Simulation', {
      fontFamily: 'BitPotionExt, monospace',
      fontSize: '24px',
      color: '#8899AA',
      stroke: '#0A0E1A',
      strokeThickness: 3,
    }).setOrigin(0.5).setDepth(20);

    this.btnText = this.add.text(width / 2, height * 0.7, '[ NEW GAME ]', {
      fontFamily: 'BitPotionExt, monospace',
      fontSize: '28px',
      color: '#FFFBF1',
      stroke: '#0A0E1A',
      strokeThickness: 3,
    }).setOrigin(0.5).setInteractive({ useHandCursor: true }).setDepth(20);

    this.btnText.on('pointerover', () => this.btnText.setColor('#FFD93D'));
    this.btnText.on('pointerout', () => this.btnText.setColor('#FFFBF1'));

    this.btnText.on('pointerdown', async () => {
      this.btnText.setText('LOADING...');
      this.btnText.disableInteractive();
      try {
        await gameState.createGame();
        this.scene.start('GameScene');
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        this.btnText.setText('ERROR - RETRY');
        this.btnText.setInteractive({ useHandCursor: true });
        eventBus.emit(GameEvents.ERROR, msg);
      }
    });

    this.versionText = this.add.text(width / 2, height - 30, 'v0.1.0', {
      fontFamily: 'BitPotionExt, monospace',
      fontSize: '8px',
      color: '#556677',
      stroke: '#0A0E1A',
      strokeThickness: 2,
    }).setOrigin(0.5).setDepth(20);

    // Soundtrack
    if (!this.sound.get('soundtrack')) {
      this.sound.add('soundtrack', { loop: true, volume: 0.3 }).play();
    }

    // Resize
    this.scale.on('resize', (gameSize: Phaser.Structs.Size) => {
      this.handleResize(gameSize.width, gameSize.height);
    });
  }

  update(_time: number, delta: number): void {
    const dt = delta / 1000;
    const { width, height } = this.scale;

    for (const pixel of this.movingPixels) {
      pixel.x += pixel.dx * pixel.speed * dt;
      pixel.y += pixel.dy * pixel.speed * dt;

      // Respawn at opposite end when leaving screen
      if (pixel.x < -5) pixel.x = width + 3;
      if (pixel.x > width + 5) pixel.x = -3;
      if (pixel.y < -5) pixel.y = height + 3;
      if (pixel.y > height + 5) pixel.y = -3;

      pixel.gfx.clear();
      pixel.gfx.fillStyle(pixel.color, 0.9);
      pixel.gfx.fillRect(Math.round(pixel.x), Math.round(pixel.y), 1, 1);
    }
  }

  // --------------- City generation ---------------

  private generateCity(width: number, height: number): void {
    this.streets = [];
    this.buildings = [];

    this.cityGraphics = this.add.graphics();
    this.cityGraphics.setDepth(0);

    // Generate horizontal streets with varying gaps
    const hStreets: StreetSegment[] = [];
    let y = Phaser.Math.Between(BLOCK_GAP_MIN, BLOCK_GAP_MAX);
    while (y < height - 20) {
      const sw = Phaser.Math.Between(STREET_WIDTH_MIN, STREET_WIDTH_MAX);
      // Some streets don't span the full width
      const startX = Math.random() < 0.3 ? Phaser.Math.Between(0, Math.floor(width * 0.3)) : 0;
      const endX = Math.random() < 0.3 ? Phaser.Math.Between(Math.floor(width * 0.7), width) : width;
      const seg: StreetSegment = { x: startX, y, width: endX - startX, height: sw, horizontal: true };
      hStreets.push(seg);
      this.streets.push(seg);
      y += Phaser.Math.Between(BLOCK_GAP_MIN, BLOCK_GAP_MAX);
    }

    // Generate vertical streets with varying gaps
    const vStreets: StreetSegment[] = [];
    let x = Phaser.Math.Between(BLOCK_GAP_MIN, BLOCK_GAP_MAX);
    while (x < width - 20) {
      const sw = Phaser.Math.Between(STREET_WIDTH_MIN, STREET_WIDTH_MAX);
      const startY = Math.random() < 0.3 ? Phaser.Math.Between(0, Math.floor(height * 0.3)) : 0;
      const endY = Math.random() < 0.3 ? Phaser.Math.Between(Math.floor(height * 0.7), height) : height;
      const seg: StreetSegment = { x, y: startY, width: sw, height: endY - startY, horizontal: false };
      vStreets.push(seg);
      this.streets.push(seg);
      x += Phaser.Math.Between(BLOCK_GAP_MIN, BLOCK_GAP_MAX);
    }

    // Draw streets
    this.cityGraphics.fillStyle(STREET_COLOR, 1);
    for (const s of this.streets) {
      this.cityGraphics.fillRect(s.x, s.y, s.width, s.height);
    }

    // Compute building blocks from gaps between streets
    const hEdges = [0, ...hStreets.map((s) => s.y), ...hStreets.map((s) => s.y + s.height), height].sort((a, b) => a - b);
    const vEdges = [0, ...vStreets.map((s) => s.x), ...vStreets.map((s) => s.x + s.width), width].sort((a, b) => a - b);

    for (let i = 0; i < vEdges.length - 1; i++) {
      for (let j = 0; j < hEdges.length - 1; j++) {
        const bx = vEdges[i];
        const by = hEdges[j];
        const bw = vEdges[i + 1] - bx;
        const bh = hEdges[j + 1] - by;

        if (bw < 4 || bh < 4) continue;

        // Skip if this area overlaps with a street
        const isStreet = this.streets.some((s) => {
          const ox = Math.max(bx, s.x);
          const oy = Math.max(by, s.y);
          const ow = Math.min(bx + bw, s.x + s.width) - ox;
          const oh = Math.min(by + bh, s.y + s.height) - oy;
          return ow > bw * 0.5 && oh > bh * 0.5;
        });
        if (isStreet) continue;

        const color = Phaser.Math.RND.pick(BUILDING_COLORS);
        this.cityGraphics.fillStyle(color, 1);
        this.cityGraphics.fillRect(bx, by, bw, bh);
        this.buildings.push({ x: bx, y: by, width: bw, height: bh });
      }
    }
  }

  // --------------- Window lights ---------------

  private createWindowLights(_width: number, _height: number): void {
    const count = Phaser.Math.Between(WINDOW_COUNT_MIN, WINDOW_COUNT_MAX);

    for (let i = 0; i < count; i++) {
      if (this.buildings.length === 0) break;

      const building = Phaser.Math.RND.pick(this.buildings);
      const wx = Phaser.Math.Between(building.x + 1, building.x + building.width - 2);
      const wy = Phaser.Math.Between(building.y + 1, building.y + building.height - 2);
      const color = Phaser.Math.RND.pick(WINDOW_COLORS);
      const initialAlpha = Math.random() < 0.4 ? 0 : Phaser.Math.FloatBetween(0.3, 1.0);

      const gfx = this.add.graphics();
      gfx.setDepth(5);
      gfx.fillStyle(color, initialAlpha);
      gfx.fillRect(wx, wy, 1, 1);

      const blinkDelay = Phaser.Math.Between(WINDOW_BLINK_MIN, WINDOW_BLINK_MAX);

      const light: WindowLight = {
        gfx, x: wx, y: wy, color,
        timer: this.time.addEvent({
          delay: blinkDelay,
          callback: () => this.blinkWindow(light),
          loop: true,
        }),
      };

      this.windowLights.push(light);
    }
  }

  private blinkWindow(light: WindowLight): void {
    light.tween?.destroy();

    const targetAlpha = Math.random() < 0.3 ? 0 : Phaser.Math.FloatBetween(0.4, 1.0);
    const duration = Phaser.Math.Between(400, 1200);

    // We can't tween graphics alpha directly per-fill, so we redraw
    const startAlpha = light.gfx.alpha;
    light.tween = this.tweens.add({
      targets: light.gfx,
      alpha: targetAlpha,
      duration,
      ease: 'Sine.easeInOut',
      onUpdate: () => {
        light.gfx.clear();
        light.gfx.fillStyle(light.color, 1);
        light.gfx.fillRect(light.x, light.y, 1, 1);
      },
    });
  }

  // --------------- Moving pixels ---------------

  private createMovingPixels(): void {
    if (this.streets.length === 0) return;

    for (let i = 0; i < MOVING_PIXEL_COUNT; i++) {
      const street = Phaser.Math.RND.pick(this.streets);
      const horizontal = street.horizontal;

      const isHeadlight = Math.random() < 0.5;
      const color = isHeadlight ? 0xFFFFFF : 0xFF3333;
      const speed = Phaser.Math.Between(PIXEL_SPEED_MIN, PIXEL_SPEED_MAX);
      const direction = Math.random() < 0.5 ? 1 : -1;

      let px: number, py: number, dx: number, dy: number;
      if (horizontal) {
        px = Phaser.Math.Between(street.x, street.x + street.width);
        py = street.y + Math.floor(street.height / 2);
        dx = direction;
        dy = 0;
      } else {
        px = street.x + Math.floor(street.width / 2);
        py = Phaser.Math.Between(street.y, street.y + street.height);
        dx = 0;
        dy = direction;
      }

      const gfx = this.add.graphics();
      gfx.setDepth(8);
      gfx.fillStyle(color, 0.9);
      gfx.fillRect(Math.round(px), Math.round(py), 1, 1);

      this.movingPixels.push({
        gfx, x: px, y: py, dx, dy, speed, color,
        road: {
          x: street.x, y: street.y,
          horizontal, length: horizontal ? street.width : street.height,
        },
      });
    }
  }

  // --------------- Sparkle ---------------

  private spawnSparkle(width: number, height: number): void {
    const sx = Phaser.Math.Between(0, width);
    const sy = Phaser.Math.Between(0, height);
    const color = Phaser.Math.RND.pick(SPARKLE_COLORS);

    const gfx = this.add.graphics();
    gfx.setDepth(9);
    gfx.setAlpha(0);
    gfx.fillStyle(color, 1);
    gfx.fillRect(sx, sy, 1, 1);

    this.tweens.add({
      targets: gfx,
      alpha: { from: 0, to: 0.8 },
      duration: SPARKLE_DURATION / 2,
      yoyo: true,
      ease: 'Sine.easeInOut',
      onComplete: () => gfx.destroy(),
    });
  }

  // --------------- Overlay + Layout ---------------

  private drawOverlay(width: number, height: number): void {
    this.overlay.clear();
    this.overlay.fillStyle(BG_COLOR, 0.70);
    const bandH = height * 0.58;
    const bandY = height * 0.18;
    this.overlay.fillRect(0, bandY, width, bandH);
  }

  private handleResize(width: number, height: number): void {
    // Rebuild city for new dimensions
    this.cleanupCity();
    this.generateCity(width, height);
    this.createWindowLights(width, height);
    this.createMovingPixels();

    this.drawOverlay(width, height);
    this.titleText.setPosition(width / 2, height * 0.35);
    this.subtitleText.setPosition(width / 2, height * 0.35 + 70);
    this.btnText.setPosition(width / 2, height * 0.7);
    this.versionText.setPosition(width / 2, height - 30);
  }

  private cleanupCity(): void {
    this.cityGraphics?.destroy();

    for (const w of this.windowLights) {
      w.timer.destroy();
      w.tween?.destroy();
      w.gfx.destroy();
    }
    this.windowLights = [];

    for (const p of this.movingPixels) {
      p.gfx.destroy();
    }
    this.movingPixels = [];
  }

  shutdown(): void {
    this.sparkleTimer?.destroy();
    this.cleanupCity();
    this.scale.off('resize');
  }
}
