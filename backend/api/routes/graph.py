from fastapi import APIRouter, Query

from backend.api.dependencies import get_neo4j_client
from backend.api.schemas import HostResponse, AttackEventResponse, KillChainStageResponse
from backend.graph.neo4j_client import neo4j_client

router = APIRouter()


@router.get("/hosts")
async def get_hosts(limit: int = Query(100, ge=1, le=1000)):
    query = """
    MATCH (h:Host)
    OPTIONAL MATCH (h)-[:COMMUNICATES_WITH]->(h2:Host)
    RETURN h.ip AS ip, h.hostname AS hostname, h.role AS role,
           h.compromise_status AS compromise_status,
           h.first_seen AS first_seen, h.last_seen AS last_seen,
           count(DISTINCT h2) AS connected_peers
    ORDER BY h.last_seen DESC
    LIMIT $limit
    """
    results = await neo4j_client.execute(query, {"limit": limit})
    return {"hosts": results, "total": len(results)}


@router.get("/hosts/{ip}")
async def get_host(ip: str):
    query = """
    MATCH (h:Host {ip: $ip})
    OPTIONAL MATCH (e:AttackEvent)-[:ON_HOST]->(h)
    OPTIONAL MATCH (k:KillChainStage)-[:ON_HOST]->(h)
    OPTIONAL MATCH (a:AgentAction)-[:TARGETED_HOST]->(h)
    OPTIONAL MATCH (asset:Asset)-[:ASSET_OF]->(h)
    RETURN h, collect(DISTINCT properties(e)) AS events,
           collect(DISTINCT properties(k)) AS stages,
           collect(DISTINCT properties(a)) AS actions,
           collect(DISTINCT properties(asset)) AS assets
    LIMIT 1
    """
    results = await neo4j_client.execute(query, {"ip": ip})
    return results[0] if results else {"error": "Host not found"}


@router.get("/events")
async def get_events(limit: int = Query(100, ge=1, le=1000)):
    query = """
    MATCH (e:AttackEvent)
    OPTIONAL MATCH (e)<-[:SOURCE_OF]-(src:Host)
    OPTIONAL MATCH (e)-[:ON_HOST|TRIGGERED_BY]->(dst:Host)
    RETURN e.event_id AS event_id, e.stage AS stage, e.timestamp AS timestamp,
           e.confidence AS confidence, e.attack_label AS attack_label,
           e.ml_model AS ml_model, src.ip AS source_ip, dst.ip AS dest_ip
    ORDER BY e.timestamp DESC
    LIMIT $limit
    """
    results = await neo4j_client.execute(query, {"limit": limit})
    return {"events": results, "total": len(results)}


@router.get("/stages")
async def get_stages():
    query = """
    MATCH (k:KillChainStage)
    MATCH (h:Host {ip: k.host_ip})
    RETURN k.stage_id AS stage_id, k.stage AS stage, k.host_ip AS host_ip,
           k.status AS status, k.first_detected AS first_detected,
           k.last_updated AS last_updated, k.containment_attempts AS containment_attempts,
           k.dwell_time_seconds AS dwell_time_seconds, h.role AS host_role
    ORDER BY k.last_updated DESC
    """
    results = await neo4j_client.execute(query)
    return {"stages": results}


@router.get("/edges")
async def get_edges(limit: int = Query(500, ge=1, le=5000)):
    query = """
    MATCH (src:Host)-[r:COMMUNICATES_WITH]->(dst:Host)
    RETURN src.ip AS src_ip, dst.ip AS dst_ip,
           r.first_seen AS first_seen, r.last_seen AS last_seen,
           r.flow_count AS flow_count, r.total_bytes AS total_bytes,
           r.protocols AS protocols, r.suspicious AS suspicious
    LIMIT $limit
    """
    results = await neo4j_client.execute(query, {"limit": limit})
    return {"edges": results, "total": len(results)}


@router.get("/snapshot")
async def get_graph_snapshot():
    return await neo4j_client.get_graph_snapshot()
