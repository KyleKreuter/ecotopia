import Phaser from 'phaser';
import { gameState } from '../state/GameStateManager.ts';
import { GameOverPanel } from '../ui/GameOverPanel.ts';

export class GameOverScene extends Phaser.Scene {
  private panel: GameOverPanel | null = null;

  constructor() {
    super({ key: 'GameOverScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor('rgba(0,0,0,0)');

    const state = gameState.gameState;
    if (!state) {
      this.scene.start('TitleScene');
      return;
    }

    this.events.on('shutdown', this.shutdown, this);

    // Show game over panel (HTML overlay)
    this.panel = new GameOverPanel(state, () => {
      this.panel?.destroy();
      this.panel = null;
      this.scene.start('TitleScene');
    });
  }

  shutdown(): void {
    this.panel?.destroy();
    this.panel = null;
  }
}
