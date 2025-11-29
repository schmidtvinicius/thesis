## Questions

- I can't create a free-tier account on AWS because I had previously created one. I'll try to create one using a different phone number and credit card, but if that doesn't work, is it okay if I create one using someone else's name?
- I tried using Spark's native metrics to measure time, but the level of detail differs per Lakehouse. What would be a solution for measuring the time it takes to read the metadata files? I could use 
- The implementation of NexMARK runs queries sequentially, so for each query they start a new workload and run the specific query on the data. An alternative would be to run queries in parallel, but then I'd have to instantiate separate nodes that each run a query and consume from the same Kafka topic/source.
- I think it would be easier to generate all data before hand and then stream it into Kafka, so that we keep the ids consistent. Otherwise, we need to make sure that events that reference foreign ids always match.

## Discussion points

- Using something like NexMARK would defeat a bit of the purpose of benchmarking lakehouses, since that benchmarks like these are meant to measure SPE performances. So instead it would make more sense to ingest some "raw" streaming data directly into the lakehouses and measure the performance of those frequent, small updates.