#benchmarking #streaming 

[Link to paper](zotero://select/library/collections/NNCK7D2G/items/2RK9EPAI)
[Source code](https://github.com/jawadtahir/DSPF-BM)

## Paper summary
This papers presents PGVal: A benchmarking system for evaluating processing guarantees of stream processing systems (SPSs). This benchmark looks at aspects such as latency, reliability, correctness, reliable throughput and failure cost. In addition, the authors expand on failure models to include network failures, instead of only process failures.  The paper also provides an evaluation of three SPSs using PGVal, namely Apache Storm, Apache Flink and Kafka Streams. These systems are evaluated with both single-stream and multi-stream topologies, as well as different levels of parallelism.

An important distinction introduced by the authors is that between *correctness* and *reliability*. They define the former as the ability of a SPS to produce correct results, e.g. an aggregation operation should yield a value of $X$ for a given input. In contrast, *reliability* refers to a SPS's ability to correctly process its input. This takes into account situations in which processing the same input twice while ignoring a second input yields the same result as processing both inputs once. By verifying the list of inputs that produced a given output, we can tell how reliable a system is. 

In addition, the authors define *reliable throughput* as the number of unique event ids that make all outputs in a given unit of time. Further, they adapt the concept of latency introduced by [[Benchmarking Distributed Stream Data Processing Systems|(Karimov et al., 2018)]], which defined latency as the time span between the moment a windowed output is produced and the event time of the last event that was included in that window. The authors of this paper, however, argue that a given window is only processed when the first event of the next window arrives, so their definition of latency is slightly changed to be between the time of output and the event time of the first item in the next window. Finally, the authors propose a *failure cost* metric, which measures the maximum amount of latency a system presents during a failure.

In terms of infrastructure, the authors kept the SPS and data sources separated from their benchmark, in order to avoid impact on SPS performance. Additionally, the authors developed an "oracle" as one of the components of PGVal. This component is responsible for measuring the *reliability* of the SPS. It does so by executing the same processing steps on the SPS input, but it uses fixed-time windows and is single-threaded, which help avoid synchronization errors. However, the authors stress the importance of making sure the "oracle" works correctly through test cases.

## Remarks

## Related sources to look into
### Papers
- [Evaluation of Stream Processing Frameworks](zotero://select/library/collections/NNCK7D2G/items/JPC2ZTER)
