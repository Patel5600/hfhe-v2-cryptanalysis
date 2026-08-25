# Phase 6 — Wrapped-Mask Ratio Attacks

## Target relation

The wrapped pair is:

`T0 = R0(v + m) mod p`

`T1 = -R1 m mod p`

Define:

`lambda = R0 / R1 mod p`.

Then:

`T0 + lambda*T1 = R0*v mod p`.

Thus a useful public predictor for `lambda` would directly remove the fresh mask `m`.

## Experiment 6A — Legendre character

Test the quadratic character of:

`-T0/T1`

against the corresponding character of `lambda` in a known-key toy model.

Result:

- N = 20,000
- chi² = 1.3448
- p = 0.2462

## Experiment 6B — Sign / character prediction

Predict `chi2(lambda)` from `chi2(-T0/T1)`.

Result:

- prediction rate = **50.00%**
- chi² = 0.0968
- p = 0.7557

This is consistent with a coin flip.

## Experiment 6C — Joint LSB

Compare `(T0 mod 2, T1 mod 2)` under the toy model.

Result:

- chi² = 3.0991
- p = 0.3766

## Experiment 6D — Joint popcount parity

Compare `(popcount(T0) mod 2, popcount(T1) mod 2)`.

Result:

- chi² = 6.2472
- p = 0.1002

## Null interpretation

For uniformly random nonzero `m`, the quotient obeys:

`-T0/T1 = lambda * (1 + v/m)`.

Low-dimensional character tests did not detect information about `lambda` under the tested toy construction.

## Verdict

**CLOSED for the tested low-dimensional ratio estimators.**

This is not a proof that every possible high-dimensional ratio estimator is impossible.
