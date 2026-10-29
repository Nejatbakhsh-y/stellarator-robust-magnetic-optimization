"""Paired simulated-scenario statistics, distinct from numerical error."""
import numpy as np


def paired_summary(nominal, robust, seed=20261101, resamples=2000):
    a, b = np.asarray(nominal, float), np.asarray(robust, float)
    if a.ndim != 1 or a.shape != b.shape or len(a) < 2:
        raise ValueError('Require at least two paired observations')
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any(a < 0) or np.any(b < 0):
        raise ValueError('Require finite nonnegative RMS in tesla')
    d = b-a
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(d, len(d), replace=True).mean() for _ in range(resamples)])
    return {'count': len(d), 'delta_T': d.tolist(), 'mean_T': float(d.mean()),
            'median_T': float(np.median(d)), 'q90_T': float(np.quantile(d, .9)),
            'q95_T': float(np.quantile(d, .95)), 'max_T': float(d.max()),
            'fraction_improved': float(np.mean(d < 0)),
            'mean_bootstrap_95_T': np.quantile(means, [.025, .975]).tolist(),
            'bootstrap_seed': seed, 'resamples': resamples,
            'interpretation': 'positive means robust worse; percentile bootstrap assumes IID paired draws; no population guarantee'}
