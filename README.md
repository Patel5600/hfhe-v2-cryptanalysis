# HFHE v2 — Cryptanalytic Investigation & Forensic Laboratory Archive

<div align="center">

<!-- Row 1: Core Research Status Badges -->
[![Status: Negative Result](https://img.shields.io/badge/Result-Negative_Cryptanalysis-crimson?style=for-the-badge&logo=target&logoColor=white)](docs/08_FINAL_CONCLUSION.md)
[![Branches: 26 Closed](https://img.shields.io/badge/Branches-26%2F26_Closed-success?style=for-the-badge&logo=checkmarx&logoColor=white)](docs/04_ATTACK_TREE.md)
[![Residual: LPN Core](https://img.shields.io/badge/Residual_Hard_Core-LPN(4096%2C_1%2F8)-blueviolet?style=for-the-badge&logo=matrix&logoColor=white)](docs/mathematics/lpn.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge&logo=open-source-initiative&logoColor=white)](LICENSE)

<!-- Row 2: Target & Source Specification Badges -->
[![Target: Octra Challenge](https://img.shields.io/badge/Target-octra--labs%2Fhfhe--challenge-black?style=flat-square&logo=github)](https://github.com/octra-labs/hfhe-challenge)
[![Pinned Commit](https://img.shields.io/badge/Pinned_Source-pvac__hfhe__cpp%40071b0e9-2ea44f?style=flat-square&logo=git&logoColor=white)](https://github.com/octra-labs/pvac_hfhe_cpp/commit/071b0e909c119de815e284b347c4bd979cb59ef3)
[![Reproducibility: 100% Deterministic](https://img.shields.io/badge/Reproducibility-100%25_Deterministic-brightgreen?style=flat-square&logo=safari&logoColor=white)](experiments/reproduce/run_all.py)
[![Security Policy](https://img.shields.io/badge/Security-Responsible_Disclosure-orange?style=flat-square&logo=securityscorecard&logoColor=white)](SECURITY.md)

<!-- Row 3: Cryptographic Parameter Widgets -->
[![Field: Fp 127-bit](https://img.shields.io/badge/Field-%F0%9D%94%B9(2%5E127--1)-blue?style=flat-square&logo=affinitydesigner&logoColor=white)](docs/mathematics/field_Fp.md)
[![Group: Ristretto255](https://img.shields.io/badge/Group-Ristretto255_(\u2113%E2%89%882%5E252)-indigo?style=flat-square&logo=subversion&logoColor=white)](docs/mathematics/ristretto_math.md)
[![Cipher: AES-256-CTR](https://img.shields.io/badge/PRF-AES--256--CTR-teal?style=flat-square&logo=gnuprivacyguard&logoColor=white)](docs/mathematics/prf_R_core.md)
[![Parity: GF(2) 8192x16384](https://img.shields.io/badge/Parity_Check-GF(2)_8192%C3%9716384-informational?style=flat-square&logo=databricks&logoColor=white)](docs/mathematics/H_matrix.md)

<!-- Row 4: Toolchain & Runtime Environment Widgets -->
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![C++: 17](https://img.shields.io/badge/C%2B%2B-17-00599C?style=flat-square&logo=c%2B%2B&logoColor=white)](cpp/)
[![NumPy](https://img.shields.io/badge/NumPy-%3E%3D2.0-013243?style=flat-square&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-%3E%3D1.12-8CAAE6?style=flat-square&logo=scipy&logoColor=white)](https://scipy.org/)
[![PyCryptodome](https://img.shields.io/badge/PyCryptodome-%3E%3D3.20-yellowgreen?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/pycryptodome/)
[![Code Style: Black & Ruff](https://img.shields.io/badge/Code_Style-Black_%26_Ruff-black?style=flat-square&logo=codefactor&logoColor=white)](pyproject.toml)

</div>

---

> **EXECUTIVE SUMMARY:** No practical exploit, secret-key recovery, or plaintext recovery was identified across the tested public attack surface of the Octra Labs HFHE v2 challenge. This repository contains the complete forensic research record, theoretical proofs of negative results, C++ verification binaries, reproducible Python experiments, execution transcripts, and chronological research journals.

---

## 📌 GitHub Repository Metadata

- **About Description:** Exhaustive cryptanalytic investigation and forensic laboratory notebook for the Octra Labs HFHE v2 challenge (pvac_hfhe_cpp@071b0e9).
- **Website:** `https://github.com/octra-labs/hfhe-challenge`
- **Topics / Tags:** `cryptography`, `cryptanalysis`, `homomorphic-encryption`, `post-quantum`, `lpn`, `ristretto255`, `security-research`, `finite-fields`, `information-set-decoding`

---

## 1. Cryptographic Primitives & System Parameters

| Component | Symbol / Dimension | Mathematical Domain | Concrete Value / Property | Security Role |
|---|---|---|---|---|
| **Scalar Field** | $p$ | $\mathbb{F}_p$ | $2^{127} - 1$ (Mersenne Prime) | Edge weight and mask coefficient arithmetic |
| **Commitment Group** | $\ell$ | $\mathbb{Z}/\ell\mathbb{Z}$ | $2^{252} + 27742317777372353535851937790883648493$ | Ristretto255 prime-order group for Pedersen blinding |
| **LPN Secret Dimension** | $n$ | $\mathbb{F}_2^n$ | $4,096$ bits | Binary secret vector $s \in \mathbb{F}_2^{4096}$ |
| **LPN Sample Length** | $m$ | $\mathbb{F}_2^m$ | $16,384$ bits / instance | Parity equations per LPN sample |
| **LPN Error Rate** | $\tau$ | $\mathbb{Q}$ | $1/8 = 0.125$ | Bernoulli noise parameter $e_i \sim \text{Ber}(\tau)$ |
| **Total LPN Samples** | $N_{lpn}$ | - | $44 \times 16,384 = 720,896$ | Available public sample equations |
| **Ciphertext Objects** | $N_{ct}$ | - | $22$ objects in `secret.ct` | Compressed serialized bundle |
| **Base Layers per CT** | $N_{layers}$ | - | $2$ ($T_0$ Layer 0, $T_1$ Layer 1) | Wrapped mask layers |
| **Edges per Layer** | $N_{edges}$ | - | $\approx 1,829$ tuples | Average sparse edge realization |
| **Public Parity Matrix** | $H$ | $\mathbb{F}_2^{8192 \times 16384}$ | Rank $8,192$, Column wt $192 / 193$ | Code parity check matrix |
| **Cyclic Base Order** | $B$ | $\mathbb{Z}$ | $337 = \text{ord}(g)$ | Base group generator order ($g^B = 1$) |

---

## 2. Rigorous Mathematical Formulation

### 2.1. Dual Field Architecture & Embedding Gap
The construction operates simultaneously over two distinct algebraic structures:
1. **The Mersenne Field $\mathbb{F}_p$:** $p = 2^{127} - 1$. Arithmetic is optimized via $X = X_1 \cdot 2^{127} + X_0 \implies X \equiv X_0 + X_1 \pmod p$.
2. **The Ristretto255 Scalar Ring $\mathbb{Z}/\ell\mathbb{Z}$:** Prime order $\ell \approx 2^{252.14}$.

The conversion function `sc_from_fp(x)` in `include/pvac/crypto/ristretto255.hpp` embeds a 127-bit integer $x \in [0, 2^{127}-2]$ directly into the lower 16 bytes of a 32-byte scalar without calling `sc_reduce256`.

$$\iota: \mathbb{F}_p \hookrightarrow \mathbb{Z}/\ell\mathbb{Z}, \quad \iota(x) = x \in \mathbb{Z}$$

#### The Cross-Field Non-Cancellation Theorem
Let $R \in \mathbb{F}_p^*$ be an arbitrary nonzero mask element. In $\mathbb{F}_p$:
$$R \cdot (R^{-1} \bmod p) = 1 + k \cdot p \quad \text{for some } k \in \mathbb{Z}_{\ge 0}$$
When evaluated in the scalar ring $\mathbb{Z}/\ell\mathbb{Z}$:
$$(R \cdot (R^{-1} \bmod p)) \bmod \ell = (1 + k \cdot p) \bmod \ell$$
Because $p < \ell$ and $\gcd(p, \ell) = 1$:
$$1 + k \cdot p \equiv 1 \pmod \ell \iff k \cdot p \equiv 0 \pmod \ell \iff k \equiv 0 \pmod \ell$$
Since $k < p < \ell$, $k$ must be identically $0$, which occurs if and only if $R = 1$.
$$\forall R \in \mathbb{F}_p \setminus \{1\}: \quad \iota(R) \cdot \iota(R^{-1} \bmod p) \not\equiv 1 \pmod \ell$$
*Empirical verification: 100,000 random numerical trials produced exactly 0 cancellations modulo $\ell$.*

---

### 2.2. Wrapped Ciphertext Encryption Algebra
For a plaintext message vector $m \in \mathbb{F}_p^n$ and an ephemeral vector $v \in_R \mathbb{F}_p^n$ sampled freshly per ciphertext:
$$T_0 = R_0 \cdot (v + m) \pmod p$$
$$T_1 = -R_1 \cdot m \pmod p$$
where $R_0, R_1 \in \mathbb{F}_p^{n \times n}$ are independent pseudorandom mask matrices generated from master key $prf\_k$.

Defining the matrix ratio $\lambda = R_0 \cdot R_1^{-1} \in \mathbb{F}_p^{n \times n}$:
$$T_0 + \lambda T_1 = R_0(v + m) + (R_0 R_1^{-1})(-R_1 m) = R_0 v \pmod p$$

#### Information-Theoretic Barrier to Ratio Recovery:
1. **Degrees of Freedom:** $\lambda$ is a dense $4096 \times 4096$ matrix comprising $16,777,216$ unknown field elements in $\mathbb{F}_p$.
2. **Observation Budget:** Each ciphertext exposes only $\approx 1,829$ sparse edge weights.
3. **Ephemeral Blinding:** Even under hypothetical recovery of $\lambda$, the linear combination isolates $R_0 v$, which is a pseudorandom transformation of the fresh random vector $v$, revealing 0 bits of plaintext $m$.

---

### 2.3. Master PRF & Key Derivation Tree
All cryptographic randomness originates from a 256-bit master key $prf\_k$:

```
                        prf_k (256-bit Master Key)
                                   |
    +------------------------------+------------------------------+
    |                              |                              |
Domain: r.1, r.2, r.3        Domain: noise.1..3            Pedersen Blinding rho
    |                              |                              |
SHA-256 Key Derivation        SHA-256 Key Derivation        CSPRNG Stream
    |                              |                              |
AES-256-CTR Stream            AES-256-CTR Stream            Blinding Scalar in Z/lZ
    |                              |                              |
Toeplitz Matrix & Fp Masks   Bernoulli Noise (tau=1/8)     PC = w*G + rho*H
```

The domain-separated AES key $K_D$ is computed as:
$$K_D = \text{SHA256}\Big(prf\_k \parallel \text{canon\_tag} \parallel H_{digest} \parallel ztag \parallel nonce_{lo} \parallel nonce_{hi} \parallel \text{FNV1a}(D)\Big)$$

---

### 2.4. Public Parity Matrix $H$ & Subgroup Action
1. **Parity Check Matrix $H \in \mathbb{F}_2^{8192 \times 16384}$:**
   $$\text{rank}_{\mathbb{F}_2}(H) = 8,192 \quad (\text{Full Rank})$$
   $$\text{wt}(\text{col}_j) \in \{192, 193\} \quad (\text{Target } 192 \text{ bimodal distribution, 0 duplicates})$$
2. **Cyclic Base Parameter $B = 337$:**
   $$\text{ord}(g) = 337 \implies g^B = g^{337} \equiv 1 \pmod p$$
   $g^B$ is identically the group identity. Exponent indices $idx \in [0, 16383]$ are published in the clear on each edge, rendering discrete logarithm search trivial and non-informative.

---

### 2.5. Edge Graph Permutation & Wire Serialization
Each serialized edge tuple is defined by:
$$e = \Big(idx_e, sign_e, w_e, ztag_e, nonce_e, \sigma_e, PC_e\Big)$$
- $\sigma_e \in \{0,1\}^{64}$ is generated from a fresh system CSPRNG (`csprng_u64()`).
- $PC_e = \iota(w_e) \cdot G + \rho_e \cdot H \in \text{Ristretto255}$.
- The binding verifier computes the public aggregate:
  $$T = \sum_{e} sign_e \cdot w_e \cdot g^{idx_e} \pmod p$$

**Graph Erasure:** Before serialization, `reduction::permute(edges)` performs an in-memory Fisher-Yates shuffle with fresh CSPRNG randomness, completely destroying the input edge pairing.

---

## 3. Investigation Phases & Scoreboard

| Phase | Target Surface | Observable | Null Hypothesis | Metric / Statistical Test | Sample Size | Statistic / Result | $p$-value | Final Status |
|---|---|---|---|---|---|---|---|---|
| **Phase 0** | Artifact Integrity | Byte stream & SHA-256 | Spec exact match | Binary parser validation | 22 CTs, 1 PK | Exact byte-for-byte match | - | **CLOSED** |
| **Phase 1** | Ciphertext Graph | Weight $w_e$ & edge sequence | Uniform $\mathbb{F}_p$ / FY shuffle | Autocorrelation & Chi-Square | 40,238 edges | $\chi^2=101.4$, 0 duplicates | $0.413$ | **CLOSED** |
| **Phase 2** | PRF / LPN Derivation | Cross-layer pair $(w_0, w_1)$ | Pop B (cross-CT pairs) | Two-sample Kolmogorov-Smirnov | 5,000 pairs | $\text{KS stat} = 0.0263$ | $0.523$ | **CLOSED** |
| **Phase 3** | Joint Key Correlation | Nonce vs $w$ low bits | Permuted $(nonce, w)$ | Pearson correlation $r$ | 40,238 edges | $r = -0.0218$ | $0.232$ | **CLOSED** |
| **Phase 4** | Public Key Structure | $H$ rank & $g^B$ discrete log | Full rank / Identity | Gaussian elimination & DLP | $8192$ rows | Rank $8192/8192, g^B = 1$ | - | **CLOSED** |
| **Phase 5** | Pedersen Commitments | Point distribution & $\mathbb{F}_p \to \mathbb{Z}/\ell\mathbb{Z}$ | Uniform curve point | KS 2-sample & Modular trial | 44 PCs / 100k | $\text{KS } p=0.196, 0\text{ cancel}$ | $0.196$ | **CLOSED** |
| **Phase 6** | Wrapped Ratio Attack | Legendre $\left(\frac{-T_0 T_1}{p}\right)$ & Sign | Uniform $\pm 1$ / $\text{Ber}(0.5)$ | Chi-Square GoF & Binomial | 20,000 pairs | $\chi^2=1.3448, \text{Rate}=0.500$ | $0.246$ | **CLOSED** |
| **Phase 7** | LPN Core Hardness | ISD / BJMM & BKW bounds | Asymptotic tractability | Complexity lower bounds | 720,896 eqns | Work $> 2^{200}$, Samples $\gg 2^{20}$ | - | **ASSESSED** |

> **TERMINOLOGY DEFINITIONS:**
> - **CLOSED:** The tested hypothesis produced no reproducible exploitable signal. The attack branch is experimentally and structurally falsified.
> - **ASSESSED:** Theoretical work factors and sample lower bounds evaluated; no sub-exponential shortcut found.

---

## 4. The Surviving Core: $\text{LPN}(4096, 16384, 1/8)$

With all algebraic shortcuts, implementation oracles, and statistical biases falsified, the security of HFHE v2 reduces to the hardness of Learning Parity with Noise:
$$y = A s \oplus e \in \mathbb{F}_2^m, \quad s \in \mathbb{F}_2^{4096}, \quad e \sim \text{Ber}(1/8)^{16384}$$

1. **Information Set Decoding (BJMM / Stern):**
   - Probability of finding an error-free information set:
     $$P_{\text{clean}} = (1 - \tau)^n = \left(\frac{7}{8}\right)^{4096} = 2^{-789.07}$$
   - Optimal BJMM asymptotic time complexity: $> 2^{202}$ operations.
2. **Blum-Kalai-Wasserman (BKW):**
   - Sample complexity: $\approx 2^{n / \log_2 n} = 2^{4096 / 12} \approx 2^{341}$ samples.
   - Available sample budget: $720,896 \approx 2^{19.46}$ samples across 44 independent instances.

---

## 5. Repository Structure

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
│   ├── DETAILED_EXPERIMENT_CATALOG.md       (E00 through E27 detailed experimental logs)
│   ├── SOURCE_TRACE.md                      (Mapping theory to pvac_hfhe_cpp@071b0e9)
│   ├── mathematics/                         (12 markdown docs: Fp, scalar, ristretto, LPN, etc.)
│   └── theory/                              (7 markdown docs: theoretical proofs & negative results)
├── analysis/                  — Modular Python experimental suites (Phases 0 through 7)
├── cpp/                       — High-performance C++ toolchain & experiment verifiers
│   ├── common/                              (128-bit Fp arithmetic, JSONL, I/O)
│   ├── artifact/                            (Binary deserializers for secret.ct and pk.bin)
│   ├── experiments/                         (C++ test suites for cross-field, weights, BKW bounds)
│   └── reference/                           (Source trace interfaces)
├── scripts/                   — Bash build and phase execution runners
├── terminal/                  — Exact command transcripts and forensic terminal history
├── transcripts/               — Machine-readable execution logs per phase
├── research_journal/          — Chronological research notebook (Entries 000 to 017)
├── results/                   — Machine-readable JSON outputs from all experimental executions
├── figures/                   — Publication plots (attack surface, PRF null, PC distribution, ratio)
├── tables/                    — Detailed CSV summary tables (all_experiments, attack_surface, etc.)
├── provenance/                — Cryptographic hashes, source commit pin, environment details, and commands
└── src/                       — Reusable Python cryptanalytic library
```

---

## 6. Artifact Hashes & Verification

| Artifact File | Size (Bytes) | SHA-256 Digest |
|---|---|---|
| `secret.ct` | 1,963,107 | `5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab` |
| `pk.bin` | 3,042,901 | `1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410` |

Source repository commit: [`octra-labs/pvac_hfhe_cpp@071b0e909c119de815e284b347c4bd979cb59ef3`](https://github.com/octra-labs/pvac_hfhe_cpp/commit/071b0e909c119de815e284b347c4bd979cb59ef3).

---

## 7. Reproduction Quickstart

```bash
# Clone the repository
git clone https://github.com/Patel5600/hfhe-v2-cryptanalysis.git
cd hfhe-v2-cryptanalysis

# Install Python requirements
pip install -r requirements.txt

# Run full reproduction pipeline
python experiments/reproduce/run_all.py --artifacts /path/to/challenge/artifacts

# (Optional) Build and run C++ verification tools
bash scripts/build.sh
./bin/cross_field_test 100000
```

---

## 8. License, Security Policy & Citation

- **License:** MIT — see [`LICENSE`](LICENSE).
- **Security Policy:** See [`SECURITY.md`](SECURITY.md).
- **Citation:** See [`CITATION.cff`](CITATION.cff).
