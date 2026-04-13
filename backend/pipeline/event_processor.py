from typing import Any

from backend.pipeline.orchestrator import Orchestrator
from backend.utils.logger import setup_logger

logger = setup_logger("event_processor")


class EventProcessor:
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.alert_count = 0

    async def on_flow(self, flow: dict[str, Any]) -> dict | None:
        try:
            result = await self.orchestrator.process_flow(flow)
            if result:
                self.alert_count += 1
                logger.info("flow_processed_with_alert", count=self.alert_count, **result)
            return result
        except Exception as e:
            logger.error("flow_processing_failed", error=str(e), flow_src=flow.get("src_ip"))
            return None
