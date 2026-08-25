# 03 Full Mathematical Model

## 1. Prime Fields & Rings
- Mersenne Field: $\mathbb{F}_p = \mathbb{Z} / (2^{127} - 1)\mathbb{Z}$, with prime $p = 170141183460469231731687303715884105727$.
- Ristretto255 Scalar Ring: $\mathbb{Z} / \ell\mathbb{Z}$, with prime order $\ell = 2^{252} + 27742317777372353535851937790883648493$.
- Embedding: $sc\_from\_fp(x): \mathbb{F}_p \hookrightarrow \mathbb{Z}/\ell\mathbb{Z}$ embeds $x \in [0, 2^{127}-2]$ as an integer into $[0, \ell-1]$ since $p < \ell$.

## 2. Key Derivation & PRF Structure
Master secret key: $prf\_k \in \{0,1\}^{256}$.
For domain $D \in \{ \text{r.1}, \text{r.2}, \text{r.3}, \text{noise.1}, \text{noise.2}, \text{noise.3} \}$:
$$K_D = \text{SHA256}(prf\_k \parallel \text{canon\_tag} \parallel H_{digest} \parallel ztag \parallel nonce_{lo} \parallel nonce_{hi} \parallel \text{FNV1a}(D))$$
$$stream = \text{AES-256-CTR}(K_D, counter=0)$$
$$R_i = \text{hash\_to\_fp\_nonzero}(stream) \in \mathbb{F}_p^*$$

## 3. Wrapped Ciphertext Encryption
For plaintext message vector $v \in \mathbb{F}_p^n$ (packed with message bytes) and fresh random mask vector $m \in_R \mathbb{F}_p^n$:
- Base Layer 0: $T_0 = R_0 \cdot (v + m) \pmod p$
- Base Layer 1: $T_1 = -R_1 \cdot m \pmod p$
- Ratio parameter: $\lambda = R_0 \cdot R_1^{-1} \pmod p$
- Elimination relation: $T_0 + \lambda T_1 = R_0 v \pmod p$

## 4. Edge Structure & Permutation
Each edge $e = (idx, sign, w, ztag, nonce, \sigma, PC)$:
- $idx \in [0, 16383]$ (column index of $H$)
- $sign \in \{+1, -1\}$
- $w \in \mathbb{F}_p$ (weight derived from $R$)
- $\sigma \in \{0,1\}^{64}$ sampled from fresh system CSPRNG (`csprng_u64()`)
- $PC = w \cdot G + \rho \cdot H_{rist} \in \text{Ristretto255}$
- **Permutation:** $\text{reduction::permute}(\text{reduction::merge}(edges))$ executes a fresh Fisher-Yates shuffle using CSPRNG.\n