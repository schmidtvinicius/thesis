## What should we actually be measuring?

- The benchmark is focused on testing how lakehouses perform when acting as sinks for streaming engines, so maybe we should focus on the impact of lakehouses on streaming metrics such as latency and throughput. For instance, we could combine the idea of longevity and resilience from [LST-Bench](zotero://select/library/collections/S6HVLU6N/items/7B39LXPC) and apply them to the streaming scenario, so: "How does streaming performance evolves over time as we write more and more data to the lakehouse sink?" or "What's the impact of maintenance operations on the processing of the data streams?". This way we have a well-defined set of metrics we can look at and we can choose different workloads to carry out on the streaming engine.
	- We should split the read time into time to read the catalog and time to read files
		- As data grows, file read time will naturally increase, but there's not much we can do about it
		- On the other hand, the catalog read time is interesting to look into, since that each lakehouse manages the catalog differently, so the impact of the table size on catalog read time will be different for each lakehouse
	- Optimization operations

## Infrastructure

- Use Kubernetes with Docker containers on the university cluster. Although it limits us in terms of nodes, we could treat each container as a node with a given amount of CPU allocated to it. This way, we can setup thing similar to what [LST-Bench](zotero://select/library/collections/S6HVLU6N/items/7B39LXPC) did. Maybe just use Docker compose?

- University clusters do not support docker (cannot install it either), how to proceed?

## Workloads
- Nexmark would be a nice benchmark to implement, since it is well-defined and implemented in other systems, such as Arroyo. However, how should we implement the queries? Using SQL would mean we could make things more generic, but not all streaming engines support SQL queries in streaming, as pointed out [here](https://github.com/nexmark/nexmark?tab=readme-ov-file#roadmap).

## Miscellaneous
- How deep should I go into the theory of streaming processing? I feel like the focus is on lakehouses, which are the main novelty, so how much should I explain of how they work?

## Future
- Iceberg+polaris
- Run experiments on cluster
- Contact Guillermo about streaming?