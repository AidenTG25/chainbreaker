from fastapi import APIRouter, Query

from backend.graph.neo4j_client import neo4j_client

router = APIRouter()


@router.get("")
async def get_alerts(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=500),
):
    query = """
    MATCH (a:Alert)
    OPTIONAL MATCH (a)-[:CAUSED]->(e:AttackEvent)
    WHERE 1=1
    """
    params = {"limit": limit}
    if status:
        query += " AND a.status = $status"
        params["status"] = status
    if severity:
        query += " AND a.severity = $severity"
        params["severity"] = severity

    query += """
    OPTIONAL MATCH (e)-[:ON_HOST]->(h:Host)
    WITH a, count(DISTINCT e) AS event_count, collect(DISTINCT h.ip) AS affected
    RETURN a.alert_id AS alert_id, a.title AS title, a.severity AS severity,
           a.status AS status, a.stage AS stage, a.description AS description,
           a.created_at AS created_at, a.updated_at AS updated_at,
           affected AS affected_hosts, event_count
    ORDER BY a.created_at DESC
    LIMIT $limit
    """
    results = await neo4j_client.execute(query, params)
    return {"alerts": results, "total": len(results)}


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    query = """
    MATCH (a:Alert {alert_id: $alert_id})
    OPTIONAL MATCH (a)-[:CAUSED]->(e:AttackEvent)
    OPTIONAL MATCH (e)-[:ON_HOST]->(h:Host)
    OPTIONAL MATCH (agent:AgentAction)-[:TARGETED_HOST]->(h)
    RETURN a, collect(DISTINCT properties(e)) AS events,
           collect(DISTINCT h.ip) AS affected_hosts,
           collect(DISTINCT properties(agent)) AS agent_actions
    LIMIT 1
    """
    results = await neo4j_client.execute(query, {"alert_id": alert_id})
    return results[0] if results else {"error": "Alert not found"}
