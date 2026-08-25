"""Wrappers around scipy statistical tests."""
from scipy import stats
import numpy as np


def ks_test_2samp(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Two-sample KS test. Returns (statistic, pvalue)."""
    r = stats.ks_2samp(a, b)
    return float(r.statistic), float(r.pvalue)


def chi2_uniform(observed: np.ndarray) -> tuple[float, float]:
    """Chi-squared goodness-of-fit against uniform. Returns (statistic, pvalue)."""
    expected = np.ones(len(observed)) * observed.sum() / len(observed)
    r = stats.chisquare(observed, f_exp=expected)
    return float(r.statistic), float(r.pvalue)


def pearson_corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Pearson correlation. Returns (r, pvalue)."""
    r = stats.pearsonr(x, y)
    return float(r.statistic), float(r.pvalue)
