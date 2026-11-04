"""Adversarial STEP52 safeguards. Synthetic evidence is never scientific evidence."""
import json
from pathlib import Path
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import phase2d_step52_audit as s


def write(path, value):
    path.write_bytes(s.encode(value))


def baseline(tmp_path):
    root = tmp_path/'archives'; root.mkdir()
    evidence = tmp_path/'step51'; evidence.mkdir()
    manifest = tmp_path/'manifest.json'; write(manifest,dict(runs=[]))
    payloads = {n:{} for n in s.previous.FILES}
    payloads['solver-reproduction.json'] = dict(archives=[],inputs=[],manifest_sha256=s.archive_tools.digest(manifest.read_bytes()))
    for name, value in payloads.items():
        write(evidence/name,value)
    status = dict(assessment='COMPLETED_WITH_UNRESOLVED_REQUIREMENTS',scientific_comparison='FAIL',
        production_acceptance='FAIL',overall_scientific_status='INCOMPLETE',exit_code=2,
        rtol=1e-11,atol=1e-13,refinement_limit=1e-4,denominator_guard_T=1e-15,
        implementation_sha256=s.archive_tools.digest((ROOT/'scripts/phase2d_step51_numerical.py').read_bytes()),
        output_sha256={n:s.archive_tools.digest((evidence/n).read_bytes()) for n in s.previous.FILES})
    write(evidence/'status.json',status)
    return root,manifest,evidence,status


def args(root,manifest,evidence,out):
    return ['--archive-root',str(root),'--manifest',str(manifest),'--step51-status',str(evidence/'status.json'),
            '--step51-output',str(evidence),'--output',str(out)]


def archive_fixture(tmp_path):
    path = tmp_path/'a.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('result.json',b'{"historical":"FAIL"}')
    seal = s.archive_tools.digest(path.read_bytes())
    item = dict(id=1,name='original',file='a.zip',github_sha256='sha256:'+seal,verified_sha256=seal)
    return path,dict(runs=[dict(run_id=17,source_sha='0'*40,artifacts=[item])])


def test_original_archive_bytes_and_result_hash(tmp_path):
    path,m = archive_fixture(tmp_path)
    rows,_,_,errors = s.authenticate(tmp_path,m)
    assert rows[0]['status']=='BYTES_VERIFIED'
    assert rows[0]['members']['result.json']==s.archive_tools.digest(b'{"historical":"FAIL"}')
    assert '71-archive' in errors[0]


@pytest.mark.parametrize('mode',['corrupt','missing','wrong_hash','duplicate','escape'])
def test_archive_rejections(tmp_path,mode):
    path,m = archive_fixture(tmp_path)
    item=m['runs'][0]['artifacts'][0]
    if mode=='corrupt': path.write_bytes(b'corrupt')
    if mode=='missing': path.unlink()
    if mode=='wrong_hash': item['verified_sha256']='0'*64
    if mode=='duplicate': m['runs'][0]['artifacts'].append(item.copy())
    if mode=='escape': item['file']='../a.zip'
    rows,*_ = s.authenticate(tmp_path,m)
    assert any(r['status']=='REJECTED_OR_MISSING' for r in rows)


def test_source_mismatch(tmp_path,monkeypatch):
    _,m=archive_fixture(tmp_path)
    monkeypatch.setattr(s.archive_tools,'source',lambda *a:[dict(association='CONFLICT',files=[])])
    assert any('source identity mismatch' in e for e in s.authenticate(tmp_path,m)[3])


@pytest.mark.parametrize('mode',['altered','missing','wrong_hash','source','false_pass','threshold'])
def test_step51_tampering(tmp_path,mode):
    _,_,evidence,status=baseline(tmp_path)
    name=s.previous.FILES[0]
    if mode=='altered': write(evidence/name,dict(forged=True))
    if mode=='missing': (evidence/name).unlink()
    if mode=='wrong_hash': status['output_sha256'][name]='0'*64
    if mode=='source': status['implementation_sha256']='0'*64
    if mode=='false_pass': status['scientific_comparison']='PASS'
    if mode=='threshold': status['rtol']=1e-6
    write(evidence/'status.json',status)
    assert s.step51_files(evidence/'status.json',evidence)[3]


def test_input_semantic_fingerprint_mismatch():
    with pytest.raises(ValueError,match='digest mismatch'):
        s.previous.input_seals({'input-sha256.json':s.encode({'inputs.json':'0'*64}),
                              'problem-sha256.json':b'{}'},'inputs.json',b'{}')


def test_forged_scientific_pass_with_updated_file_seal(tmp_path):
    _,_,evidence,status=baseline(tmp_path)
    name='scientific-blockers.json'
    write(evidence/name,dict(production_acceptance='PASS',blockers=[]))
    status['output_sha256'][name]=s.archive_tools.digest((evidence/name).read_bytes())
    write(evidence/'status.json',status)
    assert any('Unsupported scientific PASS' in e for e in s.step51_files(evidence/'status.json',evidence)[3])


@pytest.mark.parametrize('claim',['PASS','EXECUTED','COMPLETE'])
def test_unexecuted_environment_claims(claim):
    result=s.causal_audit(dict(controlled_configurations={k:dict(status=claim) for k in s.previous.COHORTS}))
    assert result['status']=='INCONCLUSIVE'
    assert len(result['unsupported_execution_claims'])==4
    assert all(v['status']=='INCOMPLETE' for v in result['required'].values())


