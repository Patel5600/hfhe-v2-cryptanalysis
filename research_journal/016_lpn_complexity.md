# Entry 016 \u2014 LPN Complexity Assessment

**Date:** Phase 7
**Status:** ASSESSED

## What was assessed

The work factor for generic LPN attacks on (n=4096, m=16384, tau=1/8).

## ISD / BJMM

Information Set Decoding (specifically BJMM variant):
  Estimated work: >> 2^100, likely 2^200+ range
  Practical: No

This is a LOWER BOUND on the best ISD; the actual security may be higher.

## BKW (Blum-Kalai-Wasserman)

Required samples: ~2^341
Available samples: 720,896 ~ 2^20
Deficit: 321 bits worth of samples
Practical: No

## What is NOT established

- A formal concrete security level
- A lower bound on the best possible algorithm
- Security against quantum algorithms

## Correct statement

"Our tested generic attack families do not give a practical attack at
the available resources. A formal concrete security level has not been
established by this investigation."

This is the language used throughout the repository.
