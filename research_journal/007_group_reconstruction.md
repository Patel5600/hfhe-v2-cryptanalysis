# Entry 007 — Group Reconstruction Attack

**Date:** Phase 1
**Status:** CLOSED

## Hypothesis
If edges sharing the same column $idx$ can be grouped across layers, can we isolate the linear subspace of $R_0, R_1$?

## Analysis
Because of the fresh Fisher-Yates shuffle, edges with the same $idx$ across layers do not share a known row correspondence in $R$.
Grouping by $idx$ yields only marginal weight multisets with no algebraic relation.\n