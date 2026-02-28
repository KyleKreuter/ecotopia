import React from 'react';
import type { GameState } from '../types/game';

interface GameOverScreenProps {
  state: GameState;
  onPlayAgain: () => void;
}

export function GameOverScreen({ state, onPlayAgain }: GameOverScreenProps): React.JSX.Element {
  const isWin = state.gameResult === 'win';
  const promisesKept = state.promises.filter((p) => p.status === 'kept').length;
  const promisesBroken = state.promises.filter((p) => p.status === 'broken').length;
  const totalPromises = state.promises.length;

  return (
    <div className={`game-over-screen ${isWin ? 'game-over-win' : 'game-over-lose'}`}>
      <div className="game-over-content">
        <h1 className="game-over-title">
          {isWin ? 'Victory' : 'Defeat'}
        </h1>

        <p className="game-over-message">
          {isWin
            ? 'You guided the city through the ecological transition. The citizens thrive in a sustainable future.'
            : 'The city could not survive the collapse. The citizens lost faith in your leadership.'}
        </p>

        <div className="game-over-stats">
          <div className="stat-card">
            <span className="stat-label">Ecology</span>
            <span className="stat-value" style={{ color: getStatColor(state.ecology) }}>
              {state.ecology}%
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Economy</span>
            <span className="stat-value" style={{ color: getStatColor(state.economy) }}>
              {state.economy}%
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Research</span>
            <span className="stat-value" style={{ color: getStatColor(state.research) }}>
              {state.research}%
            </span>
          </div>
        </div>

        {totalPromises > 0 && (
          <div className="game-over-promises">
            <h3>Promises</h3>
            <div className="promise-summary">
              <span className="promises-kept">{promisesKept} kept</span>
              <span className="promises-broken">{promisesBroken} broken</span>
              <span className="promises-total">{totalPromises} total</span>
            </div>
          </div>
        )}

        <button className="play-again-button" onClick={onPlayAgain}>
          Play Again
        </button>
      </div>
    </div>
  );
}

function getStatColor(value: number): string {
  if (value >= 60) return '#16a34a';
  if (value >= 30) return '#d97706';
  return '#dc2626';
}
