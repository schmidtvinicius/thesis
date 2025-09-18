#benchmarking #streaming 

[Link to paper](zotero://select/library/collections/NNCK7D2G/items/CCEYL3D4)

## Paper summary
The paper introduces a framework for benchmarking streaming data processing systems (SDPSs). The authors claim that current (in 2018) benchmarks fail to accurately measure the most prominent aspects of SDPSs, such as latency and throughput. The reason for this is that benchmarks usually measure metrics within the system under test, which would lead to different latency and throughput results, since each system might define those metrics in different ways. In addition, the authors suggest that many benchmarks do not properly measure the latency of stateful operations, such as windowed aggregations, as these benchmarks only take processing time into account, without considering the time it takes to "fill up" a window.

Given these shortcomings of benchmarking systems at the time, the authors introduce a few concepts that form the foundations of their framework: Firstly, the authors define a so-called *sustainable throughput*, which refers to maximum throughput of a SDPS without a continuously increasing latency. This helps minimize system throttling, which should lead to more accurate measurements of latency. 

Secondly, they make a distinction between *event-time latency* and *processing-time latency*. The former refers to the time span between the creation of an event, e.g. a measurement is emitted from an IoT sensor, and the moment that event has been processed and output by the SUT. *Processing-time latency*, on the other hand, refers to the interval between the ingestion of an event by the SUT and the moment it gets output by the system. In both cases, windowing is taken into account by taking the latency of the latest entry in the window, since other entries were just waiting to be processed.

Additionally, the authors defined their own data generators for data ingestion. They argue that using systems like Kafka and Redis can introduce bottlenecks in the benchmarking process.

## Remarks
* The paper does not provide any source code or VM snapshots, which highly reduces reproducibility of the results. This is also one of the pitfalls mentioned in [[Fair Benchmarking Considered Difficult - Common Pitfalls In Database Performance Testing#Paper summary|the fair benchmarking paper]].
* The paper does not include all results (not even in the appendix), due to limited space. They claim that if systems yielded similar results across different configurations, only the most "interesting" results were provided. This also hampers the verification of their results, since some claims are not backed by any graphs or tables.
* The main contribution of this paper would be the concepts that the authors introduced such as *sustainable throughput*, *event-time latency* and *processing-time latency*, which we could use in our experiments as well. Meanwhile, the results are a bit harder to verify and thus they are harder to trust.