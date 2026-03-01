import { GRID_SIZE } from '../config.ts';
import type { TileGrid } from './TileGrid.ts';

// ---------------------------------------------------------------------------
// City type detection
// ---------------------------------------------------------------------------

const CITY_TYPES = new Set(['CITY_INNER', 'CITY_OUTER']);

export function isCity(tileType: string): boolean {
  return CITY_TYPES.has(tileType);
}

// ---------------------------------------------------------------------------
// 8-neighbor bitmask (same convention as WaterTransitions / ShoreTransitions)
// ---------------------------------------------------------------------------

const NW = 1 << 0;
const N  = 1 << 1;
const NE = 1 << 2;
const W  = 1 << 3;
const E  = 1 << 4;
const SW = 1 << 5;
const S  = 1 << 6;
const SE = 1 << 7;

const OFFSETS: [number, number, number][] = [
  [-1, -1, NW], [0, -1, N], [1, -1, NE],
  [-1,  0, W],              [1,  0, E],
  [-1,  1, SW], [0,  1, S], [1,  1, SE],
];

// ---------------------------------------------------------------------------
// City border mask — inverted logic: which neighbors are NOT city?
// ---------------------------------------------------------------------------

export function computeCityBorderMask(grid: TileGrid, x: number, y: number): number {
  let mask = 0;
  for (const [dx, dy, bit] of OFFSETS) {
    const nx = x + dx;
    const ny = y + dy;
    if (nx < 0 || nx >= GRID_SIZE || ny < 0 || ny >= GRID_SIZE) {
      mask |= bit;
      continue;
    }
    const neighbor = grid.getTile(nx, ny);
    if (!neighbor || neighbor.ocean || !isCity(neighbor.tileType)) {
      mask |= bit;
    }
  }
  return mask;
}

// ---------------------------------------------------------------------------
// Overlay resolution
// ---------------------------------------------------------------------------

export interface CityOverlaySpec {
  key: string;
}

export function resolveCityOverlays(mask: number): CityOverlaySpec[] {
  const specs: CityOverlaySpec[] = [];

  const hasN  = (mask & N)  !== 0;
  const hasE  = (mask & E)  !== 0;
  const hasS  = (mask & S)  !== 0;
  const hasW  = (mask & W)  !== 0;
  const hasNE = (mask & NE) !== 0;
  const hasNW = (mask & NW) !== 0;
  const hasSE = (mask & SE) !== 0;
  const hasSW = (mask & SW) !== 0;

  // Cardinal edges
  if (hasN) specs.push({ key: 'city_edge_n' });
  if (hasE) specs.push({ key: 'city_edge_e' });
  if (hasS) specs.push({ key: 'city_edge_s' });
  if (hasW) specs.push({ key: 'city_edge_w' });

  // Inner corners (two adjacent edges meet)
  if (hasN && hasE) specs.push({ key: 'city_inner_ne' });
  if (hasN && hasW) specs.push({ key: 'city_inner_nw' });
  if (hasS && hasE) specs.push({ key: 'city_inner_se' });
  if (hasS && hasW) specs.push({ key: 'city_inner_sw' });

  // Outer corners (diagonal non-city without adjacent cardinal non-city)
  if (hasNE && !hasN && !hasE) specs.push({ key: 'city_outer_ne' });
  if (hasNW && !hasN && !hasW) specs.push({ key: 'city_outer_nw' });
  if (hasSE && !hasS && !hasE) specs.push({ key: 'city_outer_se' });
  if (hasSW && !hasS && !hasW) specs.push({ key: 'city_outer_sw' });

  return specs;
}

// ---------------------------------------------------------------------------
// All texture keys (used by BootScene for generation)
// ---------------------------------------------------------------------------

export const CITY_TEXTURE_KEYS = [
  'city_edge_n', 'city_edge_e', 'city_edge_s', 'city_edge_w',
  'city_inner_ne', 'city_inner_nw', 'city_inner_se', 'city_inner_sw',
  'city_outer_ne', 'city_outer_nw', 'city_outer_se', 'city_outer_sw',
] as const;
