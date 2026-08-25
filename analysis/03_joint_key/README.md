# Phase 3 — Joint `prf_k` / `public_T` Correlation

## Question

Do the 44 public layer aggregates retain detectable joint structure caused by reuse of the same master `prf_k` across layers?

## Public data

For each BASE layer:

- `public_T_hex`
- `ztag`
- `nonce.lo`
- `nonce.hi`
- object index
- layer index

The 44 published LPN sample files are all `pvac.prf.r.1` and provide the metadata mapping.

## Experiment

Three conditions were used:

1. **REAL** — the 44 observed `T` values with their genuine metadata labels.
2. **SHUFFLED** — the same observed values with metadata labels randomly permuted.
3. **NULL_B** — independent null draws under the matched null model.

The primary test statistic was a normalized pairwise feature distribution over the 44 values.

## Reported result

REAL vs NULL_B:

- KS statistic: 0.02626
- p = 0.523

REAL vs SHUFFLED:

- p = 0.405

The SHUFFLED vs NULL_B significance is treated as a distributional artifact because the shuffled sample reuses real `hash_to_fp_nonzero` outputs while the null comparison used ideal field draws.

## Verdict

**CLOSED.** No reproducible joint-key signal was identified in the tested public observables.

CLOSED means the tested hypothesis did not produce an exploitable signal; it is not a proof that all related-key structure is impossible.
