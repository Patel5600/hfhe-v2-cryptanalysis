# Phase 5 — Pedersen Commitments

## Public serialization question

The BASE-layer writer serializes:

- `rule`
- `ztag`
- `nonce.lo`
- `nonce.hi`
- `PC[]`

It does **not** serialize `R_com`.

Therefore the v1 direct commitment-oracle attack is unavailable on the v2 wire format.

## Experiment 5A — PC extraction

The live artifact contains exactly 44 serialized 32-byte PC points.

All extracted points were distinct under the tested representation.

## Experiment 5B — PC distribution

REAL pairwise distribution:

- n = 946
- mean Hamming distance = 0.49770
- SD = 0.03146
- KS p = 0.1964

Within-cipher pair:

- n = 22
- mean = 0.49059
- SD = 0.02289
- p = 0.1205

No point-level statistical bias was observed at this resolution.

## Experiment 5C — Fp versus scalar-field inversion

Let:

`p = 2^127 - 1`

and let `ell` denote the Ristretto scalar modulus.

`sc_from_fp(x)` copies the Fp representation into the scalar representation without first calling scalar reduction. Since `p < ell`, an Fp element is an exact integer embedding.

For:

`a = R^{-1} mod p`

we have:

`R*a = 1 + k*p`.

There is no general reason for `1 + k*p = 1 mod ell`.

Empirical result:

- embedding checks: 50,000/50,000 exact
- inversion compatibility checks: 0/100,000 exact cancellations

## Interpretation

The obvious attack:

`T * sc_from_fp(R^{-1} mod p) -> v`

cannot work through a simple cross-field homomorphism.

This does not prove that every possible PC/T algebraic relation is impossible.

## Verdict

**CLOSED.** No direct R_com, PC-distribution, or naive cross-field cancellation exploit survived.
