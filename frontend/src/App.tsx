import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import AttackGraph from './components/AttackGraph';
import { KillChainTimeline } from './components/KillChainTimeline';
import { HostTable } from './components/HostTable';
import { AlertCard } from './components/AlertCard';
import { StageProgress } from './components/StageProgress';
import { graphApi, forensicsApi, alertsApi } from './api/client';
import type { Host, BlastRadius, Alert, ForensicTimelineItem, AgentAction, KillChainStageData } from './types';

const queryClient = new QueryClient();

function Navbar() {
  return (
    <nav className="bg-slate-900 border-b border-slate-700 px-6 py-3 flex items-center gap-6">
      <h1 className="text-xl font-bold text-cyan-400">ChainBreaker</h1>
      <Link to="/" className="text-gray-300 hover:text-white">Dashboard</Link>
      <Link to="/forensic" className="text-gray-300 hover:text-white">Forensics</Link>
      <Link to="/alerts" className="text-gray-300 hover:text-white">Alerts</Link>
      <Link to="/agent" className="text-gray-300 hover:text-white">RL Agent</Link>
    </nav>
  );
}

interface KillChainSummary {
  [key: string]: {
    active?: number;
    contained?: number;
    completed?: number;
    total?: number;
  };
}

interface StageData {
  stage?: string;
  status?: string;
}

function Dashboard() {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [blastRadius, setBlastRadius] = useState<BlastRadius | null>(null);
  const [killChain, setKillChain] = useState<KillChainSummary>({});
  const [stages, setStages] = useState<StageData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hostsRes, blastRes, killChainRes, stagesRes] = await Promise.all([
          graphApi.getHosts(50),
          forensicsApi.getBlastRadius(),
          forensicsApi.getKillChainSummary(),
          graphApi.getStages(),
        ]);
        setHosts(hostsRes.data?.hosts || []);
        setBlastRadius(blastRes.data);
        setKillChain(killChainRes.data || {});
        setStages(stagesRes.data?.stages || []);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      }
    };
    fetchData();
  }, []);

  const activeStages = Object.entries(killChain)
    .filter(([, v]) => (v?.active || 0) > 0)
    .map(([k, v]) => ({ stage: k, count: v?.active || 0 }));

  const severityLevel = blastRadius?.severity_level || 'LOW';

  return (
    <div className="flex gap-4 p-4 h-[calc(100vh-64px)]">
      <div className="flex-1 bg-slate-900 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-lg font-semibold text-white">Attack Graph</h2>
        </div>
        <div className="h-[calc(100%-56px)]">
          <AttackGraph />
        </div>
      </div>
      <div className="w-80 flex flex-col gap-4">
        <div className="bg-slate-900 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Blast Radius</h3>
          <div className="text-3xl font-bold text-red-400">{blastRadius?.total_compromised || 0}</div>
          <div className="text-sm text-gray-400">compromised hosts</div>
          <div className={`mt-2 text-lg font-semibold ${
            severityLevel === 'CRITICAL' ? 'text-red-400' :
            severityLevel === 'HIGH' ? 'text-orange-400' :
            'text-yellow-400'
          }`}>{severityLevel}</div>
        </div>
        <div className="bg-slate-900 rounded-lg p-4 flex-1 overflow-auto">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Kill Chain Status</h3>
          <StageProgress activeStages={activeStages} />
          <KillChainTimeline stages={stages.slice(0, 8)} />
        </div>
        <div className="bg-slate-900 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Host Overview</h3>
          <HostTable hosts={hosts.slice(0, 10)} />
        </div>
      </div>
    </div>
  );
}

interface BlastRadiusData {
  total_compromised?: number;
  severity_level?: string;
}

function Forensic() {
  const [timeline, setTimeline] = useState<ForensicTimelineItem[]>([]);
  const [blastRadius, setBlastRadius] = useState<BlastRadiusData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [timelineRes, blastRes] = await Promise.all([
          forensicsApi.getTimeline(100),
          forensicsApi.getBlastRadius(),
        ]);
        setTimeline(timelineRes.data?.timeline || []);
        setBlastRadius(blastRes.data);
      } catch (err) {
        console.error('Failed to fetch forensics data:', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Forensic Analysis</h2>
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-2">Blast Radius</h3>
          <p className="text-3xl text-red-400">{blastRadius?.total_compromised || 0} hosts</p>
          <p className="text-gray-400">Severity: {blastRadius?.severity_level || 'N/A'}</p>
        </div>
      </div>
      <div className="bg-slate-900 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Attack Timeline</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-slate-700">
                <th className="px-3 py-2 text-left">Time</th>
                <th className="px-3 py-2 text-left">Stage</th>
                <th className="px-3 py-2 text-left">Source</th>
                <th className="px-3 py-2 text-left">Destination</th>
                <th className="px-3 py-2 text-left">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {timeline.map((item) => (
                <tr key={item.event_id || Math.random()} className="border-b border-slate-800 hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-gray-400">{item.timestamp || 'N/A'}</td>
                  <td className="px-3 py-2 text-red-400">{item.stage || 'N/A'}</td>
                  <td className="px-3 py-2 font-mono text-blue-400">{item.source_ip || 'N/A'}</td>
                  <td className="px-3 py-2 font-mono text-red-400">{item.dest_ip || 'N/A'}</td>
                  <td className="px-3 py-2 text-green-400">{((item.confidence || 0) * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await alertsApi.getAlerts();
        setAlerts(res.data?.alerts || []);
      } catch (err) {
        console.error('Failed to fetch alerts:', err);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Security Alerts</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {alerts.map((alert) => (
          <AlertCard key={alert.alert_id || Math.random()} alert={alert} />
        ))}
      </div>
    </div>
  );
}

interface AgentStatus {
  agent_active?: boolean;
  mode?: string;
}

function Agent() {
  const [status, setStatus] = useState<AgentStatus>({});
  const [actions, setActions] = useState<AgentAction[]>([]);

  useEffect(() => {
    const fetchAgentData = async () => {
      try {
        const { agentApi } = await import('./api/client');
        const [statusRes, actionsRes] = await Promise.all([
          agentApi.getStatus(),
          agentApi.getActions(),
        ]);
        setStatus(statusRes.data || {});
        setActions(actionsRes.data?.actions || []);
      } catch (err) {
        console.error('Failed to fetch agent data:', err);
      }
    };
    fetchAgentData();
  }, []);

  const isActive = status.agent_active || false;
  const mode = status.mode || 'N/A';

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-6">RL Agent</h2>
      <div className="bg-slate-900 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-white">Agent Status</h3>
        <p className="text-green-400 mt-2">Active: {String(isActive)}</p>
        <p className="text-gray-400 mt-1">Mode: {mode}</p>
      </div>
      <div className="bg-slate-900 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Action Log</h3>
        {actions.length === 0 ? (
          <p className="text-gray-500">No actions taken yet.</p>
        ) : (
          actions.map((action) => (
            <div key={action.action_id || Math.random()} className="p-2 border-b border-slate-800 text-sm">
              {JSON.stringify(action)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-950">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/forensic" element={<Forensic />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/agent" element={<Agent />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}