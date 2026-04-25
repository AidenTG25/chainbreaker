import { Activity, ShieldCheck, Zap } from 'lucide-react';

interface TopBarProps {
  activeThreats: number;
  totalFlows: number;
  isConnected: boolean;
}

export function TopBar({ activeThreats, totalFlows, isConnected }: TopBarProps) {
  return (
    <div className="absolute top-0 left-0 w-full z-20 flex items-center justify-between px-6 py-4 pointer-events-auto">
      {/* Brand logo */}
      <div className="flex items-center gap-3 bg-[#0a0a0a]/80 backdrop-blur-md border border-white/5 py-2 px-4 rounded-full">
        <Zap className="h-5 w-5 text-cyan-500" />
        <span className="font-semibold text-slate-100 tracking-wide text-sm">ChainBreaker</span>
      </div>

      {/* Stats cluster */}
      <div className="flex items-center gap-4">
        {/* Total Flows */}
        <div className="flex items-center gap-3 bg-[#0a0a0a]/80 backdrop-blur-md border border-white/5 py-2 px-4 rounded-full text-sm">
          <Activity className="h-4 w-4 text-slate-400" />
          <span className="text-slate-300 font-mono">{totalFlows.toLocaleString()}</span>
          <span className="text-slate-500 text-xs uppercase tracking-wider">Flows</span>
        </div>

        {/* Active Threats */}
        <div className="flex items-center gap-3 bg-[#0a0a0a]/80 backdrop-blur-md border border-red-500/20 py-2 px-4 rounded-full text-sm">
          <ShieldCheck className={`h-4 w-4 ${activeThreats > 0 ? 'text-red-500' : 'text-green-500'}`} />
          <span className={`${activeThreats > 0 ? 'text-red-400' : 'text-green-400'} font-mono`}>{activeThreats}</span>
          <span className="text-slate-500 text-xs uppercase tracking-wider">Threats</span>
        </div>

        {/* Connection Status */}
        <div className="flex items-center gap-2 bg-[#0a0a0a]/80 backdrop-blur-md border border-white/5 py-2 px-4 rounded-full text-sm">
          <div className="relative flex h-2 w-2">
            {isConnected && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
          </div>
          <span className="text-slate-400 text-xs uppercase tracking-wider">
            {isConnected ? 'Live' : 'Paused'}
          </span>
        </div>
      </div>
    </div>
  );
}
