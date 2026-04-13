import numpy as np

from backend.mitre.attack_matrix import KillChainStage
from backend.utils.config import config

ACTION_LIST = [
    "block_ip",
    "isolate_host",
    "kill_process",
    "reset_connection",
    "block_port",
    "quarantine_subnet",
    "notify_admin",
    "collect_forensics",
]

STAGE_ACTION_MASK = {
    "Initial_Access": [True, False, False, True, True, False, True, False],
    "Persistence": [False, True, True, False, False, False, True, False],
    "Command_and_Control": [True, False, False, True, True, True, False, False],
    "Discovery": [True, False, False, False, True, False, True, False],
    "Credential_Access": [False, True, True, False, False, False, True, True],
    "Lateral_Movement": [True, True, False, True, False, True, False, False],
    "Defense_Evasion": [False, True, True, False, False, True, False, True],
    "Exfiltration": [True, False, False, True, False, True, False, True],
}


class ActionMasker:
    def __init__(self):
        self.action_dim = len(ACTION_LIST)
        self.stage_mask = STAGE_ACTION_MASK

    def get_mask(self, active_stage: str | None) -> np.ndarray:
        mask = np.zeros(self.action_dim, dtype=np.float32)
        if active_stage and active_stage in self.stage_mask:
            valid_actions = self.stage_mask[active_stage]
            for i, valid in enumerate(valid_actions):
                if valid:
                    mask[i] = 1.0
        else:
            mask[:] = 1.0
        return mask

    def get_valid_actions(self, active_stage: str | None) -> list[int]:
        mask = self.get_mask(active_stage)
        return [i for i, v in enumerate(mask) if v == 1.0]

    def get_action_name(self, action_idx: int) -> str:
        if 0 <= action_idx < len(ACTION_LIST):
            return ACTION_LIST[action_idx]
        return "unknown"
