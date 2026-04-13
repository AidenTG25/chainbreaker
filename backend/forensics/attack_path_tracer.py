from backend.graph.neo4j_client import neo4j_client
from backend.mitre.attack_matrix import STAGE_PRIORITY, KillChainStage
from backend.utils.logger import setup_logger

logger = setup_logger("attack_path_tracer")


async def trace_attack_path(start_ip: str, limit: int = 50) -> list[dict]:
    query = """
    MATCH path = (start:Host {ip: $start_ip})-[:COMMUNICATES_WITH*1..5]->(end:Host)
    WHERE any(h IN nodes(path) WHERE exists((a:AttackEvent)-[:ON_HOST]->(h)) OR exists((k:KillChainStage {host_ip: h.ip})))
    WITH path, nodes(path) AS hops
    UNWIND range(0, size(hops)-2) AS idx
    WITH path, hops[idx] AS src, hops[idx+1] AS dst, idx AS step
    OPTIONAL MATCH (e:AttackEvent)-[:ON_HOST]->(dst)
    OPTIONAL MATCH (k:KillChainStage {host_ip: dst.ip})
    RETURN src.ip AS src_ip, dst.ip AS dst_ip, step,
           k.stage AS attack_stage, k.status AS stage_status,
           e.attack_label AS attack_label, e.confidence AS confidence,
           e.timestamp AS event_timestamp
    ORDER BY step
    LIMIT $limit
    """
    return await neo4j_client.execute(query, {"start_ip": start_ip, "limit": limit})


async def trace_full_attack_path(alert_id: str) -> list[dict]:
    query = """
    MATCH (alert:Alert {alert_id: $alert_id})-[:CAUSED]->(e:AttackEvent)
    MATCH (e)<-[:SOURCE_OF]-(src:Host)
    MATCH (e)-[:ON_HOST|TRIGGERED_BY]->(dst:Host)
    OPTIONAL MATCH (k:KillChainStage)-[:TRIGGERED_BY]->(e)
    OPTIONAL MATCH (a:AgentAction)-[:TARGETED_HOST]->(dst)
    RETURN src.ip AS source_ip, dst.ip AS dest_ip, e.event_id AS event_id,
           e.stage AS stage, e.attack_label AS attack_label,
           e.confidence AS confidence, e.timestamp AS event_time,
           k.status AS kill_chain_status, k.dwell_time_seconds AS dwell_time,
           a.action_type AS action_taken, a.success AS action_success
    ORDER BY e.timestamp
    """
    return await neo4j_client.execute(query, {"alert_id": alert_id})


async def find_attack_source(compromised_ip: str) -> dict | None:
    query = """
    MATCH (src:Host)-[:SOURCE_OF]->(e:AttackEvent)-[:ON_HOST]->(dst:Host {ip: $compromised_ip})
    WITH src, e ORDER BY e.timestamp DESC LIMIT 5
    MATCH path = shortestPath((src)-[:COMMUNICATES_WITH*1..3]-(:Host))
    RETURN src.ip AS source_ip, src.role AS source_role,
           [n IN nodes(path) | n.ip] AS intermediate_hops,
           [n IN nodes(path) | n.ip] AS full_path,
           count(e) AS event_count,
           min(e.timestamp) AS first_seen, max(e.timestamp) AS last_seen
    LIMIT 1
    """
    results = await neo4j_client.execute(query, {"compromised_ip": compromised_ip})
    return results[0] if results else None
