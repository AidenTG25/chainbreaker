from backend.mitre.attack_matrix import KillChainStage, STAGE_MITRE_TACTICS


ATTACK_TYPE_TO_TACTICS = {
    "bruteforce": [KillChainStage.INITIAL_ACCESS, KillChainStage.CREDENTIAL_ACCESS],
    "password_spray": [KillChainStage.INITIAL_ACCESS, KillChainStage.CREDENTIAL_ACCESS],
    "dictionary": [KillChainStage.INITIAL_ACCESS, KillChainStage.CREDENTIAL_ACCESS],
    "ddos": [KillChainStage.DENIAL_OF_SERVICE],
    "dos": [KillChainStage.DENIAL_OF_SERVICE],
    "mirai": [KillChainStage.INITIAL_ACCESS, KillChainStage.DENIAL_OF_SERVICE],
    "syn_flood": [KillChainStage.DENIAL_OF_SERVICE],
    "udp_flood": [KillChainStage.DENIAL_OF_SERVICE],
    "http_flood": [KillChainStage.DENIAL_OF_SERVICE],
    "portscan": [KillChainStage.DISCOVERY],
    "reconnaissance": [KillChainStage.DISCOVERY],
    "host_discovery": [KillChainStage.DISCOVERY],
    "service_discovery": [KillChainStage.DISCOVERY],
    "vulnerability_scan": [KillChainStage.DISCOVERY],
    "backdoor": [KillChainStage.PERSISTENCE, KillChainStage.COMMAND_AND_CONTROL],
    "rootkit": [KillChainStage.PERSISTENCE],
    "trojan": [KillChainStage.PERSISTENCE],
    "ransomware": [KillChainStage.PERSISTENCE, KillChainStage.EXFILTRATION],
    "data_theft": [KillChainStage.EXFILTRATION],
    "data_exfiltration": [KillChainStage.EXFILTRATION],
    "lateral_movement": [KillChainStage.LATERAL_MOVEMENT],
    "pass_the_hash": [KillChainStage.LATERAL_MOVEMENT, KillChainStage.CREDENTIAL_ACCESS],
    "smb_relay": [KillChainStage.LATERAL_MOVEMENT, KillChainStage.CREDENTIAL_ACCESS],
    "wmi": [KillChainStage.LATERAL_MOVEMENT, KillChainStage.PERSISTENCE],
    "powershell": [KillChainStage.COMMAND_AND_CONTROL, KillChainStage.DEFENSE_EVASION],
    "c2": [KillChainStage.COMMAND_AND_CONTROL],
    "beacon": [KillChainStage.COMMAND_AND_CONTROL],
    "dns_tunnel": [KillChainStage.COMMAND_AND_CONTROL],
    "http_tunnel": [KillChainStage.COMMAND_AND_CONTROL],
    "log_tampering": [KillChainStage.DEFENSE_EVASION],
    "disable_security": [KillChainStage.DEFENSE_EVASION],
    "clear_logs": [KillChainStage.DEFENSE_EVASION],
    "obfuscation": [KillChainStage.DEFENSE_EVASION],
}


def align_attack_type_to_tactics(attack_type: str) -> list[KillChainStage]:
    normalized = attack_type.lower().strip()
    for key, tactics in ATTACK_TYPE_TO_TACTICS.items():
        if key in normalized or normalized in key:
            return tactics
    return [KillChainStage.INITIAL_ACCESS]


def get_all_mitre_tactics_for_attack(attack_type: str) -> list[str]:
    stages = align_attack_type_to_tactics(attack_type)
    tactics = []
    for stage in stages:
        tactics.extend(STAGE_MITRE_TACTICS.get(stage, []))
    return list(set(tactics))


def infer_stage_from_flow_features(
    src_port: int, dst_port: int, packet_count: int, byte_count: int
) -> list[KillChainStage]:
    likely_stages = []
    if dst_port in [22, 23, 3389, 21]:
        likely_stages.append(KillChainStage.INITIAL_ACCESS)
    if packet_count > 1000 and byte_count > 1000000:
        likely_stages.append(KillChainStage.DENIAL_OF_SERVICE)
    if src_port in [4444, 5555, 6666, 8080, 31337]:
        likely_stages.append(KillChainStage.COMMAND_AND_CONTROL)
    if dst_port == 445 or dst_port == 139:
        likely_stages.append(KillChainStage.LATERAL_MOVEMENT)
    if dst_port in [53, 443, 80]:
        likely_stages.append(KillChainStage.DISCOVERY)
    return likely_stages
