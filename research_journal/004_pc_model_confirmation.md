# Entry 004 \u2014 PC Model Confirmation

**Date:** Phase 5
**Status:** CLOSED

## The question

Do the Pedersen commitment points PC show any distributional anomaly
that could indicate a biased blinding scalar rho?

## The experiment

44 PC values extracted from phase3_pc_data.json.
KS test against permuted-null (Population B model).
p = 0.196.

## Interpretation

p = 0.196 >> 0.05. The PC distribution is statistically consistent
with the null hypothesis (no signal).

## Implication

The Pedersen commitment blinding scalar rho is indistinguishable from
uniform. This is consistent with the source: rho is derived from
a CSPRNG seeded by rho_seed which is not in the wire format.
