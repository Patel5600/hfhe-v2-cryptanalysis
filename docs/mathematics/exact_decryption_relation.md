# Exact Attacker-Facing Decryption Relation

## 1. The Direct Implementation Decryptor
From `include/pvac/ops/decrypt.hpp:81-99`, the exact algebraic accumulator computed during decryption across all serialized edges is:

$$v_{\text{dec}} = c_0 + \sum_{\ell} T_\ell R_\ell^{-1} \pmod p$$

where for each layer $\ell$:
$$T_\ell = \sum_{e \in E_\ell} \operatorname{sgn}(e) \cdot w_e \cdot \mathrm{powg_B}[idx_e] \pmod p$$

## 2. Noise Cancellation Within Layer Aggregates
During encryption (`include/pvac/ops/encrypt.hpp:770-790`), the base layer synthesizes:
- Signal edges: $(v_\ell - \Delta_\ell) \cdot R_\ell$
- Delta tuple edges: $\Delta_\ell \cdot R_\ell$

When aggregated across all edges in layer $\ell$:
$$T_\ell = (v_\ell - \Delta_\ell) R_\ell + \Delta_\ell R_\ell = R_\ell \cdot v_\ell \pmod p$$

Thus, the internal noise $\Delta_\ell$ cancels identically within the public aggregate $T_\ell$.

## 3. The 2-Layer Wrapped Text Target
For each 15-byte text block ($c_0 = 0$, $L=2$ base layers with $v_0 = v + m$ and $v_1 = -m$):
$$T_0 = R_0 (v + m) \pmod p$$
$$T_1 = -R_1 m \pmod p$$

Decryption evaluates:
$$v = T_0 R_0^{-1} + T_1 R_1^{-1} \pmod p$$

## 4. The Attacker-First Target Formulation
The attacker does NOT need to:
1. Invert SHA-256 / recover master key $prf_k$,
2. Solve all 44 LPN sample instances globally,
3. Break 14-round AES-256, or
4. Compute Ristretto discrete logarithms.

The **minimal necessary and sufficient attacker condition** is:
$$\boxed{\text{Evaluate the specific linear combination } \sum_\ell T_\ell R_\ell^{-1} \pmod p \text{ for the challenge ciphertext.}}$$

## 5. Structural Barrier: The Scalar Masking Wall
- Let $u_0 = R_0^{-1}$ and $u_1 = R_1^{-1}$.
- Multiplying by the ratio $\lambda = R_0 R_1^{-1} = u_1 u_0^{-1}$:
  $$T_0 + \lambda T_1 = R_0(v + m) - \lambda R_1 m = R_0 v \pmod p$$
- While $\lambda$ perfectly eliminates the ephemeral mask $m$, the result is $R_0 v \pmod p$.
- Recovering $v \in [0, 2^{120})$ from $R_0 v \pmod p$ requires $R_0^{-1}$, since multiplication by the uniform random field element $R_0 \in \mathbb{F}_p^*$ acts as a one-time pad in the multiplicative group $\mathbb{F}_p^*$.
