# Methodology

## Guiding principle: Wald's survivor bias

Following Wald's WWII lesson, we attack the unexplored surface rather than
re-testing already-rejected hypotheses. At each stage we ask:
*"Which branch has never been meaningfully exercised?"*

## Experiment template

Each experiment documents:

| Field | Description |
|-------|-------------|
| Observable | The concrete quantity measured |
| Null model | Distribution under no signal (e.g., uniform, permuted-label) |
| Decision rule | Pre-specified threshold and test |
| Sample size | Fixed before running |
| Seed | Fixed integer for reproducibility |
| Outcome | Statistic, p-value, interpretation |

## Five-condition exploit candidate test

A statistical deviation alone is insufficient. A candidate becomes an
**exploit candidate** only when:

1. The deviation is reproducible (same script, same seed → same result).
2. The deviation survives the matched null (label-permuted or simulated ideal).
3. Multiple-testing effects are controlled (Bonferroni or equivalent).
4. A concrete mechanism explains the deviation.
5. The mechanism permits secret/plaintext recovery.

If any condition fails, the branch is marked CLOSED.

## Null models used

- **Population B (label-permuted):** Pair samples from different ciphertexts.
  Should have identical distribution to Population A if there is no signal.
- **Ideal world:** Generate T0, T1 from independent uniform random Fp values.
  Used for character and parity tests.
- **Toy world (known key):** Run encryption with a known key to verify that
  a positive control would be detectable.

## Statistical tests

See `docs/STATISTICAL_METHODS.md` for full details.

## Feature set for Phase 2+ discriminator

Included: T (ciphertext scalars), idx, sign, w, ztag, nonce.
Excluded: sigma (csprng_u64, not prf_k-rooted), raw Delta.

## All 44 LPN files

All 44 published samples are domain `pvac.prf.r.1`.
They are NOT 44 files covering all six R/noise domains.
