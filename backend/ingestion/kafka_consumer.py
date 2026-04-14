import json
import time
from confluent_kafka import Consumer

config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "chainbreaker-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
}

consumer = Consumer(config)
consumer.subscribe(["network-events"])


def process_message(msg):
    data = json.loads(msg.value().decode("utf-8"))

    
    print(
        f"{msg.topic()} | P{msg.partition()} | O{msg.offset()} | "
        f"{data.get('Src IP')} → {data.get('Dst IP')}"
    )

    return data


BATCH_SIZE = 100
batch = []
total_processed = 0
start_time = time.time()

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        batch.append(msg)

        if len(batch) >= BATCH_SIZE:
            for m in batch:
                process_message(m)

            
            consumer.commit()

            total_processed += len(batch)

            
            elapsed = time.time() - start_time
            print(f" Processed {total_processed} messages in {elapsed:.2f}s")

            batch.clear()

except KeyboardInterrupt:
    print("\nStopping consumer...")

    
    for m in batch:
        process_message(m)

    consumer.commit()

finally:
    consumer.close()