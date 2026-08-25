# Phase 7 — LPN Complexity Assessment

## Core problem

The published equations are modeled as:

`y_i = <A_i,S> XOR e_i`

with:

- n = 4096
- t = 16384 per instance
- 44 instances
- M = 720,896 total equations
- tau = 1/8

## ISD intuition

A fully noise-free information set of n equations has probability:

`(1 - tau)^n = (7/8)^4096 ≈ 2^-789.07`.

This immediately rules out the naive strategy of repeatedly guessing a completely clean information set.

Advanced ISD methods do not have this exact cost; therefore this expression is an intuition and **not a lower bound** on BJMM or every future decoding algorithm.

## BKW

A basic collision/elimination step transforms the effective bit-error probability according to:

`tau' = 2*tau*(1-tau)`.

Starting from tau=1/8, repeated elimination drives the noise rapidly toward 1/2.

The challenge also has a finite sample pool. Aggressive BKW therefore encounters both sample and memory constraints before eliminating all 4096 dimensions.

## Statistical pooling

The 44 files share the hidden LPN secret within the challenge design, but a large number of samples alone does not imply an exploitable BKW attack. The tested simple cross-instance cancellation families produced no actionable relation.

## Dependency gap

The LPN secret `S` is independent key material. The source does not define `S` as a direct reversible encoding of `prf_k`.

Therefore even a hypothetical recovery of `S` would not algebraically invert the SHA-256/AES derivation of `prf_k`.

## Verdict

**ASSESSED, NOT CLOSED AS A SECURITY PROOF.**

No practical generic ISD/BKW attack was identified at the published parameters. No claim of a universal `2^X` security level is made.
