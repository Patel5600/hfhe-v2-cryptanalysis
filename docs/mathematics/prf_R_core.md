# PRF_R_core: The prf_k-to-mask-matrix Derivation

## Source

`include/pvac/crypto/lpn.hpp`

## Construction

```cpp
// Step 1: Derive a 32-byte AES key from prf_k
aes_key = derive_aes_key(prf_k, canonical_tag, H_digest, ztag, nonce_lo, nonce_hi, domain);

// Step 2: Use AES-CTR to generate a stream of pseudorandom bytes
stream = AES_CTR(aes_key, counter=0);

// Step 3: Interpret bytes as Fp elements (rejection sampling)
R[i][j] = next_fp_element(stream);
```

## Domain tags

The domain tag encodes which R matrix is being derived:

| Domain       | Tag constant |
|--------------|--------------|
| R1 (layer 0) | `pvac.prf.r.1` |
| R2 (layer 1) | `pvac.prf.r.2` |
| R3 (layer 2) | `pvac.prf.r.3` |
| R_noise1     | `pvac.prf.noise.1` |
| R_noise2     | `pvac.prf.noise.2` |
| R_noise3     | `pvac.prf.noise.3` |

**All 44 published LPN samples are domain `pvac.prf.r.1` only.**
The R2/R3/noise domains were not released with the challenge.

## Key derivation formula

    K_D = SHA256(prf_k || canon_tag || H_digest || ztag || nonce_lo || nonce_hi || FNV1a(D))

where D is the domain string.

## Why prf_k is the master secret

All six R matrices and ρ (Pedersen blinding) derive from prf_k through
independent domain-separated calls. Recovering any single R_i value from
public observables would require either:
- Breaking AES-CTR with a 256-bit key (infeasible)
- Distinguishing the AES output from uniform bytes (infeasible under AES assumption)
