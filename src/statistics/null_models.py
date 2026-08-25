"""Null model generators."""
import numpy as np
from typing import Sequence


def permuted_labels(data: Sequence, rng: np.random.Generator) -> np.ndarray:
    """Return a copy of data with labels permuted (Population B null model)."""
    arr = np.array(data)
    return rng.permutation(arr)


def ideal_uniform_fp(n: int, rng: np.random.Generator) -> np.ndarray:
    """Sample n values uniformly from Fp = Z/(2^127-1)Z (as 128-bit integers)."""
    P = (1 << 127) - 1
    hi = rng.integers(0, 1 << 63, size=n, dtype=np.uint64)
    lo = rng.integers(0, 1 << 64, size=n, dtype=np.uint64)
    vals = (hi.astype(object) << 64) | lo.astype(object)
    return np.array([int(v) % P for v in vals], dtype=object)
