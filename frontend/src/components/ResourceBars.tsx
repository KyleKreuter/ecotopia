import React from 'react';
interface ResourceBarsProps {
  ecology: number;
  economy: number;
  research: number;
}

interface BarConfig {
  label: string;
  value: number;
  color: string;
}

function ResourceBar({ label, value, color }: BarConfig): React.JSX.Element {
  return (
    <div className="resource-bar">
      <div className="resource-label">
        <span>{label}</span>
        <span className="resource-value">{value}%</span>
      </div>
      <div className="resource-track">
        <div
          className="resource-fill"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export function ResourceBars({ ecology, economy, research }: ResourceBarsProps): React.JSX.Element {
  const bars: BarConfig[] = [
    { label: 'Ecology', value: ecology, color: '#4ade80' },
    { label: 'Economy', value: economy, color: '#fbbf24' },
    { label: 'Research', value: research, color: '#60a5fa' },
  ];

  return (
    <div className="resource-bars">
      {bars.map((bar) => (
        <ResourceBar key={bar.label} {...bar} />
      ))}
    </div>
  );
}