def test_missing_four_environments():
    result=s.causal_audit({})
    assert len(result['required'])==4
    assert result['status']=='INCONCLUSIVE'


def test_incorrect_ratio_classification_and_historical_preservation():
    original=dict(reference=.5,candidate=.50000001,status='FAIL')
    rows=s.classifications(original)
    assert rows[0]['recomputed_pass'] is False
    assert not rows[0]['contradictory']
    assert original['status']=='FAIL'
    original['status']='PASS'
    assert s.classifications(original)[0]['contradictory']
    assert s.classifications(dict(failures=11,status='PASS'))[0]['contradictory']


def test_quotient_and_original_guard():
    r=s.quotient(['1e-5','2e-5','1.5e-5'])
    assert r['ratio']=='0.5'
    assert r['numerator_T']=='0.000005'
    assert not s.quotient(['1','1.000000000000001','1'])['denominator_guard_pass']
    assert s.quotient(['1','1.000000000000002','1'])['denominator_guard_pass']
    assert not s.close('0.50000001','.5')
    assert s.close('1.00000000001','1')
    assert (s.RTOL,s.ATOL,s.REFINEMENT,s.GUARD)==tuple(map(s.D,('1e-11','1e-13','1e-4','1e-15')))


@pytest.mark.parametrize('saved',[{},dict(x=[1.01],passed=True),dict(x=[1.],passed=False)])
def test_missing_or_forged_quantitative_outputs(saved):
    assert s.compare_tree(saved,dict(x=[1.],passed=True))


def test_empty_inputs_cannot_pass():
    result=s.numerical_audit({}, {})
    assert result['errors']==['No numerical inputs assessed']


@pytest.mark.parametrize('mode',['missing','hash','seal'])
def test_scientific_input_binding(mode):
    entry=dict(run_id=17,artifact_id=1,member='inputs.json',input_sha256='a'*64,
               status='VERIFIED',seals=dict(status='VERIFIED'))
    record=dict(run_id=17,artifact_id=1,path='inputs.json',input_sha256='a'*64,
                input_seals=dict(status='VERIFIED'))
    if mode=='hash': record['input_sha256']='b'*64
    if mode=='seal': record['input_seals']={}
    payload={n:dict(inputs=[] if mode=='missing' else [record]) for n in s.previous.FILES[:3]}
    result=s.numerical_audit({(17,1,'inputs.json'):(entry,b'{}')},payload)
    assert result['inputs'][0]['status']=='INCOMPLETE_OR_INVALID'
    assert result['errors']


def test_output_contract_determinism_and_no_scientific_pass(tmp_path):
    root,manifest,evidence,_=baseline(tmp_path)
    first,second=tmp_path/'first',tmp_path/'second'
    assert s.main(args(root,manifest,evidence,first))==2
    assert s.main(args(root,manifest,evidence,second))==2
    assert set(p.name for p in first.iterdir())=={*s.OUTPUTS,'output-manifest.json'}
    for p in first.iterdir():
        assert p.read_bytes()==(second/p.name).read_bytes()
    d=json.loads((first/'decision.json').read_bytes())
    assert d['production_acceptance']==d['scientific_comparison']=='FAIL'
    assert d['overall_scientific_status']=='INCOMPLETE'
    assert d['exit_code']==2
    seals=json.loads((first/'output-manifest.json').read_bytes())['outputs']
    assert all(s.archive_tools.digest((first/n).read_bytes())==v for n,v in seals.items())
    assert s.main(args(root,manifest,evidence,first))==1


@pytest.mark.parametrize('where',['archives','step51','parent'])
def test_distinct_output_and_evidence_paths(tmp_path,where):
    root,manifest,evidence,_=baseline(tmp_path)
    out={'archives':root/'out','step51':evidence/'out','parent':tmp_path}[where]
    assert s.main(args(root,manifest,evidence,out))==1
    if where!='parent': assert not out.exists()


def test_unexpected_failure_is_exit_one(tmp_path,monkeypatch):
    root,manifest,evidence,_=baseline(tmp_path)
    def fail(*a): raise RuntimeError('unexpected')
    monkeypatch.setattr(s,'assess',fail)
    out=tmp_path/'out'
    assert s.main(args(root,manifest,evidence,out))==1
    assert json.loads((out/'decision.json').read_bytes())['assessment_status']=='UNEXPECTED_EXECUTION_FAILURE'


def test_missing_baseline_is_exit_two(tmp_path):
    root,manifest,evidence,_=baseline(tmp_path)
    (evidence/'status.json').unlink()
    assert s.main(args(root,manifest,evidence,tmp_path/'out'))==2


def test_no_publication_or_production_mutation():
    source=(ROOT/'scripts/phase2d_step52_audit.py').read_text()
    assert 'gh pr merge' not in source
    assert 'git push' not in source
    assert 'workflow run' not in source
    assert 'recover_objects(' not in source
    assert 'extractall(' not in source


def test_real_71_original_archive_hashes():
    root=ROOT/'results/phase2d/step49-original-archives-20261102-120255-a1314650'
    if not root.exists(): pytest.skip('Original STEP49 evidence not installed')
    manifest=s.archive_tools.decode((root/'manifest.json').read_bytes())
    items=[i for r in manifest['runs'] for i in r['artifacts']]
    assert len(items)==71
    for item in items:
        assert s.archive_tools.digest((root/item['file']).read_bytes())==item['verified_sha256']==item['github_sha256'].removeprefix('sha256:')
