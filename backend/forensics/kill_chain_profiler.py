from datetime import datetime

from backend.graph.neo4j_client import neo4j_client
from backend.mitre.attack_matrix import STAGE_ORDER, STAGE_PRIORITY, STAGE_DESCRIPTIONS, KillChainStage
from backend.utils.logger import setup_logger

logger = setup_logger("kill_chain_profiler")


async def profile_host_kill_chain(host_ip: str) -> dict:
    query = """
    MATCH (k:KillChainStage {host_ip: $host_ip})
    OPTIONAL MATCH (e:AttackEvent)-[:TRIGGERED_BY]->(h:Host {ip: $host_ip})
    OPTIONAL MATCH (k)<-[r:PROGRESSED_TO]-(prev:KillChainStage)
    RETURN k.stage AS stage, k.status AS status,
           k.first_detected AS first_detected, k.last_updated AS last_updated,
           k.containment_attempts AS containment_attempts,
           k.dwell_time_seconds AS dwell_time_seconds,
           k.mitre_tactic_ids AS mitre_tactic_ids,
           r.timestamp AS progression_ts, prev.stage AS prev_stage,
           count(DISTINCT e) AS event_count
    ORDER BY k.first_detected
    """
    stages = await neo4j_client.execute(query, {"host_ip": host_ip})
    if not stages:
        return {"host_ip": host_ip, "stages": [], "overall_status": "clean"}

    stage_progression = []
    for s in stages:
        stage_name = s.get("stage", "")
        try:
            stage_enum = KillChainStage(stage_name)
            priority = STAGE_PRIORITY.get(stage_enum, 0)
        except ValueError:
            priority = 99
        stage_progression.append({
            "stage": stage_name,
            "status": s.get("status", "unknown"),
            "priority": priority,
            "description": STAGE_DESCRIPTIONS.get(KillChainStage(stage_name), "") if stage_name else "",
            "first_detected": s.get("first_detected"),
            "last_updated": s.get("last_updated"),
            "dwell_time_seconds": s.get("dwell_time_seconds", 0),
            "containment_attempts": s.get("containment_attempts", 0),
            "mitre_tactic_ids": s.get("mitre_tactic_ids", []),
            "event_count": s.get("event_count", 0),
        })

    active_count = sum(1 for s in stage_progression if s["status"] == "active")
    status = "compromised" if active_count > 0 else "contained"
    return {"host_ip": host_ip, "stages": stage_progression, "overall_status": status, "active_stage_count": active_count}


async def get_kill_chain_summary() -> dict:
    query = """
    MATCH (k:KillChainStage)
    MATCH (h:Host {ip: k.host_ip})
    RETURN k.stage AS stage, k.status AS status, count(DISTINCT k.host_ip) AS host_count,
           count(DISTINCT k) AS total_events
    ORDER BY k.status
    """
    results = await neo4j_client.execute(query)
    summary = {s.value: {"active": 0, "contained": 0, "completed": 0, "total": 0} for s in KillChainStage}
    for r in results:
        stage = r.get("stage", "")
        status = r.get("status", "")
        count = r.get("total_events", 0)
        if stage in summary and status in summary[stage]:
            summary[stage][status] = count
            summary[stage]["total"] += count
    return summary
