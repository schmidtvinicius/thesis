#benchmarking 

[Link to paper](zotero://select/library/collections/FHD6IXWM/items/UIXRQWU9)

## Paper summary

This paper highlights some of common pitfalls when benchmarking database systems. These pitfalls were obtained from a literature review on best practices and recommendations for both benchmarking in general and benchmarking of DBMSes. The authors then identified eight different pitfalls that can occur during DBMS benchmarking, namely: (i) reporting non-reproducible results; (ii) sub-optimally configuring systems; (iii) benchmarking code that contains bugs; (iv) overly-optimizing a system solely for improving benchmark results; (v) comparing systems that are fundamentally different; (vi) ignoring preprocessing time; (vii) comparing "cold", "warm" and (viii) "hot" runs.

In addition, the authors also suggest practices on how to prevent these pitfalls from happening. In some cases, such as that of non-reproducible experiments, it can be easily avoided by e.g. including a detailed specification of the configuration parameters used, as well as the source code when available. However, other pitfalls are not so trivial  to avoid. That is the case for "cold" vs "hot" runs, where collecting proper "cold" run data might involve restarting entire (cloud) environments to clear out caches from previous runs.

Finally, the authors conclude the paper by acknowledging the challenges of DBMS benchmarking and they provide a checklist covering the identified pitfalls and the main ways to avoid each of them.

## Remarks
* [[Concepts and definitions#DeWitt clause|DeWitt clause]] might be a limiting factor for the project, although I don't think it will be a big issue.
* 

