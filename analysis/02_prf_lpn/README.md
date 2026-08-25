# Phase 2 — PRF/LPN Generation

This phase separates pure PRF/AES-stream observables from statistics that also depend on the hidden LPN secret.

## Exact construction model

For a domain `D`, the implementation derives an AES key from:

`prf_k || canon_tag || H_digest || ztag || nonce.lo || nonce.hi || FNV1a(D)`

then generates the LPN rows and labels:

`y_i = <A_i,S> XOR e_i`.

The PRF core subsequently feeds the LPN output into its Toeplitz path.

## Population A

44 published files × 16,384 rows = 720,896 equations.

Observed statistics:

- mean row weight = 2047.9401
- row-weight SD = 31.9966
- global y=1 rate = 0.4996893
- pairwise A Hamming mean = 2048.00863
- wrapped-pair A Hamming mean = 2048.00016
- pairwise y agreement = 0.5001130
- repeated A rows = 0

## Population B contract

The valid matched null freezes all public metadata and resamples `prf_k`.

The pinned constructor independently generates `S_B`. The experiment must not set `S_B = S_A` because the challenge secret `S_A` is unknown.

## Tests

### A-only

- bit balance
- row/column weights
- cross-file Hamming distance
- repeated rows
- autocorrelation

### y-dependent

- y balance
- A-to-y marginal bias
- y cross-file agreement
- low-weight cross-instance relations

## Verdict

The real sample statistics were ordinary at the tested resolution. The joint public-T matched-null experiment is documented in Phase 3.

**CLOSED** for the tested cheap PRF/LPN statistical attack surface.
