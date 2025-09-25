#benchmarking #streaming 

[Link to paper](zotero://select/library/collections/NNCK7D2G/items/Y6PAFTK3)
[Source code](https://github.com/pratyushagnihotri/PDSPBench)

## Paper summary
The authors of this paper identify a lack of benchmarking systems that support evaluation of parallel and distributed workloads, as well as support for heterogeneous hardware configurations. They claim these are essential features of stream processing systems running in real-world scenarios at scale. Therefore, this paper introduces PDSP-Bench, which is supposed to be the first benchmarking framework to include the aforementioned aspects as part of SPSs benchmarking.

The paper focuses on three main aspects of benchmarking SPSs: (1) Offering users flexibility to create parallel benchmarking applications with a diversity of data and operators, (2) running benchmarks on heterogeneous hardware, and (3) supporting learned SPS models as components of the benchmark. Out of these three aspects, we believe that (1) is the most relevant for our work, although (2) and (3) could be considered for future expansions of our proposed benchmark. In order to support a diverse range of data/operator combinations, PDSP-Bench provides both real-world and standard (synthetic) stream processing applications. In addition, they provide configurable parameters such as degree of parallelism (DoP), window size/length, window policy, data tuple size, event rate, etc. 

In terms of experiments, the authors only tested Apache Flink, although they claim that it is possible to use other SPSs. For data generation, they used Apache Kafka running on a separate machine, which could be configured with varying data generation rates as mentioned previously. Regarding metrics, they only report end-to-end latency, although they state that other metrics might be used depending on the benchmark.

When executing different workloads with varying levels of parallelism, the authors found that although the DoP can help improve latency, most systems reach a point where the overhead introduced by parallelism leads to a higher latency than at lower levels of parallelism. In addition, they observed that real-world custom applications have less predictable behavior than standard SP applications when increasing the level of parallelism. This is in part due to standard functions being more well-defined and having less complex state management.

## Remarks

## Related sources to look into
### Papers
- [DSPBench: A Suite of Benchmark Applications for Distributed Data Stream Processing Systems](zotero://select/library/collections/NNCK7D2G/items/SGMF5URU)
- [SPBench: a framework for creating benchmarks of stream processing applications](zotero://select/library/collections/NNCK7D2G/items/37LQISS6)
### Blogs
- 
### Miscellaneous
- [TPCx-IoT](https://www.tpc.org/tpcx-iot/)