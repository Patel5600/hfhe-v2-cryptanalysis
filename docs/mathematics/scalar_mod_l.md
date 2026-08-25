# Ristretto255 Scalar Field Z/ℓZ

## Group order

    ℓ = 2^252 + 27742317777372353535851937790883648493
      = 7237005577332262213973186563042994240857116359379907606001950938285454250989

## Scalar arithmetic

All Pedersen commitment scalars are computed mod ℓ.
The commitment PC = w*G + ρ*H where G, H are Ristretto255 generators,
and w, ρ are scalars in Z/ℓZ.

## sc_from_fp — the crucial non-reduction

Source: `include/pvac/crypto/ristretto255.hpp`

```cpp
inline Scalar sc_from_fp(const Fp& x) {
    uint8_t buf[32] = {};
    // copy 128-bit val into buf little-endian
    memcpy(buf, &x.val, 16);
    return sc_from_bytes(buf);  // NO sc_reduce256 call
}
```

Since p = 2^127 - 1 < ℓ, any element of Fp fits in 127 bits, which is
well below ℓ's 252-bit order. Therefore sc_from_fp embeds x ∈ Fp into Z/ℓZ
as the same integer — no reduction needed or applied.

## Cross-field inversion failure

Let R ∈ Fp, R ≠ 0.
Let a = R^(-1) mod p  (computed in Fp arithmetic).

As integers:  R * a = 1 + k*p   for some integer k ≥ 0.

In Z/ℓZ:  R * a ≡ 1 + k*p (mod ℓ)

Since p ≠ 0 mod ℓ (because p < ℓ and gcd(p,ℓ) = 1 by Mersenne properties),
this is NOT 1 mod ℓ unless k = 0, which requires R = 1.

**Conclusion:** The Fp inverse of R does not serve as a Ristretto255 scalar
inverse of sc_from_fp(R). This kills the cross-field inversion attack branch.

Verified experimentally: 0 / 100,000 random R ∈ Fp satisfy R*(R^-1 mod p) ≡ 1 mod ℓ.
