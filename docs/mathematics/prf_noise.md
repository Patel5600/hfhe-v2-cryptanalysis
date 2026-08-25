# PRF Noise Generation

Noise vectors $e \in \mathbb{F}_2^m$ for LPN are derived via:
$$\Delta_i = PRF_{\text{noise}}(seed_i, i, domain)$$
Thresholding generates Bernoulli noise with parameter $\tau = 1/8$.
In ciphertext emission, noise is masked under $R_{\text{noise}}$:
$$\Delta_{masked} = R_{\text{noise}} \cdot \Delta_i \pmod p$$\n