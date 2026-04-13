import pytest
from backend.agent.action_masker import ActionMasker


def test_action_masker_initial_access():
    masker = ActionMasker()
    mask = masker.get_mask("Initial_Access")
    assert mask.shape[0] == 8
    assert mask[0] == 1.0
    assert mask[3] == 1.0
    assert mask[1] == 0.0


def test_action_masker_lateral_movement():
    masker = ActionMasker()
    mask = masker.get_mask("Lateral_Movement")
    assert mask[0] == 1.0
    assert mask[1] == 1.0
    assert mask[3] == 1.0
    assert mask[5] == 1.0


def test_action_masker_unknown_stage():
    masker = ActionMasker()
    mask = masker.get_mask(None)
    assert mask.sum() == 8.0


def test_get_valid_actions():
    masker = ActionMasker()
    valid = masker.get_valid_actions("Initial_Access")
    assert 0 in valid
    assert 3 in valid
    assert 4 in valid
    assert 6 in valid
    assert 1 not in valid


def test_action_names():
    masker = ActionMasker()
    assert masker.get_action_name(0) == "block_ip"
    assert masker.get_action_name(7) == "collect_forensics"
    assert masker.get_action_name(99) == "unknown"
