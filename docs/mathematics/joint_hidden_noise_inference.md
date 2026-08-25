# Joint Hidden-Noise Inference: Primal, Dual, and AES-Co-Location Model

## 1. The Joint System of Equations
For each LPN instance ($m = 16384, n = 4096, 	au = 1/8$):
1. **Primal LPN Equation:**
   $$y = A S \oplus e \in \mathbb{F}_2^{16384}, \quad S \in \mathbb{F}_2^{4096}, \quad e \sim 	ext{Ber}(1/8)^{16384}$$
2. **Dual Syndrome Equation:**
   Let $\mathbf{H}_A \in \mathbb{F}_2^{12288 	imes 16384}$ be the parity check matrix of the code spanned by the columns of $A$ ($\mathbf{H}_A A = 0$).
   Multiplying the primal equation by $\mathbf{H}_A$:
   $$\mathbf{H}_A y = \mathbf{H}_A (A S \oplus e) = \mathbf{H}_A e \pmod 2$$
   The syndrome $s_A = \mathbf{H}_A y \in \mathbb{F}_2^{12288}$ is **fully computable from public data ($A$ and $y$)**.
3. **AES Co-Location Condition:**
   Every noise bit $e_r \in \{0, 1\}$ is determined by the lowest 3 bits of a 64-bit secret limb $Y_{	ext{hidden}, r}$:
   $$e_r = (Y_{	ext{hidden}, r} mod 8 < 1)$$
   where the corresponding 64-bit limb $Y_{	ext{known}, r}$ of the same 128-bit block $B = 	ext{AES-256}_K(CTR)$ is published in matrix $A$.

## 2. Joint Inference Reduction
The joint hidden-noise recovery problem is to find a vector $e \in \mathbb{F}_2^{16384}$ of weight $	ext{wt}(e) pprox 2048$ satisfying:
$$\mathbf{H}_A e = s_A \pmod 2$$
subject to the conditional prior:
$$P(e_r = 1 \mid Y_{	ext{known}, r})$$

Under the standard **14-round AES-256 Pseudorandom Permutation (PRP) assumption**, observing 64 bits of block output provides zero non-trivial advantage in predicting the low 3 bits of the remaining 64 bits:
$$P(e_r = 1 \mid Y_{	ext{known}, r}) = rac{1}{8} + 	ext{negl}(256)$$

## 3. Cryptanalytic Conclusion
The conditional distribution of $e$ remains identically Bernoulli($1/8$).
Consequently, the joint hidden-noise inference problem reduces strictly to **Syndrome Decoding of a random binary linear code of length $m = 16384$, dimension $k = 4096$, and noise rate $	au = 1/8$**.
Without an intra-block output correlation in AES-256 itself, the AES stream schedule does not lower the complexity of Syndrome Decoding / ISD below standard generic bounds.
