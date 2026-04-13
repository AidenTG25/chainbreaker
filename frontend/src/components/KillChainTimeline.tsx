import { KILL_CHAIN_STAGES, STAGE_COLORS } from '../types';
import type { KillChainStageData } from '../types';

interface StageProps {
  activeStage?: string;
  stages: KillChainStageData[];
}

export function KillChainTimeline({ stages, activeStage }: StageProps) {
  const getStageStatus = (stageName: string): 'active' | 'contained' | 'completed' | 'none' => {
    const match = stages.find(s => s?.stage === stageName);
    if (!match) return 'none';
    if (match.status === 'active') return 'active';
    if (match.status === 'contained' || match.status === 'completed') return 'contained';
    return 'none';
  };

  return (
    <div className="flex flex-col gap-2 p-4">
      {KILL_CHAIN_STAGES.map((stage) => {
        const status = getStageStatus(stage);
        const isActive = activeStage === stage || status === 'active';
        const isContained = status === 'contained';
        
        const stageColor = STAGE_COLORS[stage] || '#6b7280';
        
        return (
          <div key={stage} className="flex items-center gap-3">
            <div
              className="w-4 h-4 rounded-full"
              style={{
                backgroundColor: isActive
                  ? stageColor
                  : isContained
                  ? '#22c55e'
                  : '#374151',
              }}
            />
            <span className={`text-sm ${isActive ? 'text-white font-medium' : 'text-gray-400'}`}>
              {stage.replace(/_/g, ' ')}
            </span>
            {isActive && <span className="text-xs text-red-400 ml-auto">ACTIVE</span>}
            {isContained && <span className="text-xs text-green-400 ml-auto">CONTAINED</span>}
          </div>
        );
      })}
    </div>
  );
}