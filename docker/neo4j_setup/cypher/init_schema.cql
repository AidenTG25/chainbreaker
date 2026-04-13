// ============================
// ChainBreaker — Neo4j Schema
// ============================

// Drop existing constraints/indexes (idempotent)
DROP CONSTRAINT host_ip IF EXISTS;
DROP CONSTRAINT attackevent_id IF EXISTS;
DROP CONSTRAINT killchainstage_id IF EXISTS;
DROP CONSTRAINT agentaction_id IF EXISTS;
DROP CONSTRAINT asset_id IF EXISTS;
DROP CONSTRAINT alert_id IF EXISTS;

// ============================
// NODE CONSTRAINTS
// ============================

CREATE CONSTRAINT host_ip FOR (h:Host) REQUIRE h.ip IS UNIQUE;
CREATE CONSTRAINT attackevent_id FOR (a:AttackEvent) REQUIRE a.event_id IS UNIQUE;
CREATE CONSTRAINT killchainstage_id FOR (k:KillChainStage) REQUIRE k.stage_id IS UNIQUE;
CREATE CONSTRAINT agentaction_id FOR (a:AgentAction) REQUIRE a.action_id IS UNIQUE;
CREATE CONSTRAINT asset_id FOR (a:Asset) REQUIRE a.asset_id IS UNIQUE;
CREATE CONSTRAINT alert_id FOR (a:Alert) REQUIRE a.alert_id IS UNIQUE;

// ============================
// NODE INDEXES
// ============================

CREATE INDEX host_hostname_idx FOR (h:Host) ON (h.hostname);
CREATE INDEX host_compromise_status_idx FOR (h:Host) ON (h.compromise_status);
CREATE INDEX host_role_idx FOR (h:Host) ON (h.role);

CREATE INDEX attackevent_stage_idx FOR (a:AttackEvent) ON (a.stage);
CREATE INDEX attackevent_timestamp_idx FOR (a:AttackEvent) ON (a.timestamp);
CREATE INDEX attackevent_confidence_idx FOR (a:AttackEvent) ON (a.confidence);

CREATE INDEX killchainstage_stage_idx FOR (k:KillChainStage) ON (k.stage);
CREATE INDEX killchainstage_status_idx FOR (k:KillChainStage) ON (k.status);
CREATE INDEX killchainstage_host_idx FOR (k:KillChainStage) ON (k.host_ip);

CREATE INDEX agentaction_stage_idx FOR (a:AgentAction) ON (a.stage);
CREATE INDEX agentaction_timestamp_idx FOR (a:AgentAction) ON (a.timestamp);
CREATE INDEX agentaction_action_type_idx FOR (a:AgentAction) ON (a.action_type);

CREATE INDEX alert_severity_idx FOR (a:Alert) ON (a.severity);
CREATE INDEX alert_timestamp_idx FOR (a:Alert) ON (a.timestamp);
CREATE INDEX alert_status_idx FOR (a:Alert) ON (a.status);

CREATE INDEX asset_asset_type_idx FOR (a:Asset) ON (a.asset_type);
CREATE INDEX asset_criticality_idx FOR (a:Asset) ON (a.criticality);

// ============================
// EDGE INDEXES (relationship properties)
// ============================

CREATE INDEX comm_w_timestamp_idx FOR ()-[r:COMMUNICATES_WITH]-() ON (r.first_seen);
CREATE INDEX comm_w_last_seen_idx FOR ()-[r:COMMUNICATES_WITH]-() ON (r.last_seen);
CREATE INDEX comm_w_flow_count_idx FOR ()-[r:COMMUNICATES_WITH]-() ON (r.flow_count);

CREATE INDEX progressed_timestamp_idx FOR ()-[r:PROGRESSED_TO]-() ON (r.timestamp);
CREATE INDEX triggered_timestamp_idx FOR ()-[r:TRIGGERED_BY]-() ON (r.timestamp);

CREATE INDEX preceded_timestamp_idx FOR ()-[r:PRECEDED_BY]-() ON (r.timestamp);
CREATE INDEX caused_timestamp_idx FOR ()-[r:CAUSED]-() ON (r.timestamp);

// ============================
// NODE LABEL DEFINITIONS (documentation)
// ============================

// Host: Network endpoint in the monitored environment
// Properties: ip (string, unique), hostname (string), role (string),
//            compromise_status (enum: clean|suspected|compromised|contained),
//            first_seen (datetime), last_seen (datetime),
//            os_type (string), services (list[string])

// AttackEvent: Single ML-detected attack event
// Properties: event_id (string, unique), stage (string, ATT&CK stage),
//            timestamp (datetime), confidence (float 0-1),
//            source_ip (string), dest_ip (string), protocol (string),
//            attack_label (string), mitre_tactics (list[string]),
//            ml_model (string), feature_hash (string)

// KillChainStage: Aggregated stage status per host
// Properties: stage_id (string, unique), stage (string),
//            host_ip (string), status (enum: active|contained|completed|unknown),
//            first_detected (datetime), last_updated (datetime),
//            containment_attempts (int), dwell_time_seconds (float),
//            mitre_tactic_ids (list[string])

// AgentAction: RL or rule-based action taken in response
// Properties: action_id (string, unique), action_type (string),
//            stage (string), host_ip (string), timestamp (datetime),
//            success (boolean), reason (string),
//            target_ip (string), target_port (int)

// Asset: High-value network asset
// Properties: asset_id (string, unique), name (string),
//            ip (string), asset_type (enum: db_server|domain_controller|
//                     web_server|file_server|engineering_workstation),
//            criticality (enum: low|medium|high|critical),
//            owner (string), department (string)

// Alert: Aggregated incident from multiple events
// Properties: alert_id (string, unique), title (string),
//            severity (enum: low|medium|high|critical),
//            status (enum: open|investigating|contained|resolved),
//            created_at (datetime), updated_at (datetime),
//            affected_hosts (list[string]), affected_assets (list[string]),
//            stage (string), description (string)

// ============================
// EDGE TYPE DEFINITIONS (documentation)
// ============================

// COMMUNICATES_WITH: Bidirectional flow between hosts
// Properties: first_seen (datetime), last_seen (datetime),
//            flow_count (int), total_bytes (int),
//            protocols (list[string]), suspicious (boolean)

// TRIGGERED_BY: KillChainStage caused by AttackEvent
// Properties: timestamp (datetime), confidence (float)

// PROGRESSED_TO: KillChainStage progression with dwell time
// Properties: from_stage (string), to_stage (string),
//            timestamp (datetime), dwell_time_seconds (float),
//            host_ip (string)

// PRECEDED_BY: AgentAction chain (temporal ordering)
// Properties: timestamp (datetime), reason (string)

// CAUSED: Alert caused by AttackEvent(s)
// Properties: timestamp (datetime), event_count (int)

// ASSET_OF: Host belongs to Asset
// Properties: role (string)

// COMPROMISED_BY: Host compromised via AttackEvent
// Properties: timestamp (datetime), stage (string), event_id (string)

// AFFECTED_BY: Alert affected by AgentAction
// Properties: timestamp (datetime), action_id (string)
