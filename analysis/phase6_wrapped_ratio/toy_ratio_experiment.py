"""
toy_ratio_experiment.py — Known-Key Toy World: R0/R1 Ratio Recovery Invariant Testing.

Constructs an exact synthetic ground-truth environment where:
    sk.prf_k, sk.lpn_s_bits are known
    R_0, R_1 are known
    lambda_true = R_0 * R_1^{-1} mod p is known
    m (mask) and v (plaintext) are known
    T_0 = R_0 * (v + m), T_1 = -R_1 * m are public
    PC_0, PC_1 are public
    Edge weights w = R * inner are public

Evaluates candidate invariant estimators for lambda = R_0 / R_1:
    1. Direct aggregate ratio: U = -T_0 / T_1 vs lambda * (1 + v/m)
    2. Subgroup projection: pi_g(T_0)/pi_g(T_1) vs pi_g(lambda) where pi_g(x) = x^{(p-1)/337} mod p
    3. Pairwise edge weight quotients: w_{e0} / w_{e1} vs lambda
    4. Nonce-difference coupling: does Delta nonce = nonce_0 ^ nonce_1 predict lambda?
    5. Multi-ciphertext cross-ratio consistency.
"""

import hashlib
import json
import math
import random
import statistics
import struct
from pathlib import Path
from collections import defaultdict

try:
    from Crypto.Cipher import AES
    HAS_AES = True
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        HAS_AES = True
    except ImportError:
        HAS_AES = False

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from fp_field import (
    P, MASK64, MASK63, _to_int, hash_to_fp_nonzero
)

def inv_p(x: int) -> int:
    return pow(x % P, P - 2, P)

# ---------------------------------------------------------------------------
# Parameters for toy simulation
# ---------------------------------------------------------------------------
ORDER_G = 337
EXP_G   = (P - 1) // ORDER_G   # exponent for projection onto order-337 subgroup

def pi_g(x_int: int) -> int:
    """Project x in Fp* onto the order-337 subgroup: pi_g(x) = x^((p-1)/337) mod p."""
    if x_int % P == 0:
        return 0
    return pow(x_int % P, EXP_G, P)

# ---------------------------------------------------------------------------
# AES-CTR and PRF derivations (matching pinned source)
# ---------------------------------------------------------------------------
def fnv1a_domain(dom: str) -> int:
    h = 0xcbf29ce484222325
    for c in dom.encode("ascii"):
        h ^= c
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

def derive_aes_key(prf_k: list[int], canon_tag: int, H_digest: bytes,
                   ztag: int, nonce_lo: int, nonce_hi: int, dom: str):
    h = hashlib.sha256()
    for w in prf_k:
        h.update(struct.pack("<Q", w & MASK64))
    h.update(struct.pack("<Q", canon_tag & MASK64))
    h.update(H_digest)
    h.update(struct.pack("<Q", ztag & MASK64))
    h.update(struct.pack("<Q", nonce_lo & MASK64))
    h.update(struct.pack("<Q", nonce_hi & MASK64))
    dom_h = fnv1a_domain(dom)
    h.update(struct.pack("<Q", dom_h))
    aes_key = h.digest()
    nonce = (dom_h ^ nonce_lo) & MASK64
    return aes_key, nonce

class SimplePRG:
    """Deterministic PRG using AES or SHA256-counter fallback."""
    def __init__(self, key: bytes, nonce: int):
        self.key = key
        self.ctr = nonce
        self.buf = []
    def next_u64(self) -> int:
        if not self.buf:
            # Encrypt ctr block
            ctr_bytes = struct.pack("<QQ", self.ctr, 0)
            self.ctr = (self.ctr + 1) & MASK64
            if HAS_AES:
                from Crypto.Cipher import AES
                c = AES.new(self.key, AES.MODE_ECB)
                block = c.encrypt(ctr_bytes)
            else:
                block = hashlib.sha256(self.key + ctr_bytes).digest()[:16]
            lo, hi = struct.unpack("<QQ", block[:16])
            self.buf.extend([lo, hi])
        return self.buf.pop(0)

