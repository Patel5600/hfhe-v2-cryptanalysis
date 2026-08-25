"""
parse_secret_ct.py — Experiment 2: Parse secret.ct, extract PC values and edges.

Wire format (from pvac_artifact_serialize.hpp + hfhe_bounty_artifact.cpp):

  secret.ct:
    16 bytes  BUNDLE_MAGIC = "OCTRA-HFHE-BTY02"
    8 bytes   cipher_count (little-endian u64)
    for each cipher:
        8 bytes   blob_len (u64)
        blob_len bytes:
            PVAC_MAGIC (4 bytes = "PVAC")
            version    (1 byte  = 0x03)
            tag        (1 byte  = TAG_CIPHER = 0x01)
            slots      (u64)
            num_layers (u64)
            for each layer:
                rule       (u8: 0=BASE, 1=PROD)
                if BASE:
                    ztag     (u64)
                    nonce_lo (u64)
                    nonce_hi (u64)
                else PROD:
                    pa (u32), pb (u32)
                nPC (u64)
                PC[0..nPC-1]  (each 32 bytes, Ristretto point)
            num_c0 (u64)
            c0[0..num_c0-1]  (each 16 bytes, Fp = (lo u64, hi u64 & MASK63))
            num_edges (u64)
            for each edge:
                layer_id (u32)
                idx      (u16)
                ch       (u8: 0x2B='+', 0x2D='-')
                nw (u64)
                w[0..nw-1]  (each 16 bytes, Fp)
                nbits (u64)
                nwords (u64)
                words[0..nwords-1]  (each u64)   ← sigma BitVec

Note: R_com is NOT serialized (confirmed: write_layer skips it).
"""

import struct
import json
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
SECRET_CT   = REPO_ROOT / "secret.ct"

BUNDLE_MAGIC = b"OCTRA-HFHE-BTY02"
PVAC_MAGIC   = b"PVAC"
VERSION      = 0x03
TAG_CIPHER   = 0x00
SGN_P        = 0x2B  # '+'
SGN_M        = 0x2D  # '-'
MASK63       = (1 << 63) - 1

# ── Reader ────────────────────────────────────────────────────────────────

class Reader:
    def __init__(self, data: bytes):
        self._data = data
        self._pos  = 0

    def remaining(self) -> int:
        return len(self._data) - self._pos

    def _read(self, n: int) -> bytes:
        if self._pos + n > len(self._data):
            raise ValueError(f"truncated: need {n}, have {self.remaining()} at pos {self._pos}")
        chunk = self._data[self._pos: self._pos + n]
        self._pos += n
        return chunk

    def u8(self) -> int:
        return self._read(1)[0]

    def u16(self) -> int:
        return struct.unpack_from("<H", self._read(2))[0]

    def u32(self) -> int:
        return struct.unpack_from("<I", self._read(4))[0]

    def u64(self) -> int:
        return struct.unpack_from("<Q", self._read(8))[0]

    def i32(self) -> int:
        return struct.unpack_from("<i", self._read(4))[0]

    def raw(self, n: int) -> bytes:
        return self._read(n)

    def fp(self):
        lo = self.u64()
        hi = self.u64() & MASK63
        return (lo, hi)

    def ristretto_point(self) -> bytes:
        return self._read(32)

    def bitvec(self):
        nbits  = self.u64()
        nwords = self.u64()
        expected = (nbits + 63) // 64
        if nwords != expected:
            raise ValueError(f"bitvec word count mismatch: {nwords} vs {expected}")
        words = [self.u64() for _ in range(nwords)]
        return {"nbits": nbits, "words": words}

    def pvac_header(self, expected_tag: int):
        magic = self.raw(4)
        if magic != PVAC_MAGIC:
            raise ValueError(f"bad PVAC magic: {magic!r}")
        ver = self.u8()
        if ver != VERSION:
            raise ValueError(f"bad PVAC version: {ver:#x}")
        tag = self.u8()
        if tag != expected_tag:
            raise ValueError(f"wrong tag: {tag:#x} expected {expected_tag:#x}")

    @property
    def pos(self):
        return self._pos


