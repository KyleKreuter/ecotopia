import React from 'react';

interface StartScreenProps {
  onStart: () => void;
  loading: boolean;
}

export function StartScreen({ onStart, loading }: StartScreenProps): React.JSX.Element {
  return (
    <div className="start-screen">
      <div className="start-content">
        <h1 className="start-title">ECOTOPIA</h1>
        <p className="start-subtitle">
          Can you save a city on the edge of ecological collapse?
        </p>

        <div className="start-rules">
          <p className="start-rules-text">
            You are the mayor. 7 rounds. Each round = 5 years.
            Make speeches, keep promises, manage ecology, economy and research.
          </p>
        </div>

        <button
          className="start-button"
          onClick={onStart}
          disabled={loading}
        >
          {loading ? 'Starting...' : 'New Game'}
        </button>
      </div>
    </div>
  );
}
