# System Model

## HFHE v2 Construction Overview

### Key generation

    prf_k  (master PRF key)
     |
     +-- R1, R2, R3              (Fp^{n x n} masks via prf_R_core)
     +-- R_noise1, R_noise2, R_noise3   (noise masks)
     +-- rho                     (Pedersen blinding seed)

    H  (16384 x 8192 GF(2) parity-check matrix, public, from public randomness)
    g^B  (public group element; g has order 337, B in [1,336])

### Encryption

For a plaintext m:

    v = fresh random vector
    T0 = R0 * (v + m)    (wrapped layer 0)
    T1 = -R1 * m         (wrapped layer 1)

Each layer produces edges:

    edge = (idx, sign, w, ztag, nonce, sigma, PC)

where:
- idx     : column index into H (public, range [0, 16383])
- sign    : +1 / -1
- w       : Fp scalar weight (prf_k-derived)
- ztag    : zero-tag bit
- nonce   : per-edge nonce
- sigma   : from sigma_from_H(..., csprng_u64())  — NOT prf_k-rooted
- PC      : Pedersen commitment = w*G + rho*H (Ristretto255 point)

Edges are merged by (layer, index, sign), permuted by Fisher-Yates CSPRNG shuffle,
then serialized. R_com is NOT serialized.

### Public key structure

    B     = 337       (powg_B exponent, public)
    m_bits  = 8192
    n_bits  = 16384
    h_col_wt = 192
    x_col_wt = 128
    err_wt   = 128
    lpn_n    = 4096
    lpn_t    = 16384
    tau      = 1/8

H matrix: 16384 columns, each of Hamming weight ~192/193 (full GF(2) rank 8192).

### LPN samples

44 files, all domain `pvac.prf.r.1` (R1 derivation seed).
Each file: 16384 samples over dimension 4096, noise rate 1/8.
