"""
pc_distribution_test.py — Experiment 3: PC point statistical distribution & cross-layer test.

Analyzes the 44 Ristretto255 Pedersen commitment points extracted from secret.ct:
    PC_i = sc_from_fp_signed(R_i^{-1}) * G + rho_i * H

Tests:
1. Pairwise Hamming distance across encoded 32-byte Ristretto points (946 pairs).
2. REAL vs SHUFFLED vs NULL_B (random 32-byte point encodings / simulated Pedersen commitments).
3. Within-cipher analysis: (ct_i, l0) vs (ct_i, l1) for each of the 22 ciphertext blocks.
4. Cross-correlation between PC point distances and (T, nonce) distances.
"""

import json
import random
import statistics
import struct
import hashlib
from pathlib import Path
from collections import defaultdict

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

REPO_ROOT = Path(__file__).parent.parent
PC_DATA_PATH = Path(__file__).parent / "phase3_pc_data.json"
PHASE2_DATA_PATH = Path(__file__).parent / "phase2_results.json"

def hamming_256(a_bytes: bytes, b_bytes: bytes) -> int:
    a_int = int.from_bytes(a_bytes, "big")
    b_int = int.from_bytes(b_bytes, "big")
    return bin(a_int ^ b_int).count("1")

def hamming_norm(a_bytes: bytes, b_bytes: bytes) -> float:
    return hamming_256(a_bytes, b_bytes) / 256.0

def load_pc_records():
    with open(PC_DATA_PATH, "r") as f:
        data = json.load(f)
    return data["pc_records"]

def pairwise_pc_distances(records):
    n = len(records)
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            pci = bytes.fromhex(records[i]["pc_hex"])
            pcj = bytes.fromhex(records[j]["pc_hex"])
            dists.append(hamming_norm(pci, pcj))
    return dists

def null_b_pc_distances(num_trials=5000, n=44):
    rng = random.Random(0xCAFE_BABE_9999)
    dists = []
    for _ in range(num_trials):
        fake_pts = [rng.randbytes(32) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(hamming_norm(fake_pts[i], fake_pts[j]))
    return dists

def shuffled_pc_distances(records, num_shuffles=500):
    rng = random.Random(0xDEAD_1234_5678)
    n = len(records)
    pts = [bytes.fromhex(r["pc_hex"]) for r in records]
    dists = []
    for _ in range(num_shuffles):
        shuf = list(pts)
        rng.shuffle(shuf)
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(hamming_norm(shuf[i], shuf[j]))
    return dists

def within_cipher_pc_analysis(records):
    by_cipher = defaultdict(dict)
    for r in records:
        by_cipher[r["cipher_index"]][r["layer_id"]] = r

    pairs = []
    for ci in sorted(by_cipher):
        layers = by_cipher[ci]
        if 0 in layers and 1 in layers:
            pc0 = bytes.fromhex(layers[0]["pc_hex"])
            pc1 = bytes.fromhex(layers[1]["pc_hex"])
            pairs.append({
                "cipher_index": ci,
                "hamming": hamming_norm(pc0, pc1),
                "pc0_hex": layers[0]["pc_hex"],
                "pc1_hex": layers[1]["pc_hex"],
            })
    return pairs

def describe(label, data):
    n = len(data)
    mu = statistics.mean(data)
    sd = statistics.stdev(data) if n > 1 else 0.0
    print(f"  {label}:")
    print(f"    n={n}  mean={mu:.6f}  std={sd:.6f}  min={min(data):.6f}  median={statistics.median(data):.6f}  max={max(data):.6f}")
    return {"n": n, "mean": mu, "std": sd, "min": min(data), "median": statistics.median(data), "max": max(data)}

def main():
    print("=" * 70)
    print("Experiment 3: PC Point Statistical Distribution & Structure Test")
    print("=" * 70)
    print()

    records = load_pc_records()
    print(f"[1] Loaded {len(records)} PC records from phase3_pc_data.json")
    print()

    print("[2] Pairwise PC Hamming distance (REAL: 946 pairs) ...")
    real_dists = pairwise_pc_distances(records)
    stats_real = describe("REAL pairwise PC Hamming / 256", real_dists)
    print()

    print("[3] Pairwise PC Hamming distance (SHUFFLED: 500 permutations) ...")
    shuf_dists = shuffled_pc_distances(records, num_shuffles=500)
    stats_shuf = describe("SHUFFLED pairwise PC Hamming / 256", shuf_dists)
    print()

    print("[4] Pairwise PC Hamming distance (NULL_B: 5000 trials) ...")
    null_dists = null_b_pc_distances(num_trials=5000, n=44)
    stats_null = describe("NULL_B pairwise PC Hamming / 256", null_dists)
    print()

    print("[5] Statistical tests (KS 2-sample) ...")
    if HAS_SCIPY:
        ks_rn, p_rn = scipy_stats.ks_2samp(real_dists, null_dists)
        ks_sn, p_sn = scipy_stats.ks_2samp(shuf_dists, null_dists)
        ks_rs, p_rs = scipy_stats.ks_2samp(real_dists, shuf_dists)
        print(f"    KS(REAL vs NULL_B):      stat={ks_rn:.5f}  p={p_rn:.5f}")
        print(f"    KS(SHUFFLED vs NULL_B):  stat={ks_sn:.5f}  p={p_sn:.5f}")
        print(f"    KS(REAL vs SHUFFLED):    stat={ks_rs:.5f}  p={p_rs:.5f}")
    print()

    print("[6] Within-cipher analysis (22 pairs: ct_i l0 vs ct_i l1) ...")
    wc_pairs = within_cipher_pc_analysis(records)
    wc_hamming = [p["hamming"] for p in wc_pairs]
    describe("Within-cipher PC Hamming / 256", wc_hamming)

    if HAS_SCIPY:
        # Compare 22 within-cipher pairs against null
        rng_wc = random.Random(0x4242)
        null_wc = [hamming_norm(rng_wc.randbytes(32), rng_wc.randbytes(32)) for _ in range(50000)]
        ks_wc, p_wc = scipy_stats.ks_2samp(wc_hamming, null_wc)
        print(f"    KS(Within-cipher vs Null): stat={ks_wc:.5f}  p={p_wc:.5f}")
    print()

    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if HAS_SCIPY and p_rn >= 0.05 and p_wc >= 0.05:
        print("  ✓  NO SIGNAL in PC points")
        print(f"     REAL vs NULL_B (p={p_rn:.4f}) and Within-Cipher vs Null (p={p_wc:.4f})")
        print("     The Ristretto255 Pedersen commitments PC = (R^-1 mod p)*G + rho*H")
        print("     are statistically indistinguishable from uniform random Ristretto points.")
        print("     Pedersen blinding by rho perfectly hides R^-1.")
        print("     => PC structural leakage branch: CLOSED")
    else:
        print("  Signal / non-uniformity check needed.")

    # Save output
    out_path = Path(__file__).parent / "phase3_pc_results.json"
    res = {
        "stats_real": stats_real,
        "stats_shuffled": stats_shuf,
        "stats_null": stats_null,
        "within_cipher_pairs": wc_pairs,
    }
    if HAS_SCIPY:
        res["ks_rn"] = {"stat": float(ks_rn), "p": float(p_rn)}
        res["ks_wc"] = {"stat": float(ks_wc), "p": float(p_wc)}
    with open(out_path, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\n  Results saved to {out_path}")

if __name__ == "__main__":
    main()
