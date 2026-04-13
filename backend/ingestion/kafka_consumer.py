import asyncio
from typing import Any, Callable

from backend.ingestion.batch_collector import BatchCollector
from backend.ingestion.cicflow_parser import parse_kafka_message
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("kafka_consumer")


class KafkaFlowConsumer:
    def __init__(self, on_flow: Callable[[dict[str, Any]], None]):
        self.on_flow = on_flow
        self.consumer = None
        self.running = False
        self._task: asyncio.Task | None = None
        self._batch_collector = BatchCollector(window_seconds=60)

    async def start(self) -> None:
        try:
            from kafka import KafkaConsumer
        except ImportError:
            logger.warning("kafka_not_available_falling_back_to_csv")
            return

        servers = config.get("kafka.bootstrap_servers", "localhost:9092")
        topic = config.get("kafka.topic", "network-flows")
        group = config.get("kafka.consumer_group", "chainbreaker-consumers")

        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=servers,
                group_id=group,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                value_deserializer=lambda m: parse_kafka_message(m) or {},
                consumer_timeout_ms=5000,
            )
            self.running = True
            self._task = asyncio.create_task(self._consume_loop())
            logger.info("kafka_consumer_started", topic=topic, servers=servers)
        except Exception as e:
            logger.warning("kafka_connection_failed", error=str(e))
            self.running = False

    async def _consume_loop(self) -> None:
        while self.running and self.consumer:
            try:
                for message in self.consumer:
                    if not self.running:
                        break
                    flow = message.value
                    if flow:
                        self._batch_collector.add(flow)
                        await self.on_flow(flow)
                    await asyncio.sleep(0)
            except StopIteration:
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("kafka_consume_error", error=str(e))
                await asyncio.sleep(5)

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.consumer:
            self.consumer.close()
        logger.info("kafka_consumer_stopped")
