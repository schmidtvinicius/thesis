#benchmarking #streaming 

[Link to paper](zotero://select/library/collections/NNCK7D2G/items/JZ3TRRFJ)

## Paper summary
This paper compares different stream processing engines (SPEs) with a focus on how efficient they are at harnessing modern hardware. In particular, the authors looked at CPU-, memory- and network utilization by SPEs and they proposed both data-related and processing-related strategies to improve that utilization. In terms of technologies, the authors looked at three state-of-the-art SPEs, namely Apache Flink, Apache Storm and Apache Spark, as well as other more experimental SPEs, such as Saber and Streambox. Additionally, they include self-written C++ and Java implementations in their comparisons.

Regarding data-related aspects that can benefit from hardware optimization, the authors argue that modern networking technologies such as Infiniband and RDMA can really help improve data ingestion of SPEs. However, they observe that Java-based SPEs struggle to take full advantage of network bandwidth due to limitations of the JVM. Furthermore, they analyze the message-passing strategy of modern SPEs, which relies on the use of queues. Their findings suggest that queues can create a bottleneck in stream processing, preventing SPEs of fully using memory bandwidth. 

To mitigate these issues, the authors suggest a few processing-related optimizations, namely: (1) operator fusion through compilation-based query execution, instead of interpretation-based query execution, (2) using late local/global merge instead of upfront partitioning when partitioning and parallelizing data processing, and (3) using lock-free algorithms and data structures when performing windowed operations.

## Remarks
- Mentions the concept of lock-free algorithms. These are concurrent algorithms in which it is guaranteed that at least one thread is making progress on their task at any given time. This is achieved by using the so-called "compare-and-swap" (CAS) mechanism on atomic variables. When a thread wants to change the value of a variable, it first reads its current value to a temporary variable, it then compares the value it read with the current value of the atomic variable and, if that value hasn't changed in the meantime, it then updates the atomic variable. The process of comparing and updating the value of the atomic variable is in essence the CAS-mechanism.
- Although the experiments seem very thorough and insightful, the paper seems to make on the pitfalls mentioned in [[Fair Benchmarking Considered Difficult - Common Pitfalls In Database Performance Testing|(Raasveldt et al., 2018)]]. This is because they include their own algorithms in the experiments, which completely outperform all other SPEs in the paper. I believe this is a case of the "comparing apples and oranges" pitfall, given that their algorithms were likely made solely with these experiments in mind, so they are very limited in terms in functionality, whereas other SPEs included in the study are (mostly) fully mature and extensive frameworks, which have way more constraints than the hand-written algorithms by the authors. It is hard to tell how much the algorithms actually differ from the SPEs, since the authors did not include the source code for those. 

## Related sources to look into
### Papers

### Blogs
- 

### Miscellaneous