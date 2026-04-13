#!/bin/bash
set -e

echo "Setting up Kafka topics for ChainBreaker..."

TOPICS=("network-flows" "security-alerts")

for topic in "${TOPICS[@]}"; do
    docker exec chainbreaker-kafka kafka-topics \
        --create \
        --if-not-exists \
        --bootstrap-server localhost:9092 \
        --replication-factor 1 \
        --partitions 3 \
        --topic "$topic"
    echo "Topic '$topic' created or already exists"
done

echo "Kafka setup complete"
