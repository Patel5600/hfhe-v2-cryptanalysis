# System Model

## 1. Public-key layer

The public key contains:

- `Params`
- `canon_tag`
- public GF(2) matrix `H`
- public permutation `ubk.perm` / inverse
- `H_digest`
- `omega_B`
- `powg_B`

Parameters used by the live artifact:

```text
B          = 337
m_bits     = 8192
n_bits     = 16384
h_col_wt   = 192
x_col_wt   = 128
err_wt     = 128
lpn_n      = 4096
lpn_t      = 16384
tau        = 1/8
```

## 2. Master secret material

The secret key contains at least two logically distinct components:

```text
prf_k       -> PRF/AES-derived masks and domain-specific values
lpn_s_bits  -> LPN parity secret S
```

In `keygen()`, both are independently sampled by the CSPRNG.

Therefore:

`S` is not a reversible encoding of `prf_k`.

## 3. PRF-derived masks

The six mask domains are:

```text
pvac.prf.r.1
pvac.prf.r.2
pvac.prf.r.3
pvac.prf.noise.1
pvac.prf.noise.2
pvac.prf.noise.3
```

The masking scalar has the conceptual composition:

`R = R1 * R2 * R3 mod p`.

Noise-generation paths use their own domain-separated PRF values.

## 4. LPN sample generation

The LPN core has the form:

`y_i = <A_i,S> XOR e_i`.

`A` and error generation are driven from the PRF/AES stream, while `S` is an independently generated secret vector.

The challenge publishes 44 files for the `pvac.prf.r.1` sample path.

## 5. Wrapped ciphertext

For the wrapped pair used by the challenge:

`T0 = R0(v + m) mod p`

`T1 = -R1*m mod p`

where `m` is a fresh nonzero Fp mask.

The public layer aggregate is reconstructed from serialized edges as:

`T = Σ sign(e) * w_e * powg_B[idx_e]`.

## 6. Cipher edge representation

Each serialized edge contains:

- layer id
- public index
- public sign
- one or more Fp weights
- sigma bit-vector

Before serialization the implementation merges edges by `(layer, idx, sign)` and then permutes the result with a CSPRNG shuffle.

Therefore the serialized order does not preserve original hidden N2/N3 tuple grouping.

## 7. Pedersen commitments

Each BASE layer serializes one commitment per slot.

The writer serializes the PC point but omits the legacy `R_com` field.

The commitment path combines a scalar derived from the Fp inverse of the mask with a separate blinding component in the Ristretto group.

Because Fp and the Ristretto scalar field use different moduli, naive multiplication of `R` by `sc_from_fp(R_inv_p)` does not equal one in the scalar field in general.

## 8. Public subgroup

`powg_B` contains consecutive powers of a subgroup generator of order 337.

Every ciphertext edge publishes `idx`, so the subgroup exponent corresponding to that edge is not itself secret.

## 9. Security interpretation

The investigation treats the following as separate objects:

- public infrastructure (`H`, `powg_B`, permutation);
- PRF/AES-derived masking;
- independent LPN secret `S`;
- wrapped plaintext masking `m`;
- Pedersen commitment hiding.

A break must connect public observables to plaintext/secret recovery through an actual exploitable dependency.
