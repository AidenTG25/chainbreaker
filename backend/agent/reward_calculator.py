from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("reward_calculator")


class RewardCalculator:
    def __init__(self):
        rw = config.get_section("rl").get("reward", {})
        self.early_interrupt_weight = rw.get("early_interruption_weight", 10.0)
        self.blast_radius_weight = rw.get("blast_radius_weight", -5.0)
        self.dwell_time_weight = rw.get("dwell_time_weight", -1.0)
        self.containment_success_weight = rw.get("containment_success_weight", 5.0)
        self.containment_failure_penalty = rw.get("containment_failure_penalty", -10.0)
        self.false_positive_penalty = rw.get("false_positive_penalty", -2.0)
        self.action_cost_weight = rw.get("action_cost_weight", -0.1)
        self.stage_progress_penalty = rw.get("stage_progress_penalty", -8.0)

    def calculate(
        self,
        stage_contained: bool,
        previous_stage: str | None,
        current_stage: str | None,
        blast_radius_reduction: float,
        dwell_time_seconds: float,
        is_false_positive: bool,
        action_taken: bool,
    ) -> float:
        reward = 0.0
        if is_false_positive:
            reward += self.false_positive_penalty
        if action_taken:
            reward += self.action_cost_weight
        if stage_contained:
            reward += self.containment_success_weight
            if previous_stage and self._is_early_stage(previous_stage):
                reward += self.early_interrupt_weight
        if blast_radius_reduction > 0:
            reward += blast_radius_reduction * self.blast_radius_weight
        reward += dwell_time_seconds * self.dwell_time_weight
        if current_stage and previous_stage and current_stage != previous_stage:
            reward += self.stage_progress_penalty
        logger.info("reward_calculated", reward=reward)
        return reward

    def _is_early_stage(self, stage: str) -> bool:
        early_stages = ["Initial_Access", "Persistence", "Discovery"]
        return stage in early_stages
