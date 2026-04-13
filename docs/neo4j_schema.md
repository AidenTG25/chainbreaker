# Neo4j Graph Schema Reference

## Node Types

### Host
| Property | Type | Description |
|----------|------|-------------|
| ip | string | Unique IP address |
| hostname | string | Hostname |
| role | string | Network role (workstation, server, etc.) |
| compromise_status | string | clean/suspected/compromised/contained |
| first_seen | datetime | First seen timestamp |
| last_seen | datetime | Last activity timestamp |
| os_type | string | Operating system |
| services | list | Running services |

### AttackEvent
| Property | Type | Description |
|----------|------|-------------|
| event_id | string | Unique UUID |
| stage | string | ATT&CK kill chain stage |
| timestamp | datetime | Event timestamp |
| confidence | float | ML prediction confidence (0-1) |
| source_ip | string | Attacker IP |
| dest_ip | string | Victim IP |
| protocol | string | Network protocol |
| attack_label | string | Raw ML label |
| ml_model | string | Model that produced detection |
| mitre_tactics | list | MITRE tactic IDs |

### KillChainStage
| Property | Type | Description |
|----------|------|-------------|
| stage_id | string | Composite: {ip}_{stage} |
| stage | string | Stage name |
| host_ip | string | Associated host |
| status | string | active/contained/completed |
| first_detected | datetime | First detection time |
| last_updated | datetime | Last update time |
| containment_attempts | int | Number of containment attempts |
| dwell_time_seconds | float | Time in this stage |
| mitre_tactic_ids | list | MITRE tactic IDs |

### AgentAction
| Property | Type | Description |
|----------|------|-------------|
| action_id | string | Unique UUID |
| action_type | string | block_ip/isolate_host/kill_process/etc. |
| stage | string | Kill chain stage |
| host_ip | string | Target host |
| timestamp | datetime | Action timestamp |
| success | boolean | Action outcome |
| reason | string | Reason for action |

## Edge Types

| Edge | From | To | Properties |
|------|------|----|------------|
| COMMUNICATES_WITH | Host | Host | first_seen, last_seen, flow_count, total_bytes, suspicious |
| TRIGGERED_BY | AttackEvent | Host | timestamp, confidence |
| ON_HOST | KillChainStage | Host | — |
| PROGRESSED_TO | KillChainStage | KillChainStage | timestamp, from_stage, to_stage, dwell_time_seconds |
| PRECEDED_BY | AgentAction | AgentAction | timestamp, reason |
| TARGETED_HOST | AgentAction | Host | — |
| CAUSED | Alert | AttackEvent | timestamp, event_count |
| ASSET_OF | Asset | Host | role |
| SOURCE_OF | Host | AttackEvent | timestamp |
