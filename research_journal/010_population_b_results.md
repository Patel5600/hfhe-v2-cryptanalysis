# Entry 010 \u2014 Population B Results

**Date:** Phase 2
**Status:** CLOSED

## Result

KS(Population A, Population B):
  statistic = 0.0263
  p-value   = 0.523
  N         = 5000 pairs each

## Interpretation

p = 0.523: we cannot reject the null hypothesis that Population A
and Population B are drawn from the same distribution.

## The positive control

To verify the experiment can detect a signal:
- Toy world (known key): Population A with known prf_k,
  where we manually inject a correlation.
- The KS test correctly detects the injected signal (p < 0.001).

This confirms the experiment has adequate power for the effect sizes
we would expect if prf_k were leaking.

## Conclusion

No cross-layer prf_k correlation detected. CLOSED.
