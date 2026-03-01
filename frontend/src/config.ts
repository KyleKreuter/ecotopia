export let TILE_SIZE = 48;
export const GRID_SIZE = 10;

/** Compute tile size so the grid fills ~90% of the viewport */
export function initTileSize(viewportW: number, viewportH: number): void {
  TILE_SIZE = Math.floor(Math.min(viewportW, viewportH) * 0.9 / GRID_SIZE);
}

export const COLORS = {
  bg: 0xFFFBF1,
  camLight: 0xFFFBF1,
  camMid: 0xFFF2D0,
  camDark: 0xE3DBBB,
  panelBg: 'rgba(255, 251, 241, 0.95)',
  border: '#000000',
  accent: '#000000',
  danger: '#000000',
  textPrimary: '#000000',
  textDim: '#666666',
} as const;

export interface TileConfig {
  color: number;
  label: string;
}

export const TILE_TYPES: Record<string, TileConfig> = {
  EMPTY:            { color: 0xffffff, label: 'Empty' },
  HEALTHY_FOREST:   { color: 0xcccccc, label: 'Healthy Forest' },
  SICK_FOREST:      { color: 0xbbbbbb, label: 'Sick Forest' },
  CLEAN_RIVER:      { color: 0xaaaaaa, label: 'Clean River' },
  POLLUTED_RIVER:   { color: 0x999999, label: 'Polluted River' },
  FARMLAND:         { color: 0xdddddd, label: 'Farmland' },
  DEAD_FARMLAND:    { color: 0xbbbbbb, label: 'Dead Farmland' },
  WASTELAND:        { color: 0x888888, label: 'Wasteland' },
  FACTORY:          { color: 0xaaaaaa, label: 'Factory' },
  CLEAN_FACTORY:    { color: 0xcccccc, label: 'Clean Factory' },
  OIL_REFINERY:     { color: 0x999999, label: 'Oil Refinery' },
  COAL_PLANT:       { color: 0x888888, label: 'Coal Plant' },
  CITY_INNER:       { color: 0xdddddd, label: 'City Inner' },
  CITY_OUTER:       { color: 0xcccccc, label: 'City Outer' },
  RESEARCH_CENTER:  { color: 0xbbbbbb, label: 'Research Center' },
  SOLAR_FIELD:      { color: 0xdddddd, label: 'Solar Field' },
  FUSION_REACTOR:   { color: 0xcccccc, label: 'Fusion Reactor' },
  FOREST:           { color: 0xcccccc, label: 'Forest' },
  RIVER:            { color: 0xaaaaaa, label: 'River' },
  COMMERCIAL:       { color: 0xdddddd, label: 'Commercial' },
  INDUSTRIAL:       { color: 0xaaaaaa, label: 'Industrial' },
  PARK:             { color: 0xcccccc, label: 'Park' },
  SOLAR_FARM:       { color: 0xdddddd, label: 'Solar Farm' },
  WIND_FARM:        { color: 0xdddddd, label: 'Wind Farm' },
  CARBON_CAPTURE:   { color: 0xcccccc, label: 'Carbon Capture' },
  NUCLEAR_PLANT:    { color: 0xbbbbbb, label: 'Nuclear Plant' },
} as const;

/** Multi-tile building size in grid cells [width, height] */
export interface MultiTileSize {
  w: number;
  h: number;
}

export const MULTI_TILE_SIZES: Record<string, MultiTileSize> = {
  FACTORY:        { w: 2, h: 1 },
  CLEAN_FACTORY:  { w: 2, h: 1 },
  SOLAR_FIELD:    { w: 2, h: 1 },
  OIL_REFINERY:   { w: 2, h: 2 },
  COAL_PLANT:     { w: 2, h: 2 },
  FUSION_REACTOR: { w: 2, h: 2 },
};

// ---------------------------------------------------------------------------
// Spritesheet → TileType mapping
// ---------------------------------------------------------------------------
// Spritesheets are 16x16 grids. Frame index = row * cols + col.
// Grass.png:        11 cols x 7 rows   — center fill @ (1,1) = frame 12
// Water.png:         4 cols x 1 row    — frame 0
// Tilled_Dirt.png:  11 cols x 7 rows   — center fill @ (1,1) = frame 12
// Hills.png:        11 cols x 9 rows

export interface SpriteMapping {
  sheet: string;
  frame: number;
  tint?: number;
}

