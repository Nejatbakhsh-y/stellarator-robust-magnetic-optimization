"""Independent frozen-input contracts; these tests do not certify hosted agreement."""
import json
import math
import shutil
import subprocess
import sys
from decimal import Decimal,localcontext
from pathlib import Path
import numpy as np
import pytest
from stellarator_robust import frozen_diagnostics as fd
from stellarator_robust.model import Coil,field

SQUARE=[[-1.,-1.,0.],[0.,-1.,0.],[1.,-1.,0.],[1.,0.,0.],
        [1.,1.,0.],[0.,1.,0.],[-1.,1.,0.],[-1.,0.,0.]]
FIXTURE=Path(__file__).parents[1]/'benchmarks/phase2d-frozen-v1'


def test_independent_polygon_field_matches_closed_form():
    result=fd.decimal_field([[0.,0.,0.]],SQUARE,precision=90)[0]
    with localcontext() as ctx:
        ctx.prec=100
        exact=4*Decimal(2).sqrt()*Decimal.from_float(1e-7)
        assert abs(Decimal(result[2])-exact)<Decimal('1e-85')
    assert float(result[0])==float(result[1])==0.


def test_raw_components_match_independent_reference_and_winding():
    points=[[0.,0.,.3],[.2,.1,.4],[-.3,.2,.6]]
    reference=fd.decimal_field(points,SQUARE,precision=90)
    reverse=fd.decimal_field(points,SQUARE[::-1],precision=90)
    np.testing.assert_allclose(np.array(reference,dtype=float),-np.array(reverse,dtype=float),rtol=1e-14,atol=1e-25)
    rows=fd.vector_errors(np.array(reference,dtype=float).tolist(),field(np.array(points),Coil(np.array(SQUARE))).tolist())
    assert all(x for row in rows for x in row['passes'])


def test_relative_error_at_zero_does_not_drop_the_absolute_gate():
    row=fd.vector_errors([[0.,0.,1.]],[[1e-14,1e-9,1.]])[0]
    assert row['relative_component_error'][:2]==[None,None]
    assert row['passes']==[True,False,True]
    assert row['absolute_error_T'][1]==1e-9


def test_near_zero_component_still_uses_absolute_gate():
    row=fd.vector_errors([[1e-30,-1e-30,0.]],[[1e-14,1e-9,0.]])[0]
    assert row['passes']==[True,False,True]
    assert row['relative_component_error'][0]>1e15


def test_audited_sealed_fixture_and_source_contract(tmp_path):
    root=FIXTURE.parent/'phase2d-sealed-v1'
    contract=dict(fixture_manifest_sha256=fd.SEALED_MANIFEST_SHA256,sources=fd.source_hashes())
    fd.verify_contract(root,contract)
    contract['sources']['src/stellarator_robust/model.py']='0'*64
    with pytest.raises(ValueError,match='contract'):fd.verify_contract(root,contract)
    copy=tmp_path/'fixture';shutil.copytree(root,copy)
    (copy/'solver-inputs.json').write_bytes(b'{}')
    with pytest.raises(ValueError,match='hash'):fd.verify_contract(copy,contract)
    entries=fd.load(copy/'manifest.json')
    entries['solver-inputs.json']=fd.sha(copy/'solver-inputs.json')
    (copy/'manifest.json').write_text(json.dumps(entries),encoding='utf-8')
    with pytest.raises(ValueError,match='fingerprint'):fd.verify_contract(copy,contract)


def test_separate_physical_bound_control_requires_iterations(monkeypatch):
    monkeypatch.syspath_prepend(str(FIXTURE.parents[1]/'scripts'))
    from phase2d_frozen import bounded_problem,bounded_diagnostic
    root=FIXTURE.parent/'phase2d-sealed-v1'
    problem=bounded_problem(fd.load(root/'solver-inputs.json')['dense'])
    result=bounded_diagnostic(problem,fd.manifest(root))
    assert result['passed']
    assert result['result']['nit']>0
    assert abs(result['analytic_clipped_solution'])==1.


