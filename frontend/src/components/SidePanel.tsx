import { motion, AnimatePresence } from 'framer-motion';
import { X, Server, Activity, ShieldAlert, Crosshair } from 'lucide-react';
import type { NodeEvent } from '../hooks/useWebSocket';

interface SidePanelProps {
  selectedNode: NodeEvent | null;
  onClose: () => void;
}

export function SidePanel({ selectedNode, onClose }: SidePanelProps) {
  // Translate status to pretty text and color
  const statusConfig = {
    benign: { text: 'Benign', color: 'text-green-400', bg: 'bg-green-400/10' },
    suspicious: { text: 'Suspicious', color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
    attack: { text: 'Attack Detected', color: 'text-red-400', bg: 'bg-red-400/10' },
  };

  return (
    <AnimatePresence>
      {selectedNode && (
        <motion.div
          initial={{ x: '100%', opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: '100%', opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="absolute top-0 right-0 h-full w-96 bg-[#0f0f11]/95 backdrop-blur-xl border-l border-white/5 z-30 shadow-2xl overflow-y-auto"
        >
          <div className="p-6">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-sm uppercase tracking-widest text-slate-500 font-semibold">
                Node Details
              </h2>
              <button 
                onClick={onClose}
                className="p-2 -mr-2 rounded-full hover:bg-slate-800 text-slate-400 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Header info */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-2">
                <Server className="h-6 w-6 text-slate-300" />
                <h3 className="text-2xl font-mono text-slate-100">{selectedNode.id}</h3>
              </div>
              <p className="text-sm text-slate-500">{selectedNode.label}</p>
            </div>

            {/* Status tags */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className={`p-4 rounded-xl border border-white/5 ${statusConfig[selectedNode.status].bg}`}>
                <div className="flex items-center gap-2 mb-2">
                  <ShieldAlert className={`h-4 w-4 ${statusConfig[selectedNode.status].color}`} />
                  <span className="text-xs uppercase tracking-wider text-slate-400">Status</span>
                </div>
                <div className={`font-semibold ${statusConfig[selectedNode.status].color}`}>
                  {statusConfig[selectedNode.status].text}
                </div>
              </div>

              <div className="p-4 rounded-xl border border-white/5 bg-slate-900/50">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="h-4 w-4 text-cyan-400" />
                  <span className="text-xs uppercase tracking-wider text-slate-400">Risk Score</span>
                </div>
                <div className="font-mono text-xl text-slate-200">
                  {selectedNode.risk_score.toFixed(1)}
                  <span className="text-slate-500 text-sm ml-1">/100</span>
                </div>
              </div>
            </div>

            {/* Additional info section (mocked dynamically) */}
            <div className="space-y-6">
              <div>
                <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
                  <Crosshair className="h-3 w-3" />
                  Recent Flows
                </h4>
                <div className="space-y-2">
                  {[1, 2, 3].map((_, i) => (
                    <div key={i} className="flex justify-between items-center p-3 rounded-lg border border-white/5 bg-slate-900/30 text-sm font-mono text-slate-400">
                      <span>{selectedNode.id} &rarr; 10.0.0.{10 + i}</span>
                      <span className="text-slate-600 border border-slate-800 px-2 py-0.5 rounded text-xs select-none">
                        TCP
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
