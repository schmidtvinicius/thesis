---
annotation-target: paper.pdf
---


>%%
>```annotation-json
>{"created":"2025-06-20T14:51:00.045Z","updated":"2025-06-20T14:51:00.045Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":16113,"end":16746},{"type":"TextQuoteSelector","exact":"In this section, we sketch one possible design for Lakehousesystems, based on three recent technical ideas that have appearedin various forms throughout the industry. We have been buildingtowards a Lakehouse platform based on this design at Databricksthrough the Delta Lake, Delta Engine and Databricks ML Runtimeprojects [10, 19, 38]. Other designs may also be viable, however, asare other concrete technical choices in our high-level design (e.g.,our stack at Databricks currently builds on the Parquet storageformat, but it is possible to design a better format). We discussseveral alternatives and future directions for research.","prefix":"ise storage system such as HDFS.","suffix":"3.1 Implementing a Lakehouse Sys"}]}]}
>```
>%%
>*%%PREFIX%%ise storage system such as HDFS.%%HIGHLIGHT%% ==In this section, we sketch one possible design for Lakehousesystems, based on three recent technical ideas that have appearedin various forms throughout the industry. We have been buildingtowards a Lakehouse platform based on this design at Databricksthrough the Delta Lake, Delta Engine and Databricks ML Runtimeprojects [10, 19, 38]. Other designs may also be viable, however, asare other concrete technical choices in our high-level design (e.g.,our stack at Databricks currently builds on the Parquet storageformat, but it is possible to design a better format). We discussseveral alternatives and future directions for research.== %%POSTFIX%%3.1 Implementing a Lakehouse Sys*
>%%LINK%%[[#^bzi0g8fl5g|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^bzi0g8fl5g


>%%
>```annotation-json
>{"created":"2025-06-20T14:51:39.053Z","updated":"2025-06-20T14:51:39.053Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":23198,"end":24109},{"type":"TextQuoteSelector","exact":"Future Directions and Alternative Designs. Because metadatalayers for data lakes are a fairly new development, there are manyopen questions and alternative designs. For example, we designedDelta Lake to store its transaction log in the same object store that itruns over (e.g., S3) in order to simplify management (removing theneed to run a separate storage system) and offer high availabilityand high read bandwidth to the log (the same as the object store).However, this limits the rate of transactions/second it can supportdue to object stores’ high latency. A design using a faster storagesystem for the metadata may be preferable in some cases. Likewise,Delta Lake, Iceberg and Hudi only support transactions on onetable at a time, but it should be possible to extend them to supportcross-table transactions. Optimizing the format of transaction logsand the size of objects managed are also open questions.","prefix":"d can reliably log all accesses.","suffix":"3.3 SQL Performance in a Lakehou"}]}]}
>```
>%%
>*%%PREFIX%%d can reliably log all accesses.%%HIGHLIGHT%% ==Future Directions and Alternative Designs. Because metadatalayers for data lakes are a fairly new development, there are manyopen questions and alternative designs. For example, we designedDelta Lake to store its transaction log in the same object store that itruns over (e.g., S3) in order to simplify management (removing theneed to run a separate storage system) and offer high availabilityand high read bandwidth to the log (the same as the object store).However, this limits the rate of transactions/second it can supportdue to object stores’ high latency. A design using a faster storagesystem for the metadata may be preferable in some cases. Likewise,Delta Lake, Iceberg and Hudi only support transactions on onetable at a time, but it should be possible to extend them to supportcross-table transactions. Optimizing the format of transaction logsand the size of objects managed are also open questions.== %%POSTFIX%%3.3 SQL Performance in a Lakehou*
>%%LINK%%[[#^w94xp8jhzsb|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^w94xp8jhzsb


>%%
>```annotation-json
>{"created":"2025-06-20T14:52:00.588Z","updated":"2025-06-20T14:52:00.588Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":29195,"end":29479},{"type":"TextQuoteSelector","exact":"We report the time to run all 99 queries as well as thetotal cost for customers in each service’s pricing model (Databrickslets users choose spot and on-demand instances, so we show both).Delta Engine provides comparable or better performance than thesesystems at a lower price point.","prefix":"PUs each and local SSDstorage.1 ","suffix":"Future Directions and Alternativ"}]}]}
>```
>%%
>*%%PREFIX%%PUs each and local SSDstorage.1%%HIGHLIGHT%% ==We report the time to run all 99 queries as well as thetotal cost for customers in each service’s pricing model (Databrickslets users choose spot and on-demand instances, so we show both).Delta Engine provides comparable or better performance than thesesystems at a lower price point.== %%POSTFIX%%Future Directions and Alternativ*
>%%LINK%%[[#^22up5voxp0v|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^22up5voxp0v


>%%
>```annotation-json
>{"created":"2025-06-20T14:52:50.001Z","updated":"2025-06-20T14:52:50.001Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":29479,"end":30697},{"type":"TextQuoteSelector","exact":"Future Directions and Alternative Designs. Designing perfor-mant yet directly-accessible Lakehouse systems is a rich area forfuture work. One clear direction that we have not explored yetis designing new data lake storage formats that will work betterin this use case, e.g., formats that provide more flexibility for theLakehouse system to implement data layout optimizations or in-dexes over or are simply better suited to modern hardware. Ofcourse, such new formats may take a while for processing enginesto adopt, limiting the number of clients that can read from them,but designing a high quality directly-accessible open format fornext generation workloads is an important research problem.Even without changing the data format, there are many typesof caching strategies, auxiliary data structures and data layoutstrategies to explore for Lakehouses [4, 49, 53]. Determining whichones are likely to be most effective for massive datasets in cloudobject stores is an open question.Finally, another exciting research direction is determining whenand how to use serverless computing systems to answer queries [41]and optimizing the storage, metadata layer, and query engine de-signs to minimize latency in this case.","prefix":"esystems at a lower price point.","suffix":"1 We started all systems with da"}]}]}
>```
>%%
>*%%PREFIX%%esystems at a lower price point.%%HIGHLIGHT%% ==Future Directions and Alternative Designs. Designing perfor-mant yet directly-accessible Lakehouse systems is a rich area forfuture work. One clear direction that we have not explored yetis designing new data lake storage formats that will work betterin this use case, e.g., formats that provide more flexibility for theLakehouse system to implement data layout optimizations or in-dexes over or are simply better suited to modern hardware. Ofcourse, such new formats may take a while for processing enginesto adopt, limiting the number of clients that can read from them,but designing a high quality directly-accessible open format fornext generation workloads is an important research problem.Even without changing the data format, there are many typesof caching strategies, auxiliary data structures and data layoutstrategies to explore for Lakehouses [4, 49, 53]. Determining whichones are likely to be most effective for massive datasets in cloudobject stores is an open question.Finally, another exciting research direction is determining whenand how to use serverless computing systems to answer queries [41]and optimizing the storage, metadata layer, and query engine de-signs to minimize latency in this case.== %%POSTFIX%%1 We started all systems with da*
>%%LINK%%[[#^vfbdx2dmb9|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^vfbdx2dmb9


>%%
>```annotation-json
>{"created":"2025-06-20T15:03:29.202Z","updated":"2025-06-20T15:03:29.202Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":33827,"end":34924},{"type":"TextQuoteSelector","exact":"Future Directions and Alternative Designs. Apart from thequestions about existing APIs and efficiency that we have just dis-cussed, we can explore radically different designs for data accessinterfaces from ML. For example, recent work has proposed “fac-torized ML” frameworks that push ML logic into SQL joins, andother query optimizations that can be applied for ML algorithmsimplemented in SQL [36]. Finally, we still need standard interfacesto let data scientists take full advantage of the powerful data man-agement capabilities in Lakehouses (or even data warehouses). Forexample, at Databricks, we have integrated Delta Lake with the MLexperiment tracking service in MLflow [52] to let data scientistseasily track the table versions used in an experiment and reproducethat version of the data later. There is also an emerging abstractionof feature stores in the industry as a data management layer tostore and update the features used in an ML application [26, 27, 31],which would benefit from using the standard DBMS functions in aLakehouse design, such as transactions and data versioning.","prefix":"l need to tackle this challenge.","suffix":"4 Research Questions and Implica"}]}]}
>```
>%%
>*%%PREFIX%%l need to tackle this challenge.%%HIGHLIGHT%% ==Future Directions and Alternative Designs. Apart from thequestions about existing APIs and efficiency that we have just dis-cussed, we can explore radically different designs for data accessinterfaces from ML. For example, recent work has proposed “fac-torized ML” frameworks that push ML logic into SQL joins, andother query optimizations that can be applied for ML algorithmsimplemented in SQL [36]. Finally, we still need standard interfacesto let data scientists take full advantage of the powerful data man-agement capabilities in Lakehouses (or even data warehouses). Forexample, at Databricks, we have integrated Delta Lake with the MLexperiment tracking service in MLflow [52] to let data scientistseasily track the table versions used in an experiment and reproducethat version of the data later. There is also an emerging abstractionof feature stores in the industry as a data management layer tostore and update the features used in an ML application [26, 27, 31],which would benefit from using the standard DBMS functions in aLakehouse design, such as transactions and data versioning.== %%POSTFIX%%4 Research Questions and Implica*
>%%LINK%%[[#^plfar590dji|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^plfar590dji


>%%
>```annotation-json
>{"created":"2025-06-20T15:07:17.121Z","updated":"2025-06-20T15:07:17.121Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":37581,"end":37654},{"type":"TextQuoteSelector","exact":"How does the Lakehouse affect other data management re-search and trends?","prefix":"tics CIDR ’21, Jan. 2021, Online","suffix":" The prevalence of data lakes an"}]}]}
>```
>%%
>*%%PREFIX%%tics CIDR ’21, Jan. 2021, Online%%HIGHLIGHT%% ==How does the Lakehouse affect other data management re-search and trends?== %%POSTFIX%%The prevalence of data lakes an*
>%%LINK%%[[#^1c305rblp6k|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^1c305rblp6k


>%%
>```annotation-json
>{"created":"2025-06-20T15:07:24.507Z","updated":"2025-06-20T15:07:24.507Z","document":{"title":"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics","link":[{"href":"urn:x-pdf:49080b33814d046ad318137f9aa72075"},{"href":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf"}],"documentFingerprint":"49080b33814d046ad318137f9aa72075"},"uri":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","target":[{"source":"vault:/Lakehouse - A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics/paper.pdf","selector":[{"type":"TextPositionSelector","start":35231,"end":35283},{"type":"TextQuoteSelector","exact":"Are there other ways to achieve the Lakehouse goals?","prefix":" areas of data systems research.","suffix":" Onecan imagine other means to a"}]}]}
>```
>%%
>*%%PREFIX%%areas of data systems research.%%HIGHLIGHT%% ==Are there other ways to achieve the Lakehouse goals?== %%POSTFIX%%Onecan imagine other means to a*
>%%LINK%%[[#^cbx59ucrbpt|show annotation]]
>%%COMMENT%%
>
>%%TAGS%%
>
^cbx59ucrbpt
