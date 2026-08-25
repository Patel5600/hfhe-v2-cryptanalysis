# Toeplitz Matrix Structure

The public matrix $A$ in LPN generation is formed as a Toeplitz block matrix seeded by AES-CTR output.
A Toeplitz matrix $T \in \mathbb{F}_2^{m \times n}$ has constant diagonals $T_{i,j} = t_{i-j}$.
While structured, the rank remains maximal and no subfield projection permits distinguishing or secret extraction under $\tau = 1/8$.\n