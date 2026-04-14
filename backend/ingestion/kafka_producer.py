import pandas as pd
import json
from confluent_kafka import Producer

config = {
    "bootstrap.servers": "localhost:9092",
    "client.id": "chainbreaker-producer",
    "linger.ms": 20,
    "batch.num.messages": 1000,
    "queue.buffering.max.messages": 100000
}

producer = Producer(config)


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")


def stream_csv(filepath: str, topic: str):
    chunk_size = 1000
    total = 0

    for chunk in pd.read_csv(filepath, encoding="latin-1", chunksize=chunk_size):
        for idx, row in chunk.iterrows():
            payload = row.to_dict()
            message = json.dumps(payload).encode("utf-8")

            try:
                producer.produce(
                    topic=topic,
                    key=payload.get("Src IP", str(idx)),
                    value=message,
                    callback=delivery_report
                )
            except BufferError:
                producer.poll(1)

            producer.poll(0)
            total += 1

        print(f"✅ Sent {total} messages so far")

    print("🚀 Flushing...")
    producer.flush()


if __name__ == "__main__":
    stream_csv("data/raw/phase1_NetworkData.csv", "network-events")