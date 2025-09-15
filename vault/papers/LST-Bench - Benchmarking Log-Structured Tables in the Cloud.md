#benchmarking 

[Link to paper](zotero://select/library/collections/FHD6IXWM/items/7B39LXPC)

## Paper summary
According to the authors of the paper, modern LSTs (Delta Lake, Apache Iceberg, Apache Hudi) have such fundamental differences from traditional storage layer systems, e.g. immutable data files on object stores, that current benchmarks such as TPC-DS, are not sufficient to measure their performance accurately, often leading to incomplete/misleading results of LST performance. The authors argue further that benchmarking LSTs goes beyond those technologies alone, as engines also play a big role in LST performance due to the different configurations and optimization techniques that they offer. In light of these issues, the authors introduce LST-Bench: an open-source benchmarking framework that extends TPC-DS for evaluating log-structured tables (LSTs).

In order to design such a framework, the authors first identify the three main aspects of LSTs that need to be considered when benchmarking them: (1) The underlying (file) structure used to manage metadata, (2) the algorithms that power crucial aspects of LSTs, such as *concurrency*, *table optimization strategies*, and *data layout configuration*, e.g. CoW, and (3) the engines which are used to interact with the LSTs, e.g. Spark or Trino. They then  propose a "stability" metric, which is based on the degradation rate ($S_{DR}$) of other metrics of LSTs over time. The lower $S_{DR}$ is, the more stable an LST is considered to be:

$$
S_{DR}=\frac{1}{n} \sum_{i=1}^{n}\frac{M_{i}-M_{i-1}}{M_{i-1}}
$$
This is quite an important metric, as frequent write operations to LSTs tend to have a big impact on their performance, especially if optimization techniques are not applied properly. 

Furthermore, the authors describe four workloads that are typical to the usage of LSTs, which are based on empirical observations: (1) *longevity*, which is concerned with the degradation of LSTs performance as more data files are added without performing any optimization operations, (2) *resilience*, which is very similar to longevity, but it actually performs optimizations after updates to data files and compares their impact on performance, (3) impact of concurrent reads and (re-)writes on LST performance, and (4) *time travel*, which looks at how updates to the data files impacts performance of reading previous versions of the LST tables. These workflows were then added on top of the TPC-DS benchmark, leading to the implementation of LST-Bench. The authors also emphasize that the framework allows other workflows to be added later on for  specific use cases.  

To demonstrate the capabilities of the proposed framework, the authors used it to benchmark three of the most popular LSTs: Delta Lake, Apache Iceberg and Apache Hudi. As mentioned before, it was important to measure the performance of these technologies in combination with different engines, so they did benchmarks using both Apache Spark and Trino. Their results showed that Hudi was the most stable ($S_{DR}$) of all three LSTs, due to it performing more optimizations upfront. This stability, however, comes at a cost of Hudi having a lower base performance than Iceberg and Delta. Further, the experiments showed (unsurprisingly) that an increase in data files can lead to up 6.8 times lower performance of the LSTs when no optimizations are performed. Performing those optimizations can lead to different results depending on the engine being used, as Spark creates many more data files than Trino by default. However, the authors conclude their analysis by emphasizing that results may vary on how both the LST and engine are configured and that choosing the right settings is very use-case-dependent.

The main takeaway of this paper is that LSTs are quite different from traditional data warehouses and, as such, they require a different set of benchmarks to be properly evaluated. The authors  demonstrate this by proposing LST-Bench: a framework that builds on the well-established TPC-DS benchmark, but it includes workflows specific for LST use-cases. This framework also allows for extensibility of workflows, which can prove useful when testing more specific scenarios, such as streaming.


## Remarks
* I'll probably need to run experiments in some sort of cluster or remote server, given that many benchmarks use large amounts of data. E.g. TPC-DS can go up to 100TB of data.
* Can I reuse the proposed package and benchmark and extend it with streaming patterns, or do I have to create something entirely from scratch?
* The authors mention in Section 3.1.2 that they created their workloads using parameter values obtained empirically from customer workloads. Can I take those parameters as given, since I cannot empirically measure them?
* Benchmark results will be useful for when I have my own benchmark, so that I can see if the results are comparable in terms of e.g. performance degradation.

## Related sources to look into
### Papers
* [Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics](zotero://select/library/collections/VK5JU2ZD/items/FEU5PY4T)
* [Analysis of Big Data Storage Tools for Data Lakes based on Apache Hadoop Platform](zotero://select/library/collections/QII2M3K7/items/8QHP8W2Q)
* [Analyzing and Comparing Lakehouse Storage Systems](zotero://select/library/collections/EEX7TH88/items/2I86NXPD)
* [DIAMETRICS: benchmarking query engines at scale](zotero://select/library/collections/FHD6IXWM/items/IQ5PCJFK)
* [PEEL: A Framework for Benchmarking Distributed Systems and Algorithms](zotero://select/library/collections/FHD6IXWM/items/K5TSPTT2)

### Blogs
* https://databeans-blogs.medium.com/delta-vs-iceberg-vs-hudi-reassessing-performance-cb8157005eb0
* https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-transparent-tpc-ds-lakehouse-performance-benchmarks
* https://www.brooklyndata.co/ideas/2022/11/28/benchmarking-open-table-formats

### Miscellaneous
* https://github.com/delta-io/delta/tree/master/benchmarks