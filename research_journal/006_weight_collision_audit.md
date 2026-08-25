# Entry 006 — Weight Collision Audit

**Date:** Phase 1
**Status:** CLOSED

## Audit
Analyzed whether scalar weights $w \in \mathbb{F}_p$ exhibit duplicate values across edges or across ciphertexts.

## Result
Total edge weights: 40,238.
Distinct weights: 40,238 (0 collisions).
Field size $p = 2^{127}-1$.
Expected collisions in $40,238$ uniform samples: $\approx 4.7 \times 10^{-30}$.
Zero collisions confirmed. Distribution is uniformly distributed across the 127-bit range.\n