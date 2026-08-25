"""
real_artifact_score.py — Phase 2A: Joint-key distinguisher on the real artifact.

Feature set  (exactly what the source justifies):
    T          = public_T_hex  (= Σ_e sign(e)·w_e·g^{idx_e} for a BASE layer,
                                  computed by verify_lpn_sample_binding.cpp)
    ztag       = seed.ztag
    nonce_lo   = seed.nonce.lo
    nonce_hi   = seed.nonce.hi
    cipher_idx = which ciphertext block (0..21)
    layer_id   = 0 or 1 (two wrapped base layers per block)

Excluded by design (Q1/Q2):
    sigma      — uses system csprng, not prf_k-rooted
    raw Δ      — masked by R in the wire format; only R·Δ is public

All 44 published samples are dom = "pvac.prf.r.1".

Three experimental conditions:
    REAL      — observed 44 T values with their actual (ztag, nonce) labels
    SHUFFLED  — same 44 T values, nonce/ztag mapping randomly permuted
                → destroys the key-derived label correspondence
                → should look like NULL_B if signal comes from key structure
    NULL_B    — 44 independently random Fp elements (fresh key per layer)

Verdict criterion (Wald):
    genuine signal  ⟺  score(REAL) >> score(NULL_B)
                    AND  score(SHUFFLED) ≈ score(NULL_B)

Sub-experiments:
    2A-global   : pairwise T distances, all 44×44/2 = 946 pairs
    2B-within   : (ct_i, l0) vs (ct_i, l1) — same prf_k, different nonces
                   22 within-cipher pairs
    2C-cross    : (ct_i, l0) vs (ct_j, l0), i≠j — same domain, diff block
                   C(22,2) = 231 cross-cipher same-layer pairs
"""

import json
import math
import os
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

