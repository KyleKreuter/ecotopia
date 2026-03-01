import Phaser from 'phaser';
import { TileGrid } from '../objects/TileGrid.ts';
import { TileCursor } from '../objects/TileCursor.ts';
import { ActionMenu } from '../objects/ActionMenu.ts';
import { ParticleEffects } from '../objects/ParticleEffects.ts';
import { gameState } from '../state/GameStateManager.ts';
import { eventBus, GameEvents } from '../state/EventBus.ts';
import { UIManager } from '../ui/UIManager.ts';
import type { TileActionType } from '../types/backend.ts';

export class GameScene extends Phaser.Scene {
  private grid!: TileGrid;
  private cursor!: TileCursor;
  private actionMenu!: ActionMenu;
  private particles!: ParticleEffects;
  private uiManager!: UIManager;

  constructor() {
    super({ key: 'GameScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor('rgba(0,0,0,0)');

    this.grid = new TileGrid(this);
    this.cursor = new TileCursor(this, this.grid);
    this.actionMenu = new ActionMenu(this, this.grid);
    this.particles = new ParticleEffects(this, this.grid);

    this.uiManager = new UIManager();

    const state = gameState.gameState;
    if (state) {
      this.grid.updateFromState(state.tiles);
      this.uiManager.updateAll(state);
    }

    this.setupInput();
    this.setupEventListeners();
  }

  private setupInput(): void {
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      const cell = this.grid.screenToGrid(pointer.x, pointer.y);
      if (cell) {
        this.cursor.show(cell.x, cell.y);
      } else {
        this.cursor.hide();
      }
    });

    this.input.on('pointerdown', async (pointer: Phaser.Input.Pointer) => {
      if (this.actionMenu.getVisible()) {
        // Click inside menu → let ActionMenu handle it via pointerup
        // Click outside menu → close it
        if (!this.actionMenu.containsPoint(pointer.x, pointer.y)) {
          this.actionMenu.hide();
        }
        return;
      }

      const cell = this.grid.screenToGrid(pointer.x, pointer.y);
      if (!cell) return;

      const state = gameState.gameState;
      if (!state || state.currentRoundInfo.remainingActions <= 0) return;

      eventBus.emit(GameEvents.TILE_SELECTED, cell);

      try {
        const actions = await gameState.getTileActions(cell.x, cell.y);
        if (actions.length > 0) {
          this.actionMenu.show(cell.x, cell.y, actions, (action: TileActionType) => {
            this.executeAction(cell.x, cell.y, action);
          });
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to load actions';
        eventBus.emit(GameEvents.ERROR, msg);
      }
    });
  }

  private async executeAction(x: number, y: number, action: TileActionType): Promise<void> {
    try {
      if (action === 'DEMOLISH') {
        this.particles.demolish(x, y);
      } else if (action === 'PLANT_FOREST') {
        this.particles.nature(x, y);
      } else {
        this.particles.build(x, y);
      }

      await gameState.executeAction(x, y, action);

      const tile = this.grid.getTile(x, y);
      tile?.flash(400);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Action failed';
      eventBus.emit(GameEvents.ERROR, msg);
    }
  }

  private setupEventListeners(): void {
    eventBus.on(GameEvents.STATE_CHANGED, (state: unknown) => {
      const s = state as import('../types/backend.ts').GameStateResponse;
      this.grid.updateFromState(s.tiles);
      this.uiManager.updateAll(s);
    });

    eventBus.on(GameEvents.ROUND_ENDED, (data: unknown) => {
      const d = data as { oldRound: number; newRound: number };
      this.showRoundOverlay(d.oldRound, d.newRound);
    });

    eventBus.on(GameEvents.GAME_OVER, () => {
      this.scene.start('GameOverScene');
    });

    eventBus.on(GameEvents.ERROR, (msg: unknown) => {
      console.error('[Ecotopia]', msg);
    });
  }

  private showRoundOverlay(oldRound: number, newRound: number): void {
    const overlay = document.createElement('div');
    overlay.className = 'round-overlay';
    overlay.innerHTML = `
      <div class="round-text">Round ${newRound}</div>
      <div class="round-sub">Turn ${oldRound} complete</div>
    `;
    document.getElementById('ui-overlay')?.appendChild(overlay);

    setTimeout(() => overlay.remove(), 1500);
  }

  shutdown(): void {
    eventBus.clear();
    this.uiManager.destroy();
  }
}
