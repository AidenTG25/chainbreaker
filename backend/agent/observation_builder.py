import numpy as np
from typing import Any

from backend.graph.neo4j_client import neo4j_client
from backend.mitre.attack_matrix import STAGE_PRIORITY, KillChainStage
from backend.utils.logger import setup_logger

logger = setup_logger("observation_builder")


class ObservationBuilder:
    def __init__(self, max_hosts: int = 100):
        self.max_hosts = max_hosts

    async def build(self) -> np.ndarray:
        blast_radius = await neo4j_client.get_blast_radius()
        active_stages = await self._get_active_stage_metrics()
        host_metrics = await self._get_host_metrics()
        edge_metrics = await self._get_edge_metrics()
        stage_status = await self._get_stage_status_vector()

        obs = np.concatenate([
            blast_radius,
            active_stages,
            host_metrics,
            edge_metrics,
            stage_status,
        ])
        obs = np.nan_to_num(obs, nan=0.0, posinf=0.0, neginf=0.0)
        return obs

    async def _get_active_stage_metrics(self) -> np.ndarray:
        query = """
        MATCH (k:KillChainStage)
        WHERE k.status IN ['active', 'suspected']
        RETURN k.stage AS stage, count(*) AS count
        """
        results = await neo4j_client.execute(query)
        metrics = np.zeros(8)
        for r in results:
            stage = r.get("stage", "")
            count = r.get("count", 0)
            try:
                idx = list(KillChainStage).index(KillChainStage(stage))
                metrics[idx] = float(count)
            except (ValueError, KeyError):
                pass
        return metrics

    async def _get_host_metrics(self) -> np.ndarray:
        query = """
        MATCH (h:Host)
        RETURN h.compromise_status AS status, count(*) AS count
        """
        results = await neo4j_client.execute(query)
        compromised = 0.0
        suspected = 0.0
        clean = 0.0
        for r in results:
            status = r.get("status", "")
            count = float(r.get("count", 0))
            if status == "compromised":
                compromised = count
            elif status == "suspected":
                suspected = count
            elif status == "clean":
                clean = count
        total = max(compromised + suspected + clean, 1)
        return np.array([compromised, suspected, clean, compromised / total, suspected / total])

    async def _get_edge_metrics(self) -> np.ndarray:
        query = """
        MATCH ()-[r:COMMUNICATES_WITH]->()
        RETURN count(*) AS total, sum(r.suspicious) AS suspicious_count
        """
        results = await neo4j_client.execute(query)
        total = 1.0
        suspicious = 0.0
        if results:
            total = max(float(results[0].get("total", 1)), 1)
            suspicious = float(results[0].get("suspicious_count", 0))
        return np.array([total, suspicious, suspicious / total])

    async def _get_stage_status_vector(self) -> np.ndarray:
        query = """
        MATCH (k:KillChainStage)
        RETURN k.stage AS stage, k.status AS status
        """
        results = await neo4j_client.execute(query)
        vector = np.zeros(16)
        for r in results:
            stage = r.get("stage", "")
            status = r.get("status", "")
            try:
                stage_idx = list(KillChainStage).index(KillChainStage(stage))
                if status == "active":
                    vector[stage_idx] = 1.0
                elif status == "contained":
                    vector[stage_idx + 8] = 1.0
            except (ValueError, KeyError):
                pass
        return vector
