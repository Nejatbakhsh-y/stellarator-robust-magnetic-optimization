"""Independent diagnostic guards, including active constrained optima."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step33 as d


def test_decimal_kkt_constrained_signs_and_feasibility():
    M = np.eye(2); y = np.array([2., -2.])
    assert d.decimal_kkt(M, y, np.array([1., -1.]))['status'] == 'PASS'
    assert d.decimal_kkt(M, y, np.array([.9, -.9]))['status'] == 'FAIL'
    assert d.decimal_kkt(M, y, np.array([2., -2.]))['status'] == 'FAIL'


def test_decimal_kkt_coupled_interior():
    M = np.array([[1., 2.], [3., -1.], [0., 1.]])
    x = np.array([.25, -.5]); y = M@x
    assert d.Decimal(d.decimal_kkt(M, y, x)['kkt_max']) == 0
    assert d.decimal_kkt(M, y, x+1e-4)['status'] == 'FAIL'


def test_relabelled_windows_cannot_supply_linux_cell():
    env = dict(platform='Windows-10', python='3.11.9', numpy='2.4.6', scipy='1.17.1')
    d.cohort_environment('windows-reference', env)
    with pytest.raises(ValueError): d.cohort_environment('linux-reference', env)
    env['platform'] = 'Linux-6'
    d.cohort_environment('linux-reference', env)
    with pytest.raises(ValueError): d.cohort_environment('linux-numpy-sensitivity', env)


def test_nonfinite_kkt_rejected():
    with pytest.raises(ValueError): d.decimal_kkt(np.eye(1), np.array([np.nan]), np.zeros(1))


@pytest.mark.parametrize('x,success', [(np.nan, True), (np.inf, True),
    (1.01, True), (0.5, True), (0., False), (0., 'True')])
def test_probe_success_does_not_certify_invalid_solution(x, success):
    from types import SimpleNamespace
    d.require_candidate(np.eye(1), np.zeros(1), SimpleNamespace(x=np.zeros(1), success=True))
    with pytest.raises(ValueError):
        d.require_candidate(np.eye(1), np.zeros(1), SimpleNamespace(x=np.array([x]), success=success))


@pytest.mark.parametrize('damage', ['empty_decimal', 'missing_precision', 'empty_probes', 'nan', 'infinity', 'negative', 'kkt', 'violation', 'truthy_success'])
def test_step33_local_gate_rejects_incomplete_or_invalid_evidence(monkeypatch, damage):
    monkeypatch.setattr(d, '_require_replay', lambda result: None)
    check = dict(decimal={str(p): dict(precision=p, status='PASS', objective='0',
                 kkt_max='0', constraint_violation='0') for p in (60, 90)},
                 perturbations={key: {'success': True} for key in ('M', 'y')},
                 unperturbed_probe={'success': True})
    import copy
    result = dict(step33={name: copy.deepcopy(check) for name in d.s.CASES},
                  step33_fields={'0': {'comparison': {'status': 'PASS'}}})
    d.require_replay(result)
    target = result['step33']['dense']
    if damage == 'empty_decimal': target['decimal'] = {}
    elif damage == 'missing_precision': del target['decimal']['90']
    elif damage == 'empty_probes': target['perturbations'] = {}
    elif damage == 'truthy_success': target['unperturbed_probe']['success'] = 'False'
    else:
        key, value = {'nan': ('objective', 'NaN'), 'infinity': ('kkt_max', 'Infinity'),
                      'negative': ('objective', '-1'), 'kkt': ('kkt_max', '1e-11'),
                      'violation': ('constraint_violation', '1e-20')}[damage]
        target['decimal']['90'][key] = value
    with pytest.raises(ValueError):
        d.require_replay(result)
