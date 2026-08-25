# Wrapped Ciphertext Construction

## Layer structure

HFHE v2 uses a *wrapped* encryption scheme with two mask layers:

    T_0 = R_0 * (v + m)      (BASE layer 0, masks plaintext + random)
    T_1 = -R_1 * m           (BASE layer 1, masks plaintext only)

where:
- m ∈ Fp^n  : the plaintext message vector
- v ∈ Fp^n  : a fresh random vector (per encryption)
- R_0, R_1 ∈ Fp^{n×n}  : independent mask matrices derived from prf_k

## The ratio λ

Define:
    λ = R_0 * R_1^{-1}   (matrix ratio)

Then:
    T_0 + λ * T_1 = R_0*(v+m) + R_0*R_1^{-1}*(-R_1*m)
                  = R_0*v + R_0*m - R_0*m
                  = R_0 * v

**Key insight:** If λ were recoverable from public ciphertext, then R_0*v would
be computable. But since v is uniform random per encryption, this only gives
a random rotation of a fresh random vector — not the plaintext m.

## Why ratio recovery is hard

1. T_0 and T_1 are serialized after Fisher-Yates permutation of edges.
   The true (e_0, e_1) tuple correspondence is destroyed.
   A ratio T_0[i] / T_1[j] for arbitrary i,j is:
       w_{0,i} * (v_{idx_i} + m_{idx_i}) / (-w_{1,j} * m_{idx_j})
   which is random noise unrelated to λ for i ≠ true_pair(j).

2. Even with true tuple correspondence (toy world), R_0 and R_1 are
   independent matrices. Their ratio λ is a full n×n matrix; recovering
   it requires n^2 observations with n > 4096.

3. The character/Legendre experiments confirm: the distribution of
   -T_0/T_1 values is statistically indistinguishable from the ideal
   (uniform Fp) distribution.

## Preregistered experiment result

| Test | N | Statistic | p-value | Verdict |
|------|---|-----------|---------|--------|
| Legendre(-T_0·T_1) | 20,000 | χ²=1.3448 | 0.246 | CLOSED |
| Sign agreement χ_2(-T_0/T_1)=χ_2(λ) | 20,000 | rate=0.500 | 0.756 | CLOSED |
| Hamming ratio estimator | 20,000 | mean=0.50017 | null | CLOSED |
