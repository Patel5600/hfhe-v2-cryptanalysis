# Final Conclusion

## Result

> No practical plaintext-recovery or private-key-recovery exploit was identified
> in the tested attack surface.

This is a **strong negative result** across 26 independently falsified hypotheses
covering the full publicly accessible attack surface.

## What the experiments establish

| Claim | Basis |
|-------|-------|
| R_com oracle is absent from wire | Source read: `write_layer` does not serialize R_com |
| Tuple ordering is fully permuted | Source read: CSPRNG Fisher-Yates in `reduction::permute` |
| Sigma is not prf_k-rooted | Source read: `sigma_from_H(..., csprng_u64())` |
| H matrix is full GF(2) rank | Computation: 8192/8192 pivot rows |
| Cross-layer prf_k: no signal | KS(REAL vs NULL_B): stat=0.0263, p=0.523, N=5000 |
| PC distribution: no signal | KS(REAL vs NULL_B): p=0.196, N=44 |
| Cross-field Fp/Z-ell: no cancellation | 0/100,000 trials R*R_inv_p ≡ 1 mod ell |
| Legendre(-T0*T1): no bias | Chi2=1.34, p=0.246, N=20,000 |
| Sign agreement: no bias | Rate=0.500, p=0.756, N=20,000 |
| Ratio estimators: recovery impossible | Toy-world known-key experiment |

## Surviving attack surface

The sole surviving open attack surface is the LPN core problem:

    LPN(n=4096, m=16384, tau=1/8)

Our tested generic attack families (ISD, BKW) do not give a practical attack
at the available resources. **A formal concrete security level has not been
established by this investigation.**

## Final answer to the challenge

The tested public artifacts do not yield a recoverable plaintext or private key
via any of the analysed attack strategies. The challenge remains open in the
sense that no exploit was found, not in the sense that the construction is
proven secure.
