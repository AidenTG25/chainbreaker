# ChainBreaker — Architecture

## System Overview

ChainBreaker is a graph-driven cyber incident detection, forensic analysis, and automated kill chain interruption platform. It combines ML-based intrusion detection with a live Neo4j attack graph and (major phase) a reinforcement learning agent for automated response.

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│           React Dashboard (Frontend)             │
│   Attack Graph | Forensics | Alerts | RL Agent   │
└──────────────────────┬──────────────────────────┘
                       │ REST / WebSocket
┌──────────────────────▼──────────────────────────┐
│             FastAPI Backend                      │
│  Routes: Graph | Forensics | Alerts | ML | Agent │
└──────┬──────────┬──────────┬──────────────────────┘
       │          │          │
┌──────▼──┐  ┌────▼────┐  ┌─▼────────────────────┐
│   ML    │  │ Temporal │  │   Forensic Engine   │
│ Detector│  │ (Spark)  │  │  Timeline | Blast   │
│ RF+XGB+IF│ │ Spray   │  │   Path | Report    │
└──────┬──┘  └────┬────┘  └──────────────────────┘
       │          │
┌──────▼──────────▼──────────────────────────────┐
│        Neo4j Graph (Single Source of Truth)   │
│ Host | AttackEvent | KillChainStage | AgentAction│
└───────────────────────────────────────────────┘
       ▲          ▲
┌──────┴───┐ ┌────▼─────────┐
│Ingestion │ │ RL Agent Env │
│Kafka/CSV │ │ MaskablePPO  │
└──────────┘ └──────────────┘
```

## Data Flow

1. **Ingestion**: Network flows arrive via Kafka (live) or CSV batch processor
2. **Feature Extraction**: 71 features derived per flow (64 CICFlowMeter + 7 derived)
3. **ML Detection**: Ensemble of RF, XGBoost, Isolation Forest predicts kill chain stage
4. **Graph Writing**: Detection results written to Neo4j as AttackEvent + KillChainStage nodes
5. **Forensics**: Graph traversals reconstruct attack paths, blast radius, timelines
6. **RL Agent** (major): Observes graph metrics → stage-conditioned action → writes AgentAction

## Key Design Decisions

- **Unified Graph**: Same Neo4j written by ML, read by RL, written by RL
- **Stage-Conditioned Masking**: Action space restricted per kill chain stage via MaskablePPO
- **Graph-Topology RL**: Observation vector derived entirely from Neo4j graph metrics
- **MITRE Alignment**: All stages mapped to ATT&CK tactics via tactic_aligner
