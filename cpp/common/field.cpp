#include "field.hpp"

namespace fp {

// Square-and-multiply for a^(p-2) mod p
u128 inv(u128 a) {
    assert(a != 0);
    // p - 2 = 2^127 - 3
    // Binary exponentiation: 127 squarings + select multiplies
    u128 result = 1;
    u128 base = a;
    // p-2 in binary: 127 ones followed by one zero and one zero = 2^127-3
    // = 111...1101 (125 ones, then 0, then 1)
    // Iterate bit by bit from MSB
    // For a Mersenne prime this can be done with an addition chain;
    // here we use generic square-and-multiply for clarity.
    uint64_t exp_hi = (1ULL << 62) - 1;  // top 63 bits all 1
    uint64_t exp_lo = ~0ULL - 2;         // bottom 64 bits: all 1 except bit 1 and bit 0
    // Reconstruct: p-2 = 2^127 - 3
    // We iterate 127 bits
    for (int bit = 126; bit >= 0; bit--) {
        result = mul(result, result);
        int in_hi = (bit >= 64) ? 1 : 0;
        uint64_t word = in_hi ? exp_hi : exp_lo;
        int local_bit = bit % 64;
        if ((word >> local_bit) & 1)
            result = mul(result, base);
    }
    return result;
}

} // namespace fp
