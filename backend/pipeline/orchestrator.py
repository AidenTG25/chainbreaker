import asyncio
from typing import Any

from backend.graph.neo4j_client import neo4j_client
from backend.graph.attack_writer import write_attack_event, link_communication, mark_host_suspected
from backend.graph.kill_chain_writer import update_kill_chain_stage, mark_host_compromised
from backend.graph.host_manager import upsert_hosts
from backend.ml.model_manager import ModelManager
from backend.mitre.stage_mapper import ml_label_to_stage
from backend.utils.logger import setup_logger
from backend.utils.metrics import Metrics

logger = setup_logger("orchestrator")


class Orchestrator:
    def __init__(self):
        self.model_manager = ModelManager()
        self.running = False

    async def start(self) -> None:
        await neo4j_client.connect()
        self.model_manager.load_all()
        self.running = True
        logger.info("orchestrator_started")

    async def stop(self) -> None:
        self.running = False
        await neo4j_client.close()
        logger.info("orchestrator_stopped")

    async def process_flow(self, flow: dict[str, Any]) -> dict | None:
        Metrics.flows_processed.inc()
        src_ip = flow.get("src_ip", "")
        dst_ip = flow.get("dst_ip", "")

        if not src_ip or not dst_ip:
            return None

        await upsert_hosts([src_ip, dst_ip])

        prediction = self.model_manager.predict(flow)
        if len(prediction) == 3:
            label, confidence, model_votes = prediction
        else:
            label, confidence = prediction
            model_votes = {}

        if not label:
            await link_communication(src_ip, dst_ip, protocol=flow.get("protocol"), flow_count=1,
                                     total_bytes=flow.get("total_bytes", 0))
            return None

        stage = label
        Metrics.ml_predictions.labels(stage=stage, model="ensemble").inc()
        Metrics.ml_confidence.labels(stage=stage).observe(confidence)

        logger.info("attack_detected", src_ip=src_ip, dst_ip=dst_ip, stage=stage, confidence=confidence)

        event_id = await write_attack_event(
            source_ip=src_ip,
            dest_ip=dst_ip,
            stage=stage,
            confidence=confidence,
            attack_label=label,
            ml_model="ensemble",
            protocol=flow.get("protocol"),
            timestamp=flow.get("timestamp"),
        )

        await update_kill_chain_stage(dst_ip, stage, status="active")
        await mark_host_compromised(dst_ip, "compromised")
        await mark_host_suspected(src_ip)

        await link_communication(src_ip, dst_ip, protocol=flow.get("protocol"),
                                 flow_count=1, total_bytes=flow.get("total_bytes", 0),
                                 suspicious=True)

        return {
            "event_id": event_id,
            "stage": stage,
            "confidence": confidence,
            "dest_ip": dst_ip,
            "source_ip": src_ip,
            "attack_label": label,
        }

    async def process_batch(self, flows: list[dict[str, Any]]) -> list[dict]:
        if not flows:
            return []
        all_ips = set()
        for f in flows:
            all_ips.add(f.get("src_ip", ""))
            all_ips.add(f.get("dst_ip", ""))
        await upsert_hosts(list(all_ips))

        predictions = self.model_manager.predict_batch(flows)
        results = []
        for flow, prediction in zip(flows, predictions):
            if len(prediction) == 3:
                label, confidence, model_votes = prediction
            else:
                label, confidence = prediction
                model_votes = {}

            if not label:
                await link_communication(flow.get("src_ip", ""), flow.get("dst_ip", ""),
                                         protocol=flow.get("protocol"), flow_count=1,
                                         total_bytes=flow.get("total_bytes", 0))
                continue

            event_id = await write_attack_event(
                source_ip=flow.get("src_ip", ""),
                dest_ip=flow.get("dst_ip", ""),
                stage=label,
                confidence=confidence,
                attack_label=label,
                ml_model="ensemble",
                protocol=flow.get("protocol"),
                timestamp=flow.get("timestamp"),
            )
            await update_kill_chain_stage(flow.get("dst_ip", ""), label, status="active")
            await mark_host_compromised(flow.get("dst_ip", ""), "compromised")
            results.append({
                "event_id": event_id,
                "stage": label,
                "confidence": confidence,
                "dest_ip": flow.get("dst_ip", ""),
                "source_ip": flow.get("src_ip", ""),
            })
        return results
