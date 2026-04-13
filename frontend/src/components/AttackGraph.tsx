import { useEffect, useRef, useState } from 'react';
import ForceGraph2DImpl from 'react-force-graph-2d';
import { graphApi } from '../api/client';
import { Host, STAGE_COLORS } from '../types';

const ForceGraph2D = ForceGraph2DImpl || ((props: React.ComponentProps<typeof import('react-force-graph-2d').default>) => null);

interface GraphNode {
  id: string;
  ip: string;
  role: string;
  status: string;
  type: 'host' | 'event';
}

interface GraphLink {
  source: string;
  target: string;
  suspicious?: boolean;
  flow_count?: number;
}

interface HostData {
  ip: string;
  role: string;
  compromise_status: string;
  hostname?: string;
  first_seen?: string;
  last_seen?: string;
  connected_peers?: number;
}

interface EdgeData {
  src_ip: string;
  dst_ip: string;
  suspicious?: boolean;
  flow_count?: number;
  first_seen?: string;
  last_seen?: string;
  total_bytes?: number;
  protocols?: string[];
}

export function AttackGraph() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [links, setLinks] = useState<GraphLink[]>([]);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const loadGraph = async () => {
    try {
      const [hostsRes, edgesRes] = await Promise.all([
        graphApi.getHosts(100),
        graphApi.getEdges(200),
      ]);

      const hosts: HostData[] = hostsRes.data?.hosts || [];
      const edges: EdgeData[] = edgesRes.data?.edges || [];

      const hostNodes: GraphNode[] = hosts.map((h: HostData) => ({
        id: h.ip,
        ip: h.ip,
        role: h.role || 'unknown',
        status: h.compromise_status || 'clean',
        type: 'host' as const,
      }));

      const graphLinks: GraphLink[] = edges.map((e: EdgeData) => ({
        source: e.src_ip || '',
        target: e.dst_ip || '',
        suspicious: e.suspicious || false,
        flow_count: e.flow_count || 0,
      })).filter((l: GraphLink) => l.source && l.target);

      setNodes(hostNodes);
      setLinks(graphLinks);
    } catch (err) {
      console.error('Failed to load graph', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
    const interval = setInterval(loadGraph, 30000);
    return () => clearInterval(interval);
  }, []);

  const getNodeColor = (node: GraphNode): string => {
    if (node.type === 'host') {
      return STAGE_COLORS[node.status] || '#6b7280';
    }
    return '#ef4444';
  };

  const getNodeSize = (node: GraphNode): number => {
    if (node.type === 'host') {
      return node.status === 'compromised' ? 12 : 6;
    }
    return 5;
  };

  const getLinkColor = (link: GraphLink): string => {
    return link.suspicious ? '#ef4444' : '#94a3b8';
  };

  const getLinkWidth = (link: GraphLink): number => {
    return link.suspicious ? 3 : 1;
  };

  const getNodeLabel = (node: GraphNode): string => {
    return `${node.ip} (${node.role}) - ${node.status}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <span className="text-gray-400">Loading graph...</span>
      </div>
    );
  }

  if (!ForceGraph2D) {
    return (
      <div className="flex items-center justify-center h-full">
        <span className="text-yellow-400">Graph library not loaded. Check installation.</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full">
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes, links }}
        nodeColor={getNodeColor}
        nodeVal={getNodeSize}
        linkColor={getLinkColor}
        linkWidth={getLinkWidth}
        linkDirectionalArrowLength={4}
        nodeLabel={getNodeLabel}
        backgroundColor="#0f172a"
        width={dimensions.width}
        height={dimensions.height}
      />
    </div>
  );
}

export default AttackGraph;