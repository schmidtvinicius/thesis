## What should we actually be measuring?

The benchmark is focused on testing how lakehouses perform when acting as sinks for streaming engines, so maybe we should focus on the impact of lakehouses on streaming metrics such as latency and throughput. For instance, we could combine the idea of longevity and resilience from [LST-Bench](zotero://select/library/collections/S6HVLU6N/items/7B39LXPC) and apply them to the streaming scenario, so: "How does streaming performance evolves over time as we write more and more data to the lakehouse sink?" or "What's the impact of maintenance operations on the processing of the data streams?". This way we have a well-defined set of metrics we can look at and we can choose different workloads to carry out on the streaming engine.

## Infrastructure

Use Kubernetes with Docker containers on the university cluster. Although it limits us in terms of nodes, we could treat each container as a node with a given amount of CPU allocated to it. This way, we can setup thing similar to what [LST-Bench](zotero://select/library/collections/S6HVLU6N/items/7B39LXPC) did. Maybe just use Docker compose?