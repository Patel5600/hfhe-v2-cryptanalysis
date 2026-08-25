# 07 Limitations of the Investigation

This document defines the formal boundaries, scope constraints, and capability model of this cryptanalytic investigation.

## 1. Capability Model: Static Offline Artifacts Only
The challenge operates strictly in the **offline static artifact model** without an active oracle:
- **No Decryption Oracle:** The challenge does not expose an interactive endpoint, client verifier, or decryption error feedback channel.
- **No Side-Channel / Physical Traces:** No timing, power, cache, or EM traces are available; the target is a pre-generated binary bundle.
- **Published Scope:** The artifacts consist solely of `secret.ct` (22 ciphertexts), `pk.bin` (public key), and 44 `pvac.prf.r.1` LPN sample files. Domains `r.2`, `r.3`, and noise domains were withheld by the challenge authors.

## 2. Tested Attack Families & Calibrated Claims
The empirical falsifications in this repository apply specifically to the tested families:
- **Linear, Bilinear & Polynomial Invariants:** Evaluated over $\mathbb{F}_p$ ($p=2^{127}-1$) and $	ext{GF}(2)$ up to degree 2 (Monomial rank 22/22, Bilinear rank 4/4).
- **Sparse Edge Spectrum:** Same-index cross-layer ratios ($N=140$, KS $p=0.8260$) and index differences $\Delta idx \pmod{337}$.
- **Sampled Cross-Instance LPN Combinations:** Sampled pairwise differences $A_i \oplus A_j$ (minimum sampled Hamming distance: 1,896 bits; mean: 2,048.02 bits).
- **Cross-Field Embedding:** Fermat inverse in $\mathbb{F}_p$ vs. Ristretto scalar ring $\mathbb{Z}/\ell\mathbb{Z}$ (0 cancellations in 100,000 trials).
- **Subgroup & DLP:** Cyclic group order $B=337 \implies g^B \equiv 1 \pmod p$.

## 3. What is NOT Proven
- **No Proof of Unconditional Security:** This investigation does not prove that HFHE v2 is mathematically secure against all conceivable attacks.
- **Higher-Degree / Non-Low-Degree Algebraic Structures:** Non-low-degree multivariate relationships or global combinatorial code reductions outside the tested families were not exhaustively searched.
- **Concrete LPN Lower Bounds:** Asymptotic work factors ($	ext{ISD} pprox 2^{202}$, $	ext{BKW} pprox 2^{341}$) are reference complexity baselines, not formal lower bounds.
