1. Just before Pedro went on leave, he had mentioned I could use AWS services, and I could later get reimbursed for usage costs. However, since I'm not using Spark anymore, does it still make sense to run stuff in the cloud?  I could still use an S3 bucket and use something like Supabase for metadata storage, but can my code just run locally? I thought I would ask before creating an AWS account, just in case. What about Polaris server, does it have to run in the cloud too?
 I would have to either run everything in the cloud or nothing. Having only storage running in the cloud (e.g. S3) would not bring any contributions to the project, as we're only adding extra http calls when performing the writes, instead of having them locally on disk. I _could_ have everything setup in the cloud, but even then there would still have extra latency due to network calls and all that.
   
3. Is it okay to produce all the data beforehand into the kafka topic and just consume from there?
	1. Speaking of data,  I'm currently using the NYC Taxi Dataset found [here](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"), as it could be a good representation of "real-time" data. 
	2. Additionally, I thought I could use DuckDB's tpch extension to generate some data (or even use the pre-generated datasets for that matter). I wouldn't use any of the analytical queries, just the data to stream it into Kafka, but it would still be a good way of having a more well-defined option of running experiments at specific scale factors of data. The problem with this is that TPC-H has multiple tables, so we would either have to create separate topics for each table or we pre-generate most of the tables and only create new events for the `lineitem` table. In any case, I think this could be included in future work for now.
Keep NYC Taxi as the dataset for now, as it is a single table and contains timestamps to help simulate streaming data.

4. In terms of research questions, are my questions relevant and specific enough? 
	1. What would be an example of a good question? 
	2. Is it okay to come up with questions after the fact?
Research questions are good for now. It is important to state that what I'm trying to do is something that has never been done before, which can help reduce the complexity requirement of my experiments. It also important to mention that we're looking at the open table formats as variables in our experiments, and not the query engines.

5. Regarding metrics, I was thinking of looking at different batch sizes and intervals at which the optimization operations should be done. Would that be a good idea?

6. Now that Hannes is no longer professor at Radboud, how do we proceed? I've been told another professor will take the roll of first supervisor, do you want to schedule a meeting with him to discuss the project? 