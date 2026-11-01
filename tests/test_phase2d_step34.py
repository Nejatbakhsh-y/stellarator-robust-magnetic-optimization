"""Regression for discarded scientific verdicts in STEP 32 / STEP 33."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step32 as s
from stellarator_robust import upstream_attribution as u


@pytest.mark.parametrize('gates,incomplete', [
    ({'dense': False, 'row3': True, 'row4': True}, False),
    ({'dense': True, 'row3': True, 'row4': True}, True),
    ({}, False),
])
def test_require_solve_rejects_nonpass(monkeypatch, gates, incomplete):
    monkeypatch.setattr(u, 'validate_solve', lambda *args: (gates, incomplete))
    with pytest.raises(ValueError):
        u.require_solve({}, {}, {})


@pytest.mark.parametrize('value', [None, float('nan'), float('inf'), '0.5', True])
def test_missing_or_invalid_ratio_cannot_pass(monkeypatch, value):
    monkeypatch.setattr(u, 'validate_solve', lambda *args: (dict.fromkeys(s.CASES, True), False))
    with pytest.raises(ValueError):
        u.require_solve({'recovery': {row: {'fractional_recovery': value}
                                   for row in ('row3', 'row4')}}, {}, {})


def test_replay_enforces_solve_verdict_before_diagnostics(monkeypatch):
    monkeypatch.setattr(s, 'validate_inputs', lambda data: {})
    monkeypatch.setattr(s, 'solve_inputs', lambda data: {})
    def reject(*args):
        raise ValueError('scientific gate rejected')
    monkeypatch.setattr(s, 'require_solve', reject)
    with pytest.raises(ValueError, match='scientific gate rejected'):
        s.replay({})


@pytest.mark.parametrize('value', [None, 'NaN', 'Infinity'])
def test_replay_rejects_nonfinite_decimal_ratio(value):
    result = dict(optimality={}, sensitivity={}, ratios={})
    for case in s.CASES:
        result['optimality'][case] = dict(coordinate={'status': 'PASS'},
            production=dict(constraint_violation=0., kkt_max=0.))
        result['sensitivity'][case] = {k: {'success': True} for k in
            ('bvls', 'threads1', 'threads2', 'reverse_rows', 'reverse_columns')}
    for row in ('row3', 'row4'):
        result['ratios'][row] = {p: dict(rms_T=['1', '3', '2'], denominator_T='2', ratio=value)
                                 for p in ('60', '90')}
    with pytest.raises(ValueError, match='Invalid or unavailable'):
        s.require_replay(result)


@pytest.mark.parametrize('damage', ['nan_kkt', 'negative_kkt', 'reverse_rows', 'reverse_columns'])
def test_replay_rejects_invalid_optimality_and_failed_ordering(damage):
    result = dict(optimality={}, sensitivity={}, ratios={})
    for case in s.CASES:
        result['optimality'][case] = dict(coordinate={'status': 'PASS'},
            production=dict(constraint_violation=0., kkt_max=0.))
        result['sensitivity'][case] = {k: {'success': True} for k in
            ('bvls', 'threads1', 'threads2', 'reverse_rows', 'reverse_columns')}
    for row in ('row3', 'row4'):
        result['ratios'][row] = {p: dict(rms_T=['1', '3', '2'], denominator_T='2', ratio='0.5')
                                 for p in ('60', '90')}
    s.require_replay(result)
    if damage in ('nan_kkt', 'negative_kkt'):
        result['optimality']['dense']['production']['kkt_max'] = float('nan') if damage == 'nan_kkt' else -1.
    else:
        result['sensitivity']['dense'][damage]['success'] = False
    with pytest.raises(ValueError):
        s.require_replay(result)


def test_saved_finite_ratio_must_match_sealed_inputs(monkeypatch):
    import numpy as np
    arrays = dict(fine_A=np.eye(1), fine_b=np.array([3.]), fine_weights=np.ones(1))
    data = dict(cases={r: {'failed': 0} for r in ('row3', 'row4')})
    result = dict(solve={'currents_A': {c: s.pack([-1. if c == 'dense' else 0.]) for c in s.CASES}}, ratios={})
    monkeypatch.setattr(s, 'require_solve', lambda *args: None)
    monkeypatch.setattr(s, 'require_replay', lambda *args: None)
    result['optimality'] = {}
    arrays.update(A=np.eye(1))
    data['config'] = {'imax_A': 1.}
    for case in s.CASES:
        arrays[case+'_M'], arrays[case+'_y'] = np.eye(1), np.zeros(1)
        result['optimality'][case] = {'production': s.optimality(np.eye(1), np.zeros(1),
            s.unpack(result['solve']['currents_A'][case]))}
    data['cases']['dense'] = {}
    for row in ('row3', 'row4'):
        result['ratios'][row] = {str(p): s.decimal_metric(arrays,
            dict(dense=np.array([-1.]), recovered=np.array([0.])), 0, p) for p in (60, 90)}
    s.validate_replay(result, data, arrays)
    result['optimality']['dense']['production']['kkt_max'] = 0.
    with pytest.raises(ValueError, match='Inconsistent scientific'):
        s.validate_replay(result, data, arrays)
    result['optimality']['dense']['production']['kkt_max'] = 1.
    result['ratios']['row3']['90']['ratio'] = '0.25'
    with pytest.raises(ValueError, match='Inconsistent high precision'):
        s.validate_replay(result, data, arrays)
