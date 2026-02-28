import React from 'react';
interface RoundInfoProps {
  round: number;
  maxRounds: number;
}

/** Displays current round and simulated year (each round = 5 years from 2025). */
export function RoundInfo({ round, maxRounds }: RoundInfoProps): React.JSX.Element {
  const year = 2025 + (round - 1) * 5;
  const endYear = year + 4;

  return (
    <div className="round-info">
      <h2>Round {round} / {maxRounds}</h2>
      <span className="round-year">{year} - {endYear}</span>
    </div>
  );
}
