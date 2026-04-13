from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class KillChainStage(str, Enum):
    INITIAL_ACCESS = "Initial_Access"
    PERSISTENCE = "Persistence"
    COMMAND_AND_CONTROL = "Command_and_Control"
    DISCOVERY = "Discovery"
    CREDENTIAL_ACCESS = "Credential_Access"
    LATERAL_MOVEMENT = "Lateral_Movement"
    DEFENSE_EVASION = "Defense_Evasion"
    EXFILTRATION = "Exfiltration"
    DENIAL_OF_SERVICE = "Denial_of_Service"


STAGE_ORDER = [
    KillChainStage.INITIAL_ACCESS,
    KillChainStage.PERSISTENCE,
    KillChainStage.COMMAND_AND_CONTROL,
    KillChainStage.DISCOVERY,
    KillChainStage.CREDENTIAL_ACCESS,
    KillChainStage.LATERAL_MOVEMENT,
    KillChainStage.DEFENSE_EVASION,
    KillChainStage.EXFILTRATION,
    KillChainStage.DENIAL_OF_SERVICE,
]

STAGE_PRIORITY = {stage: idx for idx, stage in enumerate(STAGE_ORDER)}

STAGE_MITRE_TACTICS = {
    KillChainStage.INITIAL_ACCESS: [
        "T1190",  # Exploit Public-Facing Application
        "T1133",  # External Remote Services
        "T1566",  # Phishing
        "T1078",  # Valid Accounts
    ],
    KillChainStage.PERSISTENCE: [
        "T1050",  # New Service
        "T1053",  # Scheduled Task/Job
        "T1547",  # Boot or Logon Autostart Execution
        "T1543",  # Create/Modify System Process
    ],
    KillChainStage.COMMAND_AND_CONTROL: [
        "T1071",  # Application Layer Protocol
        "T1090",  # Proxy
        "T1105",  # Ingress Tool Transfer
        "T1573",  # Encrypted Channel
    ],
    KillChainStage.DISCOVERY: [
        "T1046",  # Network Service Discovery
        "T1135",  # Network Share Discovery
        "T1082",  # System Information Discovery
        "T1018",  # Remote System Discovery
    ],
    KillChainStage.CREDENTIAL_ACCESS: [
        "T1110",  # Brute Force
        "T1003",  # OS Credential Dumping
        "T1552",  # Unsecured Credentials
        "T1555",  # Credentials from Password Stores
    ],
    KillChainStage.LATERAL_MOVEMENT: [
        "T1021",  # Remote Services
        "T1570",  # Lateral Tool Transfer
        "T1534",  # Internal Spearphishing
    ],
    KillChainStage.DEFENSE_EVASION: [
        "T1562",  # Impair Defenses
        "T1070",  # Indicator Removal
        "T1027",  # Obfuscated Files or Information
    ],
    KillChainStage.EXFILTRATION: [
        "T1041",  # Exfiltration Over C2 Channel
        "T1567",  # Exfiltration Over Web Service
        "T1048",  # Exfiltration Over Alternative Protocol
    ],
}

STAGE_DESCRIPTIONS = {
    KillChainStage.INITIAL_ACCESS: "Attacker gains initial foothold into the network via phishing, exploitation, or stolen credentials.",
    KillChainStage.PERSISTENCE: "Attacker establishes foothold through scheduled tasks, services, or registry modifications.",
    KillChainStage.COMMAND_AND_CONTROL: "Attacker establishes communication channel with compromised host for remote control.",
    KillChainStage.DISCOVERY: "Attacker enumerates the network to understand topology, identify assets, and plan lateral movement.",
    KillChainStage.CREDENTIAL_ACCESS: "Attacker extracts credentials from memory, SAM database, or authentication services.",
    KillChainStage.LATERAL_MOVEMENT: "Attacker moves from initial host to other systems using credentials or remote services.",
    KillChainStage.DEFENSE_EVASION: "Attacker disables security tools, clears logs, or obfuscates activity to avoid detection.",
    KillChainStage.EXFILTRATION: "Attacker extracts sensitive data from the compromised network.",
}

STAGE_SEVERITY = {
    KillChainStage.INITIAL_ACCESS: 3,
    KillChainStage.PERSISTENCE: 4,
    KillChainStage.COMMAND_AND_CONTROL: 5,
    KillChainStage.DISCOVERY: 4,
    KillChainStage.CREDENTIAL_ACCESS: 6,
    KillChainStage.LATERAL_MOVEMENT: 7,
    KillChainStage.DEFENSE_EVASION: 5,
    KillChainStage.EXFILTRATION: 9,
}


@dataclass
class StageDefinition:
    name: KillChainStage
    priority: int
    mitre_tactics: list[str]
    description: str
    severity: int
    valid_transitions: list["KillChainStage"] = field(default_factory=list)


def get_stage_definition(stage: KillChainStage) -> StageDefinition:
    transitions = []
    idx = STAGE_ORDER.index(stage)
    if idx < len(STAGE_ORDER) - 1:
        transitions = STAGE_ORDER[idx + 1 :]

    return StageDefinition(
        name=stage,
        priority=STAGE_PRIORITY[stage],
        mitre_tactics=STAGE_MITRE_TACTICS[stage],
        description=STAGE_DESCRIPTIONS[stage],
        severity=STAGE_SEVERITY[stage],
        valid_transitions=transitions,
    )


def is_valid_transition(from_stage: KillChainStage, to_stage: KillChainStage) -> bool:
    if from_stage == to_stage:
        return True
    return to_stage in STAGE_ORDER and STAGE_ORDER.index(to_stage) > STAGE_ORDER.index(from_stage)


def get_stage_severity(stage: KillChainStage) -> int:
    return STAGE_SEVERITY.get(stage, 5)
