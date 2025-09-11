## DeWitt clause
Named after David DeWitt, this is a clause included in many end-user license agreements, which strictly forbids users of publishing benchmark results of that given software product without first obtaining (written) authorization from the authors/owners. 

Some companies also enforce a "DeWitt Embrace clause", which allows publishing of benchmark results, but it requires reciprocity from the company whose software is being benchmarked.

## OLTP
Stands for On-line Transaction Processing. It consists of rapid processing of large amounts of small data.

## Copy-on-Write (CoW)
Strategy used by certain LSTs to handle updates of data files. In this case, new copies of the data files reflecting the changes are made as soon as an update comes in. This strategy is mostly recommended when tables have infrequent updates, but are read frequently.

## Merge-on-Read (MoR)
In contrast to [[#Copy-on-Write (CoW)|CoW]], MoR defers updates to data files for when the data is being read. There are different strategies to implement this, e.g. [Delta's deletion vectors](https://delta.io/blog/2023-07-05-deletion-vectors/). This is strategy is mostly recommended for when updates are very frequent.