from backend.graph.neo4j_client import neo4j_client
from backend.mitre.attack_matrix import STAGE_ORDER, KillChainStage
from backend.mitre.stage_mapper import stage_to_mitre_id
from backend.utils.logger import setup_logger

logger = setup_logger("kill_chain_writer")


async def update_kill_chain_stage(
    host_ip: str,
    stage: str,
    status: str = "active",
) -> str:
    stage_enum = KillChainStage(stage) if stage in [s.value for s in KillChainStage] else None
    mitre_tactic_ids = []
    if stage_enum:
        from backend.mitre.attack_matrix import STAGE_MITRE_TACTICS
        mitre_tactic_ids = STAGE_MITRE_TACTICS.get(stage_enum, [])

    stage_id = await neo4j_client.upsert_kill_chain_stage(
        host_ip=host_ip,
        stage=stage,
        status=status,
        mitre_tactic_ids=mitre_tactic_ids,
    )
    await _link_stage_progression(host_ip, stage)
    logger.info("kill_chain_stage_updated", host_ip=host_ip, stage=stage, status=status)
    return stage_id


async def _link_stage_progression(host_ip: str, new_stage: str) -> None:
    query = """
    MATCH (k_prev:KillChainStage {host_ip: $host_ip})
    WHERE k_prev.stage <> $new_stage
    WITH k_prev
    ORDER BY k_prev.first_detected DESC
    LIMIT 1
    MERGE (k_prev)-[r:PROGRESSED_TO {to_stage: $new_stage, host_ip: $host_ip}]->(next:KillChainStage {stage: $new_stage, host_ip: $host_ip})
    ON CREATE SET r.timestamp = datetime(), r.from_stage = k_prev.stage, r.dwell_time_seconds = 0.0
    """
    try:
        await neo4j_client.execute(query, {"host_ip": host_ip, "new_stage": new_stage})
    except Exception as e:
        logger.debug("progression_link_skipped", error=str(e))


async def get_active_stages() -> list[dict]:
    query = """
    MATCH (k:KillChainStage)
    WHERE k.status IN ['active', 'suspected']
    MATCH (h:Host {ip: k.host_ip})
    RETURN k.stage_id AS stage_id, k.stage AS stage, k.host_ip AS host_ip,
           k.status AS status, k.first_detected AS first_detected,
           k.last_updated AS last_updated, h.role AS host_role
    ORDER BY k.last_updated DESC
    """
    return await neo4j_client.execute(query)


async def mark_stage_contained(host_ip: str, stage: str) -> None:
    stage_id = f"{host_ip}_{stage}"
    query = """
    MATCH (k:KillChainStage {stage_id: $stage_id})
    SET k.status = 'contained', k.last_updated = datetime()
    """
    await neo4j_client.execute(query, {"stage_id": stage_id})
    logger.info("stage_contained", host_ip=host_ip, stage=stage)


async def mark_stage_completed(host_ip: str, stage: str) -> None:
    stage_id = f"{host_ip}_{stage}"
    query = """
    MATCH (k:KillChainStage {stage_id: $stage_id})
    SET k.status = 'completed', k.last_updated = datetime()
    """
    await neo4j_client.execute(query, {"stage_id": stage_id})
    logger.info("stage_completed", host_ip=host_ip, stage=stage)


async def mark_host_compromised(host_ip: str, status: str = "compromised") -> None:
    await neo4j_client.mark_host_compromised(host_ip, status)
