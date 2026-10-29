"""Periodic torus peak diagnostics. Observations never certify a global supremum."""
import numpy as np
from scipy.optimize import minimize
from .model import field


def coordinates(angles, R=1., a=.25):
    angles = np.asarray(angles, dtype=float)
    if angles.ndim != 2 or angles.shape[1] != 2 or not np.isfinite(angles).all():
        raise ValueError('Require finite (N,2) angles')
    if not R > a > 0:
        raise ValueError('Require R > a > 0')
    t, p = np.remainder(angles, 2*np.pi).T
    n = np.column_stack([np.cos(t)*np.cos(p), np.cos(t)*np.sin(p), np.sin(t)])
    xyz = np.column_stack([(R+a*np.cos(t))*np.cos(p),
                           (R+a*np.cos(t))*np.sin(p), a*np.sin(t)])
    return xyz, n


def normal_field(angles, coils, currents, error=None, error_current=1500.):
    """Return B dot n in SI tesla; inherit model.field filament-distance rejection."""
    currents = np.asarray(currents, dtype=float)
    if currents.shape != (len(coils),) or not np.isfinite(currents).all():
        raise ValueError('One finite current per coil required')
    p, n = coordinates(angles)
    B = np.zeros_like(p)
    for c, I in zip(coils, currents):
        B += field(p, c, I)
    if error is not None:
        B += field(p, error, error_current)
    result = np.sum(B*n, axis=1)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite normal field')
    return result


def grid_angles(nt, np_, shift):
    if min(nt, np_) < 3 or not np.isfinite(shift):
        raise ValueError('Invalid periodic grid')
    t, p = np.meshgrid((np.arange(nt)+shift)*2*np.pi/nt,
                       (np.arange(np_)+shift)*2*np.pi/np_, indexing='ij')
    return np.column_stack([t.ravel(), p.ravel()])


def local_extrema(evaluate, seeds, maxiter=100, maxfev=200):
    """Signed deterministic searches; dimensionless objective scaled by 1 mT."""
    rows = []
    for seed in seeds:
        for sign in [-1, 1]:
            fit = minimize(lambda x: -sign*float(evaluate(x[None, :])[0])/1e-3,
                           np.asarray(seed), method='Nelder-Mead',
                           options={'maxiter': maxiter, 'maxfev': maxfev,
                                    'xatol': 1e-8, 'fatol': 1e-12})
            angles = np.remainder(fit.x, 2*np.pi)
            value = float(evaluate(angles[None, :])[0])
            if not np.isfinite(value):
                raise ValueError('Nonfinite local extremum')
            rows.append({'angles_rad': angles.tolist(), 'field_T': value,
                         'sign': sign, 'success': bool(fit.success),
                         'nfev': int(fit.nfev), 'message': str(fit.message)})
    return {'certificate': False, 'interpretation': 'observed lower bound only',
            'searches': rows, 'best': max(rows, key=lambda r: abs(r['field_T']))}
