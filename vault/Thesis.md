## Research questions/objectives

- Discuss features and metrics of current stream processing system benchmarks as well as lakehouse benchmarks
	- Propose possible improvements?
- Discuss common datasets and workloads that can be used to evaluate SPSs and lakehouses
- Propose a benchmark that evaluates SPSs in combination with lakehouses
	- Allow for extensibility to other SPSs and lakehouses
	- Allow different datasets
- Demonstrate the proposed benchmark to evaluate a few state-of-the-art SPSs and lakehouses
	- SPSs:
		- Flink
		- Storm
		- Kafka streams?
		- Spark streaming?
	- Lakehouse:
		- Iceberg
		- Delta
		- Ducklake
- What are the limitations of lakehouses for streaming?
- **How can we develop a benchmark to evaluate streaming use cases in lakehouse systems?**
## Experiments
### Design
- When running concurrent operations, each python instance has its own reader but all instances write to the same lakehouse sink
### Metrics
- When looking at latency, we could use event-time as the start time and the end time could be the timestamp when files are created on the object store. This time can be accessed via the metadata layer of the lakehouse.
- LST-Bench uses [azure monitor tools](https://learn.microsoft.com/en-us/python/api/overview/azure/monitor?view=azure-python), since they use Azure for their experiments. Amazon has something similar, namely [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), which can be accessed through the following [python library](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html). 
- In addition, there's a python library called [psutil](https://psutil.readthedocs.io/en/latest/index.html#) that can access disk I/O locally. We could use this library by creating a separate partition and analyzing the disk usage on that particular partition. I just don't know if this would be feasible on Amazon. 
### Kafka
- `docker compose down` fully destroys the container and wipes all existing topics
- `docker compose restart` keeps the topic intact 

### Spark 
- When consuming from Kafka, Spark creates its own weird group id for each query, which makes it hard to track down at which offset the consumer stopped when we run the query for a fixed time period
- When updating a table using `overwrite` in a `foreachBatch`, the table is not fully overwritten, but Spark merges the values in the micro-batch with the existing ones in the table and it inserts new values, similar to a `MERGE INTO` operation. However, this operation doesn't seem to trigger deletion vectors
- When running the example provided in the [Streaming Patterns with DuckDB](https://duckdb.org/2025/10/13/duckdb-streaming-patterns) blogpost, it seems that spark processes the same event more than once when using built-in functions and `MERGE INTO`. This is not a bug, but rather me being stupid: If we use the `agg_df` from the blog post, it will, as the name implies, make sure that all aggregations are done as data is processed by spark. So when we pass that data frame to `foreachBatch`, we need only to overwrite the table with the new data, as spark has already updated it. If we instead perform a `MERGE INTO` using the `agg_df`, we're in fact doubly updating the data, leading to the results that we (or rather I) observed. So if we want to use `MERGE INTO`, we need to use `foreachBatch` on the `parsed_df` with `outputMode` set to "append", as spark does not support "complete" mode for data frames that don't use aggregation. This way we can do the filtering and aggregation all in SQL and then merge the data into the table. We could also perform all aggregations in spark (with the `agg_df`) and use `outputMode` "update", which would then only output the updated rows. In that case we can still use `MERGE INTO`, but then we just assign the rows the new values instead of adding them up. 

### Resources
- [Radboud clusters](https://wiki.icis-intra.cs.ru.nl/Cluster#Access_to_Cluster_Resources)
- [Spark on Docker](https://karlchris.github.io/data-engineering/projects/spark-docker/)
- 

