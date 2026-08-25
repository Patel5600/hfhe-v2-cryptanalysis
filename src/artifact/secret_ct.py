"""Parse secret.ct bundle from the HFHE v2 challenge.

Usage:
    from src.artifact.secret_ct import parse_secret_ct
    layers = parse_secret_ct("path/to/secret.ct")
"""
import struct, zlib
from pathlib import Path
from typing import Any

MAGIC = b"OCTRA-HFHE-BTY02"
TAG_CIPHER = 0
TAG_PUBKEY = 1
TAG_SECKEY = 2


def _read_u8(buf, off):  return struct.unpack_from("B", buf, off)[0], off + 1
def _read_u32(buf, off): return struct.unpack_from("<I", buf, off)[0], off + 4
def _read_u64(buf, off): return struct.unpack_from("<Q", buf, off)[0], off + 8


def parse_secret_ct(path: str | Path) -> list[dict[str, Any]]:
    """Return list of layer dicts parsed from secret.ct."""
    raw = Path(path).read_bytes()
    # Strip magic + decompress
    assert raw[:16] == MAGIC, "Bad magic"
    data = zlib.decompress(raw[16:])
    off = 0
    layers: list[dict] = []
    while off < len(data):
        tag, off = _read_u8(data, off)
        size, off = _read_u64(data, off)
        blob = data[off: off + size]
        off += size
        if tag == TAG_CIPHER:
            layers.append(_parse_layer(blob))
    return layers


def _parse_layer(blob: bytes) -> dict[str, Any]:
    """Parse a single ciphertext layer blob into a dict of edge arrays."""
    off = 0
    n_edges, off = _read_u64(blob, off)
    edges = []
    for _ in range(n_edges):
        idx,  off = _read_u64(blob, off)
        sign, off = _read_u8(blob,  off)
        w_lo, off = _read_u64(blob, off)
        w_hi, off = _read_u64(blob, off)
        w = w_lo | (w_hi << 64)
        ztag, off = _read_u8(blob, off)
        nonce, off = _read_u64(blob, off)
        pc_len, off = _read_u32(blob, off)
        pc = blob[off: off + pc_len]; off += pc_len
        edges.append(dict(idx=idx, sign=sign, w=w, ztag=ztag, nonce=nonce, pc=pc))
    return {"n_edges": n_edges, "edges": edges}
