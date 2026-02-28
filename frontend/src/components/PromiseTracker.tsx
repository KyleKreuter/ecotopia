import React from 'react';
import type { GamePromise, PromiseStatus } from '../types/game';

interface PromiseTrackerProps {
  promises: GamePromise[];
}

const STATUS_COLORS: Record<PromiseStatus, string> = {
  active: '#60a5fa',
  kept: '#4ade80',
  broken: '#ef4444',
};

export function PromiseTracker({ promises }: PromiseTrackerProps): React.JSX.Element {
  if (promises.length === 0) {
    return (
      <div className="promise-tracker">
        <h3>Promises</h3>
        <p className="empty-state">No promises extracted yet.</p>
      </div>
    );
  }

  return (
    <div className="promise-tracker">
      <h3>Promises</h3>
      {promises.map((p) => (
        <div key={p.id} className="promise-card">
          <div className="promise-header">
            <span
              className="promise-status"
              style={{ color: STATUS_COLORS[p.status] }}
            >
              [{p.status.toUpperCase()}]
            </span>
            <span className="promise-type">
              {p.type === 'explicit' ? 'Explicit' : 'Implied'}
            </span>
          </div>
          <div className="promise-text">"{p.text}"</div>
          <div className="promise-meta">
            {p.targetCitizen && <span>To: {p.targetCitizen}</span>}
            {p.deadlineRound && <span>Due: Round {p.deadlineRound}</span>}
            <span>Confidence: {Math.round(p.confidence * 100)}%</span>
          </div>
        </div>
      ))}
    </div>
  );
}
