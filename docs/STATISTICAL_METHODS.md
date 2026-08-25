# Statistical Methods

## Tests used

### Kolmogorov-Smirnov (KS) test
Used to compare continuous distributions (e.g., scalar weight distributions
between REAL and NULL populations). Two-sample variant: `scipy.stats.ks_2samp`.
Significance threshold: alpha = 0.05.

### Chi-squared goodness-of-fit
Used for discrete / categorical distributions (e.g., Legendre symbol
distributions). `scipy.stats.chisquare`. df = (categories - 1).

### Pearson correlation
Used for linear dependency between continuous variables.
`scipy.stats.pearsonr`. Two-tailed p-value.

### Permutation tests
For ratio and predicate experiments: shuffle labels 1,000 times,
compute empirical p-value as fraction of permuted statistics exceeding observed.

## Multiple testing

When running k independent tests simultaneously, we apply Bonferroni correction:
effective alpha = 0.05 / k.

All p-values reported are the raw (uncorrected) values; Bonferroni-corrected
thresholds are stated per experiment.

## Sample sizes

| Experiment | N | Justification |
|------------|---|---------------|
| KS prf_k cross-layer | 5 000 pairs | Power ≥ 0.80 for effect size d ≥ 0.08 |
| Character/parity predicates | 20 000 | Power ≥ 0.95 for 1% deviation from p=0.5 |
| Cross-field inversion | 100 000 | Expected 0 events under null; no false negatives |
| PC KS distribution | 44 | Limited by artifact size |

## Seeds

All experiments use `random_seed = 42` unless otherwise noted.
