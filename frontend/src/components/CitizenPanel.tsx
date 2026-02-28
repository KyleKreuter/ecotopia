import React from 'react';
import type { Citizen, CitizenTone } from '../types/game';

interface CitizenPanelProps {
  citizens: Citizen[];
}

const TONE_COLORS: Record<CitizenTone, string> = {
  angry: '#ef4444',
  hopeful: '#4ade80',
  sarcastic: '#a78bfa',
  desperate: '#f97316',
  grateful: '#34d399',
  suspicious: '#fbbf24',
  neutral: '#9ca3af',
};

function CitizenCard({ citizen }: { citizen: Citizen }): React.JSX.Element {
  const approvalColor =
    citizen.approval >= 60 ? '#4ade80' : citizen.approval >= 40 ? '#fbbf24' : '#ef4444';

  return (
    <div className="citizen-card">
      <div className="citizen-header">
        <strong>{citizen.name}</strong>
        {citizen.isCore && <span className="core-badge">Core</span>}
      </div>
      <div className="citizen-role">{citizen.role}</div>
      <div className="citizen-approval">
        <span>Approval</span>
        <div className="approval-track">
          <div
            className="approval-fill"
            style={{ width: `${citizen.approval}%`, backgroundColor: approvalColor }}
          />
        </div>
        <span className="approval-value">{citizen.approval}%</span>
      </div>
      <div className="citizen-dialogue" style={{ borderLeftColor: TONE_COLORS[citizen.tone] }}>
        "{citizen.dialogue}"
      </div>
      <div className="citizen-tone" style={{ color: TONE_COLORS[citizen.tone] }}>
        {citizen.tone}
      </div>
    </div>
  );
}

export function CitizenPanel({ citizens }: CitizenPanelProps): React.JSX.Element {
  return (
    <div className="citizen-panel">
      <h3>Citizens</h3>
      {citizens.map((c) => (
        <CitizenCard key={c.name} citizen={c} />
      ))}
    </div>
  );
}
