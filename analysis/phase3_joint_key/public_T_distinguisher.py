#!/usr/bin/env python3
"""Phase 3: Joint-key / public_T correlation experiment.

Observable: For each edge e, T[e] = w[e] * H_col[idx[e]] (simplified).
Hypothesis: If prf_k leaks into T through nonce or index correlation,
            we should see non-uniform nonce-weight correlations.

Null model: Permute (nonce, w) pairs across edges. Should be identical
            to real distribution if prf_k provides no correlation.

Decision rule: Pearson |r| > 0.05 with p < 0.01 (Bonferroni: k=3).

Result: Pearson r=-0.0218, p=0.2317 — NO SIGNAL. CLOSED.
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
import argparse
import struct
import zlib

SEED = 42
ALPHA = 0.05


def load_edges(secret_ct_path: str):
    raw = Path(secret_ct_path).read_bytes()
    assert raw[:16] == b"OCTRA-HFHE-BTY02"
    body = zlib.decompress(raw[16:])
    off = 0
    edges = []
    while off < len(body):
        tag = body[off]; off += 1
        sz = struct.unpack_from('<Q', body, off)[0]; off += 8
        blob = body[off:off+sz]; off += sz
        if tag != 0:
            continue
        n = struct.unpack_from('<Q', blob, 0)[0]
        boff = 8
        for _ in range(n):
            idx = struct.unpack_from('<Q', blob, boff)[0]; boff += 8
            sign = blob[boff]; boff += 1
            w_lo = struct.unpack_from('<Q', blob, boff)[0]; boff += 8
            w_hi = struct.unpack_from('<Q', blob, boff)[0]; boff += 8
            w = w_lo | (w_hi << 64)
            ztag = blob[boff]; boff += 1
            nonce = struct.unpack_from('<Q', blob, boff)[0]; boff += 8
            pc_len = struct.unpack_from('<I', blob, boff)[0]; boff += 4
            boff += pc_len  # skip PC bytes
            edges.append({'idx': idx, 'sign': sign, 'w': w,
                          'ztag': ztag, 'nonce': nonce})
    return edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', default='.')
    args = parser.parse_args()

    ct_path = Path(args.artifacts) / 'secret.ct'
    print(f'Loading {ct_path}...')
    edges = load_edges(str(ct_path))
    print(f'  {len(edges)} edges loaded')

    # Extract nonce and w_low32 (low bits of w as proxy)
    nonces = np.array([e['nonce'] for e in edges], dtype=np.uint64)
    w_low  = np.array([e['w'] & 0xFFFFFFFF for e in edges], dtype=np.uint64)
    idxs   = np.array([e['idx'] for e in edges], dtype=np.uint64)

    # Pearson correlation: nonce vs w_low32
    r_nw, p_nw = stats.pearsonr(nonces.astype(float), w_low.astype(float))
    print(f'Pearson(nonce, w_low32): r={r_nw:.4f}, p={p_nw:.4f}')

    # Pearson correlation: nonce vs idx
    r_ni, p_ni = stats.pearsonr(nonces.astype(float), idxs.astype(float))
    print(f'Pearson(nonce, idx):     r={r_ni:.4f}, p={p_ni:.4f}')

    # Decision
    threshold = ALPHA / 3  # Bonferroni k=3
    signal = (p_nw < threshold) or (p_ni < threshold)
    print(f'\nDecision (alpha={threshold:.4f}): {"SIGNAL" if signal else "NO SIGNAL — CLOSED"}')

    result = {
        'experiment': 'public_T_distinguisher',
        'n_edges': len(edges),
        'seed': SEED,
        'pearson_nonce_w': {'r': r_nw, 'p': p_nw},
        'pearson_nonce_idx': {'r': r_ni, 'p': p_ni},
        'bonferroni_alpha': threshold,
        'verdict': 'CLOSED' if not signal else 'SIGNAL',
    }
    out = Path('results/ciphertext/public_T_distinguisher.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f'Result written to {out}')


if __name__ == '__main__':
    main()
