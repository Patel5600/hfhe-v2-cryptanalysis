# Statistical Methods

## Principle

Statistical testing is used to falsify concrete hypotheses, not to prove cryptographic security.

A small p-value is only meaningful relative to the correctly specified null distribution and the exact observable being tested.

## Kolmogorov-Smirnov

Two-sample KS tests were used for continuous normalized observables and distribution comparisons.

Threshold used for exploratory reporting: alpha = 0.05.

The KS test was not used as a standalone exploit criterion.

## Chi-squared

Chi-squared tests were used for discrete predicates such as:

- Legendre/quadratic character
- sign agreement
- LSB partitions
- parity partitions

Degrees of freedom are the number of categories minus one for the corresponding goodness-of-fit test.

## Pearson correlation

Pearson correlation was used only when a linear relationship was the stated hypothesis.

## Permutation controls

For label-dependent experiments, observed values were retained while labels were shuffled to destroy the hypothesized correspondence.

A permutation p-value was interpreted as empirical evidence against exchangeability under the chosen null.

## Null populations

### Ideal null

Independent random field/group values or independent Bernoulli bits, where appropriate.

### Matched construction null

The same public metadata and pinned construction with fresh cryptographic randomness.

For the LPN/PRF branch, the correct null freezes public metadata, resamples `prf_k`, and lets the constructor generate an independent `S_B`.

### Shuffled null

Observed values retained while their metadata correspondence is permuted.

## Multiple testing

Where multiple related predicates were tested, raw p-values are reported together with the number of tests. A formal family-wise claim requires a corrected threshold (e.g. Bonferroni or an appropriate false-discovery procedure).

A raw p > 0.05 is not a proof of no effect, particularly for small samples.

## Important limitations

Sample size does not establish “no false negatives.” It only establishes the detectable effect size for the chosen test at the chosen confidence/power assumptions.

This repository therefore avoids statements such as “p > 0.05 proves independence.”

## Reported sizes

| Experiment | N / corpus | Purpose |
|---|---:|---|
| Joint public_T test | 946 pair observations | cross-layer/key coupling |
| Shuffled control | 473,000 observations | destroy metadata correspondence |
| NULL_B | 4,730,000 observations | empirical null baseline |
| Character/parity predicates | 20,000 toy trials | wrapped-ratio low-dimensional tests |
| Fp/scalar inversion | 100,000 trials | cross-field compatibility check |
| PC distribution | 946 pair observations | point-level distribution |
| PC within-cipher | 22 pairs | wrapped-pair comparison |

## Seeds

Where an experiment uses pseudorandom sampling, the exact seed/configuration must be recorded in the experiment manifest.
