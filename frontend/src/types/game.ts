export type TileType =
  | 'forest'
  | 'water'
  | 'factory'
  | 'solar'
  | 'house'
  | 'farm'
  | 'empty'
  | 'research_lab'
  | 'wind_turbine'
  | 'coal_plant';

export type CitizenTone =
  | 'angry'
  | 'hopeful'
  | 'sarcastic'
  | 'desperate'
  | 'grateful'
  | 'suspicious'
  | 'neutral';

export type PromiseStatus = 'active' | 'kept' | 'broken';
export type PromiseType = 'explicit' | 'implicit';
export type ContradictionSeverity = 'low' | 'medium' | 'high';
export type GameResult = 'win' | 'lose' | null;

export interface Tile {
  x: number;
  y: number;
  type: TileType;
}

export interface Citizen {
  name: string;
  role: string;
  personality: string;
  approval: number;
  dialogue: string;
  tone: CitizenTone;
  isCore: boolean;
}

export interface GamePromise {
  id: string;
  text: string;
  type: PromiseType;
  confidence: number;
  targetCitizen: string | null;
  deadlineRound: number | null;
  status: PromiseStatus;
  roundMade: number;
}

export interface Contradiction {
  description: string;
  speechQuote: string;
  contradictingAction: string;
  severity: ContradictionSeverity;
}

export interface GameState {
  round: number;
  maxRounds: number;
  ecology: number;
  economy: number;
  research: number;
  grid: Tile[][];
  citizens: Citizen[];
  promises: GamePromise[];
  contradictions: Contradiction[];
  gameOver: boolean;
  gameResult: GameResult;
}
