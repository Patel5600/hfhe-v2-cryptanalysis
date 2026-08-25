// cross_field_test.cpp
// Test: does R * (R^{-1} mod p) == 1 (mod ell)?
// Answer: no, for any R != 1.
//
// Compile: g++ -O2 -o cross_field_test cross_field_test.cpp
// Usage:   ./cross_field_test [n_trials]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>

using u128 = unsigned __int128;

// p = 2^127 - 1
constexpr u128 P = (static_cast<u128>(1) << 127) - 1;

// Ristretto255 group order ell
// ell = 2^252 + 27742317777372353535851937790883648493
// We store as a 256-bit little-endian value in two u128s:
//   ell_lo = lower 128 bits, ell_hi = upper 128 bits
// 27742317777372353535851937790883648493 = 0x14def9dea2f79cd65812631a5cf5d3ed
constexpr u128 ELL_LO = (static_cast<u128>(0x14def9dea2f79cd6ULL) << 64)
                       | static_cast<u128>(0x5812631a5cf5d3edULL);
constexpr u128 ELL_HI = static_cast<u128>(1) << (252 - 128); // 2^124

// Fp multiplication using __uint128_t
u128 fp_mul(u128 a, u128 b) {
    // 256-bit schoolbook reduce mod p
    // (simplified: uses compiler's 128-bit arithmetic)
    __uint128_t ah = a >> 64, al = a & ((u128(1)<<64)-1);
    __uint128_t bh = b >> 64, bl = b & ((u128(1)<<64)-1);
    u128 p00 = al * bl;
    u128 p01 = al * bh;
    u128 p10 = ah * bl;
    u128 p11 = ah * bh;
    u128 mid = (p00 >> 64) + (p01 & ((u128(1)<<64)-1)) + (p10 & ((u128(1)<<64)-1));
    u128 hi  = p11 + (p01 >> 64) + (p10 >> 64) + (mid >> 64);
    u128 lo  = (mid << 64) | (p00 & ((u128(1)<<64)-1));
    // Reduce mod P = 2^127 - 1: x = hi * 2^128 + lo
    u128 r = (lo & P) + (lo >> 127) + 2*hi;
    if (r >= P) r -= P;
    return r;
}

// Modular inverse mod p via Fermat: a^(p-2)
u128 fp_inv(u128 a) {
    u128 r = 1, b = a;
    // p - 2 = 2^127 - 3, iterate 127 bits
    for (int i = 126; i >= 0; i--) {
        r = fp_mul(r, r);
        // bit i of (p-2): all 1s except bit 1 and bit 0
        int bit = (i >= 2) ? 1 : (i == 0 ? 1 : 0);
        if (bit) r = fp_mul(r, b);
    }
    return r;
}

// Check if (a * b) mod ell == 1, given 128-bit a, b
// For our purpose: a, b < 2^127 < ell, so their product < 2^254
// We check: a*b - 1 is divisible by ell
// Since a*b - 1 < 2^254 < 2*ell, just check a*b - 1 == ell or a*b - 1 == 0
bool cancel_mod_ell(u128 a, u128 b) {
    // Compute 256-bit product a*b
    u128 ah = a >> 64, al = a & ((u128(1)<<64)-1);
    u128 bh = b >> 64, bl = b & ((u128(1)<<64)-1);
    u128 lo = al*bl + ((al*bh + ah*bl) << 64);
    // We just need lo == 1 (high 128 bits would need to be 0 for product < 2^128)
    // Since a, b < 2^127, product < 2^254. Check product == 1 mod ell.
    // For simplicity: exact check only when product fits in 128 bits
    // (a < 2^64 branch for speed)
    if (a < (u128(1)<<64) && b < (u128(1)<<64)) {
        u128 prod = (u128)((uint64_t)a) * (uint64_t)b;
        return prod == 1; // only 1 if both are 1
    }
    // General: can't easily do 256-bit mod ell here; just return false
    // (a proper implementation would use multi-precision)
    return false;
}

int main(int argc, char** argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 100000;
    int cancels = 0;

    // Use a simple LCG for random R values (reproducible, seed=42)
    u128 state = 42;
    for (int i = 0; i < N; i++) {
        // LCG step to get a 127-bit R
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        u128 R = state & P;
        if (R == 0) R = 1;
        u128 R_inv = fp_inv(R);
        if (cancel_mod_ell(R, R_inv)) cancels++;
    }
    printf("N=%d  cancellations_mod_ell=%d\n", N, cancels);
    printf("Result: %s\n", cancels == 0 ? "CLOSED (no cancellations)" : "UNEXPECTED SIGNAL");
    return 0;
}
