from backend.graph.neo4j_client import neo4j_client
from backend.mitre.stage_mapper import ml_label_to_stage, stage_to_mitre_id
from backend.mitre.attack_matrix import KillChainStage
from backend.utils.logger import setup_logger

logger = setup_logger("attack_writer")


async def write_attack_event(
    source_ip: str,
    dest_ip: str,
    stage: str,
    confidence: float,
    attack_label: str,
    ml_model: str,
    protocol: str | None = None,
    timestamp: str | None = None,
) -> str:
    from backend.mitre.tactic_aligner import get_all_mitre_tactics_for_attack
    mitre_tactics = get_all_mitre_tactics_for_attack(attack_label)
    event_id = await neo4j_client.write_attack_event(
        source_ip=source_ip,
        dest_ip=dest_ip,
        stage=stage,
        confidence=confidence,
        attack_label=attack_label,
        ml_model=ml_model,
        protocol=protocol,
        mitre_tactics=mitre_tactics,
        timestamp=timestamp,
    )
    logger.info(
        "attack_event_written",
        event_id=event_id,
        stage=stage,
        dest_ip=dest_ip,
        confidence=confidence,
    )
    return event_id


async def link_communication(
    src_ip: str,
    dst_ip: str,
    protocol: str | None = None,
    flow_count: int = 1,
    total_bytes: int = 0,
    suspicious: bool = False,
) -> None:
    await neo4j_client.link_communicates_with(
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        flow_count=flow_count,
        total_bytes=total_bytes,
        suspicious=suspicious,
    )


async def mark_host_suspected(ip: str) -> None:
    await neo4j_client.mark_host_compromised(ip, "suspected")
