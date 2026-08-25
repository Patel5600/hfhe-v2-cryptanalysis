# Terminal Session 09 — Wrapped Ratio Experiment

## Context

Phase 6: Testing whether -T0/T1 leaks information about lambda = R0/R1.

## Commands

```powershell
cd C:\Dev\octra\experiments
python preregistered_predicates_experiment.py
python toy_ratio_experiment.py
```

## preregistered_predicates output

```
=== Phase 6: Preregistered Predicate Tests ===
N = 20,000 samples per class (IDEAL / TOY / REAL)

Test 1: Legendre symbol of (-T0 * T1)
  IDEAL:  chi2=1.12, p=0.291
  TOY:    chi2=1.08, p=0.299  (known-key positive control)
  REAL:   chi2=1.34, p=0.246
  Verdict: No deviation. CLOSED.

Test 2: Sign agreement Pr[chi2(-T0/T1) == chi2(lambda)]
  REAL:   rate=0.50001, p=0.756
  Verdict: Rate indistinguishable from 0.5. CLOSED.

Test 3: Hamming ratio estimator
  REAL:   mean=0.50017, null mean=0.50000
  Verdict: Deviation < noise floor. CLOSED.
```

## toy_ratio_experiment output

```
=== Toy Ratio Experiment (known key) ===
Generating 1000 pairs with known R0, R1...

Ratio recovery attempt:
  True lambda estimate:  0.499983
  Hamming distance mean: 0.500017
  Recovery rate:         indistinguishable from random (0.500)

Conclusion: Even with known key and true tuple correspondence,
  the ratio estimator cannot recover lambda from 1829 edge pairs
  (need n^2 = 16M edges for a full matrix recovery).
Status: CLOSED
```
