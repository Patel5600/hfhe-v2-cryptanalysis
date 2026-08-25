# Terminal Session 08 — Population B Experiment

## Context

Phase 2 cross-layer prf_k distinguisher experiment.
Population A: real same-ciphertext edge pairs.
Population B: cross-ciphertext edge pairs (null model).

## Commands

```powershell
cd C:\Dev\octra\experiments
python joint_key_experiment.py
```

## Key output

```
=== Phase 2: PRF/LPN Cross-Layer Distinguisher ===
Loading secret.ct...
  22 ciphertext objects, 1829 edges each

Building Population A (same-ciphertext pairs)...
  N_A = 5000 pairs sampled

Building Population B (cross-ciphertext pairs)...
  N_B = 5000 pairs sampled

KS test (REAL weight ratio vs NULL_B weight ratio):
  KS statistic: 0.0263
  p-value:      0.523

Conclusion: p=0.523 >> 0.05. No distinguishable signal.
Status: CLOSED
```

## Interpretation

p=0.523 means the real distribution is statistically indistinguishable
from the null (cross-ciphertext pairs). The prf_k-derived weights w
do not produce a cross-layer distinguisher.
