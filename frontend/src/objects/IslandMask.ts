import { GRID_SIZE } from '../config.ts';

// ---------------------------------------------------------------------------
// Island shape mask (10x10)
// ---------------------------------------------------------------------------
// true = Land, false = Ocean
// Creates rounded corners by removing corner cells.

const MASK: boolean[][] = [
  [false, false, true,  true,  true,  true,  true,  true,  false, false], // row 0
  [false, true,  true,  true,  true,  true,  true,  true,  true,  false], // row 1
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 2
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 3
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 4
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 5
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 6
  [true,  true,  true,  true,  true,  true,  true,  true,  true,  true],  // row 7
  [false, true,  true,  true,  true,  true,  true,  true,  true,  false], // row 8
  [false, false, true,  true,  true,  true,  true,  true,  false, false], // row 9
];

export const ISLAND_MASK: readonly boolean[][] = MASK;

export function isLand(x: number, y: number): boolean {
  if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return false;
  return MASK[y][x];
}

export function isOcean(x: number, y: number): boolean {
  return !isLand(x, y);
}