export const SPRITESHEETS: Record<string, { path: string; frameWidth: number; frameHeight: number }> = {
  ss_grass:       { path: '/assets/tileset/Grass.png',                  frameWidth: 16, frameHeight: 16 },
  ss_water:       { path: '/assets/tileset/Water.png',                  frameWidth: 16, frameHeight: 16 },
  ss_dirt:        { path: '/assets/tileset/Tilled_Dirt.png',            frameWidth: 16, frameHeight: 16 },
  ss_dirt_v2:     { path: '/assets/tileset/Tilled_Dirt_v2.png',         frameWidth: 16, frameHeight: 16 },
  ss_dirt_wide:   { path: '/assets/tileset/Tilled_Dirt_Wide_v2.png',    frameWidth: 16, frameHeight: 16 },
  ss_hills:       { path: '/assets/tileset/Hills.png',                  frameWidth: 16, frameHeight: 16 },
  ss_house:       { path: '/assets/tileset/Wooden House.png',           frameWidth: 16, frameHeight: 16 },
  ss_roof:        { path: '/assets/tileset/Wooden_House_Roof_Tilset.png', frameWidth: 16, frameHeight: 16 },
  ss_walls:       { path: '/assets/tileset/Wooden_House_Walls_Tilset.png', frameWidth: 16, frameHeight: 16 },
  ss_fences:      { path: '/assets/tileset/Fences.png',                 frameWidth: 16, frameHeight: 16 },
};

/** Map TileType → spritesheet frame. Falls back to generated color rect if absent. */
export const TILE_SPRITE_MAP: Record<string, SpriteMapping> = {
  // Natural terrain
  HEALTHY_FOREST: { sheet: 'ss_grass',     frame: 12 },
  SICK_FOREST:    { sheet: 'ss_grass',     frame: 12, tint: 0xBBCC88 },
  CLEAN_RIVER:    { sheet: 'ss_water',     frame: 0 },
  POLLUTED_RIVER: { sheet: 'ss_water',     frame: 0,  tint: 0x99AA77 },
  FARMLAND:       { sheet: 'ss_dirt',      frame: 12 },
  DEAD_FARMLAND:  { sheet: 'ss_dirt_v2',   frame: 12 },
  WASTELAND:      { sheet: 'ss_dirt_wide', frame: 12 },
  // Buildings with sprites
  CITY_INNER:     { sheet: 'ss_walls',     frame: 0 },
  CITY_OUTER:     { sheet: 'ss_roof',      frame: 8 },
  // Legacy demo types
  FOREST:         { sheet: 'ss_grass',     frame: 12 },
  PARK:           { sheet: 'ss_grass',     frame: 12, tint: 0x99DD99 },
};

// ---------------------------------------------------------------------------
// Pixel-art tile assets — one PNG per tile type
// ---------------------------------------------------------------------------
export const TILE_ASSETS: Record<string, string> = {
  EMPTY:            '/assets/tiles/empty.png',
  HEALTHY_FOREST:   '/assets/tiles/healthy_forest.png',
  SICK_FOREST:      '/assets/tiles/sick_forest.png',
  CLEAN_RIVER:      '/assets/tiles/clean_river.png',
  POLLUTED_RIVER:   '/assets/tiles/polluted_river.png',
  FARMLAND:         '/assets/tiles/farmland.png',
  DEAD_FARMLAND:    '/assets/tiles/dead_farmland.png',
  WASTELAND:        '/assets/tiles/wasteland.png',
  FACTORY:          '/assets/tiles/factory.png',
  CLEAN_FACTORY:    '/assets/tiles/clean_factory.png',
  OIL_REFINERY:     '/assets/tiles/oil_refinery.png',
  COAL_PLANT:       '/assets/tiles/coal_plant.png',
  CITY_INNER:       '/assets/tiles/city_inner.png',
  CITY_OUTER:       '/assets/tiles/city_outer.png',
  RESEARCH_CENTER:  '/assets/tiles/research_center.png',
  SOLAR_FIELD:      '/assets/tiles/solar_field.png',
  FUSION_REACTOR:   '/assets/tiles/fusion_reactor.png',
  FOREST:           '/assets/tiles/healthy_forest.png',
  RIVER:            '/assets/tiles/clean_river.png',
  COMMERCIAL:       '/assets/tiles/commercial.png',
  INDUSTRIAL:       '/assets/tiles/industrial.png',
  PARK:             '/assets/tiles/park.png',
  SOLAR_FARM:       '/assets/tiles/solar_farm.png',
  WIND_FARM:        '/assets/tiles/wind_farm.png',
  CARBON_CAPTURE:   '/assets/tiles/carbon_capture.png',
  NUCLEAR_PLANT:    '/assets/tiles/nuclear_plant.png',
};

export const ACTION_LABELS: Record<string, string> = {
  DEMOLISH: 'Demolish',
  BUILD_FACTORY: 'Build Factory',
  BUILD_SOLAR: 'Build Solar Farm',
  BUILD_RESEARCH_CENTER: 'Build Research Center',
  BUILD_FUSION: 'Build Fusion Reactor',
  PLANT_FOREST: 'Plant Forest',
  UPGRADE_CARBON_CAPTURE: 'Upgrade to Carbon Capture',
  REPLACE_WITH_SOLAR: 'Replace with Solar',
  CLEAR_FARMLAND: 'Clear Farmland',
} as const;
