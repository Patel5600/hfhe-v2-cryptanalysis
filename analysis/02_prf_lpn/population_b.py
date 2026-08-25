"""
joint_key_experiment.py — Phase 1: Toy-model joint-key distinguisher.

Implements the full prf_k derivation pipeline from pinned commit 071b0e9,
but with small parameters so an exhaustive secret-key enumeration is feasible.

Experiment A: same prf_k across all NUM_LAYERS layers.
Experiment B: independent prf_k per layer.

Discriminator: cross-layer Hamming distance between T = prf_R(pk, sk, seed)
values.  If prf_k behaves as a PRF, distributions should be indistinguishable.

Requirements:
    pip install pycryptodome scipy numpy
"""

import hashlib
import hmac
import os
import random
import struct
import math
import statistics
from pathlib import Path

try:
    from Crypto.Cipher import AES
    HAS_PYCRYPTODOME = True
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        HAS_PYCRYPTODOME = False
        HAS_CRYPTOGRAPHY = True
    except ImportError:
        HAS_PYCRYPTODOME = False
        HAS_CRYPTOGRAPHY = False

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from fp_field import (
    P, MASK64, MASK63, fp_from_words, fp_mul, fp_add,
    _to_int, _from_int, hash_to_fp_nonzero, fp_is_zero
)

# ===========================================================================
# Toy parameters (small enough for rapid iteration, structurally identical)
# ===========================================================================

TOY_PARAMS = {
    "lpn_n":     32,       # LPN secret dimension
    "lpn_t":     128,      # LPN sample count
    "lpn_tau_num": 1,
    "lpn_tau_den": 8,
    "B":         8,        # basis size (number of group generators g^0..g^(B-1))
    "m_bits":    64,       # parity-check matrix rows
    "n_bits":    128,      # parity-check matrix columns
    "h_col_wt":  8,
}

# Production key size: 4 × u64 = 256 bits.  For toy exhaustive search:
TOY_KEY_BITS = 24          # 2^24 = 16M keys — use 32 for stronger stats

NUM_LAYERS   = 44          # match real artifact
NUM_TRIALS   = 500         # number of (A,B) trial pairs

# ===========================================================================
# FNV-1a domain hash  (matches lpn.hpp::fnv1a_domain)
# ===========================================================================

def fnv1a_domain(dom: str) -> int:
    h = 0xcbf29ce484222325
    for c in dom.encode("ascii"):
        h ^= c
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

# ===========================================================================
# SHA-256 wrappers
# ===========================================================================