@pytest.mark.parametrize('tamper',[False,True])
def test_incomplete_or_tampered_evidence_writes_failure(tmp_path,tamper):
    root=tmp_path/'worker';root.mkdir()
    fd.write_new(root/'record.json',{'status':'PASS'})
    fd.write_new(root/'manifest.json',{'record.json':'0'*64} if tamper else {})
    out=tmp_path/'comparison.json'
    result=subprocess.run([sys.executable,'scripts/phase2d_frozen.py','compare',
        '--reference',str(root),'--current',str(root),'--output',str(out)],capture_output=True,text=True)
    assert result.returncode==1
    assert fd.load(out)['status']=='FAIL'
    assert 'incomplete' in fd.load(out)['reason']


@pytest.mark.parametrize('value',[math.nan,math.inf,-math.inf,True])
def test_invalid_reference_values_fail(value):
    with pytest.raises(ValueError):fd.decimal_field([[value,0.,0.]],SQUARE)


def test_clearance_and_invalid_polygon_fail():
    with pytest.raises(ValueError,match='close'):fd.decimal_field([[0.,-1.,0.]],SQUARE)
    with pytest.raises(ValueError):fd.decimal_field([[0.,0.,0.]],SQUARE,min_distance=-1.)
    with pytest.raises(ValueError):fd.decimal_field([[0.,0.,0.]],SQUARE[:3])


def test_high_precision_ridge_reference_and_noninterior_qualification():
    a=fd.decimal_lsq([[1.,0.],[0.,1.],[1.,1.]],[.1,.2,0.],90)
    b=fd.decimal_lsq([[1.,0.],[0.,1.],[1.,1.]],[.1,.2,0.],120)
    assert [float(x) for x in a['x']]==[0.,.1]
    assert all(abs(Decimal(x)-Decimal(y))<Decimal('1e-60') for x,y in zip(a['x'],b['x']))
    assert a['strictly_interior'] is True
    assert fd.decimal_lsq([[1.]],[2.])['strictly_interior'] is False
    with pytest.raises(ValueError):fd.decimal_lsq([[0.]],[1.])


def test_frozen_manifest_and_exact_geometry():
    cfg=fd.manifest(FIXTURE); geometry=fd.load(FIXTURE/cfg['geometry_file'])
    assert cfg['version']==fd.VERSION and len(cfg['points_m'])==8
    assert len(geometry['coils'])==25
    assert all(len(c['vertices'])==512 for c in geometry['coils'])


def test_frozen_inputs_cannot_be_changed_or_extended(tmp_path):
    root=tmp_path/'fixture';shutil.copytree(FIXTURE,root)
    (root/'unexpected').write_bytes(b'x')
    with pytest.raises(ValueError,match='Incomplete'):fd.manifest(root)
    (root/'unexpected').unlink()
    with (root/'fixture.json').open('ab') as f:f.write(b' ')
    with pytest.raises(ValueError,match='hash'):fd.manifest(root)


def test_immutable_output_and_complete_numeric_failures(tmp_path):
    path=tmp_path/'record.json';fd.write_new(path,{'original':True})
    with pytest.raises(FileExistsError):fd.write_new(path,{'replacement':True})
    assert fd.load(path)=={'original':True}
    errors=fd.scalar_differences({'Bx':1.,'By':2.,'Bz':3.},{'Bx':2.,'By':3.,'Bz':4.})
    assert {x['path'] for x in errors}=={'/Bx','/By','/Bz'}


def test_failed_workers_still_produce_complete_diagnostic_comparison(tmp_path):
    for name,value in [('left',1.),('right',2.)]:
        root=tmp_path/name;root.mkdir()
        fd.write_new(root/'record.json',dict(version=fd.VERSION,status='FAIL',completed=True,
            fixture_manifest_sha256='a'*64,primary={'Bx':value,'By':value},local_checks={'field':False}))
        fd.write_new(root/'sources.json',fd.source_hashes())
        fd.write_new(root/'manifest.json',{name:fd.sha(root/name) for name in ('record.json','sources.json')})
    output=tmp_path/'comparison.json'
    result=subprocess.run([sys.executable,'scripts/phase2d_frozen.py','compare','--reference',str(tmp_path/'left'),
        '--current',str(tmp_path/'right'),'--output',str(output)],capture_output=True,text=True)
    assert result.returncode==1,result.stderr
    record=fd.load(output)
    assert record['status']=='FAIL' and len(record['failures'])==2
    assert len(record['all_raw_differences'])>=2
