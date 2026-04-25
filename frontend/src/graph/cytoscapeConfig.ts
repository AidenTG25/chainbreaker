import { Stylesheet } from 'cytoscape';

export const darkThemeColors = {
  background: '#0a0a0a',
  nodeLabel: '#a1a1aa',
  edgeLabel: '#52525b',
  
  // Status Colors
  benign: '#22c55e',       // green
  suspicious: '#eab308',   // yellow
  attack: '#ef4444',       // red
  neutral: '#3f3f46',      // gray
  
  // Edge Colors
  edgeBase: '#27272a',
  edgeActive: '#fbbf24',
};

// Cytoscape stylesheet tailored for a high-end, minimal look
export const cytoscapeStylesheet: Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'width': 'data(size)',
      'height': 'data(size)',
      'background-color': 'data(color)',
      'label': 'data(label)',
      'color': darkThemeColors.nodeLabel,
      'font-size': '10px',
      'font-family': 'Inter, sans-serif',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'text-margin-y': 6,
      'border-width': 1,
      'border-color': 'rgba(255, 255, 255, 0.1)',
      'transition-property': 'background-color, width, height, border-width',
      'transition-duration': 300 as any, // Cytoscape JS syntax quirk for ms
    }
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 2,
      'border-color': '#fff',
      'shadow-blur': 10,
      'shadow-color': 'data(color)',
      'shadow-opacity': 0.8,
    }
  },
  {
    selector: 'edge',
    style: {
      'width': (ele) => ele.data('suspicious') ? 2 : 1,
      'line-color': (ele) => ele.data('suspicious') ? darkThemeColors.edgeActive : darkThemeColors.edgeBase,
      'curve-style': 'bezier',
      'opacity': 0.6,
      'transition-property': 'line-color, width, opacity',
      'transition-duration': 300 as any,
    }
  },
  {
    selector: 'edge:selected',
    style: {
      'opacity': 1,
      'width': 2,
      'line-color': '#fff',
    }
  },
  {
    selector: '.pulse',
    style: {
      'border-width': 4,
      'border-color': 'data(color)',
      'border-opacity': 0.6,
    }
  }
];

// Continuous layout setup for real-time visualization
export const layoutConfig = {
  name: 'cose',
  animate: true,
  animationDuration: 500,
  refresh: 20,
  fit: true,
  padding: 40,
  randomize: false,
  nodeRepulsion: 400000,
  idealEdgeLength: 100,
  edgeElasticity: 100,
  gravity: 1,
  numIter: 1000,
  initialTemp: 200,
  coolingFactor: 0.95,
  minTemp: 1.0,
};
