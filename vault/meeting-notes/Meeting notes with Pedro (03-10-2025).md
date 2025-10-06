## Key points
- What language to use for the implementation? A lot of frameworks are written in Java, as well as many streaming benchmarks use either Java or Scala
	- Just start with Python for now
- How to make it run on the cluster? Does it require installing many things on there? Maybe docker/kubernetes would suffice?
	- We'll figure it out later
- Try to work with all three lakehouses for now (Iceberg, Delta, Ducklake) with Python and DuckDB and then try to make it work with one streaming framework. After that we can expand to other streaming technologies if time permits.
- Try to find a SOTA streaming benchmark that is comparable to the TPC suite. Something like 

1. _What is the problem?_
2. _Why is it interesting and important?_
3. _Why is it hard?_ (E.g., why do naive approaches fail?)
4. _Why hasn't it been solved before?_ (Or, what's wrong with previous proposed solutions? How does mine differ?)
5. _What are the key components of my approach and results?_ Also include any specific limitations.