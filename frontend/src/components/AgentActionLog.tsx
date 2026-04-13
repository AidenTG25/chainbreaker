import { AgentAction, STAGE_COLORS } from '../types';

interface Props {
  actions: AgentAction[];
}

export function AgentActionLog({ actions }: Props) {
  const formatTimestamp = (timestamp?: string): string => {
    if (!timestamp) return 'N/A';
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return 'N/A';
    }
  };

  return (
    <div className="flex flex-col gap-2 p-4 max-h-96 overflow-y-auto">
      {actions.length === 0 && (
        <p className="text-gray-500 text-sm">No agent actions recorded.</p>
      )}
      {actions.map((action: AgentAction, index: number) => {
        const stageColor = STAGE_COLORS[action.stage || ''] || '#6b7280';
        const isSuccess = action.success !== undefined && action.success;
        
        return (
          <div
            key={action.action_id || `action-${index}`}
            className="flex items-center gap-3 p-2 rounded bg-slate-800/50 text-sm"
          >
            <span
              className="px-2 py-1 rounded text-xs font-medium text-white"
              style={{ backgroundColor: stageColor }}
            >
              {action.action_type || 'UNKNOWN'}
            </span>
            <span className="text-gray-400 font-mono">{action.host_ip || 'N/A'}</span>
            <span className={`ml-auto text-xs ${isSuccess ? 'text-green-400' : 'text-red-400'}`}>
              {isSuccess ? 'SUCCESS' : 'FAILED'}
            </span>
            <span className="text-xs text-gray-500">{formatTimestamp(action.timestamp)}</span>
          </div>
        );
      })}
    </div>
  );
}