from backend.graph.neo4j_client import neo4j_client
from backend.utils.logger import setup_logger

logger = setup_logger("blast_radius")


async def calculate_blast_radius() -> dict:
    query = """
    MATCH (h:Host)
    WHERE h.compromise_status IN ['compromised', 'suspected']
    OPTIONAL MATCH (e:AttackEvent)-[:ON_HOST]->(h)
    OPTIONAL MATCH (a:Alert)-[:CAUSED]->(e)
    OPTIONAL MATCH (k:KillChainStage)-[:ON_HOST]->(h)
    OPTIONAL MATCH (h)-[:COMMUNICATES_WITH]->(neighbor:Host)
    OPTIONAL MATCH (asset:Asset)-[:ASSET_OF]->(h)
    RETURN h.ip AS ip, h.role AS role, h.compromise_status AS status,
           count(DISTINCT e) AS event_count,
           count(DISTINCT a) AS alert_count,
           collect(DISTINCT k.stage) AS active_stages,
           count(DISTINCT neighbor) AS exposed_neighbors,
           collect(DISTINCT asset.asset_id) AS linked_assets
    ORDER BY event_count DESC
    """
    compromised_hosts = await neo4j_client.execute(query)

    total_events = sum(h.get("event_count", 0) for h in compromised_hosts)
    total_alerts = sum(h.get("alert_count", 0) for h in compromised_hosts)
    high_value_impact = sum(1 for h in compromised_hosts if h.get("linked_assets"))
    exposed_peers = sum(h.get("exposed_neighbors", 0) for h in compromised_hosts)

    severity_score = 0
    for h in compromised_hosts:
        score = h.get("event_count", 0)
        if h.get("linked_assets"):
            score *= 2
        severity_score += score

    return {
        "compromised_hosts": compromised_hosts,
        "total_compromised": len(compromised_hosts),
        "total_events": total_events,
        "total_alerts": total_alerts,
        "high_value_impact": high_value_impact,
        "exposed_peers": exposed_peers,
        "severity_score": severity_score,
        "severity_level": _severity_level(severity_score),
    }


async def get_affected_assets() -> list[dict]:
    query = """
    MATCH (asset:Asset)<-[:ASSET_OF]-(h:Host)
    WHERE h.compromise_status IN ['compromised', 'suspected']
    RETURN asset.asset_id AS asset_id, asset.name AS name,
           asset.asset_type AS asset_type, asset.criticality AS criticality,
           h.ip AS host_ip, h.compromise_status AS host_status
    ORDER BY
        CASE asset.criticality
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            ELSE 4
        END
    """
    return await neo4j_client.execute(query)


def _severity_level(score: int) -> str:
    if score >= 50:
        return "CRITICAL"
    elif score >= 20:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    else:
        return "LOW"
