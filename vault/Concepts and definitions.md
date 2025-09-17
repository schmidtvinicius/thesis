## DeWitt clause
Named after David DeWitt, this is a clause included in many end-user license agreements, which strictly forbids users of publishing benchmark results of that given software product without first obtaining (written) authorization from the authors/owners. 

Some companies also enforce a "DeWitt Embrace clause", which allows publishing of benchmark results, but it requires reciprocity from the company whose software is being benchmarked.

## OLTP
Stands for On-line Transaction Processing. It consists of rapid processing of large amounts of small data.

## Copy-on-Write (CoW)
Strategy used by certain LSTs to handle updates of data files. In this case, new copies of the data files reflecting the changes are made as soon as an update comes in. This strategy is mostly recommended when tables have infrequent updates, but are read frequently.

## Merge-on-Read (MoR)
In contrast to [[#Copy-on-Write (CoW)|CoW]], MoR defers updates to data files for when the data is being read. There are different strategies to implement this, e.g. [Delta's deletion vectors](https://delta.io/blog/2023-07-05-deletion-vectors/). This is strategy is mostly recommended for when updates are very frequent.

## Resilient Distributed Dataset (RDD)
This refers to the underlying collection used by Spark to work with datasets in parallel. It works by partitioning the dataset such that partitions are distributed across different Spark workers. RDDs can be created from both existing datasets in your Spark context and external files, e.g. HDFS, S3, etc. When creating an RDD from an external file, Spark will create one partition per block (by default blocks are 128MB in HDFS) of that file, but users can choose a higher number of partitions per block if they want.

## Selectivity in the context of SQL
The selectivity is used to estimate the percentage of a given table that will be *selected* and passed along the query plan to subsequent operators. For instance, if we have a `WHERE` clause in the form `WHERE column = value`, then the selectivity is determined by $\frac{1}{\text{number of unique values in column}}$. Therefore, a lower selectivity is desirable, as it will reduce the number of results in a query, thus leading to faster processing of the results.