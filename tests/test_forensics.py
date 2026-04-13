import pytest
from backend.agent.reward_calculator import RewardCalculator


def test_reward_early_containment():
    calc = RewardCalculator()
    reward = calc.calculate(
        stage_contained=True,
        previous_stage="Initial_Access",
        current_stage="Initial_Access",
        blast_radius_reduction=0.0,
        dwell_time_seconds=0.0,
        is_false_positive=False,
        action_taken=True,
    )
    assert reward > 0


def test_reward_false_positive():
    calc = RewardCalculator()
    reward = calc.calculate(
        stage_contained=False,
        previous_stage="Discovery",
        current_stage="Discovery",
        blast_radius_reduction=0.0,
        dwell_time_seconds=0.0,
        is_false_positive=True,
        action_taken=True,
    )
    assert reward < 0


def test_reward_stage_progression():
    calc = RewardCalculator()
    reward = calc.calculate(
        stage_contained=False,
        previous_stage="Initial_Access",
        current_stage="Persistence",
        blast_radius_reduction=0.0,
        dwell_time_seconds=0.0,
        is_false_positive=False,
        action_taken=False,
    )
    assert reward < 0
