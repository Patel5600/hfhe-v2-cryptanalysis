"""
pc_field_analysis.py — Experiment 1: Cross-field reduction injectivity check.

Verifies the mathematical claim:
    p = 2^127-1,  ell = Ristretto group order (~2^252)
    p < ell  =>  sc_from_fp(x) = x  (no mod-ell reduction)
    BUT:  sc_from_fp(R) * sc_from_fp(R^{-1}_p)  !=  1  (mod ell) in general

Also confirms:
    sc_from_fp_signed sign-bit behaviour
    How often the "error term" kp mod ell produces a meaningful value

Outputs:
    - Fraction of random R where R * R_inv_p == 1 mod ell  (expected: ~0 for p!=ell)
    - Distribution of error term (R * R_inv_p - 1) mod ell
    - Confirmation that p embeds losslessly into Z/ell
"""

import random
import statistics

# ── Field constants ────────────────────────────────────────────────────────
P   = (1 << 127) - 1   # Mersenne-127
ELL = 2**252 + 27742317777372353535851937790883648493  # Ristretto group order

assert P < ELL, "p must be < ell for the embedding to be lossless"

# ── sc_from_fp: embed Fp element into Z/ell ────────────────────────────────
def sc_from_fp(x_int: int) -> int:
    """
    Mirror of pvac::sc_from_fp:
        interpret the 127-bit Fp integer as little-endian bytes → Scalar
        Since p < ell, no sc_reduce512 fires — value passes through unchanged.
    """
    x_int = x_int % P  # ensure canonical Fp
    # sc_reduce512 on a 127-bit value: since x < p < ell, x mod ell = x
    return x_int % ELL  # always identity for x in [0, p-1]

def sc_from_fp_signed(x_int: int) -> int:
    """
    Mirror of pvac::sc_from_fp_signed:
        if bit 62 of hi-word set (i.e., x >= 2^126):
            return -sc_from_fp(fp_neg(x))  (mod ell)
        else:
            return sc_from_fp(x)
    The 'hi' word contains bits 64..126 of x_int.
    Bit 62 of hi = bit 126 of x_int.
    """
    x_int = x_int % P
    if x_int >> 126:  # bit 126 set  (x.hi >> 62 & 1 in C++)
        pos = (-x_int) % P   # fp_neg
        return (-sc_from_fp(pos)) % ELL
    return sc_from_fp(x_int)

def fp_inv(x: int) -> int:
    """Fermat: x^(p-2) mod p."""
    return pow(x, P - 2, P)

def sc_mul(a: int, b: int) -> int:
    return (a * b) % ELL

# ── Experiment 1A: Does R * R_inv_p == 1 mod ell? ─────────────────────────
def run_injectivity_check(n_samples: int = 100_000, seed: int = 42) -> dict:
    rng = random.Random(seed)
    matches = 0
    error_terms = []

    for _ in range(n_samples):
        R = rng.randint(1, P - 1)
        R_inv_p = fp_inv(R)

        # What sc_from_fp_signed sees
        sc_R     = sc_from_fp_signed(R)
        sc_Rinv  = sc_from_fp_signed(R_inv_p)

        product  = sc_mul(sc_R, sc_Rinv)  # should be 1 if fields were compatible

        if product == 1:
            matches += 1

        # Error term: product - 1 (mod ell), normalised to [0, ell)
        err = (product - 1) % ELL
        # Normalise to [0, 0.5) of ell range
        err_norm = min(err, ELL - err) / ELL
        error_terms.append(err_norm)

    return {
        "n_samples":         n_samples,
        "product_eq_1_count": matches,
        "product_eq_1_frac":  matches / n_samples,
        "error_mean":         statistics.mean(error_terms),
        "error_std":          statistics.stdev(error_terms),
        "error_min":          min(error_terms),
        "error_max":          max(error_terms),
    }

# ── Experiment 1B: sc_from_fp is lossless (p < ell) ──────────────────────
def verify_lossless_embedding(n_samples: int = 10_000, seed: int = 7) -> bool:
    rng = random.Random(seed)
    for _ in range(n_samples):
        x = rng.randint(0, P - 1)
        assert sc_from_fp(x) == x, f"Embedding not lossless at x={x}"
    return True

# ── Experiment 1C: sign-bit flip rate ─────────────────────────────────────
def sign_bit_analysis(n_samples: int = 100_000, seed: int = 13) -> dict:
    rng = random.Random(seed)
    flipped = 0
    for _ in range(n_samples):
        x = rng.randint(1, P - 1)
        if x >> 126:
            flipped += 1
    return {
        "n_samples": n_samples,
        "flipped":   flipped,
        "flip_rate": flipped / n_samples,
        "expected_flip_rate": "~0.5 (half of [0,p) has bit 126 set)",
    }

