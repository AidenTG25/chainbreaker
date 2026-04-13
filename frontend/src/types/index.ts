export interface Host {
  ip: string;
  hostname?: string;
  role: string;
  compromise_status: string;
  first_seen?: string;
  last_seen?: string;
  connected_peers?: number;
}

export interface AttackEvent {
  event_id: string;
  stage: string;
  timestamp: string;
  confidence: number;
  attack_label: string;
  source_ip: string;
  dest_ip: string;
  ml_model: string;
}

export interface KillChainStage {
  stage_id: string;
  stage: string;
  host_ip: string;
  status: string;
  first_detected?: string;
  last_updated?: string;
  containment_attempts: number;
  dwell_time_seconds: number;
}

export interface Alert {
  alert_id: string;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'contained' | 'resolved';
  stage: string;
  description?: string;
  created_at: string;
  updated_at: string;
  affected_hosts: string[];
  event_count?: number;
}

export interface ForensicTimelineItem {
  event_id: string;
  stage: string;
  label: string;
  confidence: number;
  timestamp: string;
  source_ip: string;
  dest_ip: string;
  kill_chain_status?: string;
  agent_action?: string;
  action_success?: boolean;
  alert_id?: string;
  alert_severity?: string;
}

export interface BlastRadius {
  total_compromised: number;
  total_events: number;
  total_alerts: number;
  high_value_impact: number;
  exposed_peers: number;
  severity_score: number;
  severity_level: string;
  compromised_hosts: Array<{
    ip: string;
    role: string;
    status: string;
    event_count: number;
    alert_count: number;
    active_stages: string[];
  }>;
}

export interface AgentAction {
  action_id: string;
  action_type: string;
  stage: string;
  host_ip: string;
  timestamp: string;
  success: boolean;
  reason: string;
}

export interface GraphSnapshot {
  nodes: Array<{ id: string; type: string; [key: string]: unknown }>;
  links: Array<{ source: string; target: string; [key: string]: unknown }>;
}

export interface KillChainStageData {
  stage?: string;
  status?: string;
  host_ip?: string;
  stage_id?: string;
  first_detected?: string;
  last_updated?: string;
  containment_attempts?: number;
  dwell_time_seconds?: number;
}

export const KILL_CHAIN_STAGES = [
  'Initial_Access',
  'Persistence',
  'Command_and_Control',
  'Discovery',
  'Credential_Access',
  'Lateral_Movement',
  'Defense_Evasion',
  'Exfiltration',
] as const;

export type KillChainStageName = typeof KILL_CHAIN_STAGES[number];

export const STAGE_COLORS: Record<string, string> = {
  Initial_Access: '#ef4444',
  Persistence: '#f97316',
  Command_and_Control: '#a855f7',
  Discovery: '#3b82f6',
  Credential_Access: '#eab308',
  Lateral_Movement: '#ec4899',
  Defense_Evasion: '#6b7280',
  Exfiltration: '#14b8a6',
  clean: '#22c55e',
  compromised: '#ef4444',
  suspected: '#f97316',
  contained: '#3b82f6',
};
