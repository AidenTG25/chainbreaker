from backend.graph.neo4j_client import neo4j_client
from backend.utils.logger import setup_logger

logger = setup_logger("agent_action_writer")

prev_action_id = {}


async def write_agent_action(
    action_type: str,
    stage: str,
    host_ip: str,
    success: bool,
    reason: str,
    target_ip: str | None = None,
    target_port: int | None = None,
) -> str:
    global prev_action_id
    key = f"{stage}_{host_ip}"
    prev = prev_action_id.get(key)
    action_id = await neo4j_client.write_agent_action(
        action_type=action_type,
        stage=stage,
        host_ip=host_ip,
        success=success,
        reason=reason,
        target_ip=target_ip,
        target_port=target_port,
        prev_action_id=prev,
    )
    prev_action_id[key] = action_id
    logger.info(
        "agent_action_written",
        action_id=action_id,
        action_type=action_type,
        stage=stage,
        host_ip=host_ip,
        success=success,
    )
    return action_id


async def get_recent_actions(limit: int = 50) -> list[dict]:
    query = """
    MATCH (a:AgentAction)
    OPTIONAL MATCH (h:Host {ip: a.host_ip})
    RETURN a.action_id AS action_id, a.action_type AS action_type,
           a.stage AS stage, a.host_ip AS host_ip, a.timestamp AS timestamp,
           a.success AS success, a.reason AS reason,
           h.role AS host_role
    ORDER BY a.timestamp DESC
    LIMIT $limit
    """
    return await neo4j_client.execute(query, {"limit": limit})
