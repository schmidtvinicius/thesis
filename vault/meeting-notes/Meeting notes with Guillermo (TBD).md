1. Just before Pedro went on leave, he had mentioned I could use AWS services, and I could later get reimbursed for usage costs. However, since I'm not using Spark anymore, does it still make sense to run stuff in the cloud?  I could still use an S3 bucket and use something like Supabase for metadata storage, but can my code just run locally? I thought I would ask before creating an AWS account, just in case.  
   
2. Is it okay to produce all the data beforehand into the kafka topic and just consume from there?
	1. Speaking of data,  I'm currently using the NYC Taxi Dataset found [here](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"), as it could be a good representation of "real-time" data. Additionally, I thought I could use DuckDB's tpch extension to generate some data (or even use the pre-generated datasets for that matter). I wouldn't use any of the analytical queries, just the data to stream it into Kafka, but it would still be a good way of having a more well-defined option of running experiments at specific scale factors of data.

3. In terms of research questions, are my questions relevant and specific enough? 
	1. What would be an example of a good question? 
	2. Is it okay to come up with questions after the fact?

4. Regarding metrics, I was thinking of looking at different batch sizes and intervals at which the optimization operations should be done. Would that be a good idea?