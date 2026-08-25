# The Field Fp = Z/(2^127 - 1)

## Prime

    p = 2^127 - 1 = 170141183460469231731687303715884105727

This is a Mersenne prime. Reduction modulo p is cheap:
    x mod p = (x_lo + x_hi) mod p   where x = x_hi * 2^127 + x_lo

## Representation in pvac_hfhe_cpp

Defined in `include/pvac/core/types.hpp`:

```cpp
struct Fp {
    __uint128_t val;
};
```

Arithmetic operations: `fp_add`, `fp_mul`, `fp_inv` (Fermat little theorem: a^(p-2)).

## Why Fp?

Edge scalar weights w are drawn from Fp via PRF output:
    w = prf_k(domain, layer, idx) reduced mod p

Fp is large enough that weight reuse probability is negligible:
    Pr[collision in N edges] ≈ N^2 / (2p) → 0 for N < 2^60

## Key property used in cross-field attack analysis

Since p = 2^127 - 1 < ℓ = 2^252 + ..., an element of Fp embeds naturally
into Z/ℓZ without reduction. This means sc_from_fp(x) = x as an integer.
However, multiplication in Z/ℓZ does NOT equal multiplication in Fp:
    (a * b) mod ℓ ≠ (a * b) mod p   in general
