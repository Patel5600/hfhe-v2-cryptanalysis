# LPN Core Parameters and Hardness

The Learning Parity with Noise (LPN) instance has:
- Dimension $n = 4096$
- Sample count $m = 16384$ per instance
- Noise rate $\tau = 1/8 = 0.125$
- Total instances = 44 (720,896 total samples)

For binary LPN with secret $s \in \mathbb{F}_2^n$, sample matrix $A \in \mathbb{F}_2^{m \times n}$, error $e \sim \text{Ber}(\tau)^m$:
$$y = A s \oplus e$$

Generic attack complexity:
- BJMM Information Set Decoding: Work factor $\approx 2^{202}$.
- BKW Algorithm: Sample complexity $2^{n / \log_2 n} \approx 2^{341}$ (far exceeds 720,896 available).\n