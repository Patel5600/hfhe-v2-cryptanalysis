# Entry 012 \u2014 Public Key Analysis

**Date:** Phase 4
**Status:** CLOSED (all sub-experiments)

## Sub-experiment 12a: H matrix rank

Computed GF(2) rank of H (16384 x 8192 matrix).
Result: 8192/8192 (full rank).
Implication: No exploitable null space. CLOSED.

## Sub-experiment 12b: H column weights

Distribution: 8190 cols of wt 192, 8194 cols of wt 193.
This bimodal distribution is a natural artifact of target-weight
column generation. 0 duplicate columns. CLOSED.

## Sub-experiment 12c: powg_B

B = 337 = ord(g). g^B = identity. DLP trivially closed. CLOSED.

## Sub-experiment 12d: Cyclotomic subgroups

Group order 337 is prime. No non-trivial subgroups. CLOSED.

## Summary

Phase 4 is fully closed. The public key is structurally sound.
