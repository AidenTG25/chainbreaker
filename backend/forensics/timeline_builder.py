from backend.graph.neo4j_client import neo4j_client
from backend.mitre.attack_matrix import STAGE_PRIORITY, KillChainStage
from backend.utils.logger import setup_logger

logger = setup_logger("timeline_builder")


async def build_full_timeline(limit: int = 200) -> list[dict]:
    query = """
    MATCH (e:AttackEvent)
    OPTIONAL MATCH (e)<-[:SOURCE_OF]-(src:Host)
    OPTIONAL MATCH (e)-[:TRIGGERED_BY|ON_HOST]->(dst:Host)
    OPTIONAL MATCH (k:KillChainStage)-[:TRIGGERED_BY]->(e)
    OPTIONAL MATCH (a:Alert)-[:CAUSED]->(e)
    OPTIONAL MATCH (agent:AgentAction)-[:TARGETED_HOST]->(dst)
    RETURN e.event_id AS event_id, e.stage AS stage, e.attack_label AS label,
           e.confidence AS confidence, e.timestamp AS timestamp,
           src.ip AS source_ip, dst.ip AS dest_ip,
           k.status AS kill_chain_status, k.dwell_time_seconds AS dwell_time,
           agent.action_type AS agent_action, agent.success AS action_success,
           a.alert_id AS alert_id, a.severity AS alert_severity
    ORDER BY e.timestamp DESC
    LIMIT $limit
    """
    events = await neo4j_client.execute(query, {"limit": limit})
    for event in events:
        stage = event.get("stage", "")
        try:
            event["stage_priority"] = STAGE_PRIORITY[KillChainStage(stage)]
        except (ValueError, KeyError):
            event["stage_priority"] = 99
    events.sort(key=lambda x: x.get("timestamp", ""))
    return events


async def build_host_timeline(host_ip: str) -> list[dict]:
    query = """
    MATCH (e:AttackEvent)-[:ON_HOST|TRIGGERED_BY]->(h:Host {ip: $host_ip})
    OPTIONAL MATCH (e)<-[:SOURCE_OF]-(src:Host)
    OPTIONAL MATCH (k:KillChainStage {host_ip: $host_ip})
    OPTIONAL MATCH (agent:AgentAction)-[:TARGETED_HOST]->(h)
    OPTIONAL MATCH (a:Alert)-[:CAUSED]->(e)
    RETURN e.event_id AS event_id, e.stage AS stage, e.attack_label AS label,
           e.confidence AS confidence, e.timestamp AS timestamp,
           src.ip AS source_ip,
           agent.action_type AS action, agent.success AS action_success,
           k.status AS kill_chain_status,
           a.alert_id AS alert_id, a.severity AS alert_severity
    ORDER BY e.timestamp
    """
    return await neo4j_client.execute(query, {"host_ip": host_ip})
