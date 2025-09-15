[Link to paper](zotero://select/library/collections/NNCK7D2G/items/CPJLKFMJ)

## Paper summary
This paper, although quite long, doesn't go into a lot of detail on any particular subject. Rather, it provides an overview of several papers about benchmarks/benchmarking frameworks and it categorizes them based on a set of characteristics. These characteristics are: (1) the use cases in which the benchmarks are carried out, (2) the number of applications and tasks included in each benchmark, (3) the dataset and how it is ingested into the benchmarks experiments, (4) the systems that are tested under that benchmark, and (5) the metrics that are measured by the benchmark, e.g. throughput, latency, disk I/O, etc. In total, 27 papers were analyzed using the aforementioned categories.

In terms of datasets, it seems that there is a balance between the use of both synthetic and real datasets. In our work we want to be possible to use both types of datasets, so that we can support as many benchmarks as possible. Further, something that stood out was that most (74%) benchmarks reviewed by the authors use Apache Kafka for data ingestion. Alternatives to this include either using local files or using some type of generator for ingesting data. Our implementation will probably use Kafka as well due to its high throughput and widespread usage. When it comes to systems under test (SUT), there are three systems that are frequently included in benchmarking papers, namely Apache Flink, Apache Storm and Spark Streaming. Ideally, our benchmark should be able to work with as many systems as possible, but maybe we could focus on those three first, since they seem to be the most popular ones. Finally, in terms of metrics under analysis, throughput and latency are the most common ones, with CPU-, memory- and network usage as other popular metrics.

## Related source to look into
### Papers
* [DSPBench: A Suite of Benchmark Applications for Distributed Data Stream Processing Systems](zotero://select/library/collections/NNCK7D2G/items/SGMF5URU)
* [A survey on the evolution of stream processing systems](zotero://select/library/collections/EEX7TH88/items/TFT268LL)
* [SPBench: a framework for creating benchmarks of stream processing applications](zotero://select/library/collections/NNCK7D2G/items/37LQISS6)
* [ShuffleBench: A Benchmark for Large-Scale Data Shuffling Operations with Distributed Stream Processing Frameworks](zotero://select/library/collections/NNCK7D2G/items/2DZJBNCA)

### Miscellaneous
* https://github.com/yahoo/streaming-benchmarks