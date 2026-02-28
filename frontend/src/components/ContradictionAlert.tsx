import React from 'react';
import type { Contradiction, ContradictionSeverity } from '../types/game';

interface ContradictionAlertProps {
  contradictions: Contradiction[];
  onDismiss: (index: number) => void;
}

const SEVERITY_COLORS: Record<ContradictionSeverity, string> = {
  low: '#fbbf24',
  medium: '#f97316',
  high: '#ef4444',
};

export function ContradictionAlert({
  contradictions,
  onDismiss,
}: ContradictionAlertProps): React.JSX.Element | null {
  if (contradictions.length === 0) return null;

  return (
    <div className="contradiction-overlay">
      {contradictions.map((c, i) => (
        <div
          key={i}
          className="contradiction-alert"
          style={{ borderColor: SEVERITY_COLORS[c.severity] }}
        >
          <div className="contradiction-header">
            <span
              className="contradiction-severity"
              style={{ color: SEVERITY_COLORS[c.severity] }}
            >
              CONTRADICTION [{c.severity.toUpperCase()}]
            </span>
            <button className="dismiss-btn" onClick={() => onDismiss(i)}>
              x
            </button>
          </div>
          <p className="contradiction-desc">{c.description}</p>
          <div className="contradiction-details">
            <div>
              <strong>You said:</strong> "{c.speechQuote}"
            </div>
            <div>
              <strong>But also:</strong> "{c.contradictingAction}"
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
