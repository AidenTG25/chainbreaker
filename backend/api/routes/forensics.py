from fastapi import APIRouter, Query

from backend.api.dependencies import get_neo4j_client
from backend.api.schemas import ForensicReportResponse, BlastRadiusResponse
from backend.forensics.blast_radius import calculate_blast_radius, get_affected_assets
from backend.forensics.kill_chain_profiler import get_kill_chain_summary
from backend.forensics.attack_path_tracer import trace_full_attack_path, find_attack_source
from backend.forensics.timeline_builder import build_full_timeline, build_host_timeline
from backend.forensics.report_generator import generate_forensic_report, generate_host_report
from backend.graph.neo4j_client import neo4j_client

router = APIRouter()


@router.get("/timeline")
async def get_timeline(limit: int = Query(200, ge=1, le=2000)):
    timeline = await build_full_timeline(limit)
    return {"timeline": timeline, "total": len(timeline)}


@router.get("/timeline/{host_ip}")
async def get_host_timeline(host_ip: str):
    timeline = await build_host_timeline(host_ip)
    return {"host_ip": host_ip, "timeline": timeline, "total": len(timeline)}


@router.get("/blast-radius")
async def get_blast_radius():
    return await calculate_blast_radius()


@router.get("/affected-assets")
async def get_affected():
    return {"assets": await get_affected_assets()}


@router.get("/kill-chain-summary")
async def get_kill_chain():
    return await get_kill_chain_summary()


@router.get("/attack-path/{alert_id}")
async def get_attack_path(alert_id: str):
    return {"path": await trace_full_attack_path(alert_id)}


@router.get("/attack-source/{ip}")
async def get_attack_source(ip: str):
    return await find_attack_source(ip)


@router.get("/report")
async def get_forensic_report(alert_id: str | None = None):
    return await generate_forensic_report(alert_id)


@router.get("/report/host/{ip}")
async def get_host_report(ip: str):
    return await generate_host_report(ip)
