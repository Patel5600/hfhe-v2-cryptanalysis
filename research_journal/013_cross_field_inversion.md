# Entry 013 — Cross-Field Fp/Z-l Inversion

**Date:** Phase 5  
**Status:** CLOSED

## The hypothesis

If sc_from_fp(R^{-1} mod p) served as a Ristretto255 scalar inverse of
sc_from_fp(R), then one could construct:
    sc_from_fp(R^{-1}) * (w*G) = (R^{-1}*w)*G

giving a handle on R*G without knowing R explicitly.

## The mathematics

R * (R^{-1} mod p) = 1 + k*p   as integers.
In Z/lZ: this equals 1 + k*p mod l != 1 (since k != 0 and p != 0 mod l).

## The experiment

100,000 random R in Fp tested.
Cancellations mod l: 0.

This confirmed the mathematical analysis experimentally.

## Why this matters

This branch was one of the more plausible algebraic attacks because:
1. p < l means no reduction needed in sc_from_fp (correct)
2. Scalar arithmetic is in Z/lZ, not Fp
3. The two fields are genuinely different objects

The branch was correctly identified as impossible through careful field arithmetic,
then confirmed experimentally.
