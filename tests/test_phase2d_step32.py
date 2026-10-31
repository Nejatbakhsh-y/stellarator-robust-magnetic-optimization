"""Independent STEP 32 contracts. Synthetic matrices exercise active constraints."""
import copy
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step32 as s


def test_binary64_fingerprints_preserve_signed_zero():
    assert s.fingerprint(s.pack([0.])) != s.fingerprint(s.pack([-0.]))
    assert np.array_equal(s.unpack(s.pack([1., -0., np.nextafter(1., 2.)])), [1., -0., np.nextafter(1., 2.)])


def test_problem_excludes_results_but_includes_constraints():
    data = dict(config={'imax_A': 3000}, arrays={'dense_M': s.pack([[1.]]), 'dense_y': s.pack([2.])},
                cases={'dense': dict(arguments={'bounds': [-1, 1]}, implicit_method='trf', implicit_lsq_solver='exact', cost=1.)})
    digest = s.fingerprint(s.problem(data))
    data['cases']['dense']['cost'] = 2.
    assert s.fingerprint(s.problem(data)) == digest
    data['cases']['dense']['arguments']['bounds'][0] = -2
    assert s.fingerprint(s.problem(data)) != digest


@pytest.mark.parametrize('x,y,kkt,violation', [(1., 2., 0., 0.), (-1., -2., 0., 0.), (0., 2., 2., 0.), (1.1, 2., 0., .1), (1., 0., 1., 0.)])
def test_box_kkt_signs_and_feasibility(x, y, kkt, violation):
    m = s.optimality(np.eye(1), np.array([y]), np.array([x]))
    assert m['kkt_max'] == pytest.approx(kkt)
    assert m['constraint_violation'] == pytest.approx(violation)


@pytest.mark.parametrize('bad', [np.nan, np.inf])
def test_invalid_solver_outputs(bad):
    with pytest.raises(ValueError):
        s.optimality(np.eye(1), np.zeros(1), np.array([bad]))


def test_independent_constrained_reference_active_and_free():
    M = np.diag([1., 2., 3.]); y = np.array([2., -4., .75])
    result = s.coordinate_reference(M, y, np.zeros(3))
    assert result['status'] == 'PASS'
    np.testing.assert_allclose(s.unpack(result['x']), [1., -1., .25], rtol=0, atol=1e-14)
    assert result['metrics']['active_lower'] == [1]
    assert result['metrics']['active_upper'] == [0]


def test_conditioning_and_effective_rank():
    m = s.optimality(np.diag([1., 1e-8]), np.zeros(2), np.zeros(2))
    assert m['rank'] == 2 and m['condition'] == pytest.approx(1e8)
    m = s.optimality(np.diag([1., 0.]), np.zeros(2), np.zeros(2))
    assert m['rank'] == 1 and m['condition'] is None


@pytest.mark.parametrize('wrong', ['head', 'sha256'])
def test_wrong_commit_or_source(wrong):
    left = {'head': 'abc', 'sha256': {'src/a.py': '123'}}
    right = copy.deepcopy(left); right[wrong] = 'incorrect'
    with pytest.raises(ValueError):
        s.source_check(left, right, 'abc')


def test_missing_artifacts_fail_before_comparison(tmp_path):
    with pytest.raises((FileNotFoundError, ValueError)):
        s.comparisons(tmp_path, 'abc')


def test_manifest_exact_coverage_and_historical_preservation(tmp_path):
    root = tmp_path/'artifact'; root.mkdir()
    original = b'failed scientific comparison\n'
    (root/'failed.txt').write_bytes(original)
    s.write(root/'status.json', {'diagnostic_status': 'PASS'})
    s.manifest(root); s.verified(root)
    (root/'extra.txt').write_text('unlisted')
    with pytest.raises(ValueError): s.verified(root)
    assert (root/'failed.txt').read_bytes() == original


def test_incorrect_pass_rejected(tmp_path):
    s.write(tmp_path/'status.json', {'diagnostic_status': 'FAIL'})
    s.manifest(tmp_path)
    with pytest.raises(ValueError): s.verified(tmp_path)


def test_incomplete_scientific_evidence():
    with pytest.raises(ValueError): s.require_replay({'optimality': {}})


