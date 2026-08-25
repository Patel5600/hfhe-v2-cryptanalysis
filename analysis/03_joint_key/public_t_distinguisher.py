"""Joint-key/public_T experiment scaffold.

Inputs are public per-layer records with fields:
    T, ztag, nonce_lo, nonce_hi, object_id, layer_id

The script deliberately separates the REAL, SHUFFLED, and NULL_B populations.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, stdev
import random

@dataclass(frozen=True)
class LayerRecord:
    T: int
    ztag: int
    nonce_lo: int
    nonce_hi: int
    object_id: int
    layer_id: int


def normalized_hamming_128(a: int, b: int) -> float:
    return ((a ^ b).bit_count() / 128.0)


def pair_features(records: list[LayerRecord]) -> list[float]:
    out = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            out.append(normalized_hamming_128(records[i].T, records[j].T))
    return out


def shuffled(records: list[LayerRecord], rng: random.Random) -> list[LayerRecord]:
    values = [r.T for r in records]
    meta = [(r.ztag, r.nonce_lo, r.nonce_hi, r.object_id, r.layer_id) for r in records]
    rng.shuffle(meta)
    return [LayerRecord(values[i], *meta[i]) for i in range(len(records))]


def summarize(xs: list[float]) -> dict[str, float]:
    return {
        "n": len(xs),
        "mean": mean(xs),
        "std": stdev(xs) if len(xs) > 1 else 0.0,
    }


if __name__ == "__main__":
    print("Load the 44 real layer records, then call pair_features().")
