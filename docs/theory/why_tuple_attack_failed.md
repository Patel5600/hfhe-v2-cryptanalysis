# Why the Tuple-Order Attack Failed

In v2, after generating edge tuples, the reduction pipeline invokes `reduction::permute(edges)`.
This performs an in-memory Fisher-Yates shuffle with fresh CSPRNG randomness before serialization.
The physical serialization order has zero mutual information with the true generation pairs.\n