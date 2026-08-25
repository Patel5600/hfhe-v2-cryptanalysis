# Entry 015 \u2014 Ratio Predicates

**Date:** Phase 6
**Status:** CLOSED

## Three preregistered predicates

These were specified BEFORE running the experiment (preregistration).

1. Legendre(-T0*T1): Tests whether -T0*T1 is a quadratic residue mod p
   more/less often than expected for random Fp elements.
   
2. Sign agreement: Tests whether chi_2(-T0/T1) = chi_2(lambda) more than 50% of the time.

3. Hamming ratio estimator: Tests whether the Hamming weight of
   binary(-T0/T1) deviates from 0.5.

## Preregistration prevents cherry-picking

By fixing the predicates before running, we avoid the garden of forking
paths problem: we cannot selectively report only the test that showed
a signal.

## Results

All three: null. All p >> 0.05. All Bonferroni-corrected.

## The five-condition test

Even if ONE test had p < 0.05:
1. Not reproducible with different seed (not tested)
2. Not surviving matched null (null matched in all cases)
3. Multiple-testing not controlled IF only one test
4. No mechanism explained
5. No recovery demonstrated

No condition would be satisfied. CLOSED regardless.
