import React from 'react';
import { useGameState } from '../hooks/useGameState';
import { CityGrid } from './CityGrid';
import { CitizenPanel } from './CitizenPanel';
import { ContradictionAlert } from './ContradictionAlert';
import { PromiseTracker } from './PromiseTracker';
import { ResourceBars } from './ResourceBars';
import { RoundInfo } from './RoundInfo';
import { SpeechInput } from './SpeechInput';

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

  if (loading || !state) {
    return <div className="loading">Loading Ecotopia...</div>;
  }

  if (state.gameOver) {
    const isWin = state.gameResult === 'win';
    return (
      <div className="game-over">
        <h1>{isWin ? 'Victory!' : 'Defeat'}</h1>
        <p>
          {isWin
            ? 'You guided the city through the ecological transition.'
            : 'The city could not survive the collapse. The citizens lost faith.'}
        </p>
        <div className="final-stats">
          <span>Ecology: {state.ecology}%</span>
          <span>Economy: {state.economy}%</span>
          <span>Research: {state.research}%</span>
        </div>
        <button onClick={() => void handleNewGame()}>New Game</button>
      </div>
    );
  }

  return (
    <div className="game-board">
      <ContradictionAlert
        contradictions={state.contradictions}
        onDismiss={dismissContradiction}
      />

      <header className="game-header">
        <h1>Ecotopia</h1>
        <RoundInfo round={state.round} maxRounds={state.maxRounds} />
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
