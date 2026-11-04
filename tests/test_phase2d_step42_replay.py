"""STEP42 regressions: independent assertions and rejection of false acceptance."""
from decimal import Decimal as D
import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step42_replay as r


def test_actual_solver_objective_and_interior_kkt():
    M = np.array([[2.,0.],[0.,3.],[1.,1.]])
    y = M@np.array([.25,-.5])
    fit, record = r.solve(M,y)
    assert np.max(abs(fit.x-[.25,-.5])) < 1e-14
    assert record['passed'] and record['certificate']['verified']
    assert abs(float(record['certificate']['objective'])-.5*np.sum((M@fit.x-y)**2)) < 1e-27
    assert record['nit'] == 0 and record['status'] == 3


def test_active_constraints_and_feasibility():
    fit, record = r.solve(np.eye(2), np.array([3.,-3.]))
    assert np.max(abs(fit.x)) <= 1
    assert record['passed']
    assert float(record['certificate']['stationarity']) <= 1e-12
    assert not r.certificate(np.eye(2),np.zeros(2),np.array([1.1,0.]))['verified']
    assert not r.certificate(np.eye(2),np.ones(2),np.zeros(2))['verified']


@pytest.mark.parametrize('bad',[np.nan,np.inf,-np.inf])
def test_reject_nonfinite(bad):
    with pytest.raises(ValueError):
        r.solve(np.array([[bad]]),np.ones(1))
    with pytest.raises(ValueError):
        r.recovery(bad,3,2)


def test_correct_derivative_and_precision():
    value = r.recovery(1,3,2)
    assert list(map(D,value['derivatives_B_L_P'])) == [D('.25'),D('.25'),D('-.5')]
    h = D('1e-20')
    for i,g in enumerate(map(D,value['derivatives_B_L_P'])):
        lo,hi = [D(1),D(3),D(2)],[D(1),D(3),D(2)]
        lo[i] -= h; hi[i] += h
        slope = (D(r.recovery(*hi)['ratio'])-D(r.recovery(*lo)['ratio']))/(2*h)
        assert abs(slope-g) < D('1e-7')
    assert r.recovery(1,3,2,60)['ratio'] == value['ratio'] == '0.5'


def test_direct_field_recovery_matches_analytical_example():
    a = dict(fine_A=np.array([[1.,0.]]),fine_b=np.array([1.]),fine_weights=np.array([1.]))
    # B=2, L=1, P=1.5; exact quotient = 1/2, negative denominator retained.
    value = r.metric(a,np.array([1.,0.]),np.array([.5,0.]),0)
    assert D(value['ratio']) == D('.5')
    assert list(map(D,value['rms_T'])) == [D(2),D(1),D('1.5')]
    base = r.recovery(D(1),D(3),D(2))
    candidate = r.recovery(D(1),D(3)+D('1e-15'),D(2))
    effect = r.differential(base,candidate)
    assert D(effect['terms_B_L_P'][1]) > 0
    assert abs(D(effect['nonlinear_remainder'])) < D('1e-29')


def test_guard_and_high_precision_failure():
    with pytest.raises(ValueError,match='guard'):
        r.recovery(D(1),D(1)+D('1e-16'),D(1))
    assert not r.validation.agrees(D('-.414688997080917109499'),D('-.414688997049301'))
    for invalid in (True,'1',D('NaN')):
        with pytest.raises(ValueError):
            r.recovery(invalid,3,2)


def test_history_preserves_failures_and_rejects_duplicate(tmp_path):
    p = tmp_path/'failed.json'
    original = dict(reference=1.,candidate=2.,pass_=False,failures=1,status='FAIL')
    p.write_text(json.dumps(original))
    value = r.historical([p])
    assert value['records'][0]['original'] == original
    assert value['records'][0]['sha256'] == r.transport.sha(p)
    with pytest.raises(ValueError,match='Duplicate'):
        r.historical([p,p])
    original['status'] = 'PASS'
    p.write_text(json.dumps(original))
    with pytest.raises(ValueError):
        r.historical([p])
    assert r.historical([])['status'] == 'MISSING_EVIDENCE'
    p.write_text(json.dumps([dict(high_reference='1',high_candidate='2',high_pass=True)]))
    with pytest.raises(ValueError,match='high-precision'):
        r.historical([p])


def test_missing_evidence_and_duplicate_keys(tmp_path):
    with pytest.raises(FileNotFoundError):
        r.load_capture(tmp_path)
    p = tmp_path/'dup.json'; p.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError,match='Duplicate'):
        r.transport.load(p)
    with pytest.raises(FileNotFoundError):
        r.compare(tmp_path)


def test_solver_options_are_original():
    assert r.OPTIONS == dict(method='trf',lsq_solver='exact',bounds=(-1,1),tol=1e-12,max_iter=1000)
    assert 'x0' not in r.OPTIONS


def test_false_solver_certificate_rejected():
    _,record = r.solve(np.eye(2),np.array([.25,-.5]))
    record['currents_A'] = [0.]*24
    record['currents_A_binary64_le'] = np.zeros(24,dtype='<f8').tobytes().hex()
    value = dict(cases={case:record.copy() for case in r.CASES})
    r.require_solve_record(value)
    value['cases']['dense']['currents_A_binary64_le'] = 'f'*(24*16)
    with pytest.raises(ValueError,match='transport'):
        r.require_solve_record(value)
    value['cases']['dense']['currents_A_binary64_le'] = record['currents_A_binary64_le']
    record['certificate']['stationarity'] = '1'
    with pytest.raises(ValueError,match='certificate'):
        r.require_solve_record(value)
    with pytest.raises(ValueError,match='cases'):
        r.require_solve_record(dict(cases={}))


def test_environment_provenance():
    with r.threadpool_limits(limits=1):
        env = r.environment()
    assert all(env[k] for k in ('python','executable','numpy','scipy','machine','numerical_config','head','source_sha256'))
    assert env['loaded_threadpools']
    assert all(v['num_threads'] == 1 for v in env['loaded_threadpools'])
    assert r.verdict()['production_acceptance'] == r.verdict()['scientific_comparison'] == 'FAIL'


def captures():
    root = Path(__file__).resolve().parents[1]/'results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/github-hosted'
    return sorted(p.parent for p in root.rglob('problem-sha256.json') if (p.parent/'input-sha256.json').is_file())


@pytest.mark.parametrize('capture',captures())
def test_captured_exact_matrices_and_identity(capture):
    data,a,identity = r.load_capture(capture)
    assert identity['input_sha256'] == r.transport.sha(capture/'inputs.json')
    assert all(all(v.values()) for v in identity['exact_reconstruction'].values())
    for case in r.CASES:
        assert np.isfinite(a[case+'_M']).all()
        assert np.max(abs(a[case+'_x'])) <= 1
        r.transport.solver_spec(data['cases'][case])
    with pytest.raises(ValueError,match='SHA256'):
        r.load_capture(capture,'0'*64)


def test_corrupt_payload_and_missing_matrix():
    paths = captures()
    if not paths:
        pytest.skip('Historical artifacts unavailable; hosted fresh captures tested separately')
    value = r.transport.load(paths[0]/'inputs.json')
    value['arrays'].pop('dense_M')
    with pytest.raises(ValueError,match='Incomplete'):
        r.validation.reconstruct(value)
    with pytest.raises(ValueError):
        r.transport.unpack(dict(shape=[1],binary64_le='ff'))


def test_exact_source_seal_rejection(tmp_path):
    with pytest.raises(ValueError,match='source'):
        r.validation.source_check(dict(head='0'*40,sha256={'missing.py':'0'*64}),'0'*40,tmp_path)
