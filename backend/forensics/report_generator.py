import json
from datetime import datetime

from backend.forensics.blast_radius import calculate_blast_radius, get_affected_assets
from backend.forensics.kill_chain_profiler import get_kill_chain_summary
from backend.forensics.attack_path_tracer import trace_full_attack_path
from backend.utils.logger import setup_logger

logger = setup_logger("report_generator")


async def generate_forensic_report(alert_id: str | None = None) -> dict:
    blast = await calculate_blast_radius()
    kill_chain = await get_kill_chain_summary()
    assets = await get_affected_assets()
    attack_path = []
    if alert_id:
        attack_path = await trace_full_attack_path(alert_id)

    report = {
        "report_id": f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat(),
        "blast_radius": blast,
        "kill_chain_summary": kill_chain,
        "affected_assets": assets,
        "attack_path": attack_path,
        "recommendations": _generate_recommendations(blast, kill_chain),
    }
    logger.info("forensic_report_generated", report_id=report["report_id"])
    return report


async def generate_host_report(host_ip: str) -> dict:
    from backend.forensics.kill_chain_profiler import profile_host_kill_chain
    from backend.forensics.timeline_builder import build_host_timeline

    profile = await profile_host_kill_chain(host_ip)
    timeline = await build_host_timeline(host_ip)
    blast = await calculate_blast_radius()
    host_blast = next((h for h in blast.get("compromised_hosts", []) if h["ip"] == host_ip), None)

    return {
        "report_id": f"HOST-{host_ip.replace('.', '')}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat(),
        "host_ip": host_ip,
        "kill_chain_profile": profile,
        "event_timeline": timeline,
        "blast_radius_entry": host_blast,
        "recommendations": _generate_host_recommendations(profile),
    }


def _generate_recommendations(blast: dict, kill_chain: dict) -> list[str]:
    recommendations = []
    severity = blast.get("severity_level", "LOW")
    if severity in ["CRITICAL", "HIGH"]:
        recommendations.append("Isolate all compromised hosts immediately using network segmentation")
        recommendations.append("Activate incident response team and begin containment procedures")
    if blast.get("high_value_impact", 0) > 0:
        recommendations.append("Prioritize protection of high-value assets — domain controllers, DB servers")
    active_c2 = kill_chain.get("Command_and_Control", {}).get("active", 0)
    if active_c2 > 0:
        recommendations.append("Block identified C2 communication channels at perimeter firewall")
    active_lat = kill_chain.get("Lateral_Movement", {}).get("active", 0)
    if active_lat > 0:
        recommendations.append("Disable lateral movement paths — disable SMBv1, restrict RDP")
    return recommendations


def _generate_host_recommendations(profile: dict) -> list[str]:
    recommendations = []
    stages = profile.get("stages", [])
    active = [s for s in stages if s.get("status") == "active"]
    if active:
        earliest = min(active, key=lambda x: x.get("priority", 99))
        recommendations.append(f"Prioritize containment of {earliest['stage']} on {profile['host_ip']}")
    if any(s["stage"] == "Command_and_Control" for s in active):
        recommendations.append("Block C2 communication — check firewall rules for egress filtering")
    if any(s["stage"] == "Lateral_Movement" for s in active):
        recommendations.append("Quarantine host — revoke credentials used for lateral movement")
    return recommendations
