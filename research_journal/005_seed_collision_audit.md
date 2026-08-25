# Entry 005 — Seed Collision Audit

**Date:** Phase 1
**Status:** CLOSED

## Audit
Analyzed whether 64-bit nonces or 256-bit AES seeds collide across the 40,238 edges in `secret.ct` or the 44 LPN sample files.

## Result
Total edges analyzed: 40,238.
Distinct nonces: 40,238 (0 duplicates).
Distinct $(idx, ztag, nonce)$ triples: 40,238.
Probability of 64-bit nonce collision under birthday bound for $N=40,238$:
$$P_{collision} \approx \frac{N^2}{2^{65}} \approx \frac{1.6 \times 10^9}{3.68 \times 10^{19}} \approx 4.3 \times 10^{-11}$$
Zero collisions confirmed.\n