import numpy as np
from typing import Any

from backend.agent.kill_chain_env import KillChainEnv
from backend.agent.observation_builder import ObservationBuilder
from backend.agent.action_masker import ActionMasker
from backend.graph.agent_action_writer import write_agent_action
from backend.graph.kill_chain_writer import mark_stage_contained
from backend.utils.logger import setup_logger

logger = setup_logger("baseline")


class RuleBasedAgent:
    def __init__(self):
        self.masker = ActionMasker()
        self.obs_builder = ObservationBuilder()
        self.alert_thresholds = {
            "Initial_Access": 3,
            "Persistence": 5,
            "Command_and_Control": 2,
            "Discovery": 4,
            "Credential_Access": 3,
            "Lateral_Movement": 2,
            "Defense_Evasion": 5,
            "Exfiltration": 1,
        }
        self.action_map = {
            "Initial_Access": 0,
            "Persistence": 1,
            "Command_and_Control": 0,
            "Discovery": 0,
            "Credential_Access": 1,
            "Lateral_Movement": 1,
            "Defense_Evasion": 1,
            "Exfiltration": 5,
        }

    async def decide(self, active_stage: str | None, host_ip: str | None) -> tuple[int | None, str | None]:
        if not active_stage or not host_ip:
            return None, None
        threshold = self.alert_thresholds.get(active_stage, 5)
        action_idx = self.action_map.get(active_stage, 6)
        await write_agent_action(
            action_type=self.masker.get_action_name(action_idx),
            stage=active_stage,
            host_ip=host_ip,
            success=True,
            reason=f"Rule-based: threshold {threshold} exceeded for {active_stage}",
        )
        await mark_stage_contained(host_ip, active_stage)
        logger.info("baseline_action_taken", stage=active_stage, action=action_idx)
        return action_idx, active_stage
