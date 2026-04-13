import asyncio
from typing import Any

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from backend.agent.observation_builder import ObservationBuilder
from backend.agent.action_masker import ActionMasker
from backend.agent.reward_calculator import RewardCalculator
from backend.graph.neo4j_client import neo4j_client
from backend.graph.agent_action_writer import write_agent_action
from backend.graph.kill_chain_writer import mark_stage_contained
from backend.mitre.attack_matrix import STAGE_ORDER, STAGE_PRIORITY
from backend.utils.logger import setup_logger

logger = setup_logger("kill_chain_env")


class KillChainEnv(gym.Env):
    metadata = {"render_modes": ["human"]}
    action_space = spaces.Discrete(8)
    observation_space = spaces.Box(low=-1000, high=1000, shape=(23,), dtype=np.float32)

    def __init__(self):
        super().__init__()
        self.obs_builder = ObservationBuilder()
        self.masker = ActionMasker()
        self.reward_calc = RewardCalculator()
        self.current_stage: str | None = None
        self.step_count = 0
        self.max_steps = 500
        self._previous_blast = 0.0

    async def _async_reset(self) -> np.ndarray:
        await neo4j_client.connect()
        self.step_count = 0
        self._previous_blast = 0.0
        obs = await self.obs_builder.build()
        self.current_stage = await self._detect_active_stage()
        return obs

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs = asyncio.get_event_loop().run_until_complete(self._async_reset())
        info = self._get_info()
        return obs, info

    async def _async_step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        self.step_count += 1
        action_name = self.masker.get_action_name(action)
        valid_actions = self.masker.get_valid_actions(self.current_stage)
        is_valid = action in valid_actions

        if not is_valid:
            reward = self.reward_calc.calculate(
                stage_contained=False,
                previous_stage=self.current_stage,
                current_stage=self.current_stage,
                blast_radius_reduction=0.0,
                dwell_time_seconds=0.0,
                is_false_positive=True,
                action_taken=True,
            )
            obs = await self.obs_builder.build()
            info = self._get_info()
            return obs, reward, False, False, info

        stage_contained = await self._execute_action(action)
        blast_radius = await self._get_current_blast_radius()
        blast_reduction = max(self._previous_blast - blast_radius, 0.0)
        self._previous_blast = blast_radius

        reward = self.reward_calc.calculate(
            stage_contained=stage_contained,
            previous_stage=self.current_stage,
            current_stage=self.current_stage,
            blast_radius_reduction=blast_reduction,
            dwell_time_seconds=0.0,
            is_false_positive=False,
            action_taken=True,
        )

        obs = await self.obs_builder.build()
        self.current_stage = await self._detect_active_stage()
        terminated = self.step_count >= self.max_steps or blast_radius == 0.0
        truncated = False
        info = self._get_info()
        return obs, reward, terminated, truncated, info

    def step(self, action):
        return asyncio.get_event_loop().run_until_complete(self._async_step(action))

    async def _detect_active_stage(self) -> str | None:
        query = """
        MATCH (k:KillChainStage)
        WHERE k.status = 'active'
        RETURN k.stage AS stage, k.first_detected AS detected
        ORDER BY detected DESC
        LIMIT 1
        """
        results = await neo4j_client.execute(query)
        return results[0]["stage"] if results else None

    async def _execute_action(self, action_idx: int) -> bool:
        action_name = self.masker.get_action_name(action_idx)
        query = """
        MATCH (k:KillChainStage)
        WHERE k.status = 'active'
        RETURN k.host_ip AS host_ip, k.stage AS stage
        ORDER BY k.first_detected DESC
        LIMIT 1
        """
        results = await neo4j_client.execute(query)
        if not results:
            return False
        host_ip = results[0]["host_ip"]
        stage = results[0]["stage"]

        await write_agent_action(
            action_type=action_name,
            stage=stage,
            host_ip=host_ip,
            success=True,
            reason=f"RL agent action: {action_name}",
        )
        await mark_stage_contained(host_ip, stage)
        logger.info("action_executed", action=action_name, host_ip=host_ip, stage=stage)
        return True

    async def _get_current_blast_radius(self) -> float:
        query = """
        MATCH (h:Host)
        WHERE h.compromise_status IN ['compromised', 'suspected']
        RETURN count(*) AS count
        """
        results = await neo4j_client.execute(query)
        return float(results[0]["count"]) if results else 0.0

    def _get_info(self) -> dict[str, Any]:
        return {
            "current_stage": self.current_stage,
            "step": self.step_count,
            "valid_actions": self.masker.get_valid_actions(self.current_stage),
        }

    def get_action_mask(self) -> np.ndarray:
        return self.masker.get_mask(self.current_stage)

    def close(self):
        pass
