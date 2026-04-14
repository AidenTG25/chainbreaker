"""
kafka_consumer.py — Kafka → Parser → Neo4j flow graph ingestion.

Pipeline:
    Kafka "network-events"
        → json.loads (raw CSV row dict)
        → parse_network_flow_row (normalise keys, validate IPs)
        → ingest_flow_batch (UNWIND Cypher → Neo4j)
        → consumer.commit()
"""

import asyncio
import json
import time

from confluent_kafka import Consumer, KafkaError

from backend.graph.flow_writer import ingest_flow_batch
from backend.graph.neo4j_client import neo4j_client
from backend.ingestion.cicflow_parser import parse_network_flow_row


KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "chainbreaker-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}

TOPIC = "network-events"
BATCH_SIZE = 100
MAX_WAIT_SECONDS = 5.0   # flush partial batch after this many idle seconds


async def main():
    neo4j_client.connect()
    print("[consumer] Neo4j connected")

    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe([TOPIC])
    print(f"[consumer] Subscribed to '{TOPIC}', batch_size={BATCH_SIZE}")

    batch = []
    total_inserted = 0
    total_rejected = 0
    debug_printed = 0
    last_flush = time.monotonic()
    start = time.monotonic()

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                # Flush partial batch after idle period
                if batch and (time.monotonic() - last_flush) > MAX_WAIT_SECONDS:
                    count = await ingest_flow_batch(batch)
                    total_inserted += count
                    consumer.commit()
                    batch.clear()
                    last_flush = time.monotonic()
                continue

            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[consumer] Kafka error: {msg.error()}")
                continue

            # ── Parse ──────────────────────────────────────────────────────
            try:
                raw = json.loads(msg.value().decode("utf-8"))
            except Exception as e:
                print(f"[consumer] JSON decode error at offset {msg.offset()}: {e}")
                total_rejected += 1
                continue

            flow = parse_network_flow_row(raw)

            if flow is not None:
                if debug_printed < 5:
                    print(flow)
                    debug_printed += 1
                batch.append(flow)
            else:
                print("INVALID:", raw)
                total_rejected += 1
                continue

            # ── Flush batch ────────────────────────────────────────────────
            if len(batch) >= BATCH_SIZE:
                count = await ingest_flow_batch(batch)
                total_inserted += count
                consumer.commit()

                elapsed = time.monotonic() - start
                rate = total_inserted / max(elapsed, 0.001)
                print(f"[consumer] total_inserted={total_inserted} "
                      f"rejected={total_rejected} "
                      f"rate={rate:.0f} flows/s")

                batch.clear()
                last_flush = time.monotonic()

    except KeyboardInterrupt:
        print("\n[consumer] Stopping...")

    finally:
        # Flush remaining
        if batch:
            print(f"[consumer] Flushing remaining {len(batch)} flows...")
            count = await ingest_flow_batch(batch)
            total_inserted += count
            consumer.commit()

        elapsed = time.monotonic() - start
        print(f"[consumer] Done. total_inserted={total_inserted} "
              f"rejected={total_rejected} elapsed={elapsed:.1f}s")

        consumer.close()
        await neo4j_client.close()


if __name__ == "__main__":
    asyncio.run(main())
