# Entry 000 — Initial Hypothesis

**Date:** Early in investigation  
**Status:** Baseline

## Starting point

The HFHE v2 challenge presents public artifacts (secret.ct, pk.bin, 44 LPN samples)
and asks whether a practical exploit exists.

## Initial attack surface assessment

First pass: read the challenge description and source code.
Identified the following potential attack surfaces:

1. R_com oracle (if present in wire format)
2. Tuple ordering (if edges preserve original pairing)
3. Sigma bitvectors (if prf_k-rooted)
4. H matrix weakness (low rank, duplicates, etc.)
5. Pedersen commitment bias (PC not uniformly distributed)
6. Cross-field arithmetic (Fp vs Z/lZ mismatch)
7. Wrapped-ratio algebra (T0/T1 = -lambda)
8. LPN direct attack

## Approach decision

Follow Wald's lesson: attack the unexplored surface, not the tested surface.
Begin with source read-through before any computation.

## What this entry opened

All 8 attack branches above were subsequently investigated.
See entries 001-017 for the progression.