@pytest.mark.parametrize('row,failed', [('row3', 0), ('row4', 1)])
def test_faults_high_precision_and_ratio_guard(row, failed):
    a = dict(fine_A=np.eye(2), fine_b=np.array([2., 3.]), fine_weights=np.array([.5, .5]))
    currents = dict(dense=np.array([.1, .2]), recovered=np.array([.0, .0]))
    low = s.decimal_metric(a, currents, failed, 60)
    high = s.decimal_metric(a, currents, failed, 90)
    assert abs(s.Decimal(low['ratio'])-s.Decimal(high['ratio'])) < s.Decimal('1e-50')
    currents['dense'][:] = 0
    assert s.decimal_metric(a, currents, failed)['ratio'] is None


def test_recovery_differential_independent_exact_case():
    # R=.5, denominator=2; change P only: dR=-dP/2 exactly.
    left = dict(rms_T=['1', '3', '2'], ratio='.5')
    right = dict(rms_T=['1', '3', '2.000000000002'], ratio='.499999999999')
    d = s.differential(left, right)
    assert s.Decimal(d['observed']) == s.Decimal('-1e-12')
    assert s.Decimal(d['nonlinear_remainder']) == 0


def test_support_decisions_separate_currents():
    trace = dict(deletion=[dict(support=[0, 1], removed=1, x=[1, 0])], sparse=[], fault_supports={'row3': [0]}, dense_active=[0, 1])
    other = copy.deepcopy(trace); other['deletion'][0]['x'] = [1.01, .01]
    assert s.support_decisions(trace) == s.support_decisions(other)
    other['deletion'][0]['removed'] = 0
    assert s.support_decisions(trace) != s.support_decisions(other)


def test_four_way_design_requires_all_origins_and_workers():
    assert len(s.COHORTS) == 4
    workflow = Path('.github/workflows/phase2d-step32-causal.yml').read_text(encoding='utf-8-sig')
    assert 'needs: capture' in workflow and 'needs: [capture, replay]' in workflow
    assert 'continue-on-error' not in workflow
    assert 'push:' in workflow and 'fetch-depth: 0' in workflow


def test_incomplete_source_provenance_cannot_pass():
    with pytest.raises(ValueError):
        s.source_check({'head': 'abc', 'sha256': {}}, {'head': 'abc', 'sha256': {}}, 'abc')


def test_high_precision_field_against_analytic_square():
    from stellarator_robust.upstream_attribution import decimal_field
    vertices = np.array([[-1., -1., 0.], [1., -1., 0.], [1., 1., 0.], [-1., 1., 0.]])
    result = decimal_field(np.zeros((1, 3)), vertices, 1., 90)[0]
    with s.localcontext() as context:
        context.prec = 90
        exact = 4*s.Decimal(2).sqrt()*s.Decimal('1e-7')
        assert abs(s.Decimal(result[2])-exact) < s.Decimal('1e-85')
        assert list(map(s.Decimal, result[:2])) == [0, 0]


def test_active_bound_transition():
    inside = s.optimality(np.eye(2), np.array([.9, -.9]), np.array([.9, -.9]))
    bound = s.optimality(np.eye(2), np.array([1.1, -1.1]), np.array([1., -1.]))
    assert inside['active_lower'] == inside['active_upper'] == []
    assert bound['active_lower'] == [1] and bound['active_upper'] == [0]


def test_forged_pass_with_constraint_violation_rejected():
    result = dict(optimality={name: dict(coordinate={'status': 'PASS'},
                 production={'constraint_violation': .01, 'kkt_max': 0.}) for name in s.CASES})
    with pytest.raises(ValueError): s.require_replay(result)


def test_four_way_separates_generation_solver_and_interaction():
    # Known two-factor synthetic intervention: generation +10, solver +2,
    # interaction +.5 only in the reciprocal D cell.
    result = s.reciprocal_effects([1.], [3.], [11.], [13.5])
    assert s.unpack(result['solver_on_windows_inputs'])[0] == 2
    assert s.unpack(result['solver_on_linux_inputs'])[0] == 2.5
    assert s.unpack(result['generation_on_windows_solver'])[0] == 10
    assert s.unpack(result['generation_on_linux_solver'])[0] == 10.5
    assert s.unpack(result['interaction'])[0] == .5


def test_invalid_reciprocal_cell_rejected():
    with pytest.raises(ValueError): s.reciprocal_effects([1], [2], [3], [np.nan])
