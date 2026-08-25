# Ristretto255 Mathematics in HFHE v2

The group $\mathcal{G}$ is the prime-order Ristretto255 group of order:
$$\ell = 2^{252} + 27742317777372353535851937790883648493$$

Base generators:
- $G \in \mathcal{G}$: Standard generator.
- $H \in \mathcal{G}$: Derived via SHA-512 `hash_to_group("pvac.pedersen.H")`.

Pedersen commitments are computed as:
$$PC(w, \rho) = sc\_from\_fp(w) \cdot G + \rho \cdot H$$
where $\rho \in_R \mathbb{Z}/\ell\mathbb{Z}$ is sampled during encryption.\n