import React, { useState } from 'react';
import { useGameState } from '../hooks/useGameState';
import { CityGrid } from './CityGrid';
import { CitizenPanel } from './CitizenPanel';
import { ContradictionAlert } from './ContradictionAlert';
import { GameOverScreen } from './GameOverScreen';
import { PromiseTracker } from './PromiseTracker';
import { ResourceBars } from './ResourceBars';
import { RoundInfo } from './RoundInfo';
import { SpeechInput } from './SpeechInput';
import { StartScreen } from './StartScreen';

export function GameBoard(): React.JSX.Element {
  const {
    state,
    loading,
    submitting,
    error,
    handleSpeechSubmit,
    handleNewGame,
    dismissContradiction,
  } = useGameState();

  const [started, setStarted] = useState<boolean>(false);

  const onStartGame = async (): Promise<void> => {
    await handleNewGame();
    setStarted(true);
  };

  if (!started) {
    return <StartScreen onStart={() => void onStartGame()} loading={loading} />;
  }

  if (loading || !state) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
        <p>Loading Ecotopia...</p>
      </div>
    );
  }

  if (state.gameOver) {
    return (
      <GameOverScreen
        state={state}
        onPlayAgain={() => void onStartGame()}
      />
    );
  }

  const roundProgress = ((state.round - 1) / (state.maxRounds - 1)) * 100;

  return (
    <div className="game-board">
      <ContradictionAlert
        contradictions={state.contradictions}
        onDismiss={dismissContradiction}
      />

      <header className="game-header">
        <h1>Ecotopia</h1>
        <div className="header-right">
          <RoundInfo round={state.round} maxRounds={state.maxRounds} />
          <div className="round-progress-bar">
            <div
              className="round-progress-fill"
              style={{ width: `${roundProgress}%` }}
            />
          </div>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <ResourceBars
        ecology={state.ecology}
        economy={state.economy}
        research={state.research}
      />

      <div className="game-main">
        <div className="game-left">
          <CityGrid grid={state.grid} />
          <SpeechInput
            onSubmit={handleSpeechSubmit}
            disabled={state.gameOver}
            submitting={submitting}
          />
        </div>
        <div className="game-right">
          <CitizenPanel citizens={state.citizens} />
          <PromiseTracker promises={state.promises} />
        </div>
      </div>
    </div>
  );
}
