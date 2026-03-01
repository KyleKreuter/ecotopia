export interface GameStateResponse {
  id: number;
  currentRound: number;
  status: string;
  resultRank: string | null;
  defeatReason: string | null;
  resources: ResourcesResponse;
  tiles: TileResponse[];
  citizens: CitizenResponse[];
  promises: PromiseResponse[];
  currentRoundInfo: GameRoundResponse;
  createdAt: string;
  updatedAt: string;
}

export interface ResourcesResponse {
  ecology: number;
  economy: number;
  research: number;
}

export interface TileResponse {
  x: number;
  y: number;
  tileType: string;
  roundsInCurrentState: number;
}

export interface CitizenResponse {
  id: number;
  name: string;
  citizenType: string;
  profession: string;
  age: number | null;
  personality: string;
  approval: number;
  openingSpeech: string;
  remainingRounds: number | null;
}

export interface PromiseResponse {
  id: number;
  text: string;
  roundMade: number;
  deadline: number | null;
  status: string;
  citizenName: string;
}

export interface GameRoundResponse {
  roundNumber: number;
  remainingActions: number;
  speechText: string | null;
}

export interface TileActionResponse {
  availableActions: string[];
}

export interface SpeechResponse {
  extractedPromises: PromiseResponse[];
  contradictions: ContradictionResponse[];
  citizenReactions: CitizenReactionResponse[];
}

export interface ContradictionResponse {
  description: string;
  speechQuote: string;
  contradictingAction: string;
  severity: string;
}

export interface CitizenReactionResponse {
  citizenName: string;
  dialogue: string;
  tone: string;
  approvalDelta: number;
}

export type TileActionType =
  | 'DEMOLISH'
  | 'BUILD_FACTORY'
  | 'BUILD_SOLAR'
  | 'BUILD_RESEARCH_CENTER'
  | 'BUILD_FUSION'
  | 'PLANT_FOREST'
  | 'UPGRADE_CARBON_CAPTURE'
  | 'REPLACE_WITH_SOLAR'
  | 'CLEAR_FARMLAND';
