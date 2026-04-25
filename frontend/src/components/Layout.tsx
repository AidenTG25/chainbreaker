import { useState, useMemo } from 'react';
import { TopBar } from './TopBar';
import { SidePanel } from './SidePanel';
import { GraphView } from './GraphView';
import { useWebSocket, type NodeEvent } from '../hooks/useWebSocket';

export function Layout() {
  const [selectedNode, setSelectedNode] = useState<NodeEvent | null>(null);

  // Connect to the WebSocket (using a placeholder or environment variable URL)
  // Replaces the placeholder with dynamic window location if built in production
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/ws/telemetry';
  const { isConnected, lastMessage } = useWebSocket(wsUrl);

  // We can compute derived stats from the incoming messages,
  // falling back to placeholders if no data yet.
  const activeThreats = useMemo(() => {
    if (!lastMessage) return 0;
    return lastMessage.nodes.filter(n => n.status === 'attack').length;
  }, [lastMessage]);

  const totalFlows = useMemo(() => {
    // If the backend sends an aggregate count, we'd use that.
    // For now we just mock a counter or use edge count.
    if (!lastMessage) return 0;
    return lastMessage.edges.length;
  }, [lastMessage]);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#0a0a0a] font-sans selection:bg-slate-800">
      <TopBar 
        activeThreats={activeThreats} 
        totalFlows={totalFlows} 
        isConnected={isConnected} 
      />
      
      {/* Interactive Core */}
      <GraphView 
        wsMessage={lastMessage} 
        onNodeSelect={setSelectedNode} 
      />

      <SidePanel 
        selectedNode={selectedNode} 
        onClose={() => setSelectedNode(null)} 
      />
    </div>
  );
}
