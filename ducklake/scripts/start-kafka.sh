#!/bin/bash
docker run -d --name kafka -p 9092:9092 apache/kafka:4.1.0
sleep 2
docker exec -it kafka sh -c "/opt/kafka/bin/kafka-topics.sh --create --if-not-exists --topic my-topic --bootstrap-server localhost:9092"