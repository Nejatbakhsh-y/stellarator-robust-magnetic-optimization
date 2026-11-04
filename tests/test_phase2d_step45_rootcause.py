"""Portable mechanism tests; synthetic systems never authenticate history."""
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step45_rootcause as s
import phase2d_step42_replay as replay


def test_no_false_acceptance():
    for errors in ([],['missing evidence'],['bad SHA256']):
        status = s.policy(s.BASELINE,errors,['unverified archives'])
        assert status['scientific_comparison'] == status['production_acceptance'] == 'FAIL'
        assert status['scientific_status'] == 'PARTIAL'
        assert status['evidence_authentication'] == 'INCOMPLETE'
        assert status['causal_root_cause'] == 'INCONCLUSIVE'
        assert status['diagnostic_status'] == ('INCOMPLETE' if errors else 'COMPLETE')


def test_exact_array_bytes_include_signed_zero_and_shape():
    assert s.array_identity([0.]) != s.array_identity([-0.])
    assert s.array_identity([[1.,2.]]) != s.array_identity([1.,2.])
    assert s.array_identity([1.]) != s.array_identity([np.nextafter(1.,2.)])


def test_output_isolation(tmp_path):
    source = tmp_path/'results'/'original'; source.mkdir(parents=True)
    for out in (source,source/'new',tmp_path/'results',tmp_path/'elsewhere'):
        with pytest.raises(ValueError):
            s.output_path(tmp_path,out,[source])
    out = tmp_path/'results'/'fresh'
    assert s.output_path(tmp_path,out,[source]) == out


def test_independent_qr_svd_and_qr_driver():
    M = np.array([[2.,0.],[0.,3.],[1.,1.]])
    y = M@np.array([.25,-.5])
    value = s.kernels(M,y)
    assert not value['conditioning']['rank_deficient']
    for reference in value['decimal_qr'].values():
        assert reference['status'] == 'INTERIOR_REFERENCE'
        assert float(reference['gradient_max']) < 1e-50
        assert np.max(abs(np.array(reference['x'],float)-[.25,-.5])) < 1e-15
    assert set(value['lapack']) == {'gelsd','gelss','gelsy'}
    for row in value['lapack'].values():
        assert row['rank'] == 2 and row['certificate']['verified']
        assert bytes.fromhex(row['x_binary64_le']) == np.array(row['x'],dtype='<f8').tobytes()


@pytest.mark.parametrize('failed',[3,6])
def test_faults_one_ulp_and_nonlinear_remainder(failed):
    A = np.zeros((1,8)); A[0,failed] = 1.; A[0,0] = 1.
    a = dict(fine_A=A,fine_b=np.ones(1),fine_weights=np.ones(1))
    dense = np.zeros(8); dense[failed] = 1.
    recovered = np.zeros(8); recovered[0] = .5
    changed = recovered.copy(); changed[0] = np.nextafter(.5,1.)
    value = s.recovery_controls(a,dense,recovered,dense,changed,failed)
    with localcontext() as ctx:
        ctx.prec = 90
        assert Decimal(value['reference']['ratio']) == Decimal('.5')
        assert Decimal(value['controlled_current_contribution']) != 0
        assert Decimal(value['controlled_current_contribution']) == Decimal(value['candidate']['ratio'])-Decimal('.5')
    assert value['field_matrix_contribution'] == value['disturbance_contribution'] == value['weight_contribution'] == '0'
    assert 'nonlinear_remainder' in value['differential']


def test_snapshot_detects_changed_historical_bytes(tmp_path):
    file = tmp_path/'result.json'; file.write_text('{"scientific_comparison":"FAIL"}')
    before = s.snapshot(tmp_path)
    file.write_text('{"scientific_comparison":"PASS"}')
    assert before != s.snapshot(tmp_path)


def test_archive_bytes_are_distinct_from_extracted_integrity(tmp_path):
    archive = tmp_path/'synthetic.zip'
    extracted = tmp_path/'extracted'; extracted.mkdir()
    (extracted/'input.json').write_bytes(b'{"synthetic_test_fixture":true}')
    with zipfile.ZipFile(archive,'w') as z:
        z.write(extracted/'input.json','input.json')
    seal = s.sha(archive)
    value = s.archive_identity(archive,seal,extracted)
    assert value['byte_identity'] == 'MATCH'
    assert value['github_origin'] == 'NOT_ESTABLISHED_BY_THIS_CHECK'
    with pytest.raises(ValueError,match='archive SHA256'):
        s.archive_identity(archive,'0'*64,extracted)
    (extracted/'input.json').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='coverage or SHA256'):
        s.archive_identity(archive,seal,extracted)


