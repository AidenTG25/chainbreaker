import { Alert, STAGE_COLORS } from '../types';

interface Props {
  alert: Alert;
}

export function AlertCard({ alert }: Props) {
  const severityColors: Record<string, string> = {
    low: 'border-green-500 bg-green-500/10',
    medium: 'border-yellow-500 bg-yellow-500/10',
    high: 'border-orange-500 bg-orange-500/10',
    critical: 'border-red-500 bg-red-500/10',
  };
  
  const severityClass = severityColors[alert.severity] || 'border-gray-500 bg-gray-500/10';
  const stageColor = STAGE_COLORS[alert.stage] || '#6b7280';
  const affectedHostCount = alert.affected_hosts?.length || 0;

  return (
    <div className={`border-l-4 rounded-lg p-4 ${severityClass}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-white">{alert.title || 'Untitled Alert'}</h3>
        <span
          className="px-2 py-1 rounded text-xs font-bold text-white"
          style={{ backgroundColor: stageColor }}
        >
          {alert.stage?.replace(/_/g, ' ') || 'N/A'}
        </span>
      </div>
      <p className="text-sm text-gray-400 mb-2">{alert.description || 'No description'}</p>
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span>Severity: {alert.severity?.toUpperCase() || 'UNKNOWN'}</span>
        <span>Status: {alert.status || 'unknown'}</span>
        <span>Hosts: {affectedHostCount}</span>
      </div>
    </div>
  );
}