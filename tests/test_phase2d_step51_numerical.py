"""Deterministic STEP51 scientific safeguards and independent arithmetic checks."""
import importlib.util
from pathlib import Path
import sys
import zipfile
from decimal import Decimal as D, localcontext

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import phase2d_step51_numerical as s
import phase2d_step46_independent as scalar


def test_archive_authentication(tmp_path):
    path = tmp_path/'a.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('input.json',b'{}')
    seal = s.archive_tools.digest(path.read_bytes())
    assert s.archive_tools.archive(path,seal)['input.json'] == b'{}'
    with pytest.raises(ValueError,match='SHA256'):
        s.archive_tools.archive(path,'0'*64)


def test_identical_binary64_and_serialization():
    a = np.array([1.,0.])
    b = a.copy(); b[0] = np.nextafter(1.,2.)
    assert s.comparison(a,a)['bitwise_identical']
    assert not s.comparison(a,b)['bitwise_identical']
    assert s.comparison(a,b)['original_tolerance_pass']
    assert s.fingerprint(a) != s.fingerprint(b)


@pytest.mark.parametrize('x,violation', [([.5], '0'),([1.1],None)])
def test_bounds_and_kkt(x,violation):
    cert = scalar.certificate([[1.]],[.5],x)
    if violation is not None:
        assert D(cert['bound_violation']) == D(violation)
        assert D(cert['kkt_max']) == 0
    else:
        assert D(cert['bound_violation']) > 0
        assert D(cert['kkt_max']) > 0


def test_high_precision_reference():
    result = scalar.reference([[1.,0.],[0.,2.]],[.5,1.],90)
    assert result['status'] == 'INTERIOR_REFERENCE'
    assert all(abs(D(x)-D('.5')) < D('1e-80') for x in result['x'])


@pytest.mark.parametrize('failed',[3,6],ids=['row3','row4'])
def test_recovery_fault_identity(failed):
    A = [[1e-6]*7]
    dense = [1.]*7
    recovered = [1.]*7; recovered[failed] = 0; recovered[(failed+1)%7] = 2.
    value,_ = scalar.metric(A,[1e-5],[1.],dense,recovered,failed)
    assert D(value['ratio']) == 1
    assert scalar.agrees(scalar.ratio([1e-5,2e-5,1.5e-5],60)['ratio'], '.5')


def test_denominator_guard():
    with pytest.raises(ValueError,match='guard'):
        scalar.ratio([1.,1.,.5])


def test_sensitivity_remainder():
    result = scalar.intervention([[1e-6,2e-6]],[1e-5],[1.], [1.,1.],[0.,1.5],
                                [1.,1.],[0.,np.nextafter(1.5,2.)],0)
    with localcontext() as ctx:
        ctx.prec = 90
        assert abs(D(result['delta_R'])-D(result['linearized_delta_R'])-D(result['nonlinear_residual'])) < D('1e-80')


def test_missing_input_seals():
    assert s.input_seals({},'inputs.json',b'{}')['status'] == 'INCOMPLETE'


def test_input_fingerprint_rejection():
    members = {'input-sha256.json': b'{"inputs.json":"0000000000000000000000000000000000000000000000000000000000000000"}',
               'problem-sha256.json': b'{}'}
    with pytest.raises(ValueError,match='digest mismatch'):
        s.input_seals(members,'inputs.json',b'{}')


def test_field_xyz_orientation_and_convergence():
    v = np.array([[-1.,-1.,0.],[1.,-1.,0.],[1.,1.,0.],[-1.,1.,0.]])
    p = [[0.,0.,.3]]
    a,b,c = [s.integrated_field(p,v,k) for k in (8,16,32)]
    assert np.max(abs(c-b)) < np.max(abs(b-a))
    assert s.comparison(b,c)['original_tolerance_pass']
    assert np.allclose(c,-s.integrated_field(p,v[::-1],32),rtol=1e-13,atol=1e-20)
    assert abs(c[0,0])+abs(c[0,1]) < 1e-20
    assert c[0,2] > 0


def test_missing_archive(tmp_path):
    manifest = dict(runs=[dict(run_id=1,source_sha='0'*40,artifacts=[dict(id=1,name='missing',file='absent.zip',github_sha256='0'*64,verified_sha256='0'*64)])])
    auth,*_ = s.assess(tmp_path,manifest)
    assert auth[0]['status'] == 'REJECTED_OR_MISSING'


def test_no_false_scientific_acceptance(tmp_path,monkeypatch):
    manifest = tmp_path/'manifest.json'; manifest.write_text('{"runs": []}')
    root = tmp_path/'archives'; root.mkdir()
    out = tmp_path/'out'
    monkeypatch.setattr(s,'environment',lambda: {'scope':'test'})
    assert s.main(['--archive-root',str(root),'--manifest',str(manifest),'--output',str(out)]) == 2
    status = s.archive_tools.decode((out/'status.json').read_bytes())
    assert status['scientific_comparison'] == status['production_acceptance'] == 'FAIL'
    assert status['overall_scientific_status'] == 'INCOMPLETE'
    causal = s.archive_tools.decode((out/'causal-attribution.json').read_bytes())
    assert all(v['status'] == 'INCOMPLETE' for v in causal['controlled_configurations'].values())
    assert set(p.name for p in out.iterdir()) == {'status.json',*s.FILES}
    assert s.main(['--archive-root',str(root),'--manifest',str(manifest),'--output',str(out)]) == 1


def test_real_matrix_reconstruction_and_faults():
    # Exercise original captures, not a synthetic implementation mirror.
    root = ROOT/'results/phase2d/step49-original-archives-20261102-120255-a1314650'
    if not root.exists():
        pytest.skip('Original archives not installed')
    import phase2d_step40_validation as schema
    manifest = s.archive_tools.decode((root/'manifest.json').read_bytes())
    for run in manifest['runs']:
        for item in run['artifacts']:
            members = s.archive_tools.archive(root/item['file'],item['verified_sha256'])
            for name,raw in members.items():
                if name.split('/')[-1] != 'inputs.json':
                    continue
                data = s.archive_tools.decode(raw)
                if data.get('schema') != 'production-upstream-v1':
                    continue
                arrays = schema.reconstruct(data)
                assert data['cases']['row3']['failed'] == 3
                assert data['cases']['row4']['failed'] == 6
                assert arrays['dense_M'].shape[1] == 24
                return
    pytest.fail('No original production capture')
