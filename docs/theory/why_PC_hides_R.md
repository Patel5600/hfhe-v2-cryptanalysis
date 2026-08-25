# Why Pedersen Commitments Perfectly Hide R

Pedersen commitments $PC = w \cdot G + \rho \cdot H$ provide information-theoretic hiding.
For any weight $w$, as $\rho \in_R \mathbb{Z}/\ell\mathbb{Z}$ varies uniformly, $PC$ is uniformly distributed over the curve group $\mathcal{G}$.
Statistical KS testing against uniform Ristretto points yielded $p = 0.196$.\n