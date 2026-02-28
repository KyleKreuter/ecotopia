/**
 * TypeScript interfaces matching Kyle's Spring Boot backend DTOs.
 * These mirror the Java records in eu.ecotopia.backend.common.dto.
 */

export interface BackendSpeechResponse {
  extractedPromises: BackendPromiseResponse[];
  contradictions: BackendContradictionResponse[];
  citizenReactions: BackendCitizenReactionResponse[];
}

export interface BackendPromiseResponse {
  id: number;
  text: string;
  roundMade: number;
  deadline: number | null;
  status: string;
  citizenName: string | null;
}

export interface BackendContradictionResponse {
  description: string;
  speechQuote: string;
  contradictingAction: string;
  severity: string;
}

export interface BackendCitizenReactionResponse {
  citizenName: string;
  dialogue: string;
  tone: string;
  approvalDelta: number;
}

export interface BackendResourcesResponse {
  ecology: number;
  economy: number;
  research: number;
}

export interface BackendTileResponse {
  x: number;
  y: number;
  tileType: string;
  roundsInCurrentState: number;
}

export interface BackendCitizenResponse {
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

export interface BackendGameRoundResponse {
  roundNumber: number;
  remainingActions: number;
  speechText: string | null;
}

export interface BackendGameStateResponse {
  id: number;
  currentRound: number;
  status: string;
  resultRank: string | null;
  defeatReason: string | null;
  resources: BackendResourcesResponse;
  tiles: BackendTileResponse[];
  citizens: BackendCitizenResponse[];
  promises: BackendPromiseResponse[];
  currentRoundInfo: BackendGameRoundResponse | null;
  createdAt: string;
  updatedAt: string;
}
