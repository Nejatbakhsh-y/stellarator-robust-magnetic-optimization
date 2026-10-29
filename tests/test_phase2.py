import numpy as np
import pytest
from stellarator_robust.peak import coordinates, grid_angles, normal_field, local_extrema
from stellarator_robust.model import surface, circle
from stellarator_robust.analysis import paired_summary


def test_periodic_grid_and_linearity():
    angles = grid_angles(5, 9, .5)
    p, n = coordinates(angles)
    pp, nn, _ = surface(1., .25, 5, 9, .5)
    np.testing.assert_allclose(p, pp, atol=1e-14)
    np.testing.assert_allclose(n, nn, atol=1e-14)
    p2, n2 = coordinates(angles+2*np.pi*np.array([2, -3]))
    np.testing.assert_allclose(p2, p, atol=1e-14)
    np.testing.assert_allclose(n2, n, atol=1e-14)
    coil = circle([0, 0, 0], [0, 0, 1], .4, 64)
    f = normal_field(angles, [coil], [2.])
    np.testing.assert_allclose(normal_field(angles, [coil], [-4.]), -2*f, atol=1e-20)
    with pytest.raises(ValueError):
        coordinates([[np.nan, 0]])


def test_search_reproducible_and_no_certificate():
    fun = lambda x: np.cos(x[:, 0])+.3*np.sin(x[:, 1])
    a = local_extrema(fun, [[.2, .4]], 200, 400)
    b = local_extrema(fun, [[.2, .4]], 200, 400)
    assert a == b and a['certificate'] is False
    assert abs(abs(a['best']['field_T'])-1.3) < 1e-10


def test_paired_sign_units_and_failure():
    a = paired_summary([1e-6, 2e-6, 3e-6], [2e-6, 3e-6, 4e-6])
    assert a == paired_summary([1e-6, 2e-6, 3e-6], [2e-6, 3e-6, 4e-6])
    assert abs(a['mean_T']-1e-6) < 1e-20 and a['fraction_improved'] == 0
    np.testing.assert_allclose(a['mean_bootstrap_95_T'], [1e-6, 1e-6])
    with pytest.raises(ValueError):
        paired_summary([1.], [np.nan])


def test_torus_axis_analytic_loop():
    from stellarator_robust.model import MU0
    c = circle([1, 0, 0], [0, 0, 1], .1, 1024)
    value = normal_field([[np.pi/2, 0]], [c], [7.])[0]
    reference = MU0*7*.1**2/(2*(.1**2+.25**2)**1.5)
    assert abs(value/reference-1) < 1e-4


def test_scalar_convex_reference():
    from scipy.optimize import minimize_scalar
    from stellarator_robust.optimize import robust
    As = np.array([[[1.]], [[2.]], [[.5]]])
    bs = np.array([[.7], [-.1], [.3]])
    ridge = .03
    x, status = robust(As, bs, np.ones(1), [0], ridge)
    loss = lambda z: float(np.max((As[:, 0, 0]*z+bs[:, 0])**2)+ridge*z*z)
    ref = minimize_scalar(loss, bounds=(-1, 1), method='bounded', options={'xatol': 1e-13})
    assert ref.success and status['success']
    assert abs(loss(x[0])-ref.fun) < 1e-8
    assert abs(x[0]-ref.x) < 1e-6


def test_source_hash_portability_and_raw_evidence(tmp_path):
    from stellarator_robust.evidence import file_hash
    p = tmp_path/'source.py'
    p.write_bytes(b'x = 1\n'); first = file_hash(p)
    p.write_bytes(b'x = 1\r\n'); assert file_hash(p) == first
    p.write_bytes(b'x = 2\r\n'); assert file_hash(p) != first
    p = tmp_path/'results.json'
    p.write_bytes(b'{}\n'); first = file_hash(p)
    p.write_bytes(b'{}\r\n'); assert file_hash(p) != first
