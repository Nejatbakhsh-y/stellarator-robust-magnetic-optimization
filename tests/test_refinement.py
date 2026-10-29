import numpy as np
from stellarator_robust.model import circle, field, MU0
from stellarator_robust.validation import independent_circle


def test_independent_smooth_circle_reference():
    p = np.array([[0., 0., 0.], [0., 0., .3], [0., 0., 1.]])
    c = circle([0, 0, 0], [0, 0, 1], 1., 32)
    B, estimate = independent_circle(p, c)
    reference = MU0/(2*(1+p[:, 2]**2)**1.5)
    np.testing.assert_allclose(B[:, 2], reference, rtol=1e-12, atol=1e-18)
    assert estimate<1e-15


def test_off_axis_polygon_convergence_to_smooth_reference():
    p = np.array([[.2, .3, .4], [1.3, .2, .3], [-.4, .3, -.2]])
    c = circle([0, 0, 0], [0, 0, 1], 1., 32)
    reference, estimate = independent_circle(p, c)
    errors = []
    for count in [32, 64, 128, 256, 512]:
        B = field(p, circle([0, 0, 0], [0, 0, 1], 1., count))
        errors.append(np.linalg.norm(B-reference)/np.linalg.norm(reference))
    rates = np.log2(np.array(errors[:-1])/errors[1:])
    assert np.all((rates[-3:]>1.95)&(rates[-3:]<2.05))
    assert errors[-1]<1e-4
    assert estimate<np.linalg.norm(reference)*1e-9
