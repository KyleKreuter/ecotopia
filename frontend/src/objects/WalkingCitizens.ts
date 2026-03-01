import Phaser from 'phaser';
import { TileGrid } from './TileGrid.ts';
import { isOcean } from './IslandMask.ts';

/** Small citizen sprites that walk around the tile grid for visual life. */
export class WalkingCitizens {
  private scene: Phaser.Scene;
  private grid: TileGrid;
  private sprites: Phaser.GameObjects.Image[] = [];
  private readonly CITIZEN_COUNT = 5;
  private readonly NAMES = ['bernd', 'henning', 'karl', 'kerstin', 'lena', 'mia', 'oleg', 'pavel', 'sarah', 'yuki'];

  constructor(scene: Phaser.Scene, grid: TileGrid) {
    this.scene = scene;
    this.grid = grid;
    this.spawnCitizens();
  }

  private randomLandCell(): { x: number; y: number } {
    let x: number, y: number;
    do {
      x = Phaser.Math.Between(0, 9);
      y = Phaser.Math.Between(0, 9);
    } while (isOcean(x, y));
    return { x, y };
  }

  private spawnCitizens(): void {
    for (let i = 0; i < this.CITIZEN_COUNT; i++) {
      const name = Phaser.Math.RND.pick(this.NAMES);
      const startCell = this.randomLandCell();
      const worldPos = this.grid.gridToScreen(startCell.x, startCell.y);

      const sprite = this.scene.add.image(worldPos.x, worldPos.y, `char_${name}`);
      sprite.setScale(0.5);
      sprite.setDepth(100);
      sprite.setAlpha(0.7);
      this.sprites.push(sprite);

      this.walkTo(sprite);
    }
  }

  private walkTo(sprite: Phaser.GameObjects.Image): void {
    const targetCell = this.randomLandCell();
    const worldPos = this.grid.gridToScreen(targetCell.x, targetCell.y);

    if (worldPos.x < sprite.x) sprite.setFlipX(true);
    else sprite.setFlipX(false);

    const distance = Phaser.Math.Distance.Between(sprite.x, sprite.y, worldPos.x, worldPos.y);
    const duration = Math.max(2000, distance * 15);

    this.scene.tweens.add({
      targets: sprite,
      x: worldPos.x,
      y: worldPos.y,
      duration,
      ease: 'Linear',
      onComplete: () => {
        this.scene.time.delayedCall(Phaser.Math.Between(1000, 3000), () => this.walkTo(sprite));
      },
    });
  }

  destroy(): void {
    for (const sprite of this.sprites) {
      sprite.destroy();
    }
    this.sprites = [];
  }
}
