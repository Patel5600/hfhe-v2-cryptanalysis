# Cross-Field Inversion Failure Analysis

Let $R \in \mathbb{F}_p^*$.
In $\mathbb{F}_p$, $R^{-1} \cdot R = 1 \pmod p \implies R \cdot R^{-1} = 1 + k \cdot p$ as an integer in $\mathbb{Z}$.
When embedded into $\mathbb{Z}/\ell\mathbb{Z}$:
$$(R \cdot R^{-1}) \bmod \ell = (1 + k \cdot p) \bmod \ell$$
Because $p < \ell$ and $\gcd(p, \ell) = 1$, $1 + k \cdot p \not\equiv 1 \pmod \ell$ unless $k \equiv 0 \pmod \ell$, which requires $R = 1$.
100,000 random numerical trials confirmed exactly 0 cancellations modulo $\ell$.\n