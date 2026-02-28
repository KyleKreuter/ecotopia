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

const AVATAR_COLORS: Record<string, string> = {
  angry: '#991b1b',
  hopeful: '#166534',
  sarcastic: '#5b21b6',
  desperate: '#9a3412',
  grateful: '#065f46',
  suspicious: '#92400e',
  neutral: '#374151',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2);
}

function CitizenCard({ citizen }: { citizen: Citizen }): React.JSX.Element {
  const approvalColor =
    citizen.approval >= 60 ? '#4ade80' : citizen.approval >= 40 ? '#fbbf24' : '#ef4444';
  const avatarBg = AVATAR_COLORS[citizen.tone] || AVATAR_COLORS.neutral;

  return (
    <div className="citizen-card">
      <div className="citizen-header">
        <div className="citizen-identity">
          <div className="citizen-avatar" style={{ backgroundColor: avatarBg }}>
            {getInitials(citizen.name)}
          </div>
          <strong>{citizen.name}</strong>
        </div>
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
      <div className="citizen-dialogue">
        &ldquo;{citizen.dialogue}&rdquo;
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
      <h3>Citizens ({citizens.length})</h3>
      {citizens.map((c) => (
        <CitizenCard key={c.name} citizen={c} />
      ))}
    </div>
  );
}
