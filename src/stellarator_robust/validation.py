"""Executable independent circular-loop and polygon quadrature references."""
import numpy as np
from scipy.integrate import quad_vec
from .model import circle, field, MU0


def convergence():
    points = np.array([[0., 0., 0.], [0., 0., .3], [0., 0., 1.]])
    reference = MU0/(2*(1+points[:, 2]**2)**1.5)
    rows = []
    for n in [16, 32, 64, 128, 256]:
        B = field(points, circle([0, 0, 0], [0, 0, 1], 1., n))
        rows.append({"segments": n, "max_relative_error": float(max(abs(B[:, 2]/reference-1))),
                     "center_relative_error": float(abs(B[0, 2]/reference[0]-1))})
    if not all(b["max_relative_error"] < a["max_relative_error"]/3.9 for a, b in zip(rows, rows[1:])):
        raise AssertionError("Expected second-order polygon convergence")
    if rows[-1]["max_relative_error"] > 6e-5:
        raise AssertionError("Circular-loop error exceeds polygon tolerance")
    return rows


def independent_midpoint(points, coil, current, subdivisions=100):
    """Separate composite midpoint integral over polygon segments, for testing only."""
    result = np.zeros_like(points)
    for a, b in zip(coil.vertices, np.roll(coil.vertices, -1, axis=0)):
        dl = (b-a)/subdivisions
        for k in range(subdivisions):
            r = points-(a+(k+.5)*dl)
            result += np.cross(dl, r)/np.linalg.norm(r, axis=1)[:, None]**3
    return MU0*current/(4*np.pi)*result


def independent_circle(points, coil, current=1.):
    """Adaptive smooth-circle integral, independent of polygon segment formula.

    Recover orthogonal radius vectors from quarter-circle vertices. This routine
    only accepts circle polygons with segment count divisible by four. quad_vec's
    error estimate is returned in tesla (norm over the complete vector array).
    """
    count = len(coil.vertices)
    if count % 4:
        raise ValueError('Circle reference requires quarter-circle vertices')
    center = coil.vertices.mean(axis=0)
    u = coil.vertices[0]-center
    v = coil.vertices[count//4]-center
    if not np.isclose(u@v, 0., atol=1e-12) or not np.isclose(u@u, v@v, rtol=1e-12):
        raise ValueError('Reference requires orthogonal equal circle radii')
    def integrand(t):
        source = center+u*np.cos(t)+v*np.sin(t)
        tangent = -u*np.sin(t)+v*np.cos(t)
        r = points-source
        return np.cross(tangent, r)/np.linalg.norm(r, axis=1)[:, None]**3
    result, error = quad_vec(integrand, 0., 2*np.pi, epsabs=1e-10, epsrel=1e-11)
    scale = MU0*current/(4*np.pi)
    return scale*result, abs(scale)*float(error)
