# Entry 017 — Final Status

**Date:** 2026-08-25  
**Status:** Investigation complete

## What was accomplished

26 attack branches independently tested and closed.
All public-artifact attack surfaces exhausted.

## Final scoreboard

| Branch | Method | Status |
|--------|--------|--------|
| R_com oracle | Source read | CLOSED |
| Tuple ordering | Source read + CSPRNG analysis | CLOSED |
| Sigma bitvectors | Source read | CLOSED |
| H rank (GF2) | Computation: 8192/8192 | CLOSED |
| H duplicates | Computation: 0 | CLOSED |
| powg_B DLP | Analysis: B=ord(g)=337 | CLOSED |
| Cyclotomic subgroup | Analysis: prime order | CLOSED |
| Cross-layer prf_k | KS p=0.523, N=5000 | CLOSED |
| PC distribution | KS p=0.196, N=44 | CLOSED |
| Cross-field Fp/Zell | 0/100,000 cancellations | CLOSED |
| Legendre(-T0*T1) | Chi2=1.34, p=0.246, N=20000 | CLOSED |
| Sign agreement | Rate=0.500, p=0.756, N=20000 | CLOSED |
| Ratio estimator | Hamming=0.500, toy-world | CLOSED |

## Surviving surface

    LPN(n=4096, m=16384, tau=1/8)

No sub-exponential practical attack known. No formal security proof established.

## The honest final answer

> No practical exploit was found. The investigation was exhaustive across the
> tested attack surface. The construction's security now rests on LPN hardness,
> for which we found no shortcut.
>
> This is a negative cryptanalytic result, not a proof of security.
