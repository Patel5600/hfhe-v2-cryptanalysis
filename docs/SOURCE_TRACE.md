# Source-Level Trace — Mapping Mathematics to `pvac_hfhe_cpp@071b0e9`

Pinned source commit: `octra-labs/pvac_hfhe_cpp@071b0e909c119de815e284b347c4bd979cb59ef3`.

## Source Trace Mapping Table

| Mathematical Concept | Source File | Function / Symbol | Lines | Notes |
|---|---|---|---|---|
| $\mathbb{F}_p$ Mersenne Field | `include/pvac/core/types.hpp` | `struct Fp` | 32-45 | 128-bit unsigned representation ($p = 2^{127}-1$) |
| Ristretto Scalar | `include/pvac/crypto/ristretto255.hpp` | `sc_from_fp` | 324-335 | Direct byte copy without `sc_reduce256` |
| Group Order $\ell$ | `include/pvac/crypto/ristretto255.hpp` | `SC_L` | 223-228 | $2^{252} + 277423...$ |
| Pedersen Commitment | `include/pvac/crypto/ristretto255.hpp` | `pedersen_commit` | 754-768 | $w \cdot G + \rho \cdot H$ |
| Ciphertext Serialization | `source/pvac_artifact_serialize.hpp` | `write_layer` | 292-306 | Serializes $PC$, excludes $R_{com}$ |
| Edge Permutation | `include/pvac/ops/encrypt.hpp` | `reduction::permute` | 585-688 | Fisher-Yates CSPRNG shuffle |
| PRF AES-CTR Key Gen | `include/pvac/crypto/lpn.hpp` | `derive_aes_key` | 145-180 | SHA256 key derivation |
| Public Layer Aggregate | `source/tools/verify_lpn_sample_binding.cpp` | `main` | 80-140 | Excludes $\sigma$ entirely |

---

## Detailed Component Responsibilities

### 1. Field arithmetic
`include/pvac/core/field.hpp`
Responsibilities:
- $\mathbb{F}_p$ representation with $p = 2^{127} - 1$.
- $\mathbb{F}_p$ addition, subtraction, multiplication, and inversion via Fermat.
- Conversion from $\mathbb{F}_p$ to scalar representation.

Relevant mathematical boundary:
$\mathbb{F}_p$ arithmetic is modulo $p$, while Ristretto scalar arithmetic is modulo $\ell$.

### 2. Scalar conversion
`include/pvac/crypto/ristretto255.hpp`
`sc_from_fp(x)` copies the 127-bit $\mathbb{F}_p$ representation into a 32-byte scalar representation without first invoking a scalar reduction routine.

### 3. LPN / PRF
`include/pvac/crypto/lpn.hpp`
Responsibilities:
- Domain-derived AES key material;
- AES-CTR stream;
- LPN $A$ rows and noisy labels $y$;
- Toeplitz transform;
- Reduction to the 127-bit $\mathbb{F}_p$ output.

### 4. Public H matrix
`include/pvac/crypto/matrix.hpp`
`gen_H()` deterministically samples public $H$ columns from public parameters and `canon_tag`. The investigation treated $H$ as public infrastructure, not as a hidden secret.

### 5. Public subgroup powers
`include/pvac/crypto/keygen.hpp`
`powg_B` is generated as consecutive powers of a public subgroup generator $g$ of order 337. Because ciphertext edges publish $idx$, the corresponding exponent is not secret.

### 6. Cipher serialization
`hfhe-challenge/source/pvac_artifact_serialize.hpp`
A BASE layer writes: rule, ztag, nonce.lo, nonce.hi, PC records. The writer does NOT serialize $R_{com}$.

### 7. Edge aggregation
The challenge binding verifier reconstructs the public layer aggregate as:
$$T = \sum_{e} \text{sign}(e) \cdot w_e \cdot powg\_B[idx_e]$$
This makes `public_T_hex` an authoritative public aggregate for the published LPN sample bindings.

### 8. Noise tuple generation
`include/pvac/ops/encrypt.hpp`
The N2/N3 noise construction generates secret-derived delta values, realizes edge coefficients with the layer mask, and finally merges/permutates the edge representation. The tuple partition is destroyed by Fisher-Yates shuffle.

### 9. Commitment path
The commitment path derives a Ristretto point from an $\mathbb{F}_p$ weight converted to a scalar and combines it with a separate blinding scalar/point path.

### 10. Interpretation
The source trace supports the attack tree's separation between public graph infrastructure, public subgroup infrastructure, PRF/LPN hidden material, $\mathbb{F}_p$ vs $\mathbb{Z}/\ell\mathbb{Z}$ boundaries, and wrapped masking.\n