from fp_field import (
    fp_from_hex, fp_hex, fp_mul, fp_inv, fp_add, fp_sub,
    _to_int, _from_int, P, MASK64, MASK63
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
LPN_DIR   = REPO_ROOT / "lpn_samples"

# ---------------------------------------------------------------------------
# 1.  Load all 44 records from JSONL headers
# ---------------------------------------------------------------------------

def load_all_T() -> list[dict]:
    records = []
    for fpath in sorted(LPN_DIR.glob("*.jsonl")):
        with open(fpath, "r", encoding="ascii") as fh:
            meta = json.loads(fh.readline())

        assert meta["format"] == "octra-bounty-target-seed-lpn-ay-v1"
        assert meta["dom"]    == "pvac.prf.r.1", \
            f"{fpath.name}: unexpected dom={meta['dom']}"

        T_int = int(meta["public_T_hex"], 16)
        T_fp  = fp_from_hex(meta["public_T_hex"])

        records.append({
            "filename":     fpath.name,
            "cipher_index": meta["cipher_index"],
            "layer_id":     meta["layer_id"],
            "seed_ztag":    meta["seed_ztag"],
            "nonce_lo":     int(meta["nonce_lo_hex"], 16),
            "nonce_hi":     int(meta["nonce_hi_hex"], 16),
            "public_T_hex": meta["public_T_hex"],
            "T_int":        T_int,
            "T_fp":         T_fp,
        })

    records.sort(key=lambda r: (r["cipher_index"], r["layer_id"]))
    assert len(records) == 44, f"Expected 44 records, got {len(records)}"
    return records

# ---------------------------------------------------------------------------
# 2.  Distance / feature functions (no sigma, no raw Δ)
# ---------------------------------------------------------------------------

def hamming(a_int: int, b_int: int) -> int:
    return bin(a_int ^ b_int).count("1")

def hamming_norm(a_int: int, b_int: int) -> float:
    return hamming(a_int, b_int) / 128.0

def fp_ratio_dist(a_fp: tuple, b_fp: tuple) -> float:
    """
    Multiplicative distance in F_p:
        d = min(a/b mod p,  p - a/b mod p) / (p//2)
    If a/b ≈ 1 (same value) → 0.  Uniformly random → ≈ 0.5.
    """
    ratio = _to_int(fp_mul(a_fp, fp_inv(b_fp)))
    d = min(ratio, P - ratio)
    return d / (P // 2)


def label_hash(ztag: int, nonce_lo: int, nonce_hi: int) -> int:
    """
    128-bit hash of (ztag, nonce_lo, nonce_hi) — used to include metadata
    in the joint statistic without needing the secret key.
    Matches the data that prf_R_core is deterministically keyed on.
    """
    raw = struct.pack("<QQQ", ztag, nonce_lo, nonce_hi)
    digest = hashlib.sha256(raw).digest()
    return int.from_bytes(digest[:16], "little")


def joint_feature(ri: dict, rj: dict) -> float:
    """
    Joint statistic for a pair (i, j).

    Combines:
      (a) Hamming distance between T_i and T_j — tests T independence
      (b) Hamming distance between label_hash(meta_i) XOR T_i  and
                               label_hash(meta_j) XOR T_j
          — tests whether the T values are correlated *via* the public metadata
            (ztag, nonce) in a way that depends on prf_k.

    Under the null (fresh key per layer), both parts should give uniform distances.
    Under the shared-key hypothesis, part (b) might show structure because
    prf_k participates in *both* the metadata derivation and the T derivation.
    """
    Ti = ri["T_int"]
    Tj = rj["T_int"]

    lhi = label_hash(ri["seed_ztag"], ri["nonce_lo"], ri["nonce_hi"])
    lhj = label_hash(rj["seed_ztag"], rj["nonce_lo"], rj["nonce_hi"])

    # (a) raw T distance
    d_T = hamming_norm(Ti, Tj)

    # (b) T XOR label_hash distance
    d_TL = hamming_norm(Ti ^ lhi, Tj ^ lhj)

    # (c) nonce-vs-T correlation term: nonce XOR distance
    d_nonce = hamming(ri["nonce_lo"], rj["nonce_lo"]) / 64.0

    return (d_T + d_TL + d_nonce) / 3.0


def score(records: list[dict]) -> list[float]:
    """Return all upper-triangle joint_feature values (946 values for n=44)."""
    n = len(records)
    return [joint_feature(records[i], records[j])
            for i in range(n)
            for j in range(i + 1, n)]


# ---------------------------------------------------------------------------
# 3.  Three conditions
# ---------------------------------------------------------------------------

def condition_real(records: list[dict]) -> list[float]:
    """REAL: observed T values with their true (ztag, nonce) labels."""
    return score(records)


def condition_shuffled(records: list[dict], rng: random.Random) -> list[float]:
    """
    SHUFFLED: same T_int values but (ztag, nonce) mapping randomly permuted.
    Destroys the key-derived label correspondence.
    If signal is present in REAL, it should disappear here.
    """
    # Permute the metadata independently of T
    meta_fields = [(r["seed_ztag"], r["nonce_lo"], r["nonce_hi"]) for r in records]
    rng.shuffle(meta_fields)
    shuffled = []
    for i, r in enumerate(records):
        s = dict(r)
        s["seed_ztag"] = meta_fields[i][0]
        s["nonce_lo"]  = meta_fields[i][1]
        s["nonce_hi"]  = meta_fields[i][2]
        shuffled.append(s)
    return score(shuffled)


def condition_null_B(n: int = 44, rng: random.Random = None) -> list[float]:
    """
    NULL_B: fresh independent random T_int and fresh random metadata per layer.
    Simulates a world where each layer has a completely independent key.
    """
    if rng is None:
        rng = random.Random()
    fake = []
    for i in range(n):
        T_int = rng.getrandbits(127) % P
        if T_int == 0:
            T_int = 1
        T_fp = _from_int(T_int)
        fake.append({
            "T_int":     T_int,
            "T_fp":      T_fp,
            "seed_ztag": rng.getrandbits(64),
            "nonce_lo":  rng.getrandbits(64),
            "nonce_hi":  rng.getrandbits(64),
        })
    return score(fake)


# ---------------------------------------------------------------------------
# 4.  Within-cipher and cross-cipher sub-experiments
# ---------------------------------------------------------------------------

def within_cipher_analysis(records: list[dict]) -> dict:
    """
    Sub-experiment 2B: (ct_i, l0) vs (ct_i, l1).
    Same underlying prf_k, same plaintext block, independent nonces.
    Under the wrapped construction:
        T_0 = R_0 * (v + m)    T_1 = -R_1 * m
    with R_0, R_1 independently derived from prf_k but different nonces.
    """
    by_cipher = defaultdict(dict)
    for r in records:
        by_cipher[r["cipher_index"]][r["layer_id"]] = r

    pairs = []
    for ci in sorted(by_cipher):
        layers = by_cipher[ci]
        if 0 not in layers or 1 not in layers:
            continue
        l0, l1 = layers[0], layers[1]
        pairs.append({
            "cipher_index": ci,
            "hamming_T":    hamming_norm(l0["T_int"], l1["T_int"]),
            "fp_ratio":     fp_ratio_dist(l0["T_fp"], l1["T_fp"]),
            "joint":        joint_feature(l0, l1),
            # Additive sum in Fp: T0 + T1 = R0(v+m) - R1*m
            # Under null (independent R0, R1): uniformly random Fp element
            "fp_sum_int":   _to_int(fp_add(l0["T_fp"], l1["T_fp"])),
            "T0_hex":       l0["public_T_hex"],
            "T1_hex":       l1["public_T_hex"],
        })
    return pairs


def cross_cipher_same_layer_analysis(records: list[dict]) -> dict:
    """
    Sub-experiment 2C: (ct_i, l_k) vs (ct_j, l_k) for i≠j, k in {0,1}.
    Different blocks, same layer slot — tests shared-key structure across blocks.
    """
    by_layer = defaultdict(list)
    for r in records:
        by_layer[r["layer_id"]].append(r)

    results = {}
    for lid, recs in by_layer.items():
        dists = []
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                dists.append(joint_feature(recs[i], recs[j]))
        results[lid] = dists
    return results


# ---------------------------------------------------------------------------
# 5.  Statistics
# ---------------------------------------------------------------------------

def describe(label: str, data: list[float], indent: int = 4) -> dict:
    n   = len(data)
    mu  = statistics.mean(data)
    sd  = statistics.stdev(data) if n > 1 else 0.0
    pad = " " * indent
    print(f"{pad}{label}:")
    print(f"{pad}  n={n}  mean={mu:.6f}  std={sd:.6f}  "
          f"min={min(data):.6f}  median={statistics.median(data):.6f}  max={max(data):.6f}")
    return {"n": n, "mean": mu, "std": sd, "min": min(data),
            "median": statistics.median(data), "max": max(data)}


def ks2(a: list[float], b: list[float], label_a: str, label_b: str) -> dict:
    if HAS_SCIPY:
        stat, pval = scipy_stats.ks_2samp(a, b)
        print(f"    KS({label_a} vs {label_b}): stat={stat:.5f}  p={pval:.5f}")
        return {"statistic": float(stat), "p_value": float(pval)}
    else:
        mu_a, mu_b = statistics.mean(a), statistics.mean(b)
        sd_a, sd_b = statistics.stdev(a), statistics.stdev(b)
        se = math.sqrt(sd_a**2/len(a) + sd_b**2/len(b))
        z  = (mu_a - mu_b) / se if se > 0 else 0.0
        pv = 2.0*(1.0 - 0.5*(1.0 + math.erf(abs(z)/math.sqrt(2.0))))
        print(f"    Normal-approx({label_a} vs {label_b}): z={z:.4f}  p≈{pv:.5f}")
        return {"z_score": float(z), "p_value_approx": float(pv)}


# ---------------------------------------------------------------------------
# 6.  Verdict helper
# ---------------------------------------------------------------------------

def verdict(ks_real_vs_null: dict, ks_shuffled_vs_null: dict) -> str:
    pv_r = ks_real_vs_null.get("p_value") or ks_real_vs_null.get("p_value_approx", 1.0)
    pv_s = ks_shuffled_vs_null.get("p_value") or ks_shuffled_vs_null.get("p_value_approx", 1.0)

    stat_r = ks_real_vs_null.get("statistic", 0.0)
    stat_s = ks_shuffled_vs_null.get("statistic", 0.0)

    if pv_r < 0.01 and pv_s >= 0.05:
        label = "⚠  SIGNAL DETECTED"
        detail = (f"REAL differs from NULL_B (p={pv_r:.4f}) "
                  f"but SHUFFLED does not (p={pv_s:.4f}).\n"
                  "     Shared prf_k creates detectable cross-layer coupling.\n"
                  "     → Proceed to Phase 2B (masked-Δ relation test).")
    elif pv_r < 0.01 and pv_s < 0.05:
        label = "⚠  AMBIGUOUS SIGNAL"
        detail = (f"Both REAL and SHUFFLED differ from NULL_B "
                  f"(p_real={pv_r:.4f}, p_shuffled={pv_s:.4f}).\n"
                  "     Signal is not key-specific — may be an artifact of the\n"
                  "     Fp distribution structure. Run more NULL_B trials.")
    elif pv_r >= 0.05:
        label = "✓  NO SIGNAL"
        detail = (f"REAL is indistinguishable from NULL_B (p={pv_r:.4f}).\n"
                  "     Shared prf_k behaves as a PRF across layers at this\n"
                  "     observable resolution.\n"
                  "     → Close joint-key branch; move to named cryptanalytic attack.")
    else:
        label = "?  BORDERLINE"
        detail = (f"p_real={pv_r:.4f}  p_shuffled={pv_s:.4f}.\n"
                  "     Increase NULL_B trials (NUM_NULL_TRIALS) for confidence.")

    return f"{label}\n     {detail}"


# ---------------------------------------------------------------------------
# 7.  Main
# ---------------------------------------------------------------------------

NUM_NULL_TRIALS    = 5000    # number of independent NULL_B simulations
NUM_SHUFFLE_TRIALS = 500     # number of random permutations for SHUFFLED condition


def main():
    print("=" * 70)
    print("HFHE v2  Phase 2A — Joint-key distinguisher (real artifact)")
    print("Feature set: T, ztag, nonce  |  Excluded: sigma, raw Delta")
    print("Three conditions: REAL / SHUFFLED / NULL_B")
    print("=" * 70)
    print()

    # ── Load ──────────────────────────────────────────────────────────────
    print("[1] Loading 44 public_T_hex records ...")
    records = load_all_T()
    print(f"    {len(records)} records loaded. "
          f"Ciphertexts: {sorted(set(r['cipher_index'] for r in records))[0]}"
          f"–{sorted(set(r['cipher_index'] for r in records))[-1]}, "
          f"layers: {sorted(set(r['layer_id'] for r in records))}")
    print()

    # Sanity: verify ct00_l0 / ct00_l1 ordering
    for r in records[:4]:
        print(f"    [{r['cipher_index']:02d} l{r['layer_id']}]  "
              f"T={r['public_T_hex'][:20]}...  "
              f"ztag={r['seed_ztag']:016x}")
    print()

    # ── REAL condition ─────────────────────────────────────────────────────
    print("[2] REAL condition (all 44 T values with true metadata) ...")
    real_scores = condition_real(records)
    stats_real  = describe("joint_feature distribution", real_scores)
    print()

    # ── SHUFFLED condition ─────────────────────────────────────────────────
    print(f"[3] SHUFFLED condition ({NUM_SHUFFLE_TRIALS} permutations) ...")
    rng_shuf = random.Random(0xDEADBEEF_CAFEBABE)
    shuffled_all = []
    for _ in range(NUM_SHUFFLE_TRIALS):
        shuffled_all.extend(condition_shuffled(records, rng_shuf))
    stats_shuf = describe("joint_feature distribution (shuffled)", shuffled_all)
    print()

    # ── NULL_B condition ───────────────────────────────────────────────────
    print(f"[4] NULL_B condition ({NUM_NULL_TRIALS} trials, fresh key per layer) ...")
    rng_null = random.Random(0x1234567890ABCDEF)
    null_all = []
    for _ in range(NUM_NULL_TRIALS):
        null_all.extend(condition_null_B(n=44, rng=rng_null))
    stats_null = describe("joint_feature distribution (null B)", null_all)
    print()

    # ── KS tests ───────────────────────────────────────────────────────────
    print("[5] KS tests ...")
    ks_rn = ks2(real_scores,    null_all,    "REAL",     "NULL_B")
    ks_sn = ks2(shuffled_all,   null_all,    "SHUFFLED", "NULL_B")
    ks_rs = ks2(real_scores,    shuffled_all,"REAL",     "SHUFFLED")
    print()

    # ── Sub-experiment 2B: within-cipher ──────────────────────────────────
    print("[6] Sub-experiment 2B — within-cipher pairs (same prf_k, diff nonce)")
    wc_pairs = within_cipher_analysis(records)
    print(f"    {len(wc_pairs)} within-cipher pairs (ct_i l0 vs ct_i l1):")

    wc_hamming = [p["hamming_T"]  for p in wc_pairs]
    wc_ratio   = [p["fp_ratio"]   for p in wc_pairs]
    wc_joint   = [p["joint"]      for p in wc_pairs]

    describe("Hamming(T_l0, T_l1)/128", wc_hamming)
    describe("Fp-ratio dist(T_l0, T_l1)", wc_ratio)
    describe("joint_feature(l0, l1)", wc_joint)

    # Expected under null: Hamming ≈ 0.5, ratio ≈ 0.5
    # Null reference
    rng_wc = random.Random(42)
    null_wc_hamming = [
        hamming_norm(rng_wc.getrandbits(127) % P, rng_wc.getrandbits(127) % P)
        for _ in range(len(wc_pairs) * 200)
    ]
    if HAS_SCIPY:
        ks_wc_h, p_wc_h = scipy_stats.ks_2samp(wc_hamming, null_wc_hamming)
        print(f"    KS(within-cipher Hamming vs null): stat={ks_wc_h:.5f}  p={p_wc_h:.5f}")
    print()

    # ── Sub-experiment 2C: cross-cipher same-layer ──────────────────────────
    print("[7] Sub-experiment 2C — cross-cipher pairs (diff block, same layer slot)")
    cc = cross_cipher_same_layer_analysis(records)
    for lid, dists in sorted(cc.items()):
        describe(f"joint_feature cross-cipher layer_id={lid} ({len(dists)} pairs)", dists)
    print()

    # ── Wald verdict ───────────────────────────────────────────────────────
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    v = verdict(ks_rn, ks_sn)
    for line in v.split("\n"):
        print(f"  {line}")
    print()

    # ── Save results ───────────────────────────────────────────────────────
    import json as _json
    out_path = Path(__file__).parent / "phase2_results.json"
    out = {
        "num_records":      len(records),
        "num_null_trials":  NUM_NULL_TRIALS,
        "num_shuf_trials":  NUM_SHUFFLE_TRIALS,
        "stats_real":       stats_real,
        "stats_shuffled":   stats_shuf,
        "stats_null_B":     stats_null,
        "ks_real_vs_null":  {k: (float(v) if isinstance(v, float) else str(v))
                             for k, v in ks_rn.items()},
        "ks_shuffled_vs_null": {k: (float(v) if isinstance(v, float) else str(v))
                                for k, v in ks_sn.items()},
        "ks_real_vs_shuffled": {k: (float(v) if isinstance(v, float) else str(v))
                                for k, v in ks_rs.items()},
        "within_cipher_pairs": wc_pairs,
        "T_manifest": [
            {
                "filename":     r["filename"],
                "cipher_index": r["cipher_index"],
                "layer_id":     r["layer_id"],
                "seed_ztag":    r["seed_ztag"],
                "nonce_lo_hex": hex(r["nonce_lo"]),
                "nonce_hi_hex": hex(r["nonce_hi"]),
                "public_T_hex": r["public_T_hex"],
            }
            for r in records
        ],
    }
    with open(out_path, "w") as f:
        _json.dump(out, f, indent=2)
    print(f"  Full results written to: {out_path}")


if __name__ == "__main__":
    main()
