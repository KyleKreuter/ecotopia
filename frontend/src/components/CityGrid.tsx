import React from 'react';
import { useState } from 'react';
import type { Tile, TileType } from '../types/game';

interface CityGridProps {
  grid: Tile[][];
}

/** Visual representation and label for each tile type. */
const TILE_CONFIG: Record<TileType, { color: string; icon: string }> = {
  forest: { color: '#166534', icon: 'T' },
  water: { color: '#1e40af', icon: '~' },
  factory: { color: '#78716c', icon: 'F' },
  solar: { color: '#eab308', icon: 'S' },
  house: { color: '#a16207', icon: 'H' },
  farm: { color: '#65a30d', icon: 'W' },
  empty: { color: '#374151', icon: '.' },
  research_lab: { color: '#7c3aed', icon: 'R' },
  wind_turbine: { color: '#06b6d4', icon: 'V' },
  coal_plant: { color: '#451a03', icon: 'C' },
};

const TILE_LABELS: Record<TileType, string> = {
  forest: 'Forest',
  water: 'Water',
  factory: 'Factory',
  solar: 'Solar Panel',
  house: 'Housing',
  farm: 'Farmland',
  empty: 'Empty Lot',
  research_lab: 'Research Lab',
  wind_turbine: 'Wind Turbine',
  coal_plant: 'Coal Plant',
};

export function CityGrid({ grid }: CityGridProps): React.JSX.Element {
  const [hoveredTile, setHoveredTile] = useState<Tile | null>(null);

  return (
    <div className="city-grid-container">
      <h3>City Map</h3>
      <div className="city-grid">
        {grid.map((row, y) =>
          row.map((tile) => {
            const config = TILE_CONFIG[tile.type];
            return (
              <div
                key={`${tile.x}-${y}`}
                className="grid-tile"
                style={{ backgroundColor: config.color }}
                onMouseEnter={() => setHoveredTile(tile)}
                onMouseLeave={() => setHoveredTile(null)}
              >
                {config.icon}
              </div>
            );
          })
        )}
      </div>
      {hoveredTile && (
        <div className="tile-tooltip">
          {TILE_LABELS[hoveredTile.type]} ({hoveredTile.x}, {hoveredTile.y})
        </div>
      )}
    </div>
  );
}
