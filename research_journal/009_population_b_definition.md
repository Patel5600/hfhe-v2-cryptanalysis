# Entry 009 \u2014 Population B Definition

**Date:** Phase 2
**Status:** Methodology decision

## The null model design problem

How do we create a null model for prf_k-derived weights?

## Solution: Population B

Population B pairs edges from DIFFERENT ciphertext objects.
Since different CT objects are encrypted under different randomness
(different v, different R application), the w values from different
objects should be statistically independent.

If there is a cross-layer prf_k signal, Population A (same CT) should
differ from Population B (different CT).
If there is no signal, A and B should be identical.

## Why this is the right null model

Population B uses real w values from real artifacts.
It does NOT use simulated values.
This means any systematic bias in the w distribution itself
(e.g., from the Fp sampling algorithm) is the same in both populations,
so the KS test isolates the cross-layer correlation specifically.

This is the matched-null design.
