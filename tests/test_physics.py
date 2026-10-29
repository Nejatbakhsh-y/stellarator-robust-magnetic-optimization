import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from stellarator_robust.model import circle, field, surface, response, benchmark, MU0
from stellarator_robust.validation import convergence, independent_midpoint


def test_analytic_convergence():
    assert convergence()[-1]['max_relative_error'] < 6e-5


def test_surface_and_planarity():
    p, n, area = surface(1., .25, 13, 27)
    np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1., atol=1e-14)
    assert np.all(area > 0)
    assert abs(area.sum()-4*np.pi**2*.25) < 1e-13
    with pytest.raises(ValueError):
        surface(.2, .3, 10, 10)
    _, _, _, coils, _, b = benchmark()
    assert np.linalg.norm(b)>1e-6
    for coil in coils:
        assert np.linalg.svd(coil.vertices-coil.vertices.mean(0), compute_uv=False)[-1]<1e-13


def test_independent_vector_response():
    p, n, _, coils, _, _ = benchmark(4, 5, 32, 3, 2)
    I = np.random.default_rng(123).normal(size=len(coils))*200
    direct = sum(independent_midpoint(p, coil, i, 30) for coil, i in zip(coils, I))
    np.testing.assert_allclose(response(p, n, coils)@I, np.sum(direct*n, axis=1), atol=1e-10, rtol=2e-5)


def test_linearity_orientation_rotation_and_singularity():
    coil = circle([0, 0, 0], [0, 0, 1], 1., 128)
    p = np.array([[0., 0., .3], [.2, .1, .4]])
    B = field(p, coil)
    assert B[0, 2]>0
    np.testing.assert_allclose(field(p, coil, -2), -2*B, atol=1e-20)
    np.testing.assert_array_equal(field(p, coil, 0), np.zeros_like(p))
    rot = np.array([.2, -.3, .1]); Q = Rotation.from_rotvec(rot).as_matrix()
    np.testing.assert_allclose(field(p@Q.T, coil.moved(np.zeros(3), rot)), B@Q.T, atol=1e-19)
    with pytest.raises(ValueError):
        field(coil.vertices[:1], coil)
    assert abs(B[0, 0])+abs(B[0, 1]) < 1e-20
    assert abs(B[0, 2]/(MU0/(2*(1+.3**2)**1.5))-1)<3e-4
