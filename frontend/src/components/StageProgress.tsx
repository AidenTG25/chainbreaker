import { STAGE_COLORS } from '../types';

interface ActiveStageData {
  stage: string;
  count: number;
}

interface StageProgressProps {
  activeStages: ActiveStageData[];
}

export function StageProgress({ activeStages }: StageProgressProps) {
  const total = activeStages.reduce((sum: number, s: ActiveStageData) => sum + s.count, 0);

  if (activeStages.length === 0) {
    return (
      <div className="flex flex-col gap-3 p-4">
        <p className="text-sm text-gray-500">No active stages detected.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-4">
      {activeStages.map(({ stage, count }: ActiveStageData) => {
        const percentage = total > 0 ? (count / total) * 100 : 0;
        const stageColor = STAGE_COLORS[stage] || '#6b7280';
        
        return (
          <div key={stage}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-300">{stage.replace(/_/g, ' ')}</span>
              <span className="text-sm text-gray-500">{count}</span>
            </div>
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${percentage}%`,
                  backgroundColor: stageColor,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}