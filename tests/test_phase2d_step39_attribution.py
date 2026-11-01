"""Mathematical and hostile-input tests for STEP 39; no saved-label oracles."""
from decimal import Decimal as Q
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('step39', SCRIPTS/'phase2d_step39_attribution.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def test_exact_fingerprint(tmp_path):
    p = tmp_path/'input'; p.write_bytes(b'original')
    assert s.seal(p, s.transport.sha(p)) == s.transport.sha(p)
    assert s.fingerprint({'b': 2, 'a': 1}) == s.fingerprint({'a': 1, 'b': 2})


def test_mismatch_fingerprint(tmp_path):
    p = tmp_path/'input'; p.write_bytes(b'changed')
    with pytest.raises(ValueError, match='fingerprint'):
        s.seal(p, '0'*64)


def test_incomplete_inventory():
    with pytest.raises(ValueError, match='inventory'):
        s.reconstruct({'arrays': {}, 'cases': {}})


@pytest.mark.parametrize('x', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_currents(x):
    with pytest.raises(ValueError):
        s.kkt([[1.]], [0.], [x])


def test_invalid_diagnostics():
    with pytest.raises((KeyError, ValueError)):
        s.transport.diagnostics({'success': True, 'cost': -1}, 1)


def test_ill_conditioned():
    c = s.conditioning(np.diag([1., 1e-10]))
    assert c['effective_rank'] == 2
    assert c['condition'] == pytest.approx(1e10)
    assert c['normal_equation_condition'] == pytest.approx(1e20)


def test_singular():
    c = s.conditioning([[1., 1.], [2., 2.]])
    assert c['rank_deficient'] and c['effective_rank'] == 1
    assert c['condition'] is None


def test_kkt_interior_and_wrong_candidate():
    assert Q(s.kkt([[2.]], [1.], [.5])['kkt_max']) == 0
    assert Q(s.kkt([[2.]], [1.], [0.])['stationarity']) == 2


def test_active_set_transition_and_signs():
    interior = s.kkt([[1.]], [.5], [.5])
    upper = s.kkt([[1.]], [2.], [1.])
    lower = s.kkt([[1.]], [-2.], [-1.])
    assert interior['active_upper'] == [] and upper['active_upper'] == [0]
    assert lower['active_lower'] == [0]
    assert Q(upper['kkt_max']) == Q(lower['kkt_max']) == 0
    assert Q(s.kkt([[1.]], [0.], [1.])['stationarity']) == 1
    assert Q(s.kkt([[1.]], [0.], [1.1])['primal']) > 0


def test_analytic_recovery_derivatives():
    r = s.recovery(Q(1), Q(3), Q(2))
    assert Q(r['ratio']) == Q('.5')
    assert list(map(Q, r['derivatives_B_L_P'])) == [Q('.25'), Q('.25'), Q('-.5')]
    # Quotient rule: dN=dL-dP; dD=dL-dB.
    dB, dL, dP = Q('.3'), Q('-.2'), Q('.7')
    via_rule = ((dL-dP)*2-(3-2)*(dL-dB))/4
    via_gradient = sum(v*d for v, d in zip(map(Q, r['derivatives_B_L_P']), (dB,dL,dP)))
    assert via_rule == via_gradient


def test_decimal_finite_differences():
    r = s.recovery(Q('1e-5'), Q('1.000001e-5'), Q('1.0000005e-5'))
    assert all(Q(f['max_error']) < Q('1e-15') for f in r['finite_differences'])


def test_requested_dL_sign_is_wrong():
    r = s.recovery(Q(1), Q(3), Q(2))
    # The requested B-P coefficient predicts -1/4; the exact quotient gives +1/4.
    finite_difference = Q(r['finite_differences'][1]['derivatives'][1])
    assert abs(finite_difference-Q('.25')) < Q('1e-30')
    assert abs(finite_difference-Q('-.25')) > Q('.49')


def test_high_precision_ratio():
    r = s.recovery(Q(1), Q(4), Q(3), digits=90)
    assert r['ratio'].startswith('0.33333333333333333333333333333333333333333333333333')


@pytest.mark.parametrize('gap', ['0', '1e-16', '1e-15', '-1e-15'])
def test_guard(gap):
    with pytest.raises(ValueError, match='guard'):
        s.recovery(Q(0), Q(gap), Q(2))


def test_missing_historical_artifact(tmp_path):
    with pytest.raises(FileNotFoundError):
        s.transport.load(tmp_path/'missing.json')


def test_historical_failure_preserved():
    ref, cur = -.414688997029067, -.4146889970636461
    assert not s.compare(cur, ref)['passed']
    assert not s.transport.close(cur, ref)


def test_false_scientific_pass_rejected():
    with pytest.raises(ValueError, match='acceptance'):
        s.transport.comparison_record(dict(reference=1., candidate=2., status='PASS'))


def test_deterministic_repeated_execution():
    a = s.kkt([[1., 2.], [3., 4.]], [1., 2.], [.1, -.2])
    assert a == s.kkt([[1., 2.], [3., 4.]], [1., 2.], [.1, -.2])
    assert s.recovery(1., 3., 2.) == s.recovery(1., 3., 2.)


def test_independent_square_field():
    # Square side 2a, center Bz = sqrt(2)*mu0 I/(pi*a).
    vertices = [[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0]]
    field = s.field_reference([[0.,0.,0.]], vertices)
    assert Q(field[0][0]) == Q(field[0][1]) == 0
    assert float(field[0][2]) == pytest.approx(4e-7*np.sqrt(2), rel=1e-14)
    reverse = s.field_reference([[0.,0.,0.]], vertices[::-1])
    assert float(reverse[0][2]) == pytest.approx(-float(field[0][2]), rel=1e-14)


def test_weighted_metric_exact_example():
    # B=1, frozen L=2, recovered P=1.5 -> R=0.5.
    a = dict(fine_A=np.array([[1.]]), fine_b=np.array([2.]), fine_weights=np.array([1.]))
    r = s.metric(a, [-1.], [-.5], 0)
    assert Q(r['ratio']) == Q('.5')
