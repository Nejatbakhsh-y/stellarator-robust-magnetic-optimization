"""Versioned cancellation-resistant evaluation of the unchanged RMS recovery ratio."""
import math
import numpy as np

VERSION = 'residual-energy-v3'


def stable_recovery(A, b, w, pre, frozen, recovered):
    """Evaluate (L-P)/(L-B) through factored residual-energy differences.

    Residual increments are computed from current increments, never by
    subtracting nearly equal field vectors. fsum accumulates binary64 products.
    The original absolute denominator guard (1e-15 T) remains unchanged.
    """
    raw = [np.asarray(x) for x in (A, b, w, pre, frozen, recovered)]
    if any(x.dtype.kind not in 'fi' for x in raw):
        raise ValueError('Residual-energy inputs must be real numeric arrays')
    arrays = [x.astype(float) for x in raw]
    A, b, w, pre, frozen, recovered = arrays
    if (A.ndim != 2 or b.shape != (len(A),) or w.shape != b.shape
            or any(x.shape != (A.shape[1],) for x in (pre, frozen, recovered))
            or any(not np.isfinite(x).all() for x in arrays)
            or np.any(w < 0) or not np.any(w > 0)):
        raise ValueError('Invalid finite residual-energy inputs')
    def dot(row, current):
        return math.fsum(float(a)*float(x) for a, x in zip(row, current))
    residuals = [np.array([math.fsum((float(bb), dot(row, x))) for bb, row in zip(b, A)])
                 for x in (pre, frozen, recovered)]
    rms = [math.sqrt(math.fsum(float(ww)*float(y)*float(y) for ww,y in zip(w,r)))
           for r in residuals]
    def energy(i, j):
        delta = np.array([dot(row, (pre, frozen, recovered)[i]-(pre, frozen, recovered)[j]) for row in A])
        terms = [float(ww)*float(dd)*math.fsum((2*float(y), float(dd)))
                 for ww,dd,y in zip(w,delta,residuals[j])]
        value = math.fsum(terms)
        return value, math.fsum(abs(x) for x in terms)
    numerator, numerator_l1 = energy(1, 2)
    denominator, denominator_l1 = energy(1, 0)
    denominator_T = denominator/(rms[1]+rms[0]) if rms[1]+rms[0] else 0.
    ratio = (numerator/denominator*(rms[1]+rms[0])/(rms[1]+rms[2])
             if abs(denominator_T)>1e-15 else None)
    if ratio is not None and not math.isfinite(ratio):
        raise ValueError('Nonfinite recovery ratio')
    return dict(fractional_recovery=ratio, evaluation_version=VERSION,
                rms_T=rms, numerator_energy_T2=numerator, denominator_energy_T2=denominator,
                denominator_rms_difference_T=denominator_T,
                numerator_sum_abs_T2=numerator_l1, denominator_sum_abs_T2=denominator_l1,
                recovered_currents_A=recovered.tolist(),
                pre_residual_T=residuals[0].tolist(), frozen_residual_T=residuals[1].tolist(),
                recovered_residual_T=residuals[2].tolist())
