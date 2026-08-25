# Why Recovering the R0/R1 Ratio is Hard

Given $T_0 = R_0(v+m)$ and $T_1 = -R_1 m$, the ratio $\lambda = R_0 R_1^{-1}$ satisfies $T_0 + \lambda T_1 = R_0 v$.
However:
1. $v$ is a fresh uniform ephemeral vector per ciphertext.
2. $\lambda$ is a dense matrix in $\mathbb{F}_p^{n \times n}$ ($16 \times 10^6$ parameters).
3. The available edges provide at most 1,829 scalar observations, leaving $> 99.98\%$ of matrix degrees of freedom unconstrained.\n