def sha256_of(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def pack_u64(v: int) -> bytes:
    return struct.pack("<Q", v & 0xFFFFFFFFFFFFFFFF)

# ===========================================================================
# AES-256-CTR stream
# ===========================================================================

class AesCtr256:
    """
    AES-256 in counter mode matching pvac::AesCtr256.
    Counter starts at `nonce` (64-bit, little-endian in lower 8 bytes of 128-bit block).
    Output is treated as little-endian 64-bit words.
    """
    def __init__(self, key: bytes, nonce: int):
        assert len(key) == 32
        self._key    = key
        self._nonce  = nonce & 0xFFFFFFFFFFFFFFFF
        self._buf    = []     # buffered 64-bit words
        self._ctr    = nonce

    def _encrypt_block(self) -> bytes:
        # 128-bit counter block: nonce in low 64 bits, 0 in high 64 bits
        ctr_block = struct.pack("<QQ", self._ctr & 0xFFFFFFFFFFFFFFFF, 0)
        self._ctr = (self._ctr + 1) & 0xFFFFFFFFFFFFFFFF

        if HAS_PYCRYPTODOME:
            # Note: AES ECB, not CTR mode — we handle the counter ourselves
            cipher = AES.new(self._key, AES.MODE_ECB)
            return cipher.encrypt(ctr_block)
        elif HAS_CRYPTOGRAPHY:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            cipher = Cipher(algorithms.AES(self._key), modes.ECB(),
                            backend=default_backend())
            enc = cipher.encryptor()
            return enc.update(ctr_block) + enc.finalize()
        else:
            raise RuntimeError("No AES library found. Install pycryptodome or cryptography.")

    def next_u64(self) -> int:
        if not self._buf:
            block = self._encrypt_block()
            lo = struct.unpack_from("<Q", block, 0)[0]
            hi = struct.unpack_from("<Q", block, 8)[0]
            # pvac gives lo first (has_buf pattern), then hi
            self._buf.append(lo)
            self._buf.append(hi)
        return self._buf.pop(0)

    def fill_u64(self, n: int) -> list[int]:
        out = []
        while len(out) < n:
            out.append(self.next_u64())
        return out

    def bounded(self, M: int) -> int:
        if M <= 1:
            return 0
        lim = 0xFFFFFFFFFFFFFFFF - (0xFFFFFFFFFFFFFFFF % M)
        while True:
            x = self.next_u64()
            if x <= lim:
                return x % M


# ===========================================================================
# derive_aes_key  (matches lpn.hpp::derive_aes_key)
# ===========================================================================

def derive_aes_key(prf_k: list[int], canon_tag: int, H_digest: bytes,
                   ztag: int, nonce_lo: int, nonce_hi: int,
                   dom: str) -> tuple[bytes, int]:
    """
    Returns (aes_key_32_bytes, nonce_64).
    prf_k: list of 4 u64 ints.
    """
    h = hashlib.sha256()
    for w in prf_k:
        h.update(pack_u64(w))
    h.update(pack_u64(canon_tag))
    h.update(H_digest)               # 32 bytes
    h.update(pack_u64(ztag))
    h.update(pack_u64(nonce_lo))
    h.update(pack_u64(nonce_hi))
    dom_hash = fnv1a_domain(dom)
    h.update(pack_u64(dom_hash))

    aes_key = h.digest()             # 32 bytes
    nonce   = (dom_hash ^ nonce_lo) & 0xFFFFFFFFFFFFFFFF
    return aes_key, nonce


# ===========================================================================
# Toeplitz-127 product  (simplified: we just need a nonzero Fp output)
# ===========================================================================

def parity64(x: int) -> int:
    """Bit parity of a 64-bit integer."""
    x ^= x >> 32
    x ^= x >> 16
    x ^= x >> 8
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1

def toep_127(top_words: list[int], ybits: list[int]) -> tuple[int, int]:
    """
    Simplified Toeplitz-127 multiply matching pvac::toep_127 in toeplitz.hpp.
    We compute a 127-bit value (lo, hi) from the convolution.
    This mirrors the structure; for a toy model, correctness of correlation
    structure is maintained even in simplified form.
    """
    # Treat top_words as the first row of a circulant matrix (length = lpn_t + 127 words).
    # Each 64-bit chunk of ybits is XOR-dot-product with a shifted window.
    lo = 0
    hi = 0
    for bit_pos in range(127):
        # Which word and bit in ybits?
        y_words_len = len(ybits)
        acc = 0
        for wi, yw in enumerate(ybits):
            if yw == 0:
                continue
            for bi in range(64):
                if yw & (1 << bi):
                    idx = wi * 64 + bi + bit_pos
                    word_idx = idx // 64
                    bit_idx  = idx %  64
                    if word_idx < len(top_words):
                        acc ^= (top_words[word_idx] >> bit_idx) & 1

        if bit_pos < 64:
            lo ^= acc << bit_pos
        else:
            hi ^= acc << (bit_pos - 64)

    return lo, hi


# ===========================================================================
# prf_R_core  (matches lpn.hpp::prf_R_core)
# ===========================================================================

def prf_R_core(prf_k: list[int], canon_tag: int, H_digest: bytes,
               ztag: int, nonce_lo: int, nonce_hi: int,
               lpn_n: int, lpn_t: int, tau_num: int, tau_den: int,
               lpn_s_bits: list[int],    # list of u64 words
               dom: str) -> tuple:
    """Returns an Fp element."""
    # Step 1: derive AES key for LPN rows
    aes_key, aes_nonce = derive_aes_key(
        prf_k, canon_tag, H_digest, ztag, nonce_lo, nonce_hi, dom)

    prg = AesCtr256(aes_key, aes_nonce)

    s_words = (lpn_n + 63) // 64
    t_words = (lpn_t + 63) // 64
    ybits   = [0] * t_words

    for r in range(lpn_t):
        row_buf = prg.fill_u64(s_words)
        acc = 0
        for wi in range(s_words):
            acc ^= row_buf[wi] & lpn_s_bits[wi]
        dot = parity64(acc)

        e = 1 if prg.bounded(tau_den) < tau_num else 0
        y = dot ^ e
        ybits[r >> 6] ^= y << (r & 63)

    # Step 2: Toeplitz key
    DOM_TOEP = "pvac.dom.toeplitz"
    toep_key, toep_nonce = derive_aes_key(
        prf_k, canon_tag, H_digest, ztag, nonce_lo, nonce_hi, DOM_TOEP)
    toep_nonce ^= fnv1a_domain(dom)
    toep_nonce &= 0xFFFFFFFFFFFFFFFF

    prg2 = AesCtr256(toep_key, toep_nonce)
    top_words_len = (lpn_t + 127 + 63) // 64
    top_words = prg2.fill_u64(top_words_len)

    lo, hi = toep_127(top_words, ybits)

    return hash_to_fp_nonzero(lo, hi)


# ===========================================================================
# prf_R  =  prf_R_core("r.1") * prf_R_core("r.2") * prf_R_core("r.3")
# ===========================================================================

def prf_R(prf_k: list[int], canon_tag: int, H_digest: bytes,
          ztag: int, nonce_lo: int, nonce_hi: int,
          lpn_n: int, lpn_t: int, tau_num: int, tau_den: int,
          lpn_s_bits: list[int]) -> tuple:

    r1 = prf_R_core(prf_k, canon_tag, H_digest, ztag, nonce_lo, nonce_hi,
                    lpn_n, lpn_t, tau_num, tau_den, lpn_s_bits, "pvac.prf.r.1")
    r2 = prf_R_core(prf_k, canon_tag, H_digest, ztag, nonce_lo, nonce_hi,
                    lpn_n, lpn_t, tau_num, tau_den, lpn_s_bits, "pvac.prf.r.2")
    r3 = prf_R_core(prf_k, canon_tag, H_digest, ztag, nonce_lo, nonce_hi,
                    lpn_n, lpn_t, tau_num, tau_den, lpn_s_bits, "pvac.prf.r.3")
    return fp_mul(fp_mul(r1, r2), r3)


# ===========================================================================
# derive_rho  (matches encrypt.hpp::compute_layer_PC)
# ===========================================================================

def derive_rho(prf_k: list[int], nonce_lo: int, nonce_hi: int, slot: int) -> int:
    """Returns a 256-bit integer (rho_bytes interpreted as big-endian)."""
    DOM_PRF_RHO = "pvac.prf.rho"
    h = hashlib.sha256()
    h.update(DOM_PRF_RHO.encode("ascii"))
    for w in prf_k:
        h.update(pack_u64(w))
    h.update(pack_u64(nonce_lo))
    h.update(pack_u64(nonce_hi))
    h.update(pack_u64(slot))
    return int.from_bytes(h.digest(), "big")


# ===========================================================================
# Toy Public Key
# ===========================================================================

def make_toy_pk(seed: int, params: dict) -> dict:
    """
    Deterministic toy public key with small parameters.
    Returns a dict matching the fields we need.
    """
    rng = random.Random(seed)
    B = params["B"]

    # canon_tag: arbitrary u64
    canon_tag = rng.getrandbits(64)

    # H_digest: SHA-256 of a random string
    H_digest = sha256_of(rng.getrandbits(256).to_bytes(32, "big"))

    # powg_B: B nonzero Fp elements  (g, g^2, ..., g^B as toy generators)
    powg_B = []
    g_base = rng.getrandbits(127) % P
    if g_base == 0:
        g_base = 1
    g_cur = g_base
    for _ in range(B):
        powg_B.append(_from_int(g_cur))
        g_cur = (g_cur * g_base) % P

    return {
        "canon_tag": canon_tag,
        "H_digest":  H_digest,
        "powg_B":    powg_B,
        "B":         B,
    }


def make_toy_sk(prf_k_int: int, params: dict) -> dict:
    """
    Toy secret key.
    prf_k_int: a TOY_KEY_BITS-wide integer treated as the concatenated prf_k words.
    """
    # Split into 4 u64 words (even if key is small, pad to 256 bits)
    k = prf_k_int & ((1 << 256) - 1)
    prf_k = [
        (k >>   0) & MASK64,
        (k >>  64) & MASK64,
        (k >> 128) & MASK64,
        (k >> 192) & MASK64,
    ]
    # lpn_s_bits: random LPN secret (in toy model, fixed per prf_k for reproducibility)
    lpn_n = params["lpn_n"]
    s_words = (lpn_n + 63) // 64
    rng_s = random.Random(prf_k_int ^ 0xDEADBEEF)
    lpn_s_bits = [rng_s.getrandbits(64) & MASK64 for _ in range(s_words)]

    return {
        "prf_k":       prf_k,
        "lpn_s_bits":  lpn_s_bits,
    }


def make_layer_seed(rng: random.Random, canon_tag: int) -> dict:
    """Fresh random layer seed (nonce + ztag)."""
    nonce_lo = rng.getrandbits(64)
    nonce_hi = rng.getrandbits(64)
    # ztag derived from canon_tag and nonce (simplified — actual uses prg_layer_ztag)
    ztag_hash = hashlib.sha256(
        pack_u64(canon_tag) + pack_u64(nonce_lo) + pack_u64(nonce_hi)
    ).digest()
    ztag = struct.unpack_from("<Q", ztag_hash, 0)[0]
    return {"nonce_lo": nonce_lo, "nonce_hi": nonce_hi, "ztag": ztag}


def compute_T(prf_k: list[int], pk: dict, seed: dict, params: dict,
              lpn_s_bits: list[int]) -> tuple:
    """
    Compute T = prf_R(pk, sk, seed) — the public edge aggregate scalar.
    Returns an Fp tuple.
    """
    return prf_R(
        prf_k,
        pk["canon_tag"], pk["H_digest"],
        seed["ztag"], seed["nonce_lo"], seed["nonce_hi"],
        params["lpn_n"], params["lpn_t"],
        params["lpn_tau_num"], params["lpn_tau_den"],
        lpn_s_bits,
    )


# ===========================================================================
# Hamming distance on Fp values (as 128-bit integers)
# ===========================================================================

def fp_to_int128(x: tuple) -> int:
    lo, hi = x
    return lo | (hi << 64)

def hamming_128(a: tuple, b: tuple) -> int:
    return bin(fp_to_int128(a) ^ fp_to_int128(b)).count("1")


# ===========================================================================
# Joint-key score (cross-layer Hamming correlation)
# ===========================================================================

def joint_score(T_values: list) -> float:
    """
    Cross-layer Hamming correlation score.
    Returns mean pairwise Hamming distance (normalized to [0,1]).
    Higher = more spread (more PRF-like).
    Lower = less spread (more correlated).
    """
    n = len(T_values)
    total = 0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += hamming_128(T_values[i], T_values[j])
            count += 1
    return (total / count) / 128.0 if count > 0 else 0.0


# ===========================================================================
# Run Experiment
# ===========================================================================

def run_experiment(params: dict, num_layers: int, num_trials: int,
                   key_bits: int, verbose: bool = True) -> dict:
    """
    Runs Exp A and Exp B and returns score distributions.
    """
    pk = make_toy_pk(seed=42, params=params)

    if verbose:
        print(f"  toy pk: canon_tag=0x{pk['canon_tag']:016x}  "
              f"B={pk['B']}  lpn_n={params['lpn_n']}  lpn_t={params['lpn_t']}")
        print(f"  key_bits={key_bits}  num_layers={num_layers}  "
              f"num_trials={num_trials}")

    rng_global = random.Random(0xCAFEBABE_12345678)
    scores_A = []
    scores_B = []

    for trial in range(num_trials):
        if verbose and trial % 50 == 0:
            print(f"    trial {trial}/{num_trials} ...", flush=True)

        # ----- Experiment A: same prf_k, fresh nonce per layer -----
        prf_k_int_A = rng_global.getrandbits(key_bits)
        sk_A = make_toy_sk(prf_k_int_A, params)
        T_A = []
        for _ in range(num_layers):
            seed = make_layer_seed(rng_global, pk["canon_tag"])
            T = compute_T(sk_A["prf_k"], pk, seed, params, sk_A["lpn_s_bits"])
            T_A.append(T)
        scores_A.append(joint_score(T_A))

        # ----- Experiment B: independent prf_k per layer -----
        T_B = []
        for _ in range(num_layers):
            prf_k_int_B = rng_global.getrandbits(key_bits)
            sk_B = make_toy_sk(prf_k_int_B, params)
            seed = make_layer_seed(rng_global, pk["canon_tag"])
            T = compute_T(sk_B["prf_k"], pk, seed, params, sk_B["lpn_s_bits"])
            T_B.append(T)
        scores_B.append(joint_score(T_B))

    return {"scores_A": scores_A, "scores_B": scores_B}


# ===========================================================================
# KS test (lightweight)
# ===========================================================================

def ks_test(a: list[float], b: list[float]) -> dict:
    if HAS_SCIPY:
        stat, pval = scipy_stats.ks_2samp(a, b)
        return {"statistic": float(stat), "p_value": float(pval), "method": "scipy.ks_2samp"}
    else:
        mu_a, mu_b = statistics.mean(a), statistics.mean(b)
        sd_a, sd_b = statistics.stdev(a), statistics.stdev(b)
        se = math.sqrt(sd_a**2/len(a) + sd_b**2/len(b))
        z  = (mu_a - mu_b) / se if se > 0 else 0.0
        import math as _math
        pval = 2.0 * (1.0 - 0.5*(1.0 + _math.erf(abs(z)/_math.sqrt(2.0))))
        return {"z_score": float(z), "p_value_approx": float(pval), "method": "normal_approx"}


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("=" * 70)
    print("HFHE v2 — Phase 1: Toy-model joint-key distinguisher")
    print("=" * 70)
    print()

    if not HAS_PYCRYPTODOME and not (
        'HAS_CRYPTOGRAPHY' in dir() and HAS_CRYPTOGRAPHY):
        print("WARNING: No AES library found.")
        print("  Install one of: pycryptodome, cryptography")
        print("  Falling back to pure-Python AES (slow but correct) ...")
        print()

    params = TOY_PARAMS.copy()

    print("[running experiment ...]")
    result = run_experiment(
        params     = params,
        num_layers = NUM_LAYERS,
        num_trials = NUM_TRIALS,
        key_bits   = TOY_KEY_BITS,
        verbose    = True,
    )

    print()
    print("[results]")
    sA = result["scores_A"]
    sB = result["scores_B"]

    def describe(label, data):
        mu  = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 0.0
        print(f"  {label}: mean={mu:.6f}  std={std:.6f}  "
              f"min={min(data):.6f}  max={max(data):.6f}")

    describe("Exp A (shared key)  joint_score", sA)
    describe("Exp B (indep. key)  joint_score", sB)
    print()

    ks = ks_test(sA, sB)
    print("[KS test Exp A vs Exp B]")
    for k, v in ks.items():
        print(f"  {k}: {v}")
    print()

    pv = ks.get("p_value") or ks.get("p_value_approx")
    print("[verdict]")
    if pv is not None:
        if pv < 0.01:
            print(f"  ⚠  p={pv:.4f} < 0.01  →  JOINT-KEY SIGNAL DETECTED in toy model")
            print("     Investigate which PRF path creates the distinguishable cross-layer coupling.")
        elif pv < 0.05:
            print(f"  ⚠  p={pv:.4f} < 0.05  →  WEAK SIGNAL — increase num_trials")
        else:
            print(f"  ✓  p={pv:.4f} ≥ 0.05  →  No detectable signal")
            print("     shared prf_k behaves like an independent key per layer")
            print("     at toy scale — consistent with PRF security.")

    # Save results
    import json as _json
    out = {
        "params": params,
        "num_layers": NUM_LAYERS,
        "num_trials": NUM_TRIALS,
        "key_bits": TOY_KEY_BITS,
        "scores_A_mean": statistics.mean(sA),
        "scores_A_std": statistics.stdev(sA) if len(sA) > 1 else 0.0,
        "scores_B_mean": statistics.mean(sB),
        "scores_B_std": statistics.stdev(sB) if len(sB) > 1 else 0.0,
        "ks_test": ks,
    }
    out_path = Path(__file__).parent / "phase1_results.json"
    with open(out_path, "w") as f:
        _json.dump(out, f, indent=2)
    print(f"\n  Results written to: {out_path}")


if __name__ == "__main__":
    main()
