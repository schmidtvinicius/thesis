[Datastream overview](https://nightlies.apache.org/flink/flink-docs-release-2.1/docs/dev/datastream/overview/)
[Config](https://nightlies.apache.org/flink/flink-docs-release-2.1/docs/deployment/config/)

- Flink streams are immutable and can only be transformed into other streams
- There's always a source and sink, which could be files, databases, message brokers, etc.
- Execution always happens in a **Flink Environment**
	- Usually, you can use `getExecutionEnvironment()`, which will resolve to the appropriate environment depending on where your program is running. If it runs locally, it will be given an environment in your local JVM. When running on a cluster as a JAR, it will be given the proper environment on the cluster to carry out execution

