import type { GameState, Tile, TileType } from '../types/game';

/** Tile layout blueprint for the 10x10 grid. Row-major, top to bottom. */
const GRID_LAYOUT: TileType[][] = [
  ['forest', 'forest', 'water', 'water', 'forest', 'forest', 'empty', 'empty', 'forest', 'forest'],
  ['forest', 'farm', 'water', 'farm', 'forest', 'empty', 'house', 'house', 'empty', 'forest'],
  ['farm', 'farm', 'empty', 'farm', 'empty', 'house', 'house', 'factory', 'empty', 'empty'],
  ['empty', 'empty', 'house', 'house', 'house', 'house', 'factory', 'factory', 'coal_plant', 'empty'],
  ['empty', 'solar', 'house', 'house', 'house', 'house', 'house', 'factory', 'empty', 'empty'],
  ['farm', 'empty', 'house', 'house', 'research_lab', 'house', 'house', 'empty', 'empty', 'water'],
  ['farm', 'farm', 'empty', 'house', 'empty', 'empty', 'wind_turbine', 'empty', 'water', 'water'],
  ['forest', 'farm', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'water', 'water'],
  ['forest', 'forest', 'empty', 'empty', 'solar', 'empty', 'empty', 'forest', 'forest', 'water'],
  ['forest', 'forest', 'forest', 'empty', 'empty', 'empty', 'forest', 'forest', 'forest', 'forest'],
];

function buildGrid(): Tile[][] {
  return GRID_LAYOUT.map((row, y) =>
    row.map((type, x) => ({ x, y, type }))
  );
}

export const INITIAL_GAME_STATE: GameState = {
  round: 1,
  maxRounds: 7,
  ecology: 65,
  economy: 45,
  research: 30,
  grid: buildGrid(),
  citizens: [
    {
      name: 'Karl',
      role: 'Factory Worker',
      personality: 'Pragmatic, worried about jobs',
      approval: 55,
      dialogue: 'We need those factory jobs, mayor. My family depends on it.',
      tone: 'suspicious',
      isCore: true,
    },
    {
      name: 'Mia',
      role: 'Environmental Activist',
      personality: 'Passionate, idealistic, impatient',
      approval: 70,
      dialogue: 'The river is dying. We need action, not speeches.',
      tone: 'hopeful',
      isCore: true,
    },
    {
      name: 'Sarah',
      role: 'Opposition Leader',
      personality: 'Sharp, calculating, always looking for contradictions',
      approval: 35,
      dialogue: 'Interesting promises, mayor. Let us see if you keep them this time.',
      tone: 'sarcastic',
      isCore: true,
    },
  ],
  promises: [
    {
      id: 'p1',
      text: 'Close the coal plant by 2030',
      type: 'explicit',
      confidence: 0.92,
      targetCitizen: 'Mia',
      deadlineRound: 3,
      status: 'active',
      roundMade: 1,
    },
    {
      id: 'p2',
      text: 'No factory worker will lose their job',
      type: 'explicit',
      confidence: 0.87,
      targetCitizen: 'Karl',
      deadlineRound: null,
      status: 'active',
      roundMade: 1,
    },
    {
      id: 'p3',
      text: 'Invest in renewable energy research',
      type: 'implicit',
      confidence: 0.65,
      targetCitizen: null,
      deadlineRound: null,
      status: 'active',
      roundMade: 1,
    },
  ],
  contradictions: [
    {
      description: 'Promised to close the coal plant but also guaranteed no job losses',
      speechQuote: 'No factory worker will lose their job',
      contradictingAction: 'Close the coal plant by 2030',
      severity: 'high',
    },
  ],
  gameOver: false,
  gameResult: null,
};