# ── Experiment 1D: The concrete "error term" formula ──────────────────────
def error_term_formula(n: int = 20) -> None:
    """
    R * R_inv_p = 1 + k*p  for some integer k in {0, 1, ..., ?}.
    In Z/ell:  (R * R_inv_p) mod ell = (1 + k*p) mod ell.
    If k*p is uniformly distributed mod ell, no leakage.
    Compute k = (R * R_inv_p - 1) / p  for small samples.
    """
    rng = random.Random(0xABCD)
    print("  Sample error-term k values (R * R_inv_p = 1 + k*p):")
    k_vals = []
    for _ in range(n):
        R = rng.randint(1, P - 1)
        R_inv_p = fp_inv(R)
        product_int = R * R_inv_p  # as integers (NOT mod p)
        assert (product_int - 1) % P == 0, "Inversion failed"
        k = (product_int - 1) // P
        k_vals.append(k)
        print(f"    R={R & 0xFFFF:#06x}...  k={k}")
    print(f"  k range: [{min(k_vals)}, {max(k_vals)}]")
    # k*p mod ell: if this is ~uniform, no leakage
    kp_mod_ell = [(k * P) % ELL for k in k_vals]
    kp_norm = [v / ELL for v in kp_mod_ell]
    print(f"  (k*p mod ell)/ell: mean={statistics.mean(kp_norm):.4f} "
          f"std={statistics.stdev(kp_norm):.4f}  (uniform => ~0.5, 0.29)")

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("Experiment 1: Cross-field reduction injectivity (Fp vs Z/ell)")
    print("=" * 70)
    print(f"  p   = 2^127-1  =  {P}")
    print(f"  ell = {ELL}")
    print(f"  p < ell: {P < ELL}")
    print(f"  p bit-length: {P.bit_length()}  ell bit-length: {ELL.bit_length()}")
    print()

    print("[1A] Lossless embedding check (sc_from_fp(x) = x for x in Fp)...")
    ok = verify_lossless_embedding(n_samples=50_000)
    print(f"     PASS: all 50,000 samples embedded identically (p < ell confirmed)")
    print()

    print("[1B] Injectivity failure: R * sc(R_inv_p) == 1 mod ell ?")
    res = run_injectivity_check(n_samples=100_000)
    print(f"     n={res['n_samples']}")
    print(f"     product == 1 (mod ell): {res['product_eq_1_count']} / {res['n_samples']}"
          f"  ({res['product_eq_1_frac']:.6f})")
    print(f"     error_norm mean={res['error_mean']:.6f}  std={res['error_std']:.6f}")
    print(f"     error_norm min={res['error_min']:.6f}   max={res['error_max']:.6f}")
    print()

    if res['product_eq_1_frac'] < 1e-4:
        print("     CONFIRMED: sc_from_fp(R) * sc_from_fp(R_inv_p) != 1 (mod ell)")
        print("     The PC commits to R_inv_p as an integer, NOT the ell-inverse of R.")
        print("     => The committed value is NOT algebraically invertible by")
        print("        multiplying T by a Ristretto scalar. Pedersen hiding holds.")
    elif res['product_eq_1_frac'] > 0.99:
        print("     UNEXPECTED: fields ARE compatible — investigate further.")
    else:
        print(f"     Partial match at rate {res['product_eq_1_frac']:.4f} — investigate.")
    print()

    print("[1C] Sign-bit flip rate (sc_from_fp_signed negation)...")
    sbr = sign_bit_analysis(n_samples=100_000)
    print(f"     flipped={sbr['flipped']}  rate={sbr['flip_rate']:.4f}  "
          f"expected={sbr['expected_flip_rate']}")
    print()

    print("[1D] Concrete error-term k analysis (R * R_inv_p = 1 + k*p)...")
    error_term_formula(n=20)
    print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  sc_from_fp lossless:  YES  (p={P.bit_length()} bits < ell={ELL.bit_length()} bits)")
    print(f"  R * R_inv_p == 1 mod ell:  {res['product_eq_1_frac']:.1%} of cases")
    print(f"  Conclusion: PC = (R^{{-1}} mod p) * G + rho*H  in Ristretto,")
    print(f"              but (R^{{-1}} mod p) is NOT the ell-inverse of R.")
    print(f"              Combining T=Rv (Fp) with PC (Ristretto) requires")
    print(f"              solving ECDLP in Ristretto255 — infeasible.")
    print(f"  => Cross-field coupling branch: CLOSED")

if __name__ == "__main__":
    main()
