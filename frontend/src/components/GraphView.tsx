import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import CytoscapeComponent from 'react-cytoscapejs';
import { cytoscapeStylesheet, layoutConfig, darkThemeColors } from '../graph/cytoscapeConfig';
import type { WsMessage, NodeEvent } from '../hooks/useWebSocket';

interface GraphViewProps {
  wsMessage: WsMessage | null;
  onNodeSelect: (node: NodeEvent | null) => void;
}

export const GraphView = React.memo(({ wsMessage, onNodeSelect }: GraphViewProps) => {
  const cyRef = useRef<cytoscape.Core | null>(null);

  // Initialize graph with some structural dummy data if needed,
  // or just empty array. 
  const initialElements = [
    { data: { id: 'core-router', label: 'Core Router', status: 'benign', size: 20, color: darkThemeColors.benign } }
  ];

  // Handle incoming WebSocket messages incrementally
  useEffect(() => {
    if (!wsMessage || !cyRef.current) return;
    
    const cy = cyRef.current;
    
    cy.batch(() => {
      // Add or update nodes
      wsMessage.nodes.forEach(node => {
        const existingNode = cy.getElementById(node.id);
        const color = darkThemeColors[node.status] || darkThemeColors.neutral;
        // Map risk score to size (mock scale: base 10 + risk_score/5)
        const size = 10 + (node.risk_score / 5);

        if (existingNode.length > 0) {
          existingNode.data({
            status: node.status,
            risk_score: node.risk_score,
            color,
            size
          });

          // Pulse effect if attack
          if (node.status === 'attack') {
            existingNode.flashClass('pulse', 1000);
          }
        } else {
          cy.add({
            group: 'nodes',
            data: {
              id: node.id,
              label: node.label,
              status: node.status,
              risk_score: node.risk_score,
              color,
              size
            }
          });
        }
      });

      // Add or update edges
      wsMessage.edges.forEach(edge => {
        const edgeId = `${edge.source}-${edge.target}`;
        const existingEdge = cy.getElementById(edgeId);
        
        if (existingEdge.length > 0) {
          existingEdge.data({ suspicious: edge.suspicious });
        } else {
          // Double check nodes exist
          if (cy.getElementById(edge.source).length > 0 && cy.getElementById(edge.target).length > 0) {
            cy.add({
              group: 'edges',
              data: {
                id: edgeId,
                source: edge.source,
                target: edge.target,
                suspicious: edge.suspicious
              }
            });
          }
        }
      });
    });

    // We can run layout incrementally if needed, but for performance,
    // we often just rely on position updates or continuous force layouts.
    // For now we just let cose layout settle if we need a refresh
    // cy.layout(layoutConfig).run();
  }, [wsMessage]);

  return (
    <div className="absolute inset-0 bg-[#0a0a0a]">
      <CytoscapeComponent
        elements={initialElements}
        stylesheet={cytoscapeStylesheet}
        style={{ width: '100%', height: '100%' }}
        cy={(cy) => {
          cyRef.current = cy;
          
          // Selection handler
          cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            const nodeData = node.data();
            onNodeSelect({
              id: nodeData.id,
              label: nodeData.label,
              status: nodeData.status,
              risk_score: nodeData.risk_score || 0
            });
          });

          // Deselect handler
          cy.on('tap', (evt) => {
            if (evt.target === cy) {
              onNodeSelect(null);
            }
          });
          
          // Initial layout
          cy.layout(layoutConfig).run();
        }}
      />
    </div>
  );
});

GraphView.displayName = 'GraphView';
