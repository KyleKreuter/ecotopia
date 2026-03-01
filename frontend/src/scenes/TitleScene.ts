import Phaser from 'phaser';
import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';

export class TitleScene extends Phaser.Scene {
  constructor() {
    super({ key: 'TitleScene' });
  }

  create(): void {
    const { width, height } = this.scale;

    this.cameras.main.setBackgroundColor('rgba(0,0,0,0)');

    this.add.text(width / 2, height / 3, 'ECOTOPIA', {
      fontFamily: 'monospace',
      fontSize: '32px',
      color: '#000000',
    }).setOrigin(0.5);

    this.add.text(width / 2, height / 3 + 50, 'A Political Simulation', {
      fontFamily: 'monospace',
      fontSize: '10px',
      color: '#666666',
    }).setOrigin(0.5);

    const btn = this.add.text(width / 2, height / 2 + 40, '[ NEW GAME ]', {
      fontFamily: 'monospace',
      fontSize: '14px',
      color: '#000000',
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    btn.on('pointerover', () => btn.setColor('#666666'));
    btn.on('pointerout', () => btn.setColor('#000000'));

    btn.on('pointerdown', async () => {
      btn.setText('LOADING...');
      btn.disableInteractive();
      try {
        await gameState.createGame();
        this.scene.start('GameScene');
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        btn.setText('ERROR - RETRY');
        btn.setInteractive({ useHandCursor: true });
        eventBus.emit(GameEvents.ERROR, msg);
      }
    });

    this.add.text(width / 2, height - 30, 'v0.1.0', {
      fontFamily: 'monospace',
      fontSize: '8px',
      color: '#999999',
    }).setOrigin(0.5);
  }
}
