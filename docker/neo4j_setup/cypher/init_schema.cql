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

// ============================
// FLOW-CENTRIC GRAPH SCHEMA
// ============================

// --- Node Constraints ---

DROP CONSTRAINT flow_id IF EXISTS;
DROP CONSTRAINT protocol_name IF EXISTS;
DROP CONSTRAINT attack_key IF EXISTS;

CREATE CONSTRAINT flow_id FOR (f:Flow) REQUIRE f.flow_id IS UNIQUE;
CREATE CONSTRAINT protocol_name FOR (p:Protocol) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT attack_key FOR (a:Attack) REQUIRE a.attack_key IS UNIQUE;

// --- Node Indexes ---

CREATE INDEX flow_ts_idx FOR (f:Flow) ON (f.ts);
CREATE INDEX flow_label_idx FOR (f:Flow) ON (f.label);
CREATE INDEX flow_src_ip_idx FOR (f:Flow) ON (f.src_ip);
CREATE INDEX flow_dst_ip_idx FOR (f:Flow) ON (f.dst_ip);
CREATE INDEX flow_protocol_idx FOR (f:Flow) ON (f.protocol);
CREATE INDEX flow_sublabel_idx FOR (f:Flow) ON (f.sublabel);
CREATE INDEX flow_predicted_label_idx FOR (f:Flow) ON (f.predicted_label);

CREATE INDEX attack_label_idx FOR (a:Attack) ON (a.label);
CREATE INDEX attack_sublabel_idx FOR (a:Attack) ON (a.subLabel);

// --- Relationship Indexes ---

CREATE INDEX initiated_ts_idx FOR ()-[r:INITIATED]-() ON (r.ts);
CREATE INDEX targets_ts_idx FOR ()-[r:TARGETS]-() ON (r.ts);
CREATE INDEX uses_protocol_idx FOR ()-[r:USES_PROTOCOL]-() ON (r.ts);
CREATE INDEX has_attack_type_idx FOR ()-[r:HAS_ATTACK_TYPE]-() ON (r.ts);
CREATE INDEX predicted_as_idx FOR ()-[r:PREDICTED_AS]-() ON (r.ts);

// ============================
// FLOW-CENTRIC NODE DEFINITIONS (documentation)
// ============================

// Flow: Individual network flow event (MOST IMPORTANT NODE)
// Properties: flow_id (string, unique), ts (string), src_ip (string),
//            dst_ip (string), src_port (int), dst_port (int),
//            flow_duration (float), protocol (string),
//            total_size (float), total_bytes (float),
//            rate (float), srate (float), drate (float),
//            syn_flag_count (int), ack_flag_count (int),
//            fin_flag_count (int), rst_flag_count (int),
//            psh_flag_count (int), urg_flag_count (int),
//            ece_flag_count (int), cwr_flag_count (int),
//            header_length (float), iat (float),
//            magnitude (float), radius (float),
//            covariance (float), variance (float), weight (float),
//            label (string), sublabel (string), sublabel_cat (string),
//            predicted_label (string, ML), confidence_score (float, ML)

// Protocol: Network protocol type
// Properties: name (string, unique — TCP, UDP, HTTP, DNS, etc.)

// Attack: Attack classification from dataset labels
// Properties: attack_key (string, unique — "{label}::{subLabel}"),
//            label (string), subLabel (string), subLabelCat (string)

// ============================
// FLOW-CENTRIC EDGE DEFINITIONS (documentation)
// ============================

// INITIATED: Host started this flow
//   (Host)-[:INITIATED]->(Flow)

// TARGETS: Flow directed at this host
//   (Flow)-[:TARGETS]->(Host)

// USES_PROTOCOL: Flow uses this protocol
//   (Flow)-[:USES_PROTOCOL]->(Protocol)

// HAS_ATTACK_TYPE: Flow classified as this attack
//   (Flow)-[:HAS_ATTACK_TYPE]->(Attack)

// PREDICTED_AS: ML model predicted flow as this attack (future)
//   (Flow)-[:PREDICTED_AS]->(Attack)
//   Properties: model (string), confidence (float), ts (string)
