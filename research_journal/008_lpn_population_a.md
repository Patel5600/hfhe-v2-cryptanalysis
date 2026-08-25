# Entry 008 \u2014 LPN Population A

**Date:** Phase 2
**Status:** Foundation for population distinguisher

## What Population A is

Population A consists of edge weight pairs (w_0, w_1) drawn from the
SAME ciphertext object. Both w_0 and w_1 are prf_k-derived from the
same master key, but from different (layer, idx, domain) combinations.

## The hypothesis

If prf_k introduces cross-layer correlation, then the joint distribution
of (w_0, w_1) in Population A should differ from the joint distribution
in Population B (cross-ciphertext pairs, independent prf_k).

## Result

KS(REAL, NULL_B) = 0.0263, p=0.523.
The two populations are statistically identical.

## Consequence

This closes the joint prf_k distinguisher branch. The PRF is working
as a pseudorandom function: outputs from different domain invocations
are statistically independent.
