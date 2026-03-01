import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene.ts';
import { TitleScene } from './scenes/TitleScene.ts';
import { GameScene } from './scenes/GameScene.ts';
import { GameOverScene } from './scenes/GameOverScene.ts';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: 800,
  height: 600,
  transparent: true,
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.RESIZE,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  scene: [BootScene, TitleScene, GameScene, GameOverScene],
};

new Phaser.Game(config);
