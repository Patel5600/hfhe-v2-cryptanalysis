# Entry 014 — Wrapped Ratio Model

**Date:** Phase 6  
**Status:** CLOSED

## The algebraic target

    T_0 = R_0*(v+m),  T_1 = -R_1*m
    lambda = R_0 * R_1^{-1}
    T_0 + lambda*T_1 = R_0*v

If lambda were recoverable, we get R_0*v -- a linear function of the
random vector v, not m. So even perfect lambda recovery does not give m directly.

## The three tests

1. **Legendre(-T0*T1):** Legendre symbol should be biased if T0, T1 are
   correlated. Chi2=1.34, p=0.246. No bias.

2. **Sign agreement:** Pr[chi2(-T0/T1) = chi2(lambda)] should be > 0.5
   if -T0/T1 approximates lambda. Rate=0.500, p=0.756. No signal.

3. **Hamming ratio estimator:** Mean deviation from 0.5 measures ratio
   recovery. Mean=0.50017, null=0.50000. Within noise floor.

## The toy-world control

A known-key toy world confirmed that even with perfect tuple correspondence
and known key, the ratio estimator fails because:
- Only 1829 edges available per ciphertext
- Need n^2 = 4096^2 ~= 16M observations for full matrix recovery
- Fundamental information-theoretic barrier, not a statistics problem

## Conclusion

The wrapped ratio attack is closed at the algebraic/information-theoretic level,
not just the statistical one.