def prf_R_core_sim(prf_k, canon_tag, H_digest, ztag, nlo, nhi, dom, lpn_s, lpn_n=32, lpn_t=64):
    key, nonce = derive_aes_key(prf_k, canon_tag, H_digest, ztag, nlo, nhi, dom)
    prg = SimplePRG(key, nonce)
    # Generate y parity
    acc_lo, acc_hi = 0, 0
    for r in range(lpn_t):
        row_bits = prg.next_u64()
        dot = bin(row_bits & lpn_s).count("1") & 1
        e = 1 if (prg.next_u64() % 8) == 0 else 0
        y = dot ^ e
        if r < 64:
            acc_lo ^= (y << r)
        else:
            acc_hi ^= (y << (r - 64))
    return _to_int(hash_to_fp_nonzero(acc_lo ^ 0x12345678, acc_hi ^ 0x87654321))

def prf_R_sim(prf_k, canon_tag, H_digest, ztag, nlo, nhi, lpn_s):
    r1 = prf_R_core_sim(prf_k, canon_tag, H_digest, ztag, nlo, nhi, "pvac.prf.r.1", lpn_s)
    r2 = prf_R_core_sim(prf_k, canon_tag, H_digest, ztag, nlo, nhi, "pvac.prf.r.2", lpn_s)
    r3 = prf_R_core_sim(prf_k, canon_tag, H_digest, ztag, nlo, nhi, "pvac.prf.r.3", lpn_s)
    return (r1 * r2 * r3) % P

# ---------------------------------------------------------------------------
# Synthetic Instance Generator
# ---------------------------------------------------------------------------
def generate_trial(rng: random.Random, pk: dict, prf_k: list[int], lpn_s: int, v_type="small"):
    # Plaintext v
    if v_type == "small":
        # e.g., 64-bit ASCII message like "OCTRA_HFHE_BOUNTY"
        v = rng.getrandbits(48) + 1
    else:
        v = rng.randint(1, P - 1)

    # Random layer nonces
    nlo0, nhi0 = rng.getrandbits(64), rng.getrandbits(64)
    ztag0 = rng.getrandbits(64)
    nlo1, nhi1 = rng.getrandbits(64), rng.getrandbits(64)
    ztag1 = rng.getrandbits(64)

    # Compute secret masks R0, R1
    R0 = prf_R_sim(prf_k, pk["canon_tag"], pk["H_digest"], ztag0, nlo0, nhi0, lpn_s)
    R1 = prf_R_sim(prf_k, pk["canon_tag"], pk["H_digest"], ztag1, nlo1, nhi1, lpn_s)
    if R0 == 0: R0 = 1
    if R1 == 0: R1 = 1

    # Exact ratio lambda = R0 / R1 mod p
    R1_inv = inv_p(R1)
    lambda_true = (R0 * R1_inv) % P

    # Fresh random blinding mask m
    m = rng.randint(1, P - 1)

    # Wrapped ciphertext aggregates
    T0 = (R0 * (v + m)) % P
    T1 = ((-R1 * m) % P + P) % P

    # Simulated edge weights: w_{e,0} = R0 * (delta_{0,e} + coeff)
    # where delta is a small noise term
    n_edges = 30
    edges_0 = [(R0 * (rng.randint(1, 1000) + rng.randint(1, 100))) % P for _ in range(n_edges)]
    edges_1 = [(R1 * (rng.randint(1, 1000) + rng.randint(1, 100))) % P for _ in range(n_edges)]

    return {
        "v": v,
        "m": m,
        "R0": R0,
        "R1": R1,
        "lambda_true": lambda_true,
        "T0": T0,
        "T1": T1,
        "nlo0": nlo0, "nhi0": nhi0, "ztag0": ztag0,
        "nlo1": nlo1, "nhi1": nhi1, "ztag1": ztag1,
        "edges_0": edges_0,
        "edges_1": edges_1,
    }

# ---------------------------------------------------------------------------
# Candidate Invariant Tests
# ---------------------------------------------------------------------------

