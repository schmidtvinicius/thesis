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
- How can we develop a benchmark to evaluate streaming use cases in lakehouse systems?
## Experiments
### Metrics
- When looking at latency, we could use event-time as the start time and the end time could be the timestamp when files are created on the object store. This time can be accessed via the metadata layer of the lakehouse.

### Resources
- [Radboud clusters](https://wiki.icis-intra.cs.ru.nl/Cluster#Access_to_Cluster_Resources)

