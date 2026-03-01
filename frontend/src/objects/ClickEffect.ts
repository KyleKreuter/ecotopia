import Phaser from 'phaser';

const RING_DEPTH = 500;
const RING_DURATION = 250;
const RING_SCALE_END = 1.5;

export class ClickEffect {
  private scene: Phaser.Scene;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  play(screenX: number, screenY: number): void {
    const ring = this.scene.add.image(screenX, screenY, 'click_ring');
    ring.setDepth(RING_DEPTH);
    ring.setScale(0);
    ring.setAlpha(0.7);

    this.scene.tweens.add({
      targets: ring,
      scale: RING_SCALE_END,
      alpha: 0,
      duration: RING_DURATION,
      ease: 'Cubic.easeOut',
      onComplete: () => ring.destroy(),
    });
  }
}
