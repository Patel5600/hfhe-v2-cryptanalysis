"""Permutation test utilities."""
import numpy as np


def permutation_pvalue(
    observed_stat: float,
    labels: np.ndarray,
    values: np.ndarray,
    stat_fn,
    n_permutations: int = 1000,
    seed: int = 42,
) -> float:
    """Compute two-tailed permutation p-value."""
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_permutations):
        perm = rng.permutation(labels)
        s = stat_fn(perm, values)
        if abs(s) >= abs(observed_stat):
            count += 1
    return count / n_permutations
