import type {
  GameState,
  GamePromise,
  Contradiction,
  Citizen,
  CitizenTone,
  ContradictionSeverity,
  PromiseStatus,
  PromiseType,
} from '../types/game';

// Types for Mistral service results

export interface ExtractionResult {
  promises: GamePromise[];
  contradictions: Contradiction[];
}

export interface CitizenReaction {
  citizenName: string;
  dialogue: string;
  tone: string;
  approvalDelta: number;
  referencesPromise: string | null;
}

export interface DynamicCitizen {
  name: string;
  role: string;
  personality: string;
  dialogue: string;
  tone: CitizenTone;
  approval: number;
}

export interface CitizenResult {
  reactions: CitizenReaction[];
  newDynamicCitizens: DynamicCitizen[];
  summary: string;
}

export interface TurnResult {
  extraction: ExtractionResult;
  citizens: CitizenResult;
}

// Config

const MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions';
const DEFAULT_MODEL = 'mistral-small-latest';

function getApiKey(): string | null {
  return import.meta.env.VITE_MISTRAL_API_KEY || null;
}

function getModel(): string {
  return import.meta.env.VITE_MISTRAL_MODEL || DEFAULT_MODEL;
}

/** Returns true when a valid Mistral API key is configured. */
export function isMistralAvailable(): boolean {
  const key = getApiKey();
  return key !== null && key.length > 0;
}

// Mistral API call

interface MistralMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface MistralResponse {
  choices: Array<{
    message: {
      content: string;
    };
  }>;
}

async function callMistral(messages: MistralMessage[]): Promise<string> {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('Mistral API key not configured. Set VITE_MISTRAL_API_KEY.');
  }

  const response = await fetch(MISTRAL_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: getModel(),
      messages,
      temperature: 0.7,
      response_format: { type: 'json_object' },
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Mistral API error ${response.status}: ${errorText}`);
  }

  const data = (await response.json()) as MistralResponse;
  if (!data.choices || data.choices.length === 0) {
    throw new Error('Mistral returned no choices');
  }

  return data.choices[0].message.content;
}

// System prompts

function buildExtractionSystemPrompt(): string {
  return `You are an AI analyst for a political simulation game called Ecotopia.
The player is the mayor of a city balancing ecology, economy, and research.

Analyze the mayor's speech and extract:
1. Promises (explicit or implicit commitments)
2. Contradictions with previous promises or actions

Respond in JSON with this exact structure:
{
  "promises": [
    {
      "text": "description of the promise",
      "type": "explicit" or "implicit",
      "confidence": 0.0 to 1.0,
      "targetCitizen": "citizen name or null",
      "deadlineRound": number or null
    }
  ],
  "contradictions": [
    {
      "description": "what the contradiction is",
      "speechQuote": "relevant quote from the speech",
      "contradictingAction": "what it contradicts",
      "severity": "low", "medium", or "high"
    }
  ]
}

Be thorough but fair. Only flag real contradictions, not minor nuances.`;
}

function buildCitizensSystemPrompt(): string {
  return `You are generating citizen reactions for Ecotopia, a political simulation game.
Citizens react to the mayor's promises and any contradictions found.

Each citizen has a personality that shapes their response.
Reactions should feel natural and reflect their concerns.

Respond in JSON with this exact structure:
{
  "reactions": [
    {
      "citizenName": "name",
      "dialogue": "their response (1-2 sentences)",
      "tone": "angry" | "hopeful" | "sarcastic" | "desperate" | "grateful" | "suspicious" | "neutral",
      "approvalDelta": -20 to +20,
      "referencesPromise": "promise text or null"
    }
  ],
  "newDynamicCitizens": [
    {
      "name": "new citizen name",
      "role": "their role",
      "personality": "brief personality",
      "dialogue": "their first line",
      "tone": "one of the tone values",
      "approval": 30 to 70
    }
  ],
  "summary": "brief 1-sentence summary of overall citizen sentiment"
}

Only add newDynamicCitizens (0-1) if the speech introduces a topic that would logically bring a new stakeholder into the conversation.`;
}

// Game state serialization for prompts

function serializeGameContext(gameState: GameState, speech: string): string {
  const citizenSummary = gameState.citizens
    .map((c) => `- ${c.name} (${c.role}): approval ${c.approval}%, tone: ${c.tone}`)
    .join('\n');

  const existingPromises = gameState.promises
    .map((p) => `- [${p.status}] "${p.text}" (${p.type}, confidence: ${p.confidence})`)
    .join('\n');

  return `Round ${gameState.round}/${gameState.maxRounds}
Resources: Ecology ${gameState.ecology}%, Economy ${gameState.economy}%, Research ${gameState.research}%

Citizens:
${citizenSummary}

Existing promises:
${existingPromises || '(none)'}

Previous contradictions: ${gameState.contradictions.length}

Mayor's speech this round:
"${speech}"`;
}

// Parsing helpers

function parseExtractionResponse(
  raw: string,
  round: number
): ExtractionResult {
  try {
    const parsed = JSON.parse(raw);

    const promises: GamePromise[] = (parsed.promises || []).map(
      (p: Record<string, unknown>, i: number) => ({
        id: `p${round}_${i}_${Date.now()}`,
        text: String(p.text || ''),
        type: (p.type === 'implicit' ? 'implicit' : 'explicit') as PromiseType,
        confidence: Number(p.confidence) || 0.5,
        targetCitizen: p.targetCitizen ? String(p.targetCitizen) : null,
        deadlineRound: p.deadlineRound ? Number(p.deadlineRound) : null,
        status: 'active' as PromiseStatus,
        roundMade: round,
      })
    );

    const contradictions: Contradiction[] = (parsed.contradictions || []).map(
      (c: Record<string, unknown>) => ({
        description: String(c.description || ''),
        speechQuote: String(c.speechQuote || ''),
        contradictingAction: String(c.contradictingAction || ''),
        severity: (['low', 'medium', 'high'].includes(String(c.severity))
          ? String(c.severity)
          : 'medium') as ContradictionSeverity,
      })
    );

    return { promises, contradictions };
  } catch {
    console.warn('Failed to parse extraction response, returning empty result');
    return { promises: [], contradictions: [] };
  }
}

function parseCitizensResponse(raw: string): CitizenResult {
  try {
    const parsed = JSON.parse(raw);

    const reactions: CitizenReaction[] = (parsed.reactions || []).map(
      (r: Record<string, unknown>) => ({
        citizenName: String(r.citizenName || ''),
        dialogue: String(r.dialogue || ''),
        tone: String(r.tone || 'neutral'),
        approvalDelta: Number(r.approvalDelta) || 0,
        referencesPromise: r.referencesPromise ? String(r.referencesPromise) : null,
      })
    );

    const newDynamicCitizens: DynamicCitizen[] = (
      parsed.newDynamicCitizens || []
    ).map((c: Record<string, unknown>) => ({
      name: String(c.name || 'Unknown'),
      role: String(c.role || 'Citizen'),
      personality: String(c.personality || ''),
      dialogue: String(c.dialogue || ''),
      tone: (c.tone || 'neutral') as CitizenTone,
      approval: Number(c.approval) || 50,
    }));

    return {
      reactions,
      newDynamicCitizens,
      summary: String(parsed.summary || 'Citizens react to the speech.'),
    };
  } catch {
    console.warn('Failed to parse citizens response, returning empty result');
    return { reactions: [], newDynamicCitizens: [], summary: 'No reactions generated.' };
  }
}

// Public API

/** Extracts promises and contradictions from the mayor's speech using Mistral. */
export async function extractPromises(
  speech: string,
  gameState: GameState
): Promise<ExtractionResult> {
  const messages: MistralMessage[] = [
    { role: 'system', content: buildExtractionSystemPrompt() },
    { role: 'user', content: serializeGameContext(gameState, speech) },
  ];

  const raw = await callMistral(messages);
  return parseExtractionResponse(raw, gameState.round);
}

/** Generates citizen reactions to the extracted promises and contradictions. */
export async function generateCitizenReactions(
  promises: GamePromise[],
  contradictions: Contradiction[],
  gameState: GameState
): Promise<CitizenResult> {
  const citizenDetails = gameState.citizens
    .map(
      (c) =>
        `- ${c.name} (${c.role}): "${c.personality}", approval: ${c.approval}%`
    )
    .join('\n');

  const promiseSummary = promises
    .map((p) => `- "${p.text}" (${p.type}, confidence: ${p.confidence})`)
    .join('\n');

  const contradictionSummary = contradictions
    .map((c) => `- ${c.description} [${c.severity}]`)
    .join('\n');

  const userMessage = `Citizens in the city:
${citizenDetails}

New promises made this round:
${promiseSummary || '(none)'}

Contradictions detected:
${contradictionSummary || '(none)'}

Round ${gameState.round}/${gameState.maxRounds}
Resources: Ecology ${gameState.ecology}%, Economy ${gameState.economy}%, Research ${gameState.research}%

Generate reactions for each citizen. Consider their personality and current approval.`;

  const messages: MistralMessage[] = [
    { role: 'system', content: buildCitizensSystemPrompt() },
    { role: 'user', content: userMessage },
  ];

  const raw = await callMistral(messages);
  return parseCitizensResponse(raw);
}

/** Processes a full player turn: extract promises then generate citizen reactions. */
export async function processPlayerTurn(
  speech: string,
  gameState: GameState
): Promise<TurnResult> {
  const extraction = await extractPromises(speech, gameState);
  const citizens = await generateCitizenReactions(
    extraction.promises,
    extraction.contradictions,
    gameState
  );
  return { extraction, citizens };
}

/** Applies a TurnResult to the current GameState, returning the updated state. */
export function applyTurnResult(
  currentState: GameState,
  result: TurnResult
): GameState {
  const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
  const newRound = Math.min(currentState.round + 1, currentState.maxRounds);
  const isGameOver = newRound > currentState.maxRounds;

  // Apply citizen reactions
  const updatedCitizens: Citizen[] = currentState.citizens.map((citizen) => {
    const reaction = result.citizens.reactions.find(
      (r) => r.citizenName === citizen.name
    );
    if (!reaction) return citizen;

    return {
      ...citizen,
      approval: clamp(citizen.approval + reaction.approvalDelta, 0, 100),
      dialogue: reaction.dialogue,
      tone: (['angry', 'hopeful', 'sarcastic', 'desperate', 'grateful', 'suspicious', 'neutral'].includes(
        reaction.tone
      )
        ? reaction.tone
        : citizen.tone) as CitizenTone,
    };
  });

  // Add dynamic citizens
  const dynamicCitizens: Citizen[] = result.citizens.newDynamicCitizens.map(
    (dc) => ({
      name: dc.name,
      role: dc.role,
      personality: dc.personality,
      approval: dc.approval,
      dialogue: dc.dialogue,
      tone: dc.tone,
      isCore: false,
    })
  );

  const allCitizens = [...updatedCitizens, ...dynamicCitizens];

  // Merge promises
  const allPromises = [...currentState.promises, ...result.extraction.promises];

  // Merge contradictions
  const allContradictions = [
    ...currentState.contradictions,
    ...result.extraction.contradictions,
  ];

  // Simple resource shifts based on promise themes
  let ecologyDelta = 0;
  let economyDelta = 0;
  let researchDelta = 0;

  for (const p of result.extraction.promises) {
    const text = p.text.toLowerCase();
    if (text.includes('green') || text.includes('eco') || text.includes('forest') || text.includes('clean')) {
      ecologyDelta += 3;
    }
    if (text.includes('job') || text.includes('econom') || text.includes('factory') || text.includes('business')) {
      economyDelta += 3;
    }
    if (text.includes('research') || text.includes('innovat') || text.includes('tech') || text.includes('science')) {
      researchDelta += 3;
    }
  }

  // Contradictions hurt overall trust
  for (const c of result.extraction.contradictions) {
    const penalty = c.severity === 'high' ? -5 : c.severity === 'medium' ? -3 : -1;
    ecologyDelta += penalty;
    economyDelta += penalty;
  }

  let gameResult = currentState.gameResult;
  if (isGameOver) {
    const finalEcology = clamp(currentState.ecology + ecologyDelta, 0, 100);
    const finalEconomy = clamp(currentState.economy + economyDelta, 0, 100);
    gameResult = finalEcology >= 50 && finalEconomy >= 30 ? 'win' : 'lose';
  }

  return {
    ...currentState,
    round: isGameOver ? currentState.maxRounds : newRound,
    ecology: clamp(currentState.ecology + ecologyDelta, 0, 100),
    economy: clamp(currentState.economy + economyDelta, 0, 100),
    research: clamp(currentState.research + researchDelta, 0, 100),
    citizens: allCitizens,
    promises: allPromises,
    contradictions: allContradictions,
    gameOver: isGameOver,
    gameResult,
  };
}
