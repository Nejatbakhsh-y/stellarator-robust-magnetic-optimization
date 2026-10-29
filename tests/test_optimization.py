import numpy as np
from stellarator_robust.optimize import baseline, sparse, deletion_path, robust
from stellarator_robust.model import benchmark
from stellarator_robust.uncertainty import scenarios
from stellarator_robust.faults import outage_offsets


def problem():
    rng = np.random.default_rng(3)
    return rng.normal(size=(20, 6)), rng.normal(size=20), np.ones(20)/20


def test_baseline_bounds_ridge_and_failed_support():
    A, b, w = problem()
    x, status = baseline(A, b, w, .1)
    expected = np.linalg.solve(A.T@(w[:, None]*A)+.1*np.eye(6), -A.T@(w*b))
    np.testing.assert_allclose(x, expected, atol=1e-10)
    assert status['success'] and max(abs(x))<=1
    failed, _ = baseline(A, b, w, support=[0, 2, 3])
    assert np.all(failed[[1, 4, 5]]==0)
    tight, _ = baseline(A, 100*b, w)
    assert max(abs(tight))<=1


def test_sparse_kkt_refit_and_delete():
    A, b, w = problem(); ridge = .01; penalty = .1
    x, status = sparse(A, b, w, penalty, ridge)
    g = A.T@(w*(A@x+b))+ridge*x
    for xi, gi in zip(x, g):
        if abs(xi)<1e-10:
            assert abs(gi)<=penalty+1e-6
        elif abs(xi)<.999:
            assert abs(gi+penalty*np.sign(xi))<1e-6
    support = np.flatnonzero(abs(x)>1e-6)
    refit, _ = baseline(A, b, w, ridge, support)
    assert np.all(refit[np.setdiff1d(np.arange(6), support)]==0)
    rows = deletion_path(A, b, w)
    for (before, removed), (after, _) in zip(rows, rows[1:]):
        assert after[removed]==0
    assert status['success']


def test_objective_finite_difference_and_robust():
    A, b, w = problem(); x = np.arange(6)*.01
    grad = 2*A.T@(w*(A@x+b))
    def fun(z):
        return np.sum(w*(A@z+b)**2)
    h = 1e-6
    fd = np.array([(fun(x+h*e)-fun(x-h*e))/(2*h) for e in np.eye(6)])
    np.testing.assert_allclose(grad, fd, atol=1e-9)
    As = np.stack([A, 1.1*A]); bs = np.stack([b, b])
    z, status = robust(As, bs, w, np.array([0, 1, 2]))
    assert status['success'] and status['violation']<1e-8
    assert np.all(z[3:]==0) and max(abs(z))<=1
    assert max(fun(z), np.sum(w*(1.1*A@z+b)**2)) <= np.sum(w*b*b)+1e-8


def test_scenarios_reproducibility_and_rigid_geometry():
    p, n, _, coils, _, _ = benchmark(3, 4, 16, 3, 2)
    a, b, records = scenarios(p, n, coils, 2, 123)
    aa, bb, rr = scenarios(p, n, coils, 2, 123)
    np.testing.assert_array_equal(a, aa); np.testing.assert_array_equal(b, bb)
    assert records==rr
    other, _, _ = scenarios(p, n, coils, 2, 124)
    assert not np.array_equal(a, other)
    for coil, t, r in zip(coils, records[0]['translation_m'], records[0]['rotation_rad']):
        moved = coil.moved(np.array(t), np.array(r))
        assert np.linalg.svd(moved.vertices-moved.vertices.mean(0), compute_uv=False)[-1]<1e-13


def test_outage_removes_gain_and_offset():
    raw = np.array([[[2., 3.], [5., 7.]]])
    gains = np.array([.1, -.2]); offsets = np.array([4., 6.])
    records = [{'gain': gains.tolist(), 'offset_A': offsets.tolist()}]
    effective = raw*(1+gains)
    b = raw@offsets
    faultb = outage_offsets(effective, b, records, 0)
    command = np.array([0., 10.])
    observed = faultb+effective@command
    expected_actual = np.array([0., (1+gains[1])*command[1]+offsets[1]])
    np.testing.assert_allclose(observed, raw@expected_actual, atol=1e-13)
