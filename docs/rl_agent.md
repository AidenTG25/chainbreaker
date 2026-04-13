# RL Agent Design (Major Phase)

## Environment: KillChainEnv

Gymnasium environment wrapping the Neo4j graph as state.

**Observation Space** (23 dimensions):
- Blast radius: total_compromised, severity_score, high_value_impact (3)
- Active stage counts: one per kill chain stage (8)
- Host metrics: compromised, suspected, clean, compromise_ratio, suspicion_ratio (5)
- Edge metrics: total_communications, suspicious_edges, suspicious_ratio (3)
- Stage status vector: active + contained per stage (16 → compressed)

**Action Space** (8 discrete actions):
0. block_ip
1. isolate_host
2. kill_process
3. reset_connection
4. block_port
5. quarantine_subnet
6. notify_admin
7. collect_forensics

## Stage-Conditioned Action Masking

Valid actions dynamically conditioned on active kill chain stage:

| Stage | Valid Actions |
|-------|--------------|
| Initial_Access | block_ip, reset_connection, block_port, notify_admin |
| Persistence | isolate_host, kill_process, notify_admin |
| Command_and_Control | block_ip, reset_connection, block_port, quarantine_subnet |
| Discovery | block_ip, block_port, notify_admin |
| Credential_Access | isolate_host, kill_process, notify_admin, collect_forensics |
| Lateral_Movement | block_ip, isolate_host, reset_connection, quarantine_subnet |
| Defense_Evasion | isolate_host, kill_process, quarantine_subnet, collect_forensics |
| Exfiltration | block_ip, reset_connection, quarantine_subnet, collect_forensics |

## Reward Function

Multi-objective reward:
- `+10.0` early interruption (containment at early stage)
- `+5.0` successful containment
- `-8.0` stage progression penalty
- `-5.0 * blast_radius_reduction` per host impact
- `-1.0 * dwell_time_seconds`
- `-2.0` false positive penalty
- `-0.1` per action taken

## Training

- Algorithm: MaskablePPO (sb3-contrib)
- Network: 256-256-128 MLP
- Total timesteps: 500,000
- n_steps: 2048, batch_size: 64
- Compare against rule-based baseline for evaluation
