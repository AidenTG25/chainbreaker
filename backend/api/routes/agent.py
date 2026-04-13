from fastapi import APIRouter, HTTPException

from backend.graph.agent_action_writer import get_recent_actions
from backend.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("agent_routes")


@router.get("/actions")
async def get_agent_actions(limit: int = 50):
    actions = await get_recent_actions(limit)
    return {"actions": actions, "total": len(actions)}


@router.get("/status")
async def get_agent_status():
    return {
        "agent_active": True,
        "mode": "observation",
        "supported_stages": [
            "Initial_Access", "Persistence", "Command_and_Control",
            "Discovery", "Credential_Access", "Lateral_Movement",
            "Defense_Evasion", "Exfiltration"
        ],
    }