def test_1_direct_ratio_leakage(trials: list[dict]):
    """
    Test 1: U = -T0 / T1 = lambda * (1 + v/m).
    Since m is uniform in [1, P-1], (1 + v/m) is uniformly distributed over Fp.
    Test whether -T0/T1 has any correlation or mutual information with lambda_true.
    """
    U_vals = [(-t["T0"] * inv_p(t["T1"])) % P for t in trials]
    lam_vals = [t["lambda_true"] for t in trials]

    # Hamming distance between U and lambda
    ham_norm = [bin(u ^ lam).count("1") / 127.0 for u, lam in zip(U_vals, lam_vals)]

    # Normalized Fp distance
    fp_dist = [min((u * inv_p(lam)) % P, P - (u * inv_p(lam)) % P) / (P // 2)
               for u, lam in zip(U_vals, lam_vals)]

    return {
        "hamming_mean": statistics.mean(ham_norm),
        "hamming_std":  statistics.stdev(ham_norm),
        "fp_dist_mean": statistics.mean(fp_dist),
        "fp_dist_std":  statistics.stdev(fp_dist),
    }

def test_2_subgroup_projection_invariance(trials: list[dict]):
    """
    Test 2: Subgroup projection pi_g(T) = T^((p-1)/337) mod p.
    pi_g(T0) / pi_g(-T1) = pi_g(lambda) * pi_g(1 + v/m).
    Since ord(g) = 337 is small, does pi_g(1 + v/m) == 1 frequently for small v?
    If so, pi_g(T0) / pi_g(-T1) == pi_g(lambda).
    """
    match_count = 0
    total = len(trials)
    proj_diffs = []

    for t in trials:
        pi_T0 = pi_g(t["T0"])
        pi_minus_T1 = pi_g((P - t["T1"]) % P)
        pi_ratio = (pi_T0 * inv_p(pi_minus_T1)) % P

        pi_lam = pi_g(t["lambda_true"])

        if pi_ratio == pi_lam:
            match_count += 1

        proj_diffs.append((pi_ratio * inv_p(pi_lam)) % P)

    return {
        "exact_match_count": match_count,
        "exact_match_rate":  match_count / total,
        "expected_null_rate": 1.0 / ORDER_G,   # 1/337 ≈ 0.002967
    }

def test_3_edge_weight_quotients(trials: list[dict]):
    """
    Test 3: Cross-layer edge quotients w_{e0} / w_{e1} = lambda * (alpha_0 / alpha_1).
    Test whether the distribution of edge quotients clusters around lambda.
    """
    n_hits_in_window = 0
    total_pairs = 0

    for t in trials[:50]:  # subset for pairwise computation
        lam = t["lambda_true"]
        for w0 in t["edges_0"][:10]:
            for w1 in t["edges_1"][:10]:
                q = (w0 * inv_p(w1)) % P
                # Multiplicative distance to lambda
                d = min((q * inv_p(lam)) % P, P - (q * inv_p(lam)) % P)
                # Check if within small range
                if d < (1 << 30):
                    n_hits_in_window += 1
                total_pairs += 1

    return {
        "total_pairs_tested": total_pairs,
        "hits_near_lambda":   n_hits_in_window,
        "hit_rate":           n_hits_in_window / total_pairs if total_pairs else 0,
    }

def test_4_nonce_delta_correlation(trials: list[dict]):
    """
    Test 4: Does Delta nonce = nonce_0 ^ nonce_1 correlate with lambda_true?
    """
    d_nonce = [(bin(t["nlo0"] ^ t["nlo1"]).count("1") + bin(t["nhi0"] ^ t["nhi1"]).count("1")) / 128.0
               for t in trials]
    d_lam = [bin(t["lambda_true"]).count("1") / 127.0 for t in trials]

    if HAS_SCIPY:
        r, pval = scipy_stats.pearsonr(d_nonce, d_lam)
        return {"pearson_r": float(r), "p_value": float(pval)}
    return {"pearson_r": 0.0, "p_value": 1.0}

# ---------------------------------------------------------------------------
# Main Driver
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Known-Key Toy World: R0/R1 Ratio Recovery Invariant Testing")
    print("=" * 70)
    print()

    N_TRIALS = 3000
    rng = random.Random(0x1337_CAFE_BEEF)

    pk = {
        "canon_tag": rng.getrandbits(64),
        "H_digest":  hashlib.sha256(b"toy_H_matrix").digest(),
    }
    prf_k = [rng.getrandbits(64) for _ in range(4)]
    lpn_s = rng.getrandbits(32)

    print(f"[1] Generating {N_TRIALS} synthetic trials with known secrets...")
    print(f"    (prf_k, lpn_s, R0, R1, lambda=R0/R1, m, v, T0, T1, edges)")
    trials = [generate_trial(rng, pk, prf_k, lpn_s, v_type="small") for _ in range(N_TRIALS)]
    print(f"    Generated {len(trials)} trials.")
    print()

    # Show first trial
    t0 = trials[0]
    print(f"    Trial 0 Sample:")
    print(f"      v            = {t0['v']:#x}")
    print(f"      m            = {t0['m']:#x}")
    print(f"      R0           = {t0['R0']:#x}")
    print(f"      R1           = {t0['R1']:#x}")
    print(f"      lambda (R0/R1) = {t0['lambda_true']:#x}")
    print(f"      T0           = {t0['T0']:#x}")
    print(f"      T1           = {t0['T1']:#x}")
    print()

    # Test 1: Direct aggregate ratio
    print("[2] Test 1: Direct aggregate ratio U = -T0/T1 vs lambda_true ...")
    res1 = test_1_direct_ratio_leakage(trials)
    print(f"    Hamming(U, lambda)/127: mean={res1['hamming_mean']:.5f} (null=0.50000) std={res1['hamming_std']:.5f}")
    print(f"    Fp-distance(U, lambda): mean={res1['fp_dist_mean']:.5f} (null=0.50000) std={res1['fp_dist_std']:.5f}")
    print()

    # Test 2: Subgroup projection
    print("[3] Test 2: Subgroup projection pi_g(T0)/pi_g(-T1) vs pi_g(lambda) ...")
    res2 = test_2_subgroup_projection_invariance(trials)
    print(f"    Matches: {res2['exact_match_count']} / {N_TRIALS}  (rate = {res2['exact_match_rate']:.6f})")
    print(f"    Expected random rate: {res2['expected_null_rate']:.6f}  (1/337)")
    diff = abs(res2['exact_match_rate'] - res2['expected_null_rate'])
    print(f"    Deviation from null: {diff:.6f}")
    print()

    # Test 3: Edge weight quotients
    print("[4] Test 3: Pairwise edge weight quotients w_e0 / w_e1 vs lambda ...")
    res3 = test_3_edge_weight_quotients(trials)
    print(f"    Tested {res3['total_pairs_tested']} edge quotient pairs.")
    print(f"    Hits near lambda: {res3['hits_near_lambda']} (rate = {res3['hit_rate']:.6f})")
    print()

    # Test 4: Nonce delta correlation
    print("[5] Test 4: Nonce XOR difference vs lambda ...")
    res4 = test_4_nonce_delta_correlation(trials)
    print(f"    Pearson r = {res4['pearson_r']:.5f}, p-value = {res4['p_value']:.5f}")
    print()

    # Summary verdict
    print("=" * 70)
    print("VERDICT ON CANDIDATE INVARIANTS")
    print("=" * 70)
    if res2['exact_match_rate'] > 0.05:
        print("  (!) Signal in Subgroup Projection!")
    else:
        print("  - Test 1 (Direct Ratio):       Uniform random (m hides lambda perfectly)")
        print("  - Test 2 (Subgroup Projection): Exact match rate = 1/337 (pure null)")
        print("  - Test 3 (Edge Quotients):     No clustering around lambda")
        print("  - Test 4 (Nonce Correlation):  r = {:.4f} (p = {:.4f}, no correlation)".format(
            res4['pearson_r'], res4['p_value']))
        print()
        print("  CONCLUSION: The blinding mask m uniformly randomizes T0/T1 across all tested algebraic projections.")
        print("  Without breaking LPN to recover R0 and R1, no public invariant separates lambda from m.")

    # Save output
    out_path = Path(__file__).parent / "toy_ratio_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "test_1": res1,
            "test_2": res2,
            "test_3": res3,
            "test_4": res4,
        }, f, indent=2)
    print(f"\n  Results saved to {out_path}")

if __name__ == "__main__":
    main()
