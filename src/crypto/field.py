"""
fp_field.py — Pure-Python arithmetic in F_p  where  p = 2^127 - 1 (Mersenne-127)
Mirrors pvac/core/field.hpp at pinned commit 071b0e9.

All values are (lo: int, hi: int) pairs where the field element is  lo + hi*2^64,
with the constraint  hi < 2^63  (MASK63).
"""

P   = (1 << 127) - 1          # 2^127 - 1
MASK63 = (1 << 63) - 1
MASK64 = (1 << 64) - 1

def fp_from_words(lo: int, hi: int) -> tuple:
    """Canonical field element from raw 64-bit words (hi must already have bit-63 clear)."""
    return (lo & MASK64, hi & MASK63)

def fp_from_u64(v: int) -> tuple:
    return (v & MASK64, 0)

def _to_int(x: tuple) -> int:
    lo, hi = x
    return (lo + (hi << 64)) % P

def _from_int(n: int) -> tuple:
    n = n % P
    lo = n & MASK64
    hi = (n >> 64) & MASK63
    return (lo, hi)

def fp_add(a: tuple, b: tuple) -> tuple:
    return _from_int(_to_int(a) + _to_int(b))

def fp_sub(a: tuple, b: tuple) -> tuple:
    return _from_int(_to_int(a) - _to_int(b))

def fp_mul(a: tuple, b: tuple) -> tuple:
    return _from_int(_to_int(a) * _to_int(b))

def fp_neg(a: tuple) -> tuple:
    return _from_int(-_to_int(a))

def fp_inv(a: tuple) -> tuple:
    """Fermat: a^(p-2) mod p."""
    n = _to_int(a)
    if n == 0:
        raise ZeroDivisionError("fp_inv: zero")
    return _from_int(pow(n, P - 2, P))

def fp_is_zero(a: tuple) -> bool:
    lo, hi = a
    return lo == 0 and hi == 0

def hash_to_fp_nonzero(lo: int, hi: int) -> tuple:
    """Match pvac::hash_to_fp_nonzero: mask hi to 63 bits; if result is zero, return 1."""
    r = fp_from_words(lo, hi)
    if fp_is_zero(r):
        return fp_from_u64(1)
    return r

def fp_hex(x: tuple) -> str:
    lo, hi = x
    return f"{(hi & MASK63):016x}{lo:016x}"

def fp_from_hex(h: str) -> tuple:
    """Parse a 32-char hex string (hi||lo, each 16 chars)."""
    h = h.strip()
    if len(h) != 32:
        raise ValueError(f"expected 32 hex chars, got {len(h)}: {h!r}")
    hi = int(h[:16], 16) & MASK63
    lo = int(h[16:], 16) & MASK64
    return (lo, hi)

# ---------------------------------------------------------------------------
# Sanity tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    one = fp_from_u64(1)
    assert _to_int(fp_mul(one, one)) == 1
    a = fp_from_u64(12345)
    ai = fp_inv(a)
    assert _to_int(fp_mul(a, ai)) == 1, "inversion check failed"

    # Hex round-trip
    x = fp_from_words(0xDEADBEEFCAFEBABE, 0x1234567890ABCDEF & MASK63)
    h = fp_hex(x)
    assert fp_from_hex(h) == x, "hex round-trip failed"

    print("fp_field: all self-tests passed")
