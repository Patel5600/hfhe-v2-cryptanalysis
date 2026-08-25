# Global Non-Low-Degree Composition & Cross-Chunk Decoupling Theorem

## 1. System Setup
The challenge ciphertext bundle `secret.ct` consists of $N = 22$ ciphertext objects ($i = 0, \dots, 21$).
For each object $i$:
$$v_i = T_{i, 0} u_{i, 0} + T_{i, 1} u_{i, 1} \pmod p$$
where:
- $p = 2^{127} - 1$ (Mersenne prime),
- $T_{i, 0}, T_{i, 1} \in \mathbb{F}_p^*$ are public edge aggregates,
- $u_{i, 0} = R_{i, 0}^{-1} \pmod p$ and $u_{i, 1} = R_{i, 1}^{-1} \pmod p$ are secret layer inverse masks,
- $v_i \in [0, 2^{120})$ represents the $i$-th 15-byte plaintext chunk.

## 2. Cross-Chunk Coupling Analysis
Consider any global multivariate polynomial or combinatorial relation across all 22 chunks:
$$\mathcal{F}(v_0, v_1, \dots, v_{21}) = 0 \pmod p$$

The system contains:
- **Known Public Equations:** $N = 22$ linear equations over $\mathbb{F}_p$.
- **Unknown Multiplicative Masks:** $2N = 44$ variables $(u_{0,0}, u_{0,1}, \dots, u_{21,0}, u_{21,1}) \in (\mathbb{F}_p^*)^{44}$.
- **Under-Determination Degree:** 44 unknowns against 22 scalar relations $\implies$ an affine solution subspace of dimension $22$ over $\mathbb{F}_p$, containing $p^{22} pprox 2^{2794}$ valid algebraic solutions.

## 3. The PRF Independence Barrier (Decoupling Theorem)
Each layer seed $(ztag_{i, \ell}, nonce_{i, \ell})$ is generated with fresh CSPRNG randomness (`make_nonce128()`).
The per-layer mask is derived via:
$$R_{i, \ell} = 	ext{PRF}(pk, sk, ztag_{i, \ell}, nonce_{i, \ell})$$

Under the standard **Pseudorandom Function (PRF)** assumption for `prf_R_slots`:
1. The 44 mask values $(R_{0,0}, \dots, R_{21,1})$ are computationally indistinguishable from 44 independent, identically distributed uniform samples from $\mathbb{F}_p^*$.
2. Because no secret state is reused across distinct nonces without going through the PRF, **there exist no algebraic relations linking $(u_{i,0}, u_{i,1})$ to $(u_{j,0}, u_{j,1})$ for $i 
eq j$**.
3. Consequently, the global 22-chunk system **decouples completely** into 22 independent 1-equation modular problems:
   $$orall i \in [0, 21]: \quad v_i = T_{i, 0} u_{i, 0} + T_{i, 1} u_{i, 1} \pmod p$$

## 4. The Plaintext Bounding Constraint
Each chunk $v_i$ satisfies the ASCII bounding constraint $0 \le v_i < 2^{120}$.
For a single isolated equation $T_{i,0} u_{i,0} + T_{i,1} u_{i,1} \in [0, 2^{120}) \pmod p$:
- For any arbitrary choice of $u_{i,1} \in \mathbb{F}_p^*$, there are exactly $pprox 2^{120}$ choices of $u_{i,0}$ yielding a valid bounded $v_i$.
- Number of valid candidate pairs $(u_{i,0}, u_{i,1})$ per chunk: $pprox p \cdot rac{2^{120}}{p} = 2^{120}$.
- Across 22 independent chunks, the total candidate solution space is $(2^{120})^{22} = 2^{2640}$.

## 5. Conclusion
Without breaking the underlying PRF (which requires solving $	ext{LPN}(4096, 16384, 1/8)$ or inverting SHA-256 / AES-256), global/non-low-degree cross-chunk compositions cannot reduce the dimensionality of the unknown mask space below $2^{2640}$.
