import math
import json
from decimal import Decimal, localcontext
import numpy as np
import pytest
from stellarator_robust.fault_metrics import stable_recovery
from stellarator_robust.phase2c import collector


def test_cancellation_against_independent_decimal():
    # Nonzero baseline residual and tiny current increments reproduce cancellation.
    A=np.array([[1e-8,2e-8],[3e-8,-1e-8],[2e-8,1e-8]])
    b=np.array([2.5e-5,2.6e-5,2.7e-5]); w=np.array([.2,.3,.5])
    currents=[np.array([1.,2.]),np.array([1.,1.999]),np.array([1.0001,1.9991])]
    result=stable_recovery(A,b,w,*currents)
    with localcontext() as ctx:
        ctx.prec=80; d=lambda x:Decimal.from_float(float(x))
        rms=[]
        for cur in currents:
            residual=[d(bb)+sum((d(a)*d(x) for a,x in zip(row,cur)),Decimal(0)) for bb,row in zip(b,A)]
            rms.append(sum((d(ww)*r*r for ww,r in zip(w,residual)),Decimal(0)).sqrt())
        exact=float((rms[1]-rms[2])/(rms[1]-rms[0]))
    assert abs(result['fractional_recovery']-exact)<1e-14
    assert result['evaluation_version']=='residual-energy-v3'


def test_guard_and_negative_recovery_preserved():
    A=np.eye(2); b=np.ones(2); w=np.array([.5,.5]); x=np.zeros(2)
    assert stable_recovery(A,b,w,x,x,x)['fractional_recovery'] is None
    y=np.array([.1,.1]); z=np.array([.2,.2])
    assert stable_recovery(A,b,w,x,y,z)['fractional_recovery']==pytest.approx(-1.)


@pytest.mark.parametrize('value',[math.nan,math.inf,-math.inf])
def test_nonfinite_inputs_fail(value):
    with pytest.raises(ValueError): stable_recovery(np.eye(2),[value,1.],[.5,.5],[0.,0.],[1.,0.],[0.,1.])


def test_invalid_shapes_and_weights_fail():
    for weights in ([1.],[-1.,2.],[0.,0.]):
        with pytest.raises(ValueError): stable_recovery(np.eye(2),[1.,1.],weights,[0.,0.],[1.,0.],[0.,1.])
    for invalid in ([True,True],['1','2'],[1j,2j]):
        with pytest.raises(ValueError): stable_recovery(np.eye(2),invalid,[.5,.5],[0.,0.],[1.,0.],[0.,1.])


def test_exhaustive_fail_closed_inventory():
    errors=[]; records=[]
    collector(errors)({'a':1.,'b':2.,'c':{'d':[3.,4.]}},{'a':1.1,'b':float('nan'),'c':{'d':[3.1,4.]}},records=records)
    assert {r['path'] for r in errors}=={'/a','/b','/c/d/0'}
    assert len(records)==2


def test_exact_random_draws_stay_exact():
    errors=[]
    collector(errors)([1.],[math.nextafter(1.,2.)],exact=True)
    assert len(errors)==1


def test_missing_and_invalid_evidence_fail():
    errors=[]
    collector(errors)({'a':1.},{})
    collector(errors)(1.,True)
    assert len(errors)==2


def versioned_bundle(path):
    from test_phase2b_evidence import bundle
    from stellarator_robust.phase2c import VERSION,sha
    root=bundle(path)
    q=json.loads((root/'quick/results.json').read_text())
    q['metadata']['config']['fault_metric_version']='residual-energy-v3'
    q['faults']=[dict(failed=0,fractional_recovery=.25,recovery_evidence=dict(
        evaluation_version='residual-energy-v3',fractional_recovery=.25,solver_success=True))]
    (root/'quick/results.json').write_text(json.dumps(q))
    (root/'study/phase1_input.json').write_bytes((root/'quick/results.json').read_bytes())
    study=json.loads((root/'study/study.json').read_text()); study['phase1_sha256']=sha(root/'quick/results.json')
    (root/'study/study.json').write_text(json.dumps(study))
    record=json.loads((root/'execution.json').read_text())
    record.update(benchmark_version=VERSION,quick_sha256=sha(root/'quick/results.json'),study_sha256=sha(root/'study/study.json'))
    (root/'execution.json').write_text(json.dumps(record))
    return root


