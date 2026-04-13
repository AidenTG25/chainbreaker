from backend.mitre.attack_matrix import KillChainStage


CICAPT_ML_LABEL_MAP = {
    "BENIGN": None,
    "BruteForce": KillChainStage.INITIAL_ACCESS,
    "DDoS": KillChainStage.DENIAL_OF_SERVICE,
    "DoS": KillChainStage.DENIAL_OF_SERVICE,
    "Mirai": KillChainStage.INITIAL_ACCESS,
    "Reconnaissance": KillChainStage.DISCOVERY,
    "PortScan": KillChainStage.DISCOVERY,
    "VulnerabilityScan": KillChainStage.DISCOVERY,
    "Injection": KillChainStage.INITIAL_ACCESS,
    "XSS": KillChainStage.INITIAL_ACCESS,
    "Backdoor": KillChainStage.PERSISTENCE,
    "Trojan": KillChainStage.PERSISTENCE,
    "Ransomware": KillChainStage.EXFILTRATION,
    "DataTheft": KillChainStage.EXFILTRATION,
    "LateralMovement": KillChainStage.LATERAL_MOVEMENT,
    "PrivilegeEscalation": KillChainStage.CREDENTIAL_ACCESS,
    "CredentialTheft": KillChainStage.CREDENTIAL_ACCESS,
    "C2": KillChainStage.COMMAND_AND_CONTROL,
    "Exfiltration": KillChainStage.EXFILTRATION,
    "Evasion": KillChainStage.DEFENSE_EVASION,
    "CISA": KillChainStage.INITIAL_ACCESS,
    "HTTP": KillChainStage.COMMAND_AND_CONTROL,
    "DNS": KillChainStage.COMMAND_AND_CONTROL,
    "FTP": KillChainStage.LATERAL_MOVEMENT,
    "SSH": KillChainStage.LATERAL_MOVEMENT,
    "SMB": KillChainStage.LATERAL_MOVEMENT,
    "RDP": KillChainStage.LATERAL_MOVEMENT,
}


MITRE_STAGE_ID_MAP = {
    "Initial_Access": "TA0001",
    "Persistence": "TA0003",
    "Command_and_Control": "TA0011",
    "Discovery": "TA0007",
    "Credential_Access": "TA0006",
    "Lateral_Movement": "TA0008",
    "Defense_Evasion": "TA0005",
    "Exfiltration": "TA0010",
}


def ml_label_to_stage(ml_label: str) -> KillChainStage | None:
    normalized = ml_label.strip().upper()
    for key, stage in CICAPT_ML_LABEL_MAP.items():
        if key.upper() == normalized:
            return stage
    for key, stage in CICAPT_ML_LABEL_MAP.items():
        if key.upper() in normalized or normalized in key.upper():
            return stage
    return None


def stage_to_mitre_id(stage: KillChainStage) -> str:
    return MITRE_STAGE_ID_MAP.get(stage.value, "TA0000")


def stage_to_mitre_name(stage: KillChainStage) -> str:
    return stage.value.replace("_", " ")
