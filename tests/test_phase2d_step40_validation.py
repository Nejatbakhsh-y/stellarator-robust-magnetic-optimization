"""Independent mathematical regressions; successful tests cannot confer acceptance."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step40_validation as s


def test_quotient_rule_symbolic_coefficients():
    # dN=(dL-dP), dD=(dL-dB): coefficient extraction independently.
    B,L,P = D(1),D(3),D(2)
    gradient = list(map(D,s.recovery(B,L,P)['derivatives_B_L_P']))
    assert gradient == [D('.25'),D('.25'),D('-.5')]
    for dB,dL,dP in [(1,0,0),(0,1,0),(0,0,1),(2,-3,7)]:
        quotient = ((dL-dP)*(L-B)-(L-P)*(dL-dB))/(L-B)**2
        assert quotient == sum(g*v for g,v in zip(gradient,(dB,dL,dP)))
    assert gradient[1] != (B-P)/(L-B)**2


def test_high_precision_reference_and_finite_difference():
    assert s.decimal(np.float64(.1)) == D.from_float(.1)
    assert s.decimal(np.int64(2)) == D(2)
    r = s.recovery(D(1),D(4),D(3))
    assert r['ratio'].startswith('0.'+'3'*80)
    for case in [(D(1),D(3),D(2)),(D('1e-5'),D('1.000001e-5'),D('1.0000005e-5'))]:
        rr = s.recovery(*case)
        for g,fd in zip(map(D,rr['derivatives_B_L_P']),map(D,rr['finite_difference_B_L_P'])):
            assert abs(g-fd) < max(D(1),abs(g))*D('1e-35')


@pytest.mark.parametrize('gap',['0','1e-16','1e-15','-1e-15'])
def test_guard(gap):
    with pytest.raises(ValueError,match='guard'):
        s.recovery(D(0),D(gap),D(2))


@pytest.mark.parametrize('v',[float('nan'),float('inf'),D('NaN'),D('Infinity')])
def test_nonfinite(v):
    with pytest.raises(ValueError):
        s.recovery(v,3.,2.)


@pytest.mark.parametrize('v',[float('nan'),float('inf'),-float('inf')])
def test_nonfinite_kkt_and_fields(v):
    with pytest.raises(ValueError):
        s.kkt([[1.]],[0.],[v])
    with pytest.raises(ValueError):
        s.field([[v,0.,0.]],[[-1.,-1.,0.],[1.,-1.,0.],[0.,1.,0.]])


def test_singular_and_ill_conditioned():
    singular = s.conditioning([[1.,1.],[2.,2.]])
    assert singular['effective_rank'] == 1 and singular['condition'] is None
    ill = s.conditioning(np.diag([1.,1e-10]))
    assert ill['effective_rank'] == 2
    assert ill['condition'] == pytest.approx(1e10)
    assert s.qr_reference([[1.,1.],[2.,2.]],[1.,2.])['status'] == 'NOT_CERTIFIED'


def test_independent_qr_solution():
    # Exact least-squares optimum of a nonorthogonal overdetermined matrix.
    M = [[1.,0.],[1.,1.],[0.,1.]]
    y = [.25,.75,.5]
    low,high = [s.qr_reference(M,y,d) for d in (60,90)]
    assert low['status'] == high['status'] == 'INTERIOR_REFERENCE'
    assert np.array([float(v) for v in high['x']]) == pytest.approx([.25,.5])
    assert D(high['gradient_max']) < D('1e-80')
    assert s.qr_reference([[1.]],[2.])['status'] == 'NOT_CERTIFIED'


def test_kkt_stationarity_and_objective():
    assert D(s.kkt([[2.]],[1.],[.5])['kkt_max']) == 0
    wrong = s.kkt([[2.]],[1.],[0.])
    assert D(wrong['stationarity']) == 2 and D(wrong['objective']) == D('.5')
    assert D(s.kkt([[1.]],[2.],[1.])['kkt_max']) == 0
    assert D(s.kkt([[1.]],[-2.],[-1.])['kkt_max']) == 0
    assert D(s.kkt([[1.]],[0.],[1.])['stationarity']) == 1


def test_primal_dual_and_complementarity_separate():
    assert D(s.kkt([[1.]],[0.],[1.1])['primal']) > 0
    baddual = s.kkt([[1.]],[0.],[0.],[-1.],[0.])
    assert D(baddual['dual']) == 1
    badcomp = s.kkt([[1.]],[0.],[0.],[1.],[1.])
    assert D(badcomp['stationarity']) == 0
    assert D(badcomp['dual']) == 0
    assert D(badcomp['complementarity']) == 1


def test_active_set_instability():
    interior = s.kkt([[1.]],[.999],[.999])
    bound = s.kkt([[1.]],[1.001],[1.])
    assert s.active_change(interior,bound)
    assert not s.active_change(bound,bound)


def test_exact_weighted_recovery():
    a = dict(fine_A=[[1.]],fine_b=[2.],fine_weights=[1.])
    assert D(s.metric(a,[-1.],[-.5],0)['ratio']) == D('.5')
    with pytest.raises(ValueError):
        s.metric(dict(a,fine_weights=[-1.]),[-1.],[-.5],0)


@pytest.mark.parametrize('ref,cur',[(-.414688997029067,-.4146889970636461),(.167265,.167265-2.71740963064815e-12)])
def test_fault_rows_historical_tolerance(ref,cur):
    assert not s.agrees(cur,ref)


def test_fault_row_conditioning_from_saved_rms():
    B = 2.5914425556311052e-5
    r3 = s.recovery(B,2.5914480221164456e-5,2.5914502890077691e-5)
    r4 = s.recovery(B,2.5914947624982100e-5,2.5914860300514034e-5)
    assert D(r3['denominator']) > s.GUARD
    assert D(r4['denominator']) > s.GUARD
    assert D(r3['ratio']) < 0 < D(r4['ratio'])
    assert D(r3['denominator_condition']) > D('900000')
    assert D(r4['denominator_condition']) > D('90000')


def test_mismatched_frozen_input_and_source(tmp_path):
    p = tmp_path/'input.json'
    p.write_text('original')
    assert s.seal(p,s.transport.sha(p)) == s.transport.sha(p)
    with pytest.raises(ValueError,match='fingerprint'):
        s.seal(p,'0'*64)
    for invalid in ['bad','x'*64,'0'*63]:
        with pytest.raises(ValueError):
            s.seal(p,invalid)


def test_missing_artifact_and_solver_input_mismatch(tmp_path):
    with pytest.raises(FileNotFoundError):
        s.transport.load(tmp_path/'absent.json')
    with pytest.raises(ValueError,match='Incomplete'):
        s.reconstruct({'arrays':{},'cases':{}})
    spec = dict(arguments=dict(bounds=[-1,1],max_iter=1000,tol=1e-12),implicit_method='trf',implicit_lsq_solver='exact')
    s.transport.solver_spec(spec)
    spec['arguments']['tol'] = 1e-9
    with pytest.raises(ValueError):
        s.transport.solver_spec(spec)


def test_reconstructed_input_mismatch(monkeypatch):
    # Synthetic shape-complete capture; isolates frozen M reconstruction.
    config = dict(nt=1,np=1,segments=512,imax_A=3000,bref_T=.001,ridge=1e-6,active_threshold_A=.01)
    monkeypatch.setattr(s.transport,'load',lambda path:config)
    arrays = dict(A=np.zeros((1,24)),b=np.zeros(1),D=np.zeros((1,24)),d=np.zeros(1),
        weights=np.ones(1),points=np.zeros((1,3)),normals=np.zeros((1,3)),
        original_Bxyz=np.zeros((1,3)),vertices=np.zeros((24,512,3)),error_vertices=np.zeros((512,3)),
        fine_A=np.zeros((4,24)),fine_b=np.zeros(4),fine_weights=np.full(4,.25),
        fine_points=np.zeros((4,3)),fine_normals=np.zeros((4,3)))
    cases = {}
    for case in s.CASES:
        support = list(range(24)) if case == 'dense' else [i for i in range(24) if i != int(case[-1])]
        n = len(support)
        arrays[case+'_M'] = np.vstack((np.zeros((1,n)),.001*np.eye(n)))
        arrays[case+'_y'] = np.zeros(1+n)
        arrays[case+'_x'] = np.full(24,.001)
        arrays[case+'_unconstrained_initial_x'] = np.zeros(n)
        spec = dict(arguments=dict(bounds=[-1,1],max_iter=1000,tol=1e-12),implicit_method='trf',implicit_lsq_solver='exact',initialization='internal unconstrained')
        if case != 'dense':
            failed = int(case[-1])
            arrays[case+'_x'][failed] = 0
            spec.update(support=support,failed=failed)
        cases[case] = spec
    def pack(a):
        return dict(shape=list(a.shape),binary64_le=a.astype('<f8').tobytes().hex())
    payload = dict(schema='production-upstream-v1',config=config,cases=cases,arrays={k:pack(a) for k,a in arrays.items()})
    assert s.reconstruct(payload)['dense_M'].shape == (25,24)
    arrays['dense_M'][0,0] = 1e-6
    payload['arrays']['dense_M'] = pack(arrays['dense_M'])
    with pytest.raises(ValueError,match='reconstruction mismatch'):
        s.reconstruct(payload)


def test_source_fingerprint_invalid_inventory(tmp_path):
    for record in ({},{'head':'a'*40,'sha256':{}},{'head':'a'*40,'sha256':{'x':'invalid'}}):
        with pytest.raises(ValueError):
            s.source_check(record,'a'*40,tmp_path)


def test_missing_evidence_fails_closed(tmp_path):
    result = s.run(tmp_path,tmp_path,controls=False)
    assert result['evidence_complete'] is False
    assert result['cells'] == []
    assert result['scientific_comparison'] == result['production_acceptance'] == 'FAIL'
    assert result['errors'][0]['kind'] == 'MISSING_OR_CORRUPT_EVIDENCE'
    assert set(result['experiments'].values()) == {'NOT EXECUTED'}


def test_controlled_weight_and_field_interventions():
    a = dict(fine_A=np.array([[1.],[2.]]),fine_b=np.array([2.,3.]),fine_weights=np.array([.5,.5]))
    result = s.interventions(a,[-.5],[-.25],0)
    assert set(result['probes']) == {'fine_A','fine_b','fine_weights','dense_current'}
    assert result['probes']['fine_b']['binary64_change'] > 0
    assert abs(result['probes']['fine_weights']['weight_sum_change']) <= np.finfo(float).eps


def test_corruption_and_incorrect_scientific_pass(tmp_path):
    p = tmp_path/'data.json'
    for payload in ['{"x":NaN}','{"x":1,"x":2}','{"x":1e999}']:
        p.write_text(payload)
        with pytest.raises(ValueError):
            s.transport.load(p)
    with pytest.raises(ValueError,match='acceptance'):
        s.transport.comparison_record(dict(reference=1.,candidate=2.,status='PASS'))
    for diagnostic in (False,True):
        v = s.verdict(diagnostic)
        assert v['scientific_comparison'] == v['production_acceptance'] == 'FAIL'
        assert v['causal_root_cause'] == 'INCONCLUSIVE'
    assert s.verdict(True)['diagnostic_acceptance'] == 'PASS'


def test_corrupted_binary64_records():
    for value in [dict(shape=[2],binary64_le='00'),
                  dict(shape=[1],binary64_le=np.array([np.inf],dtype='<f8').tobytes().hex()),
                  dict(shape=[0],binary64_le=''),dict(shape=[1],binary64_le='z'*16)]:
        with pytest.raises(ValueError):
            s.transport.unpack(value)


def test_independent_forward_square():
    vv = [[-1.,-1.,0.],[1.,-1.,0.],[1.,1.,0.],[-1.,1.,0.]]
    f = s.field([[0.,0.,0.]],vv)
    assert D(f[0][0]) == D(f[0][1]) == 0
    assert float(f[0][2]) == pytest.approx(4e-7*np.sqrt(2),rel=1e-14)
    reverse = s.field([[0.,0.,0.]],vv[::-1])
    assert float(reverse[0][2]) == pytest.approx(-float(f[0][2]),rel=1e-14)


def test_deterministic_repeated_execution():
    calls = [lambda:s.kkt([[1.,2.],[3.,4.]],[1.,2.],[.1,-.2]),
             lambda:s.recovery(1.,3.,2.),lambda:s.qr_reference([[1.],[2.]],[.25,.5])]
    for action in calls:
        assert action() == action()
