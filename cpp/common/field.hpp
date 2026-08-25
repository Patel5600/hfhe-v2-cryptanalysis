#pragma once
// Fp = Z/(2^127 - 1) arithmetic for HFHE v2 cryptanalysis
// Reference implementation — not optimized

#include <cstdint>
#include <cassert>

namespace fp {

// p = 2^127 - 1
// Using __uint128_t for 128-bit arithmetic
using u128 = unsigned __int128;

constexpr u128 P = (static_cast<u128>(1) << 127) - 1;

inline u128 reduce(u128 x) {
    // x is at most 2*p; one conditional subtraction suffices
    u128 lo = x & P;
    u128 hi = x >> 127;
    u128 r = lo + hi;
    if (r >= P) r -= P;
    return r;
}

inline u128 add(u128 a, u128 b) {
    // Use 256-bit intermediate via __uint128_t overflow detection
    u128 r = a + b;
    if (r < a) r -= P;  // wrapped around 2^128 > 2*P, subtract P
    return reduce(r);
}

inline u128 mul(u128 a, u128 b) {
    // 256-bit product via schoolbook (compiler intrinsics)
    // __uint128_t * __uint128_t is 256-bit; use __uint128_t carefully
    // For simplicity: use 64x64->128 multiply and accumulate
    uint64_t a_lo = (uint64_t)a;
    uint64_t a_hi = (uint64_t)(a >> 64);
    uint64_t b_lo = (uint64_t)b;
    uint64_t b_hi = (uint64_t)(b >> 64);

    u128 p00 = (u128)a_lo * b_lo;
    u128 p01 = (u128)a_lo * b_hi;
    u128 p10 = (u128)a_hi * b_lo;
    u128 p11 = (u128)a_hi * b_hi;

    // 256-bit result in (hi, lo)
    u128 lo  = p00 + (p01 << 64) + (p10 << 64);
    u128 hi  = p11 + (p01 >> 64) + (p10 >> 64) + (lo < p00 ? 1 : 0);

    // Reduce mod p = 2^127-1:
    // x = hi * 2^128 + lo
    // hi * 2^128 = hi * (2^127 - 1 + 1) * 2 = 2*hi * p + 2*hi
    // Simplified: r = (lo & P) + (lo >> 127) + 2*hi (mod P)
    u128 r = (lo & P) + (lo >> 127) + 2 * hi;
    return reduce(r);
}

// Modular inverse via Fermat: a^(p-2) mod p
u128 inv(u128 a);

} // namespace fp
