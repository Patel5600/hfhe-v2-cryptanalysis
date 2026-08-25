# Source-Level Trace

Pinned source: `octra-labs/pvac_hfhe_cpp@071b0e909c119de815e284b347c4bd979cb59ef3`.

This document maps the mathematical model to the source-level responsibilities.

## 1. Field arithmetic

`include/pvac/core/field.hpp`

Responsibilities:

- Fp representation with `p = 2^127 - 1`.
- Fp addition/subtraction/multiplication/inversion.
- conversion from Fp to scalar representation.

Relevant mathematical boundary:

`Fp` arithmetic is modulo `p`, while Ristretto scalar arithmetic is modulo `ell`.

## 2. Scalar conversion

`include/pvac/crypto/ristretto255.hpp`

`sc_from_fp(x)` copies the 127-bit Fp representation into a 32-byte scalar representation without first invoking a scalar reduction routine.

This is the source of the cross-field inversion experiment.

## 3. LPN/PRF

`include/pvac/crypto/lpn.hpp`

Responsibilities:

- domain-derived AES key material;
- AES-CTR stream;
- LPN A rows;
- noisy labels `y`;
- Toeplitz transform;
- reduction to the 127-bit Fp output.

## 4. Public H matrix

`include/pvac/crypto/matrix.hpp`

`gen_H()` deterministically samples public H columns from public parameters and `canon_tag`.

The investigation therefore treated H as public infrastructure, not as the hidden LPN matrix.

## 5. Public subgroup powers

`include/pvac/crypto/keygen.hpp`

`powg_B` is generated as consecutive powers of a public subgroup generator `g` of order 337.

Because ciphertext edges publish `idx`, the corresponding exponent is not secret.

## 6. Cipher serialization

`hfhe-challenge/source/pvac_artifact_serialize.hpp`

A BASE layer writes:

- rule;
- ztag;
- nonce.lo;
- nonce.hi;
- PC records.

The writer does not serialize `R_com`.

Edges write:

- layer_id;
- idx;
- sign;
- field weights;
- sigma bit-vector.

## 7. Edge aggregation

The challenge binding verifier reconstructs the public layer aggregate as:

`T = Σ sign(e) * w_e * powg_B[idx_e]`.

This makes `public_T_hex` an authoritative public aggregate for the published LPN sample bindings.

## 8. Noise tuple generation

`include/pvac/ops/encrypt.hpp`

The N2/N3 noise construction generates secret-derived delta values, realizes edge coefficients with the layer mask, and finally merges/permutates the edge representation.

The tuple partition is not preserved in serialized order.

## 9. Commitment path

The commitment path derives a Ristretto point from an Fp inverse converted to a scalar and combines it with a separate blinding scalar/point path.

The investigation therefore treated PC as a potential cross-view leakage point but found no direct statistical or naive algebraic cancellation.

## 10. Interpretation

The source trace supports the attack tree's separation between:

- public graph infrastructure;
- public subgroup infrastructure;
- PRF/LPN hidden material;
- Fp versus scalar-field boundaries;
- wrapped masking.

It does not itself constitute a security proof.
