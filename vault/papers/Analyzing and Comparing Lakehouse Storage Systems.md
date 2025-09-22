#benchmarking #lakehouse 

[Link to paper](zotero://select/library/collections/S6HVLU6N/items/2I86NXPD)
[Source code](https://github.com/lhbench/lhbench)

## Paper summary
This paper presents a comparison between three prominent lakehouse technologies, namely Apache Iceberg, Delta Lake and Apache Hudi. They do this by adapting the TPC-DS benchmark and a few other microbenchmarks to create LHBench. Using this benchmark, they evaluated three characteristics of each lakehouse system: (1) performance on loading and querying data, (2) different update strategies, e.g. CoW and MoR, and (3) distributed metadata processing.

The paper's findings suggest that performance of Hudi on query and load tasks is highly impacted by the fact that it stores data in smaller sized files, leading to more writes when loading the data and more reads when querying it. However, Hudi has an advantage when it comes to consecutive runs of the same query, since it caches the query plan. In terms of update strategies, Delta CoW and Hudi CoW presented very similar read latency, whereas Iceberg CoW had considerably slower reads. Interestingly, Delta CoW had faster merge times than both Hudi MoR and Iceberg MoR, which are supposed to reduce write latency. According to the authors, this difference is due to Delta creating fewer files during writes and having faster scans. Finally, when looking at distributed metadata processing, the authors found that Delta has a lower startup and execution time than Iceberg at larger scales, due to the distribution of query planning across multiple Spark nodes, whereas Iceberg does query planning on a single node.

The authors conclude the paper by raising some points for future development of lakehouse technologies. In summary, they talk about efficiently choosing between single-node and distributed query planning, depending on the size of the query. In addition, they raise concerns related to read/write latency on current lakehouse systems and suggest that future research could look at strategies to optimize these operations. Coincidentally, the latter point is something that [Ducklake](zotero://select/library/collections/MNIE5A7G/items/JIW5G2YC) addresses in an innovative way.

## Remarks

## Related sources to look into
### Papers
- 
### Blogs
- 
### Miscellaneous
- 