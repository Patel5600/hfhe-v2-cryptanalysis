# Differential Archaeology: Evolution from Bounty 1 to Bounty 2, Bounty 3, and Challenge v2

## 1. Executive Summary
By dissecting the historical bounty datasets in `pvac_hfhe_cpp` (`bounty_data`, `bounty2_data`, `bounty3_data`), we trace the exact architectural evolution, failure modes, and designer patches leading to the live Challenge v2 (`071b0e9`).

---

## 2. Bounty Evolution Matrix

| Challenge | Target Payload | Edge Count / Cipher | Noise Entropy | Known Failure Mode / Root Cause | Designer Patch in Next Version |
|---|---|---|---|---|---|
| **Bounty 1** (`bounty_data`) | `seed.ct` (12-word mnemonic) | ~200 edges | 112 bits | **PRF Delta Gap:** Small security gap in `prf_delta` allowed hypergraph syndrome solving. | Increased delta noise entropy & tuple fraction. |
| **Bounty 2** (`bounty2_data`) | `a.ct` ($a=674892...$), `b.ct` ($b=478297...$) | **40 edges** (Depth 0) | 120 bits | **Sparse Under-Saturation & R² Leak:** At depth 0 (40 edges), delta tuples under-saturated the 337-element basis; homomorphic addition (`sum.ct`) exposed $R^2$ cross-terms. | Increased depth scaling (`depth_hint >= 2`), dense edge emitter, fixed `bounty_r2_attack`. |
| **Bounty 3** (`bounty3_data`) | `seed.ct` (15k USD / 60k OCT) | ~800 edges | 120 bits | **R_com Offline Oracle:** Serialized $R_{\text{com}} = g^R \pmod p$ allowed dictionary plaintext verification. | **v2 Patch:** Completely stripped $R_{\text{com}}$ from wire format. |
| **Challenge v2** (`secret.ct`) | `secret.ct` (500k OCT / $1M) | **3,658 edges** (Depth 2..22) | **128 bits** | **Current State:** Dense CSPRNG edge emitter, 128-bit noise entropy, $R_{\text{com}}$ removed, 44 LPN samples. | Evaluated in this repository. |

---

## 3. Laboratory Dissection of Bounty 2 (`bounty2_data`)
In our C++ laboratory (`bounty2_archaeology.cpp`), loading `bounty2_data/sk.bin` against `a.ct` and `b.ct` verified:
- In Bounty 2, `enc_value(pk, sk, v)` at depth 0 produced **only 40 edges total** across 2 layers.
- In Challenge v2, `enc_text(pk, sk, v)` applies `depth_hint >= 2`, producing **3,658 edges per cipher** (a 91x increase in edge density).
- The sparse algebraic system of Bounty 2 (40 equations over $\mathbb{F}_p$) is fully saturated in v2 ($3,658$ dense edges with Fisher-Yates shuffle).

---

## 4. Synthesis & Attack Surface Implication
The historical vulnerability lineage demonstrates that every past break of this scheme relied on:
1. **Under-saturated edge counts** (40 edges in Bounty 2),
2. **Offline verification oracles** ($R_{\text{com}}$ in v1 / Bounty 3), or
3. **Multi-slot SIMD ratio leakage** ($S \ge 2$ in `test_n2_ratio`).

In Challenge v2 (`071b0e9`), all three historical prerequisites have been systematically remediated:
- Edge density is expanded by 91x (3,658 edges / cipher).
- $R_{\text{com}}$ is absent from `secret.ct`.
- The encoding is single-slot scalar ($S=1$).
