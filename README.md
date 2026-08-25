# HFHE v2 — Cryptanalytic Investigation & Forensic Research Archive

> **Summary:** No practical exploit or private-key recovery was identified across the tested attack surface. This is a **negative cryptanalytic result**, not a proof of security.

This repository documents the exhaustive cryptanalytic investigation of the [HFHE v2 challenge](https://github.com/octra-labs/hfhe-challenge) published by Octra Labs, pinned against `octra-labs/pvac_hfhe_cpp` commit [`071b0e909c119de815e284b347c4bd979cb59ef3`](https://github.com/octra-labs/pvac_hfhe_cpp/commit/071b0e909c119de815e284b347c4bd979cb59ef3).

---

## 1. System Parameters & Cryptographic Primitives

| Parameter | Symbol | Value | Field / Domain | Description |
|---|---|---|---|---|
| Scalar Field Prime | $p$ | $2^{127} - 1$ | $\mathbb{F}_p$ | Mersenne prime |
| Ristretto Scalar Order | $\ell$ | $2^{252} + 277423...$ | $\mathbb{Z}/\ell\mathbb{Z}$ | Group order for Pedersen commitment |
| LPN Dimension | $n$ | 4,096 | $\mathbb{F}_2^n$ | Secret vector length |
| LPN Sample Count | $m$ | 16,384 / instance | $\mathbb{F}_2^m$ | Sample matrix height |
| LPN Instances | - | 44 | - | 720,896 total LPN samples |
| LPN Error Rate | $\tau$ | $1/8 = 0.125$ | $\mathbb{Q}$ | Bernoulli noise rate |
| Ciphertexts | $N_{ct}$ | 22 | - | Objects in `secret.ct` |
| Base Layers per CT | - | 2 | - | $T_0$ (layer 0) and $T_1$ (layer 1) |
| Edges per Layer | - | 1,829 | - | Average edge tuples |
| Parity Matrix $H$ | - | $8192 \times 16384$ | $\mathbb{F}_2$ | Full rank 8192 parity check matrix |
| powg Base Order | $B$ | 337 | $\mathbb{Z}$ | Cyclic group base order ($g^B = 1$) |

---

## 2. Core Mathematical Structure

### Wrapped Ciphertext Masking
For plaintext vector $m \in \mathbb{F}_p^n$ and fresh ephemeral vector $v \in_R \mathbb{F}_p^n$:
$$T_0 = R_0 \cdot (v + m) \pmod p$$
$$T_1 = -R_1 \cdot m \pmod p$$
Defining the ratio $\lambda = R_0 \cdot R_1^{-1} \pmod p$:
$$T_0 + \lambda T_1 = R_0 v \pmod p$$

### Cross-Field Inversion Mismatch
In $\mathbb{F}_p$, $R \cdot (R^{-1} \bmod p) = 1 + k \cdot p$ in $\mathbb{Z}$.
When embedded into the Ristretto scalar ring $\mathbb{Z}/\ell\mathbb{Z}$ via `sc_from_fp`:
$$(R \cdot (R^{-1} \bmod p)) \bmod \ell = (1 + k \cdot p) \bmod \ell \not\equiv 1 \pmod \ell$$
This mathematically prevents transferring field inverses across the commitment boundary (0 cancellations in 100,000 empirical trials).

---

## 3. Investigation Phases & Scoreboard

All 26 tested attack branches produced null results across the public attack surface:

| Phase | Target Surface | Key Method / Hypothesis | Result / Statistic | Status |
|---|---|---|---|---|
| **Phase 0** | Artifact Verification | Binary deserialization & SHA256 digest validation | Exact byte matches on $H$, 22 CTs | **CLOSED** |
| **Phase 1** | Ciphertext / Graph | Weight collision & Fisher-Yates CSPRNG shuffle | $\chi^2=101.4$ ($p=0.41$), zero collisions | **CLOSED** |
| **Phase 2** | PRF / LPN Generation | Cross-layer $(w_0, w_1)$ correlation (Population B null) | KS stat=0.0263 ($p=0.523$) | **CLOSED** |
| **Phase 3** | Joint Key / Public $T$ | Nonce vs $w$ low-bits correlation | Pearson $r=-0.0218$ ($p=0.232$) | **CLOSED** |
| **Phase 4** | Public Key Structure | $H$ matrix GF(2) rank & $powg_B$ cyclic DLP | Rank 8192/8192, $B=ord(g) \implies g^B=1$ | **CLOSED** |
| **Phase 5** | Pedersen Commitments | Point distribution & $\mathbb{F}_p \to \mathbb{Z}/\ell\mathbb{Z}$ cross-field cancel | KS $p=0.196$, 0/100,000 cancellations | **CLOSED** |
| **Phase 6** | Wrapped Ratio Recovery | Legendre $\left(\frac{-T_0 T_1}{p}\right)$, sign agreement, toy recovery | $\chi^2=1.34$ ($p=0.246$), Rate=0.500 | **CLOSED** |
| **Phase 7** | LPN Hard Core | Generic Information Set Decoding (BJMM) & BKW bounds | Work factor $> 2^{200}$, Samples $\gg 2^{20}$ | **ASSESSED** |

> **Definition:** **CLOSED** means the tested hypothesis produced no reproducible exploitable signal. It does *not* imply a formal mathematical proof of impossibility.

---

## 4. Repository Structure

```
hfhe-v2-cryptanalysis/
├── docs/                      — Comprehensive theory, system model, attack trees, and catalogs
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_THREAT_MODEL.md
│   ├── 02_SYSTEM_MODEL.md
│   ├── 03_FULL_MATHEMATICAL_MODEL.md
│   ├── 04_ATTACK_TREE.md
│   ├── 05_METHODOLOGY.md
│   ├── 06_STATISTICAL_METHODS.md
│   ├── 07_LIMITATIONS.md
│   ├── 08_FINAL_CONCLUSION.md
│   ├── DETAILED_EXPERIMENT_CATALOG.md
│   ├── SOURCE_TRACE.md
│   ├── mathematics/          — Mathematical derivations (field, scalar, wrapped, prf, lpn, H, etc.)
│   └── theory/               — Theoretical rationale & negative result proofs
├── analysis/                  — Modular Python experiment suites (phases 0 through 7)
├── cpp/                       — Reference C++ tools, parsers, and statistical verification binaries
│   ├── common/               — Fp field arithmetic (128-bit) and I/O
│   ├── artifact/             — High-performance artifact deserializers
│   ├── experiments/          — C++ test suites (cross-field, weight collision, BKW bounds)
│   └── reference/            — Interface traces to pinned 071b0e9 commit
├── scripts/                   — Shell runners for building C++ tools and running phase experiments
├── terminal/                  — Exact command transcripts and forensic terminal history
├── transcripts/               — Machine-readable execution logs per phase
├── research_journal/          — Chronological research notes (entries 000 through 017)
├── results/                   — Machine-readable JSON outputs from all experimental executions
├── figures/                   — Publication plots (attack surface, PRF null, PC distribution, ratio)
├── tables/                    — Detailed CSV summary tables
├── provenance/                — Cryptographic hashes, source commit pin, environment details, and commands
└── src/                       — Core Python cryptanalytic library
```

---

## 5. Artifact Provenance

| Artifact | SHA-256 Digest | Size (bytes) |
|---|---|---|
| `secret.ct` | `5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab` | 1,963,107 |
| `pk.bin` | `1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410` | 3,042,901 |

Source implementation pinned at: `071b0e909c119de815e284b347c4bd979cb59ef3` (2026-07-09).

---

## 6. Quick Start & Reproduction

```bash
# Clone repository
git clone https://github.com/Patel5600/hfhe-v2-cryptanalysis.git
cd hfhe-v2-cryptanalysis

# Install dependencies
pip install -r requirements.txt

# Run Python experiment reproducer
python experiments/reproduce/run_all.py --artifacts /path/to/challenge/artifacts

# (Optional) Build and run C++ verification tools
bash scripts/build.sh
./bin/cross_field_test 100000
```

---

## 7. License & Security Policy

- **License:** MIT — see [`LICENSE`](LICENSE).
- **Security Policy:** See [`SECURITY.md`](SECURITY.md).
- **Citation:** See [`CITATION.cff`](CITATION.cff).\n