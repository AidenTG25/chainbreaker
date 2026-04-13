import pytest
from backend.mitre.attack_matrix import (
    KillChainStage, STAGE_ORDER, STAGE_PRIORITY, get_stage_severity
)
from backend.mitre.stage_mapper import ml_label_to_stage, stage_to_mitre_id
from backend.mitre.tactic_aligner import align_attack_type_to_tactics


def test_stage_order():
    assert len(STAGE_ORDER) == 9
    assert STAGE_ORDER[0] == KillChainStage.INITIAL_ACCESS
    assert STAGE_ORDER[-1] == KillChainStage.DENIAL_OF_SERVICE


def test_stage_priority():
    assert STAGE_PRIORITY[KillChainStage.INITIAL_ACCESS] == 0
    assert STAGE_PRIORITY[KillChainStage.EXFILTRATION] == 7


def test_ml_label_mapping():
    assert ml_label_to_stage("BruteForce") == KillChainStage.INITIAL_ACCESS
    assert ml_label_to_stage("DDoS") == KillChainStage.DENIAL_OF_SERVICE
    assert ml_label_to_stage("BENIGN") is None
    assert ml_label_to_stage("PortScan") == KillChainStage.DISCOVERY


def test_stage_severity():
    assert get_stage_severity(KillChainStage.INITIAL_ACCESS) == 3
    assert get_stage_severity(KillChainStage.EXFILTRATION) == 9


def test_tactic_aligner():
    tactics = align_attack_type_to_tactics("portscan")
    assert KillChainStage.DISCOVERY in tactics
    tactics = align_attack_type_to_tactics("bruteforce")
    assert KillChainStage.CREDENTIAL_ACCESS in tactics


def test_mitre_id_mapping():
    assert stage_to_mitre_id(KillChainStage.INITIAL_ACCESS) == "TA0001"
    assert stage_to_mitre_id(KillChainStage.COMMAND_AND_CONTROL) == "TA0011"
