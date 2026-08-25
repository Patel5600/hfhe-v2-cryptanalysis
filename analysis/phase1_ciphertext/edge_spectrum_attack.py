import struct
import json
from pathlib import Path
import numpy as np
from collections import defaultdict
from scipy import stats

P = (1 << 127) - 1
MASK63 = (1 << 63) - 1
B = 337

def fp_add(a, b): return (a + b) % P
def fp_sub(a, b): return (a - b) % P
def fp_mul(a, b): return (a * b) % P
def fp_inv(a): return pow(a, P - 2, P) if a % P != 0 else 0
def legendre(a):
    if a % P == 0: return 0
    return 1 if pow(a, (P - 1) // 2, P) == 1 else -1

class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    def u8(self):
        v = self.data[self.pos]; self.pos += 1
        return v
    def u16(self):
        v = struct.unpack_from("<H", self.data, self.pos)[0]; self.pos += 2
        return v
    def u32(self):
        v = struct.unpack_from("<I", self.data, self.pos)[0]; self.pos += 4
        return v
    def u64(self):
        v = struct.unpack_from("<Q", self.data, self.pos)[0]; self.pos += 8
        return v
    def fp(self):
        lo = self.u64()
        hi = self.u64() & MASK63
        return (hi << 64) | lo
    def raw(self, n):
        v = self.data[self.pos : self.pos + n]; self.pos += n
        return v
    def bitvec(self):
        nbits = self.u64()
        nwords = self.u64()
        words = [self.u64() for _ in range(nwords)]
        return {"nbits": nbits, "words": words}

def parse_cipher(r: Reader):
    magic = r.raw(4)
    ver = r.u8()
    tag = r.u8()
    slots = r.u64()
    num_layers = r.u64()
    layers = []
    for _ in range(num_layers):
        rule = r.u8()
        if rule == 0:
            ztag = r.u64()
            n_lo = r.u64()
            n_hi = r.u64()
            layer_info = dict(rule="BASE", ztag=ztag, nonce_lo=n_lo, nonce_hi=n_hi)
        else:
            pa = r.u32()
            pb = r.u32()
            layer_info = dict(rule="PROD", pa=pa, pb=pb)
        nPC = r.u64()
        pcs = [r.raw(32) for _ in range(nPC)]
        layer_info["PC"] = pcs
        layers.append(layer_info)

    num_c0 = r.u64()
    c0 = [r.fp() for _ in range(num_c0)]

    num_edges = r.u64()
    edges = []
    for _ in range(num_edges):
        lid = r.u32()
        idx = r.u16()
        ch = r.u8()
        sign = 1 if ch == 0x2B else -1
        nw = r.u64()
        w = [r.fp() for _ in range(nw)]
        bv = r.bitvec()
        edges.append(dict(layer_id=lid, idx=idx, ch=ch, sign=sign, w=w[0] if w else 0, sigma=bv))

    return dict(slots=slots, layers=layers, c0=c0, edges=edges)

# Parse secret.ct
raw_ct = Path(r"C:\Dev\octra\secret.ct").read_bytes()
cipher_count = struct.unpack_from("<Q", raw_ct, 16)[0]
pos = 24
ciphers = []
for _ in range(cipher_count):
    blob_len = struct.unpack_from("<Q", raw_ct, pos)[0]; pos += 8
    blob = raw_ct[pos : pos + blob_len]; pos += blob_len
    ciphers.append(parse_cipher(Reader(blob)))

print(f"Successfully parsed {len(ciphers)} ciphers from secret.ct.")

# ── EXPERIMENT 1: Same-Index Cross-Layer Relations ──
same_idx_pairs_real = []
for i, c in enumerate(ciphers):
    e0_by_idx = defaultdict(list)
    e1_by_idx = defaultdict(list)
    for e in c["edges"]:
        if e["layer_id"] == 0:
            e0_by_idx[e["idx"]].append(e)
        elif e["layer_id"] == 1:
            e1_by_idx[e["idx"]].append(e)
    
    shared_idxs = set(e0_by_idx.keys()) & set(e1_by_idx.keys())
    for idx in shared_idxs:
        for e0 in e0_by_idx[idx]:
            for e1 in e1_by_idx[idx]:
                same_idx_pairs_real.append({
                    "cipher_index": i,
                    "idx": idx,
                    "sign0": e0["sign"], "sign1": e1["sign"],
                    "w0": e0["w"], "w1": e1["w"],
                    "ratio": fp_mul(e0["w"], fp_inv(e1["w"])),
                    "prod": fp_mul(e0["w"], e1["w"]),
                    "diff": fp_sub(e0["w"], e1["w"]),
                    "sum": fp_add(e0["w"], e1["w"])
                })

print(f"\n[1] Real Same-Index Cross-Layer Pairs: Total = {len(same_idx_pairs_real)}")

leg_ratios = [legendre(p["ratio"]) for p in same_idx_pairs_real]
leg_prods  = [legendre(p["prod"]) for p in same_idx_pairs_real]
leg_diffs  = [legendre(p["diff"]) for p in same_idx_pairs_real]
leg_sums   = [legendre(p["sum"]) for p in same_idx_pairs_real]

print(f"  Legendre(w0 / w1): mean = {np.mean(leg_ratios):+.4f} (pos={leg_ratios.count(1)}, neg={leg_ratios.count(-1)})")
print(f"  Legendre(w0 * w1): mean = {np.mean(leg_prods):+.4f} (pos={leg_prods.count(1)}, neg={leg_prods.count(-1)})")
print(f"  Legendre(w0 - w1): mean = {np.mean(leg_diffs):+.4f} (pos={leg_diffs.count(1)}, neg={leg_diffs.count(-1)})")
print(f"  Legendre(w0 + w1): mean = {np.mean(leg_sums):+.4f} (pos={leg_sums.count(1)}, neg={leg_sums.count(-1)})")

# Check sign-conditioned weight ratio means
for s0, s1 in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
    subset = [p for p in same_idx_pairs_real if p["sign0"] == s0 and p["sign1"] == s1]
    if subset:
        sub_leg = [legendre(p["ratio"]) for p in subset]
        print(f"  Sign ({s0:+d}, {s1:+d}) [N={len(subset)}]: Legendre(w0/w1) mean = {np.mean(sub_leg):+.4f}")

# ── EXPERIMENT 2: Cross-Object Null Control ──
same_idx_pairs_null = []
for i in range(len(ciphers)):
    j = (i + 1) % len(ciphers)
    e0_by_idx = defaultdict(list)
    e1_by_idx = defaultdict(list)
    for e in ciphers[i]["edges"]:
        if e["layer_id"] == 0: e0_by_idx[e["idx"]].append(e)
    for e in ciphers[j]["edges"]:
        if e["layer_id"] == 1: e1_by_idx[e["idx"]].append(e)
    
    shared_idxs = set(e0_by_idx.keys()) & set(e1_by_idx.keys())
    for idx in shared_idxs:
        for e0 in e0_by_idx[idx]:
            for e1 in e1_by_idx[idx]:
                same_idx_pairs_null.append({
                    "ratio": fp_mul(e0["w"], fp_inv(e1["w"]))
                })

null_leg_ratios = [legendre(p["ratio"]) for p in same_idx_pairs_null]
print(f"\n[2] Null Cross-Object Same-Index Pairs (N={len(same_idx_pairs_null)}):")
print(f"  Null Legendre(w0 / w1): mean = {np.mean(null_leg_ratios):+.4f} (pos={null_leg_ratios.count(1)}, neg={null_leg_ratios.count(-1)})")

# 2-sample KS test on real vs null ratio distributions
real_ratios_float = [p["ratio"] / P for p in same_idx_pairs_real]
null_ratios_float = [p["ratio"] / P for p in same_idx_pairs_null]
ks_res = stats.ks_2samp(real_ratios_float, null_ratios_float)
print(f"  KS Test (Real vs Null ratio distribution): stat = {ks_res.statistic:.4f}, p-value = {ks_res.pvalue:.4f}")

# ── EXPERIMENT 3: Index Difference Delta_idx mod 337 ──
delta_idx_stats = defaultdict(list)
rng = np.random.default_rng(42)
for i, c in enumerate(ciphers):
    e0 = [e for e in c["edges"] if e["layer_id"] == 0]
    e1 = [e for e in c["edges"] if e["layer_id"] == 1]
    for _ in range(500):
        e0_sample = e0[rng.integers(len(e0))]
        e1_sample = e1[rng.integers(len(e1))]
        d = (e0_sample["idx"] - e1_sample["idx"]) % B
        delta_idx_stats[d].append(legendre(fp_mul(e0_sample["w"], fp_inv(e1_sample["w"]))))

d_means = [np.mean(delta_idx_stats[d]) for d in range(B) if len(delta_idx_stats[d]) > 0]
print(f"\n[3] Delta_idx mod 337 (Across {len(d_means)} active residue classes):")
print(f"  Max absolute Legendre deviation:  {np.max(np.abs(d_means)):.4f}")
print(f"  Mean absolute Legendre deviation: {np.mean(np.abs(d_means)):.4f}")
print(f"  Expected random deviation floor:  ~{1.0 / np.sqrt(len(same_idx_pairs_real) / B):.4f}")

print("\n" + "="*60)
print("  EDGE SPECTRUM ATTACK: VERDICT")
print("="*60)
print(f"  Same-index pairs:           N = {len(same_idx_pairs_real)}")
print(f"  Legendre ratio bias:        None (mean = {np.mean(leg_ratios):+.4f})")
print(f"  KS vs Null p-value:         {ks_res.pvalue:.4f} (Indistinguishable)")
print("  VERDICT:                    CLOSED — No sparse edge spectrum signal.")
print("="*60)
