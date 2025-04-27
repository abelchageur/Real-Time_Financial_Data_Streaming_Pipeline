#!/bin/bash
# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
cub kafka-ready -b kafka:9092 1 30
# Create topics
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic raw-financial-data --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic transformed-financial-data --partitions 3 --replication-factor 1
echo "Kafka topics created successfully!"