def test_archive_path_escape_and_missing_bytes(tmp_path):
    with pytest.raises(FileNotFoundError):
        s.archive_identity(tmp_path/'missing.zip','0'*64,tmp_path)
    archive = tmp_path/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('../escape.json','{}')
    with pytest.raises(ValueError,match='Unsafe archive'):
        s.archive_identity(archive,s.sha(archive),tmp_path)


def test_missing_evidence_is_not_synthetic_authentication(tmp_path):
    with pytest.raises(FileNotFoundError):
        s.historical(tmp_path)
    with pytest.raises(FileNotFoundError):
        s.investigate(tmp_path)
    with pytest.raises(FileNotFoundError):
        s.reciprocal(tmp_path,tmp_path,s.BASELINE)


@pytest.mark.parametrize('bad',[np.nan,np.inf,-np.inf])
def test_nonfinite_rejected(bad):
    with pytest.raises(ValueError):
        s.kernels(np.array([[bad]]),np.ones(1))


def test_original_gates_and_derivative():
    assert replay.OPTIONS == dict(method='trf',lsq_solver='exact',bounds=(-1,1),tol=1e-12,max_iter=1000)
    row = replay.recovery(1,3,2)
    assert list(map(Decimal,row['derivatives_B_L_P'])) == [Decimal('.25'),Decimal('.25'),Decimal('-.5')]
    with pytest.raises(ValueError,match='guard'):
        replay.recovery(Decimal(1),Decimal(1)+Decimal('1e-16'),Decimal(1))


def test_manifest_non_circular(tmp_path):
    s.write(tmp_path/'status.json',s.policy(s.BASELINE,[],[]))
    files = s.snapshot(tmp_path)
    s.write(tmp_path/'output-manifest.json',dict(outputs=files))
    assert 'output-manifest.json' not in files
    assert json.loads((tmp_path/'output-manifest.json').read_text())['outputs']['status.json'] == s.sha(tmp_path/'status.json')


@pytest.mark.parametrize('mutation',['python','head','source','hash','missing_cohort'])
def test_worker_manifest_and_environment_guards(tmp_path,mutation):
    folder = tmp_path/'step42-windows-reference'; folder.mkdir()
    source = tmp_path/'source.py'; source.write_text('synthetic portable fixture\n')
    env = dict(python='3.11.9',head=s.BASELINE,source_sha256={'source.py':s.sha(source)})
    if mutation == 'python':
        env['python'] = '3.12.0'
    if mutation == 'head':
        env['head'] = '0'*40
    if mutation == 'source':
        env['source_sha256']['source.py'] = '0'*64
    s.write(folder/'environment.json',env)
    s.write(folder/'manifest.json',{'environment.json':s.sha(folder/'environment.json')})
    if mutation == 'hash':
        (folder/'environment.json').write_text('{}')
    with pytest.raises((ValueError,FileNotFoundError)):
        s.reciprocal(tmp_path,tmp_path,s.BASELINE)


def test_exact_tolerance_boundary_and_wrong_settings():
    import phase2d_step44_acceptance as h
    from fractions import Fraction
    limit = Fraction('1e-13')+Fraction('1e-11')
    assert h.agrees(1+limit,1)
    assert not h.agrees(1+limit+Fraction(1,10**40),1)
    with pytest.raises((ValueError,KeyError)):
        replay.transport.solver_spec(dict(arguments=dict(bounds=[-1,1],tol=1e-8,max_iter=1000)))


def test_workflow_preserves_failures_and_run_identity():
    workflow = (Path(__file__).resolve().parents[1]/'.github/workflows/phase2d-step45-causal.yml').read_text()
    assert workflow.startswith('name: Phase 2D STEP 45 independent causal validation\n')
    assert 'continue-on-error' not in workflow and '|| true' not in workflow
    assert 'codex/phase2d-upstream-attribution' in workflow
    assert workflow.count('numpy:') == 8
    assert 'github.run_id' in workflow and 'github.run_attempt' in workflow
