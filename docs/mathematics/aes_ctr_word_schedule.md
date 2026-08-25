# AES-CTR Word-Consumption Schedule in LPN Generation

## 1. Overview
In `include/pvac/crypto/lpn.hpp`, both the LPN matrix rows $A_r \in \mathbb{F}_2^{4096}$ and the Bernoulli noise draws $e_r \in \{0, 1\}$ are drawn sequentially from a single `AesCtr256` PRG instance.

## 2. Word Consumption Trace
Each 128-bit AES block $B_k = 	ext{AES-256}_K(	ext{nonce} + k)$ produces two 64-bit words:
$$B_k = (B_{k, 	ext{lo}}, B_{k, 	ext{hi}})$$

- **Matrix Row Size:** $n = 4096$ bits $= 64$ `uint64` words $= 32$ AES blocks.
- **Noise Draw Size:** `prg.bounded(8)` consumes 1 `uint64` word ($64$ bits) via `next_u64()`.

### Block-by-Block Schedule:
1. **Row 0 ($r=0$):**
   - Consumes 32 full AES blocks: $B_0, B_1, \dots, B_{31}$ (Words $0 \dots 63$ of $A_0$).
   - `prg.bounded(8)` calls `next_u64()`: generates block $B_{32}$.
   - Noise draw $e_0 = (B_{32, 	ext{lo}} mod 8 < 1)$.
   - $B_{32, 	ext{hi}}$ remains stored in `buf[1]` (`has_buf = true`).

2. **Row 1 ($r=1$):**
   - Consumes $B_{32, 	ext{hi}}$ as Word 0 of $A_1$ ($A_{1, 0} = B_{32, 	ext{hi}}$).
   - Consumes 31 full AES blocks: $B_{33}, \dots, B_{63}$ (Words $1 \dots 62$ of $A_1$).
   - Consumes $B_{64, 	ext{lo}}$ as Word 63 of $A_1$ ($A_{1, 63} = B_{64, 	ext{lo}}$).
   - $B_{64, 	ext{hi}}$ remains stored in `buf[1]`.
   - `prg.bounded(8)` calls `next_u64()`: consumes $B_{64, 	ext{hi}}$ as noise draw $e_1 = (B_{64, 	ext{hi}} mod 8 < 1)$.

3. **Row 2 ($r=2$):**
   - Consumes 32 full AES blocks: $B_{65}, \dots, B_{96}$ (Words $0 \dots 63$ of $A_2$).
   - Noise draw $e_2 = (B_{97, 	ext{lo}} mod 8 < 1)$.
   - $B_{97, 	ext{hi}}$ stored in buffer.

4. **Row 3 ($r=3$):**
   - Word 0 of $A_3 = B_{97, 	ext{hi}}$.
   - Words $1 \dots 62$ of $A_3 = B_{98} \dots B_{128}$.
   - Word 63 of $A_3 = B_{129, 	ext{lo}}$.
   - Noise draw $e_3 = (B_{129, 	ext{hi}} mod 8 < 1)$.

## 3. The 64-bit Co-Location Property
For every single noise bit $e_r$, exactly **64 bits of the same 128-bit AES ciphertext block are published in matrix $A$**:
- For even rows $r = 2k$: $e_{2k} = (B_{65k+32, 	ext{lo}} mod 8 < 1)$ and $A_{2k+1, 0} = B_{65k+32, 	ext{hi}}$ (Published).
- For odd rows $r = 2k+1$: $e_{2k+1} = (B_{65k+64, 	ext{hi}} mod 8 < 1)$ and $A_{2k+1, 63} = B_{65k+64, 	ext{lo}}$ (Published).

## 4. Cryptanalytic Reduction
Predicting the noise bit $e_r$ from published matrix $A$ reduces precisely to predicting the lowest 3 bits of $Y_{	ext{lo}}$ given the full 64 bits of $Y_{	ext{hi}}$ for $Y = 	ext{AES-256}_K(CTR)$.
Under the standard pseudorandom permutation (PRP) assumption of 14-round AES-256, the two 64-bit halves of the output block are computationally indistinguishable from independent uniform random variables.