# ── Layer reader ──────────────────────────────────────────────────────────

def read_layer(r: Reader) -> dict:
    rule = r.u8()
    if rule == 0:  # BASE
        ztag     = r.u64()
        nonce_lo = r.u64()
        nonce_hi = r.u64()
        layer = {"rule": "BASE", "ztag": ztag, "nonce_lo": nonce_lo, "nonce_hi": nonce_hi}
    elif rule == 1:  # PROD
        pa = r.u32()
        pb = r.u32()
        layer = {"rule": "PROD", "pa": pa, "pb": pb}
    else:
        raise ValueError(f"unknown rule: {rule}")

    nPC = r.u64()
    PCs = [r.ristretto_point() for _ in range(nPC)]
    layer["PC"] = [pc.hex() for pc in PCs]
    layer["nPC"] = nPC
    return layer


# ── Edge reader ───────────────────────────────────────────────────────────

def read_edge(r: Reader) -> dict:
    layer_id = r.u32()
    idx      = r.u16()
    ch       = r.u8()
    nw       = r.u64()
    weights  = [r.fp() for _ in range(nw)]
    sigma    = r.bitvec()
    return {
        "layer_id": layer_id,
        "idx":      idx,
        "sign":     "+" if ch == SGN_P else "-",
        "w":        [{"lo": w[0], "hi": w[1]} for w in weights],
        "sigma_nbits": sigma["nbits"],
    }


# ── Cipher reader ─────────────────────────────────────────────────────────

def read_cipher(r: Reader) -> dict:
    r.pvac_header(TAG_CIPHER)
    slots   = r.u64()
    nL      = r.u64()
    layers  = [read_layer(r) for _ in range(nL)]
    nc0     = r.u64()
    c0      = [r.fp() for _ in range(nc0)]
    nE      = r.u64()
    edges   = [read_edge(r) for _ in range(nE)]
    return {
        "slots":  slots,
        "layers": layers,
        "c0":     [{"lo": x[0], "hi": x[1]} for x in c0],
        "n_edges": nE,
        "edges":  edges,
    }


# ── Bundle reader ─────────────────────────────────────────────────────────

def read_bundle(path: Path) -> list[dict]:
    data = path.read_bytes()
    print(f"  secret.ct: {len(data):,} bytes")

    if data[:16] != BUNDLE_MAGIC:
        raise ValueError(f"bad bundle magic: {data[:16]!r}")

    pos = 16
    count = struct.unpack_from("<Q", data, pos)[0]
    pos += 8
    print(f"  cipher count: {count}")

    ciphers = []
    for i in range(count):
        blob_len = struct.unpack_from("<Q", data, pos)[0]
        pos += 8
        r = Reader(data[pos: pos + blob_len])
        ct = read_cipher(r)
        ct["cipher_index"] = i
        ciphers.append(ct)
        if r.remaining() != 0:
            raise ValueError(f"cipher {i}: {r.remaining()} trailing bytes")
        pos += blob_len

    if pos != len(data):
        raise ValueError(f"bundle: {len(data)-pos} trailing bytes")

    return ciphers


# ── Analysis ──────────────────────────────────────────────────────────────

