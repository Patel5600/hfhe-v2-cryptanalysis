# Phase 3 — Joint Key / Public_T Correlation

## Hypothesis

If prf_k leaks into public edge metadata (nonce, idx) through the
key-derivation structure, there should be measurable correlation between
nonce values and the prf_k-derived weights w.

## Observable

- Pearson(nonce, w_low32)
- Pearson(nonce, idx)

## Null model

Permuted (nonce, w) pairs across edges.

## Decision rule

Bonferroni-corrected alpha = 0.05/3 = 0.017.
|r| > 0.05 AND p < 0.017 required for SIGNAL.

## Scripts

- `public_T_distinguisher.py` — Main Phase 3 experiment

## Result

Pearson(nonce, w_low32): r=-0.0218, p=0.2317
Pearson(nonce, idx):     r=+0.0031, p=0.8911

No correlations exceed the decision threshold.

## Status: CLOSED
