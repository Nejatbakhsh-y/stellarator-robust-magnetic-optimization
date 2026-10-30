import math
import numpy as np
import pytest
from stellarator_robust.model import deterministic_frame, circle, clearance, field, MU0
from stellarator_robust.peak import lattice_extrema


@pytest.mark.parametrize('normal', [[0, 0, 1], [0, 0, -1], [1, 0, 0],
                                  [-.3535533905932737, -.3535533905932737, .8660254037844388]])
def test_frame_and_polygon_invariants(normal):
    u, v, n = deterministic_frame(normal)
    np.testing.assert_allclose(n, np.array(normal)/np.linalg.norm(normal), atol=1e-15)
    matrix = np.column_stack([u, v, n])
    np.testing.assert_allclose(matrix.T@matrix, np.eye(3), atol=1e-15)
    np.testing.assert_allclose(np.cross(u, v), n, atol=1e-15)
    assert np.linalg.det(matrix) > 0
    center = np.array([1., 2., 3.]); radius = .16
    c = circle(center, normal, radius, 512, 'householder-v2')
    r = c.vertices-center
    np.testing.assert_allclose(np.linalg.norm(r, axis=1), radius, atol=8e-16)
    np.testing.assert_allclose(r@n, 0, atol=8e-16)
    np.testing.assert_allclose(c.vertices.mean(axis=0), center, atol=5e-15)
    edge = np.roll(c.vertices, -1, axis=0)-c.vertices
    assert np.sum(np.cross(r, np.roll(r, -1, axis=0))@n) > 0
    assert abs(np.linalg.norm(edge, axis=1).sum()/(2*512*radius*np.sin(np.pi/512))-1) < 1e-13


def test_near_tie_has_no_axis_jump_in_v2():
    a = np.array([-.3535533905932737, -.3535533905932737, .8660254037844388])
    b = a.copy(); b[0] = np.nextafter(b[0], -np.inf)
    legacy = [circle([0, 0, 0], n, .16, 512).vertices for n in (a, b)]
    corrected = [circle([0, 0, 0], n, .16, 512, 'householder-v2').vertices for n in (a, b)]
    assert np.max(abs(legacy[0]-legacy[1])) > .1
    assert np.max(abs(corrected[0]-corrected[1])) < 1e-14


@pytest.mark.parametrize('bad', [[0, 0, 0], [np.nan, 0, 1], [np.inf, 0, 1], [1, 2]])
def test_bad_normals_fail(bad):
    with pytest.raises(ValueError):
        deterministic_frame(bad)


def test_independent_scalar_clearance_and_analytical_field():
    coil = circle([0, 0, 0], [0, 0, 1], 1., 512, 'householder-v2')
    points = np.array([[.2, .1, .3], [-.3, .4, .5], [.7, .8, .9]])
    distances = []
    for p in points.tolist():
        for start, end in zip(coil.vertices.tolist(), np.roll(coil.vertices, -1, axis=0).tolist()):
            d = [end[i]-start[i] for i in range(3)]
            r = [p[i]-start[i] for i in range(3)]
            t = min(1., max(0., sum(x*y for x, y in zip(r, d))/sum(x*x for x in d)))
            distances.append(math.sqrt(sum((r[i]-t*d[i])**2 for i in range(3))))
    assert abs(clearance(points, coil)-min(distances)) < 1e-14
    axis = np.array([[0., 0., .3]])
    exact = MU0/(2*(1+.3**2)**1.5)
    assert abs(field(axis, coil)[0, 2]/exact-1) < 1e-4


def test_finite_peak_search_is_repeatable_and_exposes_budget():
    evaluate = lambda p: 1e-3*(np.cos(p[:, 0])+.3*np.sin(p[:, 1]))
    a = lattice_extrema(evaluate, [[.2, .4]])
    assert a == lattice_extrema(evaluate, [[.2, .4]])
    assert not a['certificate'] and a['algorithm'] == 'dyadic-pattern-v2'
    assert all(r['nfev'] == 217 and len(r['moves']) == 24 for r in a['searches'])
    # Finite-search completion does not imply arrival at the continuum maximum.
    assert abs(a['best']['field_T']) <= 1.3e-3+1e-15


def test_legacy_default_and_invalid_version():
    np.testing.assert_array_equal(circle([0, 0, 0], [1, 2, 3], .2).vertices,
                                  circle([0, 0, 0], [1, 2, 3], .2, geometry_version='legacy-v1').vertices)
    with pytest.raises(ValueError):
        circle([0, 0, 0], [0, 0, 1], .2, geometry_version='unknown')


def test_finite_peak_resolution_for_a_covered_analytic_maximum():
    evaluate = lambda p: 1e-3*(np.cos(p[:, 0])+.3*np.sin(p[:, 1]))
    result = lattice_extrema(evaluate, [[.02, 1.55]])
    assert abs(abs(result['best']['field_T'])-1.3e-3) < 1e-13
    assert not result['certificate']


@pytest.mark.parametrize('scale', [1e300, 1e-300])
def test_frame_normalization_handles_finite_extreme_scales(scale):
    u, v, n = deterministic_frame(np.array([1., 2., 3.])*scale)
    np.testing.assert_allclose(n, np.array([1., 2., 3.])/math.sqrt(14), atol=1e-15)
    np.testing.assert_allclose(np.cross(u, v), n, atol=1e-15)