def test_new_benchmark_repeats_and_reports_every_scientific_failure(tmp_path):
    from stellarator_robust.phase2c import pair,ScientificMismatch,sha
    a=versioned_bundle(tmp_path/'a'); b=versioned_bundle(tmp_path/'b')
    assert pair(a,b)['status']=='PASS'
    q=json.loads((b/'quick/results.json').read_text()); q['faults'][0]['fractional_recovery']=.35
    q['currents_A']['dense'][0]+=1.
    (b/'quick/results.json').write_text(json.dumps(q)); (b/'study/phase1_input.json').write_bytes((b/'quick/results.json').read_bytes())
    s=json.loads((b/'study/study.json').read_text()); s['values']=[1.]; s['phase1_sha256']=sha(b/'quick/results.json')
    (b/'study/study.json').write_text(json.dumps(s))
    r=json.loads((b/'execution.json').read_text()); r.update(quick_sha256=sha(b/'quick/results.json'),study_sha256=sha(b/'study/study.json'))
    (b/'execution.json').write_text(json.dumps(r))
    with pytest.raises(ScientificMismatch) as err: pair(a,b)
    report=err.value.report
    assert report['status']==report['study_comparison']['status']=='FAIL'
    assert {f['path'] for f in report['failures']}=={'/quick/currents_A/dense/0','/quick/faults/0/fractional_recovery','/values/0'}


def test_old_version_cannot_be_presented_as_new(tmp_path):
    from stellarator_robust.phase2c import pair
    a=versioned_bundle(tmp_path/'a'); b=versioned_bundle(tmp_path/'b')
    q=json.loads((b/'quick/results.json').read_text()); q['metadata']['config'].pop('fault_metric_version')
    (b/'quick/results.json').write_text(json.dumps(q))
    with pytest.raises(AssertionError,match='Wrong fault metric'): pair(a,b)


@pytest.mark.parametrize('tamper',['input_hash','precision','value','nonfinite','missing_fault','solver'])
def test_independent_audit_tampering_fails_closed(tmp_path,monkeypatch,tamper):
    import stellarator_robust.phase2c as contract
    def write(name,data): (tmp_path/name).write_text(json.dumps(data))
    (tmp_path/'quick').mkdir(); write('fault-reference-inputs.json',{})
    q=dict(faults=[dict(failed=0,fractional_recovery=.25,recovery_evidence=dict(fractional_recovery=.25,solver_success=True))])
    write('quick/results.json',q)
    record=dict(benchmark_version=contract.VERSION,quick_sha256=contract.sha(tmp_path/'quick/results.json'),study_sha256='a'*64)
    monkeypatch.setattr(contract,'previous_complete',lambda _:record)
    write('legacy-scientific-comparison.json',dict(status='PASS',quick_sha256=record['quick_sha256'],study_sha256=record['study_sha256']))
    audit=dict(status='PASS',quick_sha256=record['quick_sha256'],checks={'verified':True},
        reference_inputs_sha256=contract.sha(tmp_path/'fault-reference-inputs.json'),
        faults=[dict(failed=0,stable=.25,decimal_90='.25',precision_converged=True,reference_agreement=True)])
    write('fault-audit.json',audit)
    assert contract.require_complete(tmp_path)==record
    if tamper=='input_hash': audit['reference_inputs_sha256']='0'*64
    elif tamper=='precision': audit['faults'][0]['precision_converged']=False
    elif tamper=='value': audit['faults'][0]['decimal_90']='.5'
    elif tamper=='nonfinite': audit['faults'][0]['decimal_90']='NaN'
    elif tamper=='missing_fault': audit['faults']=[]
    elif tamper=='solver':
        q['faults'][0]['recovery_evidence']['solver_success']=False; write('quick/results.json',q)
    write('fault-audit.json',audit)
    with pytest.raises(AssertionError): contract.require_complete(tmp_path)
