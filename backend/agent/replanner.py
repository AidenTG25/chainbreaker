import numpy as np
from typing import Any

from backend.agent.kill_chain_env import KillChainEnv
from backend.agent.observation_builder import ObservationBuilder
from backend.agent.action_masker import ActionMasker
from backend.graph.agent_action_writer import write_agent_action
from backend.graph.kill_chain_writer import mark_stage_contained
from backend.utils.logger import setup_logger

logger = setup_logger("replanner")


class Replanner:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.containment_attempts: dict[str, int] = {}

    async def should_replan(self, stage: str, host_ip: str) -> bool:
        key = f"{stage}:{host_ip}"
        attempts = self.containment_attempts.get(key, 0)
        return attempts >= self.max_retries

    async def record_attempt(self, stage: str, host_ip: str) -> None:
        key = f"{stage}:{host_ip}"
        self.containment_attempts[key] = self.containment_attempts.get(key, 0) + 1

    async def get_next_stage_action(self, failed_stage: str) -> str:
        from backend.mitre.attack_matrix import STAGE_ORDER, STAGE_PRIORITY
        try:
            idx = STAGE_ORDER.index(failed_stage)
            if idx < len(STAGE_ORDER) - 1:
                next_stage = STAGE_ORDER[idx + 1]
                logger.info("replanning_for_next_stage", from_stage=failed_stage, to_stage=next_stage)
                return next_stage.value
        except ValueError:
            pass
        return failed_stage

    async def escalate(self, stage: str, host_ip: str) -> None:
        await write_agent_action(
            action_type="notify_admin",
            stage=stage,
            host_ip=host_ip,
            success=False,
            reason=f"REPLANNING FAILED: escalating to manual review for {stage} on {host_ip}",
        )
        logger.warning("escalation_triggered", stage=stage, host_ip=host_ip)