def analyze_ciphers(ciphers: list[dict]) -> dict:
    pc_records = []
    edge_summary = []

    for ct in ciphers:
        ci = ct["cipher_index"]
        for li, layer in enumerate(ct["layers"]):
            if layer["rule"] != "BASE":
                continue
            for slot, pc_hex in enumerate(layer["PC"]):
                pc_records.append({
                    "cipher_index": ci,
                    "layer_id":     li,
                    "slot":         slot,
                    "pc_hex":       pc_hex,
                    "ztag":         layer["ztag"],
                    "nonce_lo":     layer["nonce_lo"],
                    "nonce_hi":     layer["nonce_hi"],
                })

        edge_summary.append({
            "cipher_index": ci,
            "n_layers":     len(ct["layers"]),
            "n_edges":      ct["n_edges"],
            "slots":        ct["slots"],
        })

    # PC sanity: all-zeros would mean R_com accidentally ended up there
    zero_pc = sum(1 for r in pc_records if r["pc_hex"] == "00" * 32)
    identity_ristretto = "0000000000000000000000000000000000000000000000000000000000000000"
    # Actual Ristretto identity encodes as all-zeros
    identity_count = sum(1 for r in pc_records if r["pc_hex"] == identity_ristretto)

    # Duplicate PC values
    pc_set = set(r["pc_hex"] for r in pc_records)

    return {
        "n_pc_total":       len(pc_records),
        "n_pc_unique":      len(pc_set),
        "n_zero_pc":        zero_pc,
        "n_identity_pc":    identity_count,
        "edge_summary":     edge_summary,
        "pc_records":       pc_records,
    }


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Experiment 2: Parse secret.ct — extract PC values and edges")
    print("=" * 70)
    print()

    print(f"[1] Reading {SECRET_CT} ...")
    ciphers = read_bundle(SECRET_CT)
    print(f"    Parsed {len(ciphers)} ciphers.")
    print()

    print("[2] Analyzing PC commitments and edge structure ...")
    analysis = analyze_ciphers(ciphers)
    print(f"    Total PC values:    {analysis['n_pc_total']}")
    print(f"    Unique PC values:   {analysis['n_pc_unique']}")
    print(f"    Zero PC values:     {analysis['n_zero_pc']}")
    print(f"    Identity PC values: {analysis['n_identity_pc']}")
    print()

    print("[3] Edge structure summary (first 4 ciphers):")
    for es in analysis["edge_summary"][:4]:
        print(f"    ct{es['cipher_index']:02d}: slots={es['slots']}  "
              f"layers={es['n_layers']}  edges={es['n_edges']}")
    print()

    print("[4] PC value sample (first 6 records):")
    for rec in analysis["pc_records"][:6]:
        print(f"    [{rec['cipher_index']:02d} l{rec['layer_id']} s{rec['slot']}]  "
              f"PC={rec['pc_hex'][:32]}...")
    print()

    print("[5] Cross-referencing PC ztag/nonce against LPN sample headers ...")
    lpn_dir = REPO_ROOT / "lpn_samples"
    import json as _json
    lpn_meta = {}
    for fpath in sorted(lpn_dir.glob("*.jsonl")):
        with open(fpath) as f:
            meta = _json.loads(f.readline())
        key = (meta["cipher_index"], meta["layer_id"])
        lpn_meta[key] = meta

    matches = 0
    mismatches = 0
    for rec in analysis["pc_records"]:
        key = (rec["cipher_index"], rec["layer_id"])
        if key not in lpn_meta:
            continue
        meta = lpn_meta[key]
        ztag_match = rec["ztag"] == meta["seed_ztag"]
        nlo_match  = rec["nonce_lo"] == int(meta["nonce_lo_hex"], 16)
        nhi_match  = rec["nonce_hi"] == int(meta["nonce_hi_hex"], 16)
        if ztag_match and nlo_match and nhi_match:
            matches += 1
        else:
            mismatches += 1
            print(f"    MISMATCH at ct{rec['cipher_index']} l{rec['layer_id']}")

    print(f"    Nonce/ztag cross-check: {matches} matches, {mismatches} mismatches")
    print()

    # Save results
    out_path = Path(__file__).parent / "phase3_pc_data.json"
    save_data = {
        "n_ciphers": len(ciphers),
        "analysis": {
            "n_pc_total":    analysis["n_pc_total"],
            "n_pc_unique":   analysis["n_pc_unique"],
            "n_zero_pc":     analysis["n_zero_pc"],
            "n_identity_pc": analysis["n_identity_pc"],
        },
        "pc_records": analysis["pc_records"],
        "edge_summary": analysis["edge_summary"],
    }
    with open(out_path, "w") as f:
        _json.dump(save_data, f, indent=2)
    print(f"  PC data written to: {out_path}")


if __name__ == "__main__":
    main()
