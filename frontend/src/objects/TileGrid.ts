import Phaser from 'phaser';
import { GRID_SIZE, TILE_SIZE } from '../config.ts';
import { TileSprite } from './TileSprite.ts';
import { MultiTileManager, type MultiTileCluster } from './MultiTileManager.ts';
import { isWater, computeWaterMask, resolveOverlays } from './WaterTransitions.ts';
import type { TileResponse } from '../types/backend.ts';

export class TileGrid {
  private scene: Phaser.Scene;
  private container: Phaser.GameObjects.Container;
  private tiles: TileSprite[][] = [];
  private multiTileOverlays: Phaser.GameObjects.Image[] = [];

  /** Top-left screen position of the grid */
  originX = 0;
  originY = 0;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.computeOrigin();
    this.container = scene.add.container(this.originX, this.originY);
    this.createGrid();

    scene.scale.on('resize', () => {
      this.computeOrigin();
      this.container.setPosition(this.originX, this.originY);
    });
  }

  private computeOrigin(): void {
    const cam = this.scene.cameras.main;
    const totalW = GRID_SIZE * TILE_SIZE;
    const totalH = GRID_SIZE * TILE_SIZE;
    this.originX = Math.floor((cam.width - totalW) / 2);
    this.originY = Math.floor((cam.height - totalH) / 2);
  }

  private createGrid(): void {
    for (let y = 0; y < GRID_SIZE; y++) {
      this.tiles[y] = [];
      for (let x = 0; x < GRID_SIZE; x++) {
        const tile = new TileSprite(this.scene, x, y, 'EMPTY');
        this.container.add(tile);
        this.tiles[y][x] = tile;
      }
    }
  }

  /** Convert screen coordinates to grid coordinates (or null if outside) */
  screenToGrid(screenX: number, screenY: number): { x: number; y: number } | null {
    const gx = Math.floor((screenX - this.originX) / TILE_SIZE);
    const gy = Math.floor((screenY - this.originY) / TILE_SIZE);
    if (gx < 0 || gx >= GRID_SIZE || gy < 0 || gy >= GRID_SIZE) return null;
    return { x: gx, y: gy };
  }

  /** Convert grid coordinates to screen coordinates (top-left of cell) */
  gridToScreen(gx: number, gy: number): { x: number; y: number } {
    return {
      x: this.originX + gx * TILE_SIZE,
      y: this.originY + gy * TILE_SIZE,
    };
  }

  updateFromState(tileData: TileResponse[]): void {
    for (let y = 0; y < GRID_SIZE; y++) {
      for (let x = 0; x < GRID_SIZE; x++) {
        this.tiles[y][x].setHiddenByMultiTile(false);
      }
    }

    for (const td of tileData) {
      const tile = this.getTile(td.x, td.y);
      if (tile) tile.setTileType(td.tileType);
    }

    this.updateMultiTileOverlays(tileData);
    this.updateWaterTransitions();
  }

  private updateMultiTileOverlays(tileData: TileResponse[]): void {
    for (const overlay of this.multiTileOverlays) overlay.destroy();
    this.multiTileOverlays = [];

    const { clusters, cellToCluster } = MultiTileManager.detectClusters(tileData);

    for (const [key] of cellToCluster) {
      const [x, y] = key.split(',').map(Number);
      const tile = this.getTile(x, y);
      if (tile) tile.setHiddenByMultiTile(true);
    }

    for (const cluster of clusters) this.createClusterOverlay(cluster);
  }

  private createClusterOverlay(cluster: MultiTileCluster): void {
    const svgKey = `svg_${cluster.tileType}`;
    const fallbackKey = `tile_multi_${cluster.tileType}`;
    const texKey = this.scene.textures.exists(svgKey) ? svgKey : fallbackKey;
    if (!this.scene.textures.exists(texKey)) return;

    const px = cluster.originX * TILE_SIZE + (cluster.size.w * TILE_SIZE) / 2;
    const py = cluster.originY * TILE_SIZE + (cluster.size.h * TILE_SIZE) / 2;

    const overlay = this.scene.add.image(px, py, texKey);
    overlay.setDisplaySize(cluster.size.w * TILE_SIZE, cluster.size.h * TILE_SIZE);

    this.container.add(overlay);
    this.multiTileOverlays.push(overlay);
  }

  private updateWaterTransitions(): void {
    for (let y = 0; y < GRID_SIZE; y++) {
      for (let x = 0; x < GRID_SIZE; x++) {
        const tile = this.tiles[y][x];

        if (isWater(tile.tileType)) {
          tile.clearWaterOverlays();
          continue;
        }

        const mask = computeWaterMask(this, x, y);
        if (mask === 0) {
          tile.clearWaterOverlays();
          continue;
        }

        const specs = resolveOverlays(mask, this, x, y);
        tile.applyWaterOverlays(specs);
      }
    }
  }

  getTile(x: number, y: number): TileSprite | null {
    if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return null;
    return this.tiles[y][x];
  }

  getContainer(): Phaser.GameObjects.Container {
    return this.container;
  }
}
