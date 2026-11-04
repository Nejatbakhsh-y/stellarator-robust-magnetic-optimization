"""Adversarial acceptance tests. Passing software tests cannot certify science."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import json
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step41_acceptance as s
import phase2d_step40_validation as backend


def test_derivative_sign_and_exact_quotient_coefficients():
    r = s.recovery(1,3,2)
    assert list(map(D,r['derivatives_B_L_P'])) == [D('.25'),D('.25'),D('-.5')]
    assert D(r['derivatives_B_L_P'][1]) != (D(1)-D(2))/(D(3)-D(1))**2
    assert s.mathematics()['status'] == 'VERIFIED'


@pytest.mark.parametrize('values',[(1,3,2),(0,2,3),(-2,-5,1),('1e-5','1.000001e-5','1.0000005e-5')])
def test_finite_difference(values):
    for digits in (60,90):
        r = s.recovery(*values,digits)
        with localcontext() as ctx:
            ctx.prec = 90
            for g,fd in zip(map(D,r['derivatives_B_L_P']),map(D,r['finite_difference_B_L_P'])):
                assert abs(g-fd) <= max(D(1),abs(g))*D('2e-30')


def test_high_precision_and_context_independence():
    assert s.recovery(1,4,3)['ratio'] == '0.'+'3'*90
    assert s.scalar(.1) == D.from_float(.1)
    with localcontext() as ctx:
        ctx.prec = 2
        assert not s.agrees('1.0000000001','1')
        assert s.agrees('1.000000000001','1')


@pytest.mark.parametrize('gap',['0','1e-16','1e-15','-1e-15'])
def test_near_zero_guard(gap):
    with pytest.raises(ValueError,match='guard'):
        s.recovery(0,gap,1)


@pytest.mark.parametrize('bad',[True,None,[],float('nan'),float('inf'),'NaN','Infinity','junk'])
def test_invalid_numbers(bad):
    with pytest.raises(ValueError):
        s.scalar(bad)


def test_missing_inputs(tmp_path):
    verdict,details = s.audit(tmp_path/'missing',tmp_path/'39',tmp_path/'40',tmp_path,numerical=False)
    assert verdict['diagnostic_status'] == 'INCOMPLETE'
    assert verdict['scientific_comparison'] == 'INCONCLUSIVE'
    assert verdict['production_acceptance'] == 'FAIL'
    assert details['errors']


def test_corrupted_sha_manifest_and_missing_historical_artifact(tmp_path):
    p = tmp_path/'artifact.json'
    p.write_text('{}')
    m = tmp_path/'manifest.json'
    m.write_text(json.dumps({p.name:'0'*64}))
    with pytest.raises(ValueError,match='mismatching'):
        s.transport.manifest(m)
    m.write_text(json.dumps({'missing.json':s.transport.sha(p)}))
    with pytest.raises(ValueError,match='Missing'):
        s.transport.manifest(m)


def test_duplicate_manifest_and_nonfinite_json(tmp_path):
    p = tmp_path/'manifest.json'
    for text in ['{"x":"a","x":"b"}','{"x":NaN}','{"x":1e999}']:
        p.write_text(text)
        with pytest.raises(ValueError):
            s.transport.load(p)


def row():
    return dict(reference=1.,candidate=1.,pass_=True,high_reference='1',high_candidate='1',
                high_pass=True,run='41257645149',origin='windows-reference',worker='linux-reference',
                case='row3',input_sha256='a'*64,result_sha256='b'*64,reference_sha256='c'*64,
                **{'pass':True})


def test_inconsistent_comparisons_and_missing_record():
    r = row()
    assert s.comparison(r)['classification']=='VERIFIED'
    for patch in [{'candidate':2.},{'high_candidate':'2'},{'result_sha256':'broken'},{'pass':1}]:
        with pytest.raises(ValueError):
            s.comparison(dict(r,**patch))
    with pytest.raises(ValueError,match='Missing'):
        s.comparison({})


@pytest.mark.parametrize('ref,cur',[(-.414688997029067,-.4146889970636461),(.16726624849750296,.16726624849478555)])
def test_historical_recovery_failures_preserved(ref,cur):
    assert not s.agrees(cur,ref)
    assert s.policy([],['historical'])['scientific_comparison']=='FAIL'


def test_singular_matrix():
    result = backend.conditioning([[1.,1.],[2.,2.]])
    assert result['rank_deficient'] and result['effective_rank']==1
    assert result['condition'] is None
    assert backend.qr_reference([[1.,1.],[2.,2.]],[1.,2.])['status']=='NOT_CERTIFIED'


def test_ill_conditioned_matrix():
    result = backend.conditioning(np.diag([1.,1e-10]))
    assert result['effective_rank']==2
    assert result['condition']==pytest.approx(1e10)


def test_kkt_feasibility_optimality_and_dual():
    assert D(backend.kkt([[2.]],[1.],[.5])['kkt_max'])==0
    assert D(backend.kkt([[2.]],[1.],[0.])['stationarity'])==2
    assert D(backend.kkt([[1.]],[0.],[1.1])['primal'])>0
    assert D(backend.kkt([[1.]],[2.],[1.])['kkt_max'])==0
    assert D(backend.kkt([[1.]],[0.],[0.],[-1.],[0.])['dual'])==1
    assert D(backend.kkt([[1.]],[0.],[0.],[1.],[1.])['complementarity'])==1


def test_active_set_instability():
    interior = backend.kkt([[1.]],[.999],[.999])
    bound = backend.kkt([[1.]],[1.001],[1.])
    assert backend.active_change(interior,bound)
    assert not backend.active_change(bound,bound)


@pytest.mark.parametrize('key,value',[('scientific_comparison','PASS'),('production_acceptance','PASS'),
    ('scientific_status','PASS'),('causal_root_cause','CONCLUSIVE'),('evidence_authentication','COMPLETE')])
def test_unsupported_acceptance_or_causal_conclusion(key,value):
    expected = s.policy([],['failure'])
    with pytest.raises(ValueError,match='Unsupported'):
        s.reject_claims(dict(expected,**{key:value}),expected)


def test_exact_frozen_input_fingerprints(tmp_path):
    p = tmp_path/'input.json'
    p.write_text('{}')
    digest = s.transport.sha(p)
    assert backend.seal(p,digest)==digest
    p.write_text('{"changed":true}')
    with pytest.raises(ValueError,match='fingerprint'):
        backend.seal(p,digest)


def test_complete_grid_duplicate_missing_and_input_identity(monkeypatch,tmp_path):
    entries = [dict(id=i+1,name=f'step33-{kind}-{cohort}-{run}-1')
               for i,(run,kind,cohort) in enumerate((r,k,c) for r in s.transport.RUNS[2:]
                   for k in ('capture','replay') for c in s.transport.COHORTS)]
    def load(path):
        if path.name=='artifact-index.json':
            return {'artifacts':[e for e in entries if path.parent.name in e['name']]}
        return {'solve':{'recovery':{'row3':{'fractional_recovery':1.},'row4':{'fractional_recovery':1.}}}}
    monkeypatch.setattr(s.transport,'load',load)
    monkeypatch.setattr(s.transport,'sha',lambda path:'a'*64)
    rows = [dict(row(),run=run,origin=o,worker=w,case=c,input_sha256='a'*64,
                 result_sha256='a'*64,reference_sha256='a'*64)
            for run in s.transport.RUNS[2:] for o in s.transport.COHORTS
            for w in s.transport.COHORTS[1:] for c in ('row3','row4')]
    assert len(s.bind_comparisons(rows,tmp_path))==48
    with pytest.raises(ValueError,match='Missing'):
        s.bind_comparisons(rows[:-1],tmp_path)
    with pytest.raises(ValueError,match='Duplicate'):
        s.bind_comparisons(rows+[rows[0]],tmp_path)
    monkeypatch.setattr(s.transport,'sha',lambda path:'b'*64)
    with pytest.raises(ValueError,match='fingerprint'):
        s.bind_comparisons(rows,tmp_path)


def test_incomplete_scientific_arrays_rejected():
    with pytest.raises(ValueError,match='Incomplete'):
        backend.reconstruct({'arrays':{},'cases':{}})


def test_output_containment_and_preservation(tmp_path):
    root = tmp_path/'out'
    evidence = tmp_path/'evidence'
    assert s.output_path(root,root/'repeat',[evidence])==root/'repeat'
    for out in [tmp_path/'escape',root]:
        with pytest.raises(ValueError):
            s.output_path(root,out,[evidence])
    (root/'old').mkdir(parents=True)
    with pytest.raises(ValueError,match='overwrite'):
        s.output_path(root,root/'old',[evidence])


def test_independent_field_reference():
    square = [[-1.,-1.,0.],[1.,-1.,0.],[1.,1.,0.],[-1.,1.,0.]]
    f = backend.field([[0.,0.,0.]],square)
    assert D(f[0][0])==D(f[0][1])==0
    assert float(f[0][2])==pytest.approx(4e-7*2**.5,rel=1e-14)


def test_deterministic_repeated_execution(tmp_path):
    runs = [s.audit(tmp_path/'missing',tmp_path/'39',tmp_path/'40',tmp_path,numerical=False) for _ in range(2)]
    assert json.dumps(runs[0],sort_keys=True)==json.dumps(runs[1],sort_keys=True)
    assert s.mathematics()==s.mathematics()
