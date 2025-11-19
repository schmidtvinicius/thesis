# Kafka + Spark + Iceberg
This repository contains some experiments using Apache Spark to read and process a Kafka topic and update an Iceberg table.

## Running the experiments

### Docker
When running everything in Docker, a simple `docker compose up -d` from the root of the project will start the Kafka server, a PostgreSQL instance and a Polaris Catalog server with the appropriate containers to bootstrap PostgreSQL (see: https://github.com/apache/polaris/tree/main/getting-started/jdbc).

### Locally
WIP. We will have to download the Polaris source code from [github](https://github.com/apache/polaris) and then follow the steps to build it and run it locally [here](https://polaris.apache.org/releases/1.2.0/getting-started/deploying-polaris/local-deploy/)

## Current experiments
Currently, we only have a single script that starts a [Kafka Producer](https://confluent-kafka-python.readthedocs.io/en/latest/#producer) thread and then uses Spark to subscribe to the topic and do some simple processing on the data, which is then written to Iceberg. This was taken from a DuckDB blogpost about [Streaming Patterns with DuckDB](https://duckdb.org/2025/10/13/duckdb-streaming-patterns)