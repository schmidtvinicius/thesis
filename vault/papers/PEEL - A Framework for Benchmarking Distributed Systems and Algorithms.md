#benchmarking #distributed-systems

[Link to paper](zotero://select/library/collections/FHD6IXWM/items/K5TSPTT2)
[Source code](https://github.com/peelframework/peel)

## Paper summary
This paper proposes PEEL: a configurable and extensible benchmarking framework for distributed systems. It provides automated configuration and orchestration of experiments through a command-line interface (CLI). In addition, PEEL experiments can be easily shared using so-called "bundles", facilitating reproducibility. Furthermore, the framework is setup in a way that it efficiently re-utilizes common resources, such as datasets and compute clusters. Additionally, PEEL has an extensive log of the underlying systems, as well as the option to save results to a user-defined DBMS, facilitating analysis and debug of benchmarking experiments.

The rationale behind developing PEEL is that modern distributed data processing systems depend on multiple underlying components (systems), which all require their own set-up and configuration steps. This directly impacts how these distributed systems are evaluated, requiring  a different set of tools to benchmark than traditional RDBMS.

The framework is implemented in Scala, but it also leverages Spring's Beans for dependency injection. The main class in the system's domain defines an *Experiment* object, which depends on different *System* objects, e.g. Flink or Spark, and *I/O* objects for managing datasets. There is also an Experiment Suite object, which, as the name suggests, contains a collection of experiments to be run. Each experiment in the suite contains small variations, which refer to the varying parameters being tested by the experiment. All of the aforementioned objects are managed by the framework, such that common resources and configurations are shared among then. For instance, datasets that are used multiple times by different experiments are simply re-used instead of being created each time a new experiment runs.

The framework supports a handful of systems out of the box, but it can easily be extend to other ones according to the authors.


