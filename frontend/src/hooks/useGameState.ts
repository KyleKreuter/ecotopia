import { useCallback, useEffect, useState } from 'react';
import type { GameState } from '../types/game';
import { getGameState, startNewGame, submitSpeech } from '../services/api';

interface UseGameStateReturn {
  state: GameState | null;
  loading: boolean;
  submitting: boolean;
  error: string | null;
  handleSpeechSubmit: (speech: string) => Promise<void>;
  handleNewGame: () => Promise<void>;
  dismissContradiction: (index: number) => void;
}

export function useGameState(): UseGameStateReturn {
  const [state, setState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getGameState()
      .then(setState)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSpeechSubmit = useCallback(
    async (speech: string): Promise<void> => {
      if (!state || state.gameOver) return;
      setSubmitting(true);
      setError(null);
      try {
        const newState = await submitSpeech(speech, state);
        setState(newState);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to submit speech');
      } finally {
        setSubmitting(false);
      }
    },
    [state]
  );

  const handleNewGame = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const freshState = await startNewGame();
      setState(freshState);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start new game');
    } finally {
      setLoading(false);
    }
  }, []);

  const dismissContradiction = useCallback(
    (index: number): void => {
      if (!state) return;
      setState({
        ...state,
        contradictions: state.contradictions.filter((_, i) => i !== index),
      });
    },
    [state]
  );

  return {
    state,
    loading,
    submitting,
    error,
    handleSpeechSubmit,
    handleNewGame,
    dismissContradiction,
  };
}
