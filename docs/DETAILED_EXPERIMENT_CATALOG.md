# Detailed Experiment Catalog

This file is the index for the quantitative experiments performed during the investigation. Each item records the question, observable, result, and what was ruled out.

## E00 — Exact artifact identity

**Question:** Are the bytes being analyzed the intended challenge artifacts?

**Observed:**
- `secret.ct` = 1,963,107 bytes, `OCTRA-HFHE-BTY02`, 22 objects, zero trailing bytes.
- `pk.bin` = 3,042,901 compressed bytes, 17,110,454 decompressed bytes.

**Result:** exact structural parse.

**Closed:** corruption, truncation, accidental alternate artifact.

## E01 — Cipher layer count

**Question:** Does the live artifact actually contain the claimed wrapped structure?

**Observed:** 22 objects × 2 BASE layers = 44 BASE layers, 0 PROD layers.

**Result:** confirmed.

## E02 — LPN sample binding

**Question:** Are the published LPN files bound to the live ciphertext rather than being unrelated samples?

**Observable:** `(domain, seed_ztag, nonce_lo, nonce_hi, public_T_hex)`.

**Result:** 44/44 matches.

**Closed:** decoy-sample / mismatched-artifact hypothesis.

## E03 — Serialized weight reuse

**Question:** Does the same masked field value recur across edges/layers?

**Corpus:** 1,829 weights.

**Result:** 1,829 unique; zero zero-values; zero cross-object collisions.

**Closed:** direct scalar reuse.

## E04 — Cross-layer weight intersection

**Question:** Does a wrapped pair share masked coefficients?

**Result:** every same-object pair had empty weight intersection.

**Closed:** simple shared-edge cancellation.

## E05 — Scalar bit balance

**Question:** Are serialized Fp elements statistically non-random?

**Result:** low and high limbs were near 0.5 bit balance.

**Closed:** simple field-output bias.

## E06 — Group-level reconstruction

**Definition:**

`G = Σ sign(e) * w_e * powg_B[idx_e]`.

**Result:** all 44 nonzero; all 44 distinct.

**Closed:** trivial group collision.

## E07 — Wrapped-pair group cancellation

**Tests:** `G0 + G1 == 0` and `G0 - G1 == 0`.

**Result:** false for all 22 objects.

**Closed:** direct linear mask cancellation.

## E08 — Tuple ordering

**Source property:** merge by `(layer, idx, sign)`, canonical ordering, CSPRNG Fisher-Yates permutation.

**Result:** no surviving tuple order information.

**Closed:** serialization-order attack.

## E09 — Historical R_com oracle

**Question:** Can public `R_com` be used as a plaintext-guess verifier as in the earlier challenge version?

**Result:** `R_com` is not serialized by the v2 layer writer.

**Closed:** v1 oracle.

## E10 — Population-A matrix statistics

**Corpus:** 44 × 16,384 = 720,896 equations.

**Observed:**
- mean row weight = 2047.9401
- row-weight SD = 31.9966
- global y=1 rate = 0.4996893
- mean pairwise A Hamming distance = 2048.00863
- wrapped-pair mean A Hamming = 2048.00016
- pairwise y agreement = 0.5001130
- exact repeated rows = 0

**Closed:** basic AES/LPN-stream anomalies.

## E11 — Matched-null Population B definition

**Correct null:** freeze public challenge metadata, resample `prf_k`, let pinned construction generate independent `S_B`.

**Important:** setting `S_B = S_A` is invalid because `S_A` is unknown.

**Status:** methodology specified.

## E12 — Joint `public_T` key-structure test

**REAL:** 946 pair observations; mean 0.49844; SD 0.02958.

**NULL_B:** mean 0.49871; SD 0.02944.

**REAL vs NULL_B:** KS p = 0.523.

**REAL vs SHUFFLED:** p = 0.405.

**Closed:** cheap shared-`prf_k` coupling observable through T/metadata.

## E13 — Within-object T comparison

22 wrapped pairs.

Mean normalized Hamming distance = 0.4794; p = 0.334.

**Closed:** no statistically significant within-object T anomaly.

## E14 — H matrix structure

**Parameters:** 8192 × 16384; mixed column weight 192/193.

**Result:** full GF(2) rank = 8192; column-weight distribution matches the construction; no obvious duplicate-column shortcut.

**Closed:** easy linear-algebra weakness in public H.

## E15 — `powg_B` subgroup structure

`B = 337`, `powg_B[0] = 1`, consecutive multiplication matches across all 336 transitions; `g^337 = 1`, `g != 1`.

**Observation:** the subgroup DLP is tiny because the order is 337, but the corresponding `idx` is already public on every edge.

**Closed:** DLP-as-edge-index shortcut.

## E16 — Subgroup cyclotomic relation

Because `ord(g)=337`:

`1 + g + ... + g^336 = 0`.

**Result:** no unknown coefficient vector is exposed that lets this public relation cancel a secret.

**Closed:** direct cyclotomic shortcut.

## E17 — PC parsing

**Result:** 44 serialized 32-byte Ristretto points, all distinct and decodable under the implementation model.

**Closed:** malformed/duplicate commitment representation.

## E18 — PC distribution

REAL pairwise PC Hamming:
- n = 946
- mean = 0.49770
- SD = 0.03146
- KS p = 0.1964

Within-object PC pair:
- n = 22
- mean = 0.49059
- SD = 0.02289
- p = 0.1205

**Closed:** simple PC statistical bias.

## E19 — Fp/scalar cross-field embedding

`sc_from_fp()` embeds the 127-bit Fp representation as an integer scalar; no immediate scalar reduction occurs at that conversion.

50,000/50,000 embedding checks were exact.

## E20 — Fp-inverse versus scalar-inverse compatibility

Tested:

`R * (R^{-1} mod p) == 1 mod ell`.

100,000 trials: zero hits.

**Closed:** naive cross-field cancellation.

## E21 — Wrapped ratio Legendre test

Toy N = 20,000.

`χ2(-T0/T1)` vs null:
- χ² = 1.3448
- p = 0.2462

**Closed:** quadratic-character projection.

## E22 — Wrapped ratio sign prediction

Prediction of `χ2(lambda)` from public quotient character:

- rate = 50.00%
- χ² = 0.0968
- p = 0.7557

**Closed:** direct low-dimensional ratio prediction.

## E23 — Wrapped ratio joint LSB

χ² = 3.0991, p = 0.3766.

**Closed:** low-bit parity coupling.

## E24 — Wrapped ratio joint population parity

χ² = 6.2472, p = 0.1002.

**Closed:** global popcount coupling.

## E25 — ISD/BJMM intuition

The no-error information-set probability is:

`(7/8)^4096 = 2^-789.07`.

This demonstrates naive error-free information-set search is infeasible, but it is **not** a formal lower bound on advanced ISD.

**Result:** no practical ISD route identified.

## E26 — BKW sample/noise tradeoff

Elimination increases noise according to:

`tau' = 2*tau*(1-tau)`.

The available sample budget is insufficient for aggressive elimination without quickly approaching half-noise and exhausting memory/sample requirements.

**Result:** no practical BKW route identified.

## E27 — Private-key dependency gap

Even a hypothetical recovery of the LPN secret `S` does not algebraically invert SHA-256 to recover `prf_k`.

**Closed:** the shortcut `S -> prf_k -> R` is not available by direct inversion.

## Final interpretation

The CLOSED results eliminate concrete, tested hypotheses. They do not constitute a proof that every possible attack is impossible.
