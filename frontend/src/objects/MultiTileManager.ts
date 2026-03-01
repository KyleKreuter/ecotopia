import { GRID_SIZE, MULTI_TILE_SIZES, type MultiTileSize } from '../config.ts';
import type { TileResponse } from '../types/backend.ts';

export interface MultiTileCluster {
  tileType: string;
  size: MultiTileSize;
  /** Top-left grid coordinate */
  originX: number;
  originY: number;
}

/**
 * Detects clusters of adjacent multi-tile buildings and determines
 * which cell is the top-left origin of each cluster.
 */
export class MultiTileManager {
  /**
   * Returns a map from "x,y" → cluster for every cell that belongs
   * to a multi-tile cluster, plus a list of unique clusters.
   */
  static detectClusters(tiles: TileResponse[]): {
    clusters: MultiTileCluster[];
    cellToCluster: Map<string, MultiTileCluster>;
  } {
    const grid = new Map<string, string>();
    for (const t of tiles) {
      grid.set(`${t.x},${t.y}`, t.tileType);
    }

    const clusters: MultiTileCluster[] = [];
    const cellToCluster = new Map<string, MultiTileCluster>();
    const visited = new Set<string>();

    for (let y = 0; y < GRID_SIZE; y++) {
      for (let x = 0; x < GRID_SIZE; x++) {
        const key = `${x},${y}`;
        if (visited.has(key)) continue;

        const tileType = grid.get(key);
        if (!tileType) continue;

        const multiSize = MULTI_TILE_SIZES[tileType];
        if (!multiSize) continue;

        // Try to fit the full multi-tile pattern starting at (x, y)
        if (this.fitsAt(grid, tileType, x, y, multiSize)) {
          const cluster: MultiTileCluster = {
            tileType,
            size: multiSize,
            originX: x,
            originY: y,
          };
          clusters.push(cluster);

          for (let dy = 0; dy < multiSize.h; dy++) {
            for (let dx = 0; dx < multiSize.w; dx++) {
              const cellKey = `${x + dx},${y + dy}`;
              visited.add(cellKey);
              cellToCluster.set(cellKey, cluster);
            }
          }
        }
      }
    }

    return { clusters, cellToCluster };
  }

  private static fitsAt(
    grid: Map<string, string>,
    tileType: string,
    x: number,
    y: number,
    size: MultiTileSize,
  ): boolean {
    if (x + size.w > GRID_SIZE || y + size.h > GRID_SIZE) return false;

    for (let dy = 0; dy < size.h; dy++) {
      for (let dx = 0; dx < size.w; dx++) {
        if (grid.get(`${x + dx},${y + dy}`) !== tileType) return false;
      }
    }
    return true;
  }
}
