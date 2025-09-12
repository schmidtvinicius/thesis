#benchmarking 

[Link to paper](zotero://select/library/collections/FHD6IXWM/items/7B39LXPC)

## Paper summary
According to the authors of the paper, modern LSTs (Delta Lake, Apache Iceberg, Apache Hudi) have such fundamental differences from traditional storage layer systems, e.g. immutable data files on object stores, that current benchmarks such as TPC-DS, fail to take those aspects into account, often leading to incomplete/misleading results of LST performance. The authors argue further that benchmarking LSTs goes beyond those technologies alone, as engines also play a big role in LST performance due to the different configurations and optimization techniques that they offer. In light of these issues, the authors introduce LST-Bench: an open-source benchmarking framework that extends TPC-DS for evaluating log-structured tables (LSTs).

In order to design such a framework, the authors first identify the three main aspects of LSTs that need to be considered when benchmarking them: (1) The underlying (file) structure used to manage metadata, (2) the algorithms that power crucial aspects of LSTs, such as *concurrency*, *table optimization*, e.g. compacting files for faster reads, and (3) *layout configuration*, e.g. CoW. They then  propose a "stability" metric, which is based on the degradation rate ($S_{DR}$) of other metrics of LSTs over time. The lower $S_{DR}$ is, the more stable an LST is considered to be.

$$
S_{DR}=\frac{1}{n} \sum_{i=1}^{n}\frac{M_{i}-M_{i-1}}{M_{i-1}}
$$
This is quite an important metric, as frequent write operations to LSTs tend to have a big impact on their performance, especially if optimization techniques are not applied properly. Finally, they describe four workloads that are typical to the usage of LSTs, which are based on empirical measurements: (1) *longevity*, which is indeed concerned with the degradation of LSTs performance as more data files are added without performing any optimization operations, (2) *resilience*, which is very similar to longevity, but it actually performs optimizations after updates to data files and compares their impact on performance, (3) impact of concurrent reads and writes on LST performance, and (4) *time travel*, which looks at how updates to the data files impacts performance of reading previous versions of the LST tables. These workflows were then added on top of the TPC-DS benchmark, leading to the implementation of LST-Bench. The authors also emphasize that the framework allows other workflows to be added later on for  specific use cases.  

Using the newly implemented framework, the authors proceeded to benchmark three of the most popular LSTs currently: Delta Lake, Apache Iceberg and Apache Hudi. They did this using both the Apache Spark and Trino engines, to ensure a more complete picture of the performance of the LSTs.



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