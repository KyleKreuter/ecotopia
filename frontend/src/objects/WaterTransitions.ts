import { GRID_SIZE } from '../config.ts';
import type { TileGrid } from './TileGrid.ts';

// ---------------------------------------------------------------------------
// Water type detection
// ---------------------------------------------------------------------------

const WATER_TYPES = new Set(['CLEAN_RIVER', 'POLLUTED_RIVER', 'RIVER']);

export function isWater(tileType: string): boolean {
  return WATER_TYPES.has(tileType);
}

// ---------------------------------------------------------------------------
// 8-neighbor bitmask
// ---------------------------------------------------------------------------

export const NW = 1 << 0; //   1
export const N  = 1 << 1; //   2
export const NE = 1 << 2; //   4
export const W  = 1 << 3; //   8
export const E  = 1 << 4; //  16
export const SW = 1 << 5; //  32
export const S  = 1 << 6; //  64
export const SE = 1 << 7; // 128

const OFFSETS: [number, number, number][] = [
  [-1, -1, NW], [0, -1, N], [1, -1, NE],
  [-1,  0, W],              [1,  0, E],
  [-1,  1, SW], [0,  1, S], [1,  1, SE],
];

export function computeWaterMask(grid: TileGrid, x: number, y: number): number {
  let mask = 0;
  for (const [dx, dy, bit] of OFFSETS) {
    const nx = x + dx;
    const ny = y + dy;
    if (nx < 0 || nx >= GRID_SIZE || ny < 0 || ny >= GRID_SIZE) continue;
    const neighbor = grid.getTile(nx, ny);
    if (neighbor && isWater(neighbor.tileType)) {
      mask |= bit;
    }
  }
  return mask;
}

// ---------------------------------------------------------------------------
// Overlay resolution
// ---------------------------------------------------------------------------

export interface OverlaySpec {
  key: string;
  tintPolluted: boolean;
}

export function resolveOverlays(
  mask: number,
  grid: TileGrid,
  x: number,
  y: number,
): OverlaySpec[] {
  const specs: OverlaySpec[] = [];

  const hasN  = (mask & N)  !== 0;
  const hasE  = (mask & E)  !== 0;
  const hasS  = (mask & S)  !== 0;
  const hasW  = (mask & W)  !== 0;
  const hasNE = (mask & NE) !== 0;
  const hasNW = (mask & NW) !== 0;
  const hasSE = (mask & SE) !== 0;
  const hasSW = (mask & SW) !== 0;

  const isPolluted = (nx: number, ny: number): boolean => {
    const t = grid.getTile(nx, ny);
    return t?.tileType === 'POLLUTED_RIVER';
  };

  // Cardinal edges
  if (hasN) specs.push({ key: 'wt_edge_n', tintPolluted: isPolluted(x, y - 1) });
  if (hasE) specs.push({ key: 'wt_edge_e', tintPolluted: isPolluted(x + 1, y) });
  if (hasS) specs.push({ key: 'wt_edge_s', tintPolluted: isPolluted(x, y + 1) });
  if (hasW) specs.push({ key: 'wt_edge_w', tintPolluted: isPolluted(x - 1, y) });

  // Inner corners (where two adjacent edges meet)
  if (hasN && hasE) specs.push({ key: 'wt_inner_ne', tintPolluted: isPolluted(x + 1, y - 1) });
  if (hasN && hasW) specs.push({ key: 'wt_inner_nw', tintPolluted: isPolluted(x - 1, y - 1) });
  if (hasS && hasE) specs.push({ key: 'wt_inner_se', tintPolluted: isPolluted(x + 1, y + 1) });
  if (hasS && hasW) specs.push({ key: 'wt_inner_sw', tintPolluted: isPolluted(x - 1, y + 1) });

  // Outer corners (diagonal water with no adjacent cardinal water)
  if (hasNE && !hasN && !hasE) specs.push({ key: 'wt_outer_ne', tintPolluted: isPolluted(x + 1, y - 1) });
  if (hasNW && !hasN && !hasW) specs.push({ key: 'wt_outer_nw', tintPolluted: isPolluted(x - 1, y - 1) });
  if (hasSE && !hasS && !hasE) specs.push({ key: 'wt_outer_se', tintPolluted: isPolluted(x + 1, y + 1) });
  if (hasSW && !hasS && !hasW) specs.push({ key: 'wt_outer_sw', tintPolluted: isPolluted(x - 1, y + 1) });

  return specs;
}

// ---------------------------------------------------------------------------
// Asset paths (loaded in BootScene)
// ---------------------------------------------------------------------------

export const WATER_TRANSITION_ASSETS: Record<string, string> = {
  wt_edge_n:   '/assets/tiles/transitions/water_edge_n.png',
  wt_edge_e:   '/assets/tiles/transitions/water_edge_e.png',
  wt_edge_s:   '/assets/tiles/transitions/water_edge_s.png',
  wt_edge_w:   '/assets/tiles/transitions/water_edge_w.png',
  wt_outer_ne: '/assets/tiles/transitions/water_outer_ne.png',
  wt_outer_nw: '/assets/tiles/transitions/water_outer_nw.png',
  wt_outer_se: '/assets/tiles/transitions/water_outer_se.png',
  wt_outer_sw: '/assets/tiles/transitions/water_outer_sw.png',
  wt_inner_ne: '/assets/tiles/transitions/water_inner_ne.png',
  wt_inner_nw: '/assets/tiles/transitions/water_inner_nw.png',
  wt_inner_se: '/assets/tiles/transitions/water_inner_se.png',
  wt_inner_sw: '/assets/tiles/transitions/water_inner_sw.png',
};
