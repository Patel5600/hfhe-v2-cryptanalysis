# Phase 1 — Ciphertext Structure

Analyse the serialized ciphertext before assuming any cryptographic weakness.

## Public observables

Each serialized edge exposes:

- `layer_id`
- `idx`
- `sign`
- field weight vector `w`
- `sigma` bit-vector

Each BASE layer exposes:

- `ztag`
- `nonce.lo`
- `nonce.hi`
- serialized PC point(s)

## Experiment 1A — Weight reuse

Corpus: 1,829 field weights.

Result:

- unique weights = 1,829
- duplicate weights = 0
- zero weights = 0
- cross-object collisions = 0

Interpretation: no direct masked-coefficient reuse was available.

## Experiment 1B — Cross-layer intersections

For each of the 22 wrapped ciphertexts, compute the exact set intersection between the two layers' serialized field weights.

Result: all 22 intersections empty.

## Experiment 1C — Sign/index relations

Search repeated `(idx, sign)` structures and small public linear combinations.

Result: no relation repeatedly linking the two masks or producing a public constant.

## Experiment 1D — Group reconstruction

For each BASE layer:

`G = Σ sign(e) * w_e * powg_B[idx_e]`

Result:

- 44/44 nonzero
- 44/44 distinct
- no same-object `G0 + G1 = 0`
- no same-object `G0 - G1 = 0`

## Experiment 1E — Tuple-order hypothesis

The source merges edges by `(layer, idx, sign)` and then applies a CSPRNG Fisher-Yates permutation. The resulting serialized order therefore does not preserve hidden tuple grouping.

## Verdict

**CLOSED.** No direct ciphertext serialization or graph-structure exploit was identified.
