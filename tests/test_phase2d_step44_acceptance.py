"""Independent analytical and adversarial tests; software success is not science."""
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step44_acceptance as s


@pytest.mark.parametrize('values,expected',[
    ((1,3,2),Fraction(1,2)),((0,2,3),Fraction(-1,2)),
    ((2,1,3),Fraction(2)),((1,4,3),Fraction(1,3))])
def test_analytical_recovery(values,expected):
    assert Fraction(s.recovery(*values)['exact_ratio']) == expected


def test_derivative_signs_and_independent_finite_differences():
    assert list(map(Decimal,s.recovery(1,3,2)['derivatives_B_L_P'])) == [Decimal('.25'),Decimal('.25'),Decimal('-.5')]
    assert len(s.mathematics()['cases']) == 4
    # Forward differences are separate from the implementation's central check.
    B,L,P = map(Fraction,(1,3,2))
    h = Fraction(1,10**12)
    ratio = lambda b,l,p:(l-p)/(l-b)
    for j,g in enumerate((Fraction(1,4),Fraction(1,4),Fraction(-1,2))):
        v = [B,L,P]
        v[j] += h
        assert abs((ratio(*v)-ratio(B,L,P))/h-g) < Fraction(1,10**11)


@pytest.mark.parametrize('gap',['0','1e-15','-1e-15','1e-16'])
def test_original_denominator_guard(gap):
    with pytest.raises(ValueError,match='guard'):
        s.recovery(0,gap,1)
    assert s.recovery(0,'1.000000000000001e-15',0)['exact_ratio']=='1'


def test_tolerance_exact_boundaries_and_asymmetry():
    for reference in ('0','1','-2'):
        r = Fraction(reference)
        limit = s.ATOL+s.RTOL*abs(r)
        assert s.agrees(r+limit,r)
        assert s.agrees(r-limit,r)
        assert not s.agrees(r+limit+Fraction('1e-50'),r)
    with localcontext() as ctx:
        ctx.prec = 2
        assert not s.agrees('1.0000000001','1')


def test_high_precision_cancellation():
    # Exact decimal differences vanish under an inappropriate binary64 parse.
    q = s.recovery('1','1.00000000000001','1.000000000000005')
    assert q['exact_ratio']=='1/2'
    assert Fraction(q['denominator_T'])==Fraction('1e-14')
    assert s.rational(.1)==Fraction.from_float(.1)


def test_scalar_field_rms_and_linearity_example():
    # B=2,L=1,P=1.5, hence R=.5. No production calculation supplies this answer.
    for digits in (70,100):
        r = s.metric([[1.,0.]],[1.],[1.],[1.,0.],[.5,0.],0,digits)
        assert r['exact_ratio']=='1/2'
        assert list(map(Fraction,r['rms_B_L_P']))==[2,1,Fraction(3,2)]
    for A,b,w in (([],[],[]),([[1.]],[1.],[-1.]),([[1.,2.]],[1.],[1.])):
        with pytest.raises(ValueError):
            s.metric(A,b,w,[1.],[.5],0)


@pytest.mark.parametrize('bad',[True,None,[],{},float('nan'),float('inf'),float('-inf'),'NaN','Infinity','junk'])
def test_nonfinite_and_invalid_numerical_values(bad):
    with pytest.raises(ValueError):
        s.rational(bad)
    with pytest.raises(ValueError):
        s.agrees(bad,1)


def put(path,value):
    path.write_text(json.dumps(value),encoding='utf-8')


def test_missing_corrupt_and_incomplete_manifest(tmp_path):
    p = tmp_path/'manifest.json'
    with pytest.raises(FileNotFoundError):
        s.manifest_check(p)
    f = tmp_path/'x.json'
    put(f,{'value':1})
    put(p,{'x.json':s.transport.sha(f)})
    assert s.manifest_check(p)['complete']
    put(tmp_path/'extra.json',{})
    assert s.manifest_check(p)['omitted']==['extra.json']
    put(p,{'x.json':'0'*64})
    with pytest.raises(ValueError,match='SHA256'):
        s.manifest_check(p)
    put(p,{'missing.json':'a'*64})
    assert s.manifest_check(p)['missing']==['missing.json']
    for value in ({},{'../escape':'a'*64},{'x.json':'bad'}):
        put(p,value)
        with pytest.raises(ValueError):
            s.manifest_check(p)


@pytest.mark.parametrize('text',['{"a":1,"a":2}','{"a":NaN}','{"a":1e999}','{'])
def test_corrupt_json(tmp_path,text):
    p = tmp_path/'bad.json'
    p.write_text(text)
    with pytest.raises(ValueError):
        s.transport.load(p)


@pytest.mark.parametrize('key,value',[
    ('scientific_comparison','PASS'),('causal_root_cause','VERIFIED'),
    ('evidence_authentication','COMPLETE'),('production_acceptance','PASS'),
    ('scientific_status','PASS')])
def test_unsupported_authentication_and_false_pass(key,value):
    claim = s.policy()
    claim[key] = value
    with pytest.raises(ValueError,match='Unsupported'):
        s.reject_claims(claim)


def test_successful_software_tests_never_promote_historical_failure():
    software = {'pytest':'PASS','ci':'SUCCESS'}
    status = s.policy()
    s.reject_claims(status)
    assert software['ci']=='SUCCESS'
    assert status['scientific_comparison']=='FAIL'
    assert status['production_acceptance']=='FAIL'
    assert status['scientific_status']=='PARTIAL'
    assert s.policy(failures=False)['scientific_comparison']=='INCONCLUSIVE'


def test_source_commit_mismatch(monkeypatch,tmp_path):
    class Result:
        stdout = '0'*40
    monkeypatch.setattr(s.subprocess,'run',lambda *a,**k:Result())
    with pytest.raises(ValueError,match='source commit'):
        s.source_identity(tmp_path)


def test_output_new_isolated_and_repeatability(tmp_path):
    area = tmp_path/'results/phase2d'
    original = area/'step38-original'
    original.mkdir(parents=True)
    (original/'x').write_text('original')
    with pytest.raises(ValueError):
        s.output_path(tmp_path,original/'new')
    with pytest.raises(ValueError):
        s.output_path(tmp_path,tmp_path/'elsewhere')
    out = s.output_path(tmp_path,area/'step44-new')
    assert out==area/'step44-new'
    assert s.mathematics()==s.mathematics()
    out.mkdir()
    with pytest.raises(ValueError):
        s.output_path(tmp_path,out)


def test_missing_inputs_exit_one_and_report_completeness(tmp_path,monkeypatch):
    (tmp_path/'results/phase2d').mkdir(parents=True)
    monkeypatch.setattr(s,'assess',lambda root,out:(s.policy(['MISSING_EVIDENCE']),
        {'missing_evidence':['MISSING_EVIDENCE']},{},1))
    out = tmp_path/'results/phase2d/step44-test'
    assert s.main(['--root',str(tmp_path),'--output',str(out)])==1
    status = s.transport.load(out/'status.json')
    assert status['scientific_status']=='PARTIAL'
    manifest = s.transport.load(out/'evidence-manifest.json')
    assert set(manifest['outputs'])=={'status.json','numerical-comparisons.json','acceptance-report.md'}
    for name,digest in manifest['outputs'].items():
        assert s.transport.sha(out/name)==digest
    report = (out/'acceptance-report.md').read_text()
    for title in ('FAULT ROW 3','FAULT ROW 4','FOUR-ENVIRONMENT COMPARISON',
                  'COMPLETE REGRESSION RESULTS','ORIGINAL ARTIFACT AUTHENTICATION',
                  'PRODUCTION ACCEPTANCE','REMAINING BLOCKERS'):
        assert title in report


def test_execution_failure_writes_no_false_pass(tmp_path,monkeypatch):
    (tmp_path/'results/phase2d').mkdir(parents=True)
    def explode(*args):
        raise RuntimeError('corrupt execution')
    monkeypatch.setattr(s,'assess',explode)
    out = tmp_path/'results/phase2d/step44-error'
    assert s.main(['--root',str(tmp_path),'--output',str(out)])==2
    assert s.transport.load(out/'status.json')['scientific_status']=='PARTIAL'


def test_incorrect_solver_input_and_objective_kkt_rejected():
    # Explicitly reused validator is independently exercised with adversarial data.
    import phase2d_step42_replay as replay
    import numpy as np
    assert not replay.certificate(np.eye(2),np.ones(2),np.zeros(2))['verified']
    assert not replay.certificate(np.eye(2),np.zeros(2),np.array([1.1,0.]))['verified']
    _,row = replay.solve(np.eye(2),np.array([.25,-.5]))
    row.update(currents_A=[0.]*24,currents_A_binary64_le=np.zeros(24,dtype='<f8').tobytes().hex())
    value = dict(cases={case:dict(row) for case in replay.CASES})
    replay.require_solve_record(value)
    value['cases']['dense']['cost']=1.
    with pytest.raises(ValueError,match='certificate'):
        replay.require_solve_record(value)


def test_incorrect_exact_capture_identity(tmp_path):
    import phase2d_step42_replay as replay
    (tmp_path/'inputs.json').write_text('{}')
    with pytest.raises(ValueError,match='SHA256'):
        replay.load_capture(tmp_path,'0'*64)


@pytest.mark.parametrize('key,bad',[('source_head','0'*40),('input_sha256','b'*64)])
def test_captured_source_and_input_identity(key,bad):
    identity = dict(source_head=s.HEADS['41257645149'],input_sha256='a'*64)
    s.capture_identity(identity,'41257645149','a'*64)
    identity[key] = bad
    with pytest.raises(ValueError,match='identity'):
        s.capture_identity(identity,'41257645149','a'*64)


def test_early_inventory_incomplete_and_false_failure(tmp_path):
    with pytest.raises(ValueError,match='Incomplete'):
        s.early_records([],tmp_path)
    with pytest.raises(ValueError):
        s.early_records([dict(run='invalid',original_file='x',path='/')]*22,tmp_path)


def _check_real_historical_originals(root):
    raw = s.transport.load(root/s.STEP41/'recomputed-comparisons.json')
    with pytest.raises(ValueError, match='Comparison scalar differs'):
        s.prior.bind_comparisons(raw, root/s.EVIDENCE)
    rows, corrections = s.bind_comparisons(raw, root/s.EVIDENCE)
    assert len(rows) == 48
    assert corrections
    changed = [c for c in corrections if not c['binary64_equal']]
    assert len(changed) == 1
    defect = changed[0]
    assert (defect['run'], defect['origin'], defect['worker'], defect['case']) == (
        '41257645149', 'windows-reference', 'linux-reference', 'row3')
    assert defect['original_scalar_token'] == '-0.414688997078806'
    assert defect['saved_scalar_token'] == '-0.41468899707880597'
    assert Decimal(defect['exact_decimal_token_difference']) == Decimal('3e-17')
    assert Fraction(Decimal(defect['exact_difference'])) == Fraction(1,2**54)
    assert defect['result_sha256'] == 'f3e6b62a40ab48eacae8f8b06ab00502043e8197e0b7ccf711f9d29caf4ba1d4'
    assert any(c['binary64_equal'] and c['original_scalar_token'] == '-0.41468899703150891'
               and c['saved_scalar_token'] == '-0.4146889970315089' for c in corrections)
    assert [sum(not r['pass'] for r in rows if r['run'] == run)
            for run in s.transport.RUNS[2:]] == [21, 11]
    # An arbitrary scalar corruption remains an error, even within tolerance.
    damaged = [dict(r) for r in raw]
    damaged[0]['candidate'] += 1e-15
    with pytest.raises(ValueError, match='Comparison scalar differs'):
        s.bind_comparisons(damaged, root/s.EVIDENCE)
    damaged = [dict(r) for r in raw]
    damaged[0]['result_sha256'] = '0'*64
    with pytest.raises(ValueError, match='fingerprint'):
        s.bind_comparisons(damaged, root/s.EVIDENCE)


@pytest.mark.parametrize('mutation', ['candidate_identity','reference_identity','swap','cohort',
                                     'duplicate','missing','nonfinite','false_pass','genuine'])
def test_historical_binding_adversaries(mutation, synthetic_binding):
    rows, evidence, inventory, digest = synthetic_binding
    if mutation == 'candidate_identity':
        rows[0]['result_sha256'] = rows[0]['reference_sha256']
    elif mutation == 'reference_identity':
        rows[0]['reference_sha256'] = rows[0]['result_sha256']
    elif mutation == 'swap':
        rows[0]['candidate'],rows[0]['reference'] = rows[0]['reference'],rows[0]['candidate']
    elif mutation == 'cohort':
        rows[0]['origin'] = 'unknown'
    elif mutation == 'duplicate':
        rows.append(dict(rows[0]))
    elif mutation == 'missing':
        rows.pop()
    elif mutation == 'nonfinite':
        rows[0]['candidate'] = float('nan')
    elif mutation == 'false_pass':
        rows[0]['pass'] = True
    else:
        rows[0]['candidate'] += 1e-15
    with pytest.raises((ValueError, FileNotFoundError, KeyError)):
        s._bind_comparison_inventory(rows, evidence, inventory, digest)


def test_modified_original_bytes_rejected(synthetic_binding):
    rows, evidence, inventory, digest = synthetic_binding
    index = s.transport.load(evidence/'github-hosted'/rows[0]['run']/'artifact-index.json')
    artifact = next(a for a in index['artifacts'] if a['name'] ==
                    f"step33-replay-{rows[0]['worker']}-{rows[0]['run']}-1")
    file = evidence/'github-hosted'/rows[0]['run']/f"artifact-{artifact['id']}"/rows[0]['origin']/'result.json'
    original = file.read_bytes()
    file.write_bytes(original+b' ')
    with pytest.raises(ValueError, match='fingerprint'):
        s._bind_comparison_inventory(rows, evidence, inventory, digest)
    file.write_bytes(original)
    inventory.write_bytes(inventory.read_bytes()+b' ')
    with pytest.raises(ValueError, match='SHA256'):
        s._bind_comparison_inventory(rows, evidence, inventory, digest)

def test_indispensable_missing_input_returns_two(tmp_path, monkeypatch):
    monkeypatch.setattr(s, 'source_identity', lambda root: s.SOURCE_COMMIT)
    out = tmp_path/'results/phase2d/step44-missing'
    assert s.main(['--root', str(tmp_path), '--output', str(out)]) == 2
    status = s.transport.load(out/'status.json')
    assert any('MISSING_INDISPENSABLE_INPUT' in b for b in status['remaining_blockers'])
    assert status['scientific_status'] == 'PARTIAL'
    assert status['production_acceptance'] == 'FAIL'


def test_nonexistent_root_is_invalid(tmp_path):
    with pytest.raises(ValueError, match='repository'):
        s.main(['--root', str(tmp_path/'absent'), '--output', str(tmp_path/'out')])


def test_corrupted_mandatory_json_returns_two(tmp_path, monkeypatch):
    monkeypatch.setattr(s, 'source_identity', lambda root: s.SOURCE_COMMIT)
    folder = tmp_path/s.STEP41
    folder.mkdir(parents=True)
    (folder/'recomputed-comparisons.json').write_text('{', encoding='utf-8')
    out = tmp_path/'results/phase2d/step44-corrupt'
    assert s.main(['--root', str(tmp_path), '--output', str(out)]) == 2
    data = s.transport.load(out/'numerical-comparisons.json')
    assert any('JSONDecodeError' in e for e in data['errors'])

@pytest.fixture
def synthetic_binding(tmp_path):
    """Generated software fixtures ONLY; no original historical evidence."""
    import hashlib
    evidence = tmp_path/'synthetic-step38'
    inventory = tmp_path/'synthetic-comparisons.json'

    def sealed(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(value, sort_keys=True, allow_nan=False)+'\n').encode())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert s.transport.sha(path) == digest
        return digest

    rows = []
    for run in s.transport.RUNS[2:]:
        folder = evidence/'github-hosted'/run
        artifacts = []
        paths = {}
        for kind in ('capture', 'replay'):
            for cohort in s.transport.COHORTS:
                number = len(artifacts)+1
                artifacts.append(dict(id=number, name=f'step33-{kind}-{cohort}-{run}-1'))
                paths[kind, cohort] = folder/f'artifact-{number}'
        sealed(folder/'artifact-index.json',
               dict(synthetic_test_fixture=True, artifacts=artifacts))
        for origin in s.transport.COHORTS:
            inputs = dict(synthetic_test_fixture=True, origin=origin, run=run)
            input_hash = sealed(paths['capture', origin]/'inputs.json', inputs)
            results = {}
            for j, worker in enumerate(s.transport.COHORTS):
                values = dict(row3=.1+j*.1, row4=.5 if j < 2 else .7)
                if run == '41257645149' and origin == 'windows-reference' and j == 1:
                    values['row3'] = float('-0.41468899707880597')
                sub = paths['replay', worker]/origin
                assert sealed(sub/'inputs.json', inputs) == input_hash
                digest = sealed(sub/'result.json', dict(
                    synthetic_test_fixture=True, worker=worker,
                    solve=dict(recovery={case:dict(fractional_recovery=v)
                                         for case,v in values.items()})))
                results[worker] = (values, digest)
            for worker in s.transport.COHORTS[1:]:
                for case in ('row3', 'row4'):
                    candidate = results[worker][0][case]
                    if (run,origin,worker,case) == (
                            '41257645149','windows-reference','linux-reference','row3'):
                        candidate = float('-0.414688997078806')
                    reference = results[s.transport.COHORTS[0]][0][case]
                    rows.append(dict(run=run, origin=origin, worker=worker, case=case,
                        candidate=candidate, reference=reference,
                        high_candidate=candidate, high_reference=reference,
                        high_pass=s.agrees(candidate,reference),
                        **{'pass':s.agrees(candidate,reference)},
                        input_sha256=input_hash, result_sha256=results[worker][1],
                        reference_sha256=results[s.transport.COHORTS[0]][1]))
    digest = sealed(inventory, rows)
    return s.transport.load(inventory), evidence, inventory, digest


def test_observed_host_serialization_failure_bound_to_real_originals(synthetic_binding):
    # The name is retained; the portable portion reproduces the token mechanism,
    # while _check_real_historical_originals independently checks real bytes.
    rows, evidence, inventory, digest = synthetic_binding
    with pytest.raises(ValueError, match='Comparison scalar differs'):
        s.prior.bind_comparisons(rows, evidence)
    bound, corrections = s._bind_comparison_inventory(rows, evidence, inventory, digest)
    assert len(bound) == 48
    assert {tuple(r[k] for k in ('run','origin','worker','case')):r['pass'] for r in bound} == {
        tuple(r[k] for k in ('run','origin','worker','case')):r['pass'] for r in rows}
    assert len(corrections) == 1
    defect = corrections[0]
    assert not defect['binary64_equal']
    assert defect['original_scalar_token'] == '-0.414688997078806'
    assert defect['saved_scalar_token'] == '-0.41468899707880597'
    assert Decimal(defect['exact_decimal_token_difference']) == Decimal('3e-17')
    assert Fraction(Decimal(defect['exact_difference'])) == Fraction(1,2**54)
    assert Fraction.from_float(float(Decimal(defect['saved_scalar_token']))) == Fraction.from_float(
        json.loads(defect['saved_scalar_token']))
    assert float('-0.41468899703150891') == float('-0.4146889970315089')
    assert Fraction.from_float(.1) != Fraction(Decimal('.1'))
    # Production cannot authenticate this synthetic inventory.
    historical_inventory = evidence.parent/Path(s.STEP41).name/'recomputed-comparisons.json'
    historical_inventory.parent.mkdir()
    historical_inventory.write_bytes(inventory.read_bytes())
    with pytest.raises(ValueError, match='SHA256'):
        s.bind_comparisons(rows, evidence)


@pytest.mark.parametrize('target', ['capture_input', 'replay_input'])
def test_synthetic_input_bytes_rejected(synthetic_binding, target):
    rows, evidence, inventory, digest = synthetic_binding
    row = rows[0]
    folder = evidence/'github-hosted'/row['run']
    index = s.transport.load(folder/'artifact-index.json')['artifacts']
    kind, cohort = ('capture', row['origin']) if target == 'capture_input' else ('replay', row['worker'])
    artifact = next(a for a in index if a['name'] == f"step33-{kind}-{cohort}-{row['run']}-1")
    file = folder/f"artifact-{artifact['id']}"
    if kind == 'replay':
        file /= row['origin']
    file /= 'inputs.json'
    file.write_bytes(file.read_bytes()+b' ')
    with pytest.raises(ValueError, match='fingerprint'):
        s._bind_comparison_inventory(rows, evidence, inventory, digest)


def test_independent_historical_integration(tmp_path, record_property):
    """Actual local originals only; absence explicitly establishes no authentication."""
    root = Path(__file__).resolve().parents[1]
    inventory = root/s.STEP41/'recomputed-comparisons.json'
    if not inventory.is_file():
        # Only a wholly absent historical source tree is a portable checkout.
        # A partial local archive must fail rather than bypass authentication.
        assert not (root/s.STEP41).exists(), 'Incomplete historical STEP41 evidence'
        assert not (root/s.EVIDENCE).exists(), 'Incomplete historical STEP38 evidence'
        with pytest.raises(FileNotFoundError):
            s.bind_comparisons([], root/s.EVIDENCE)
        print('Historical authentication NOT ESTABLISHED: original evidence unavailable')
        record_property('historical_authentication', 'NOT ESTABLISHED: missing original evidence')
        assert s.policy()['evidence_authentication'] == 'INCOMPLETE'
        return
    _check_real_historical_originals(root)
    rows = s.transport.load(inventory)
    digest = s.transport.sha(inventory)
    for mutation in ('candidate_identity','reference_identity','swap','cohort',
                     'duplicate','missing','nonfinite','false_pass','genuine'):
        test_historical_binding_adversaries(mutation,
            (s.transport.load(inventory), root/s.EVIDENCE, inventory, digest))
    # Copy only the first original replay needed to reject modified bytes;
    # never mutate the actual original evidence directories.
    import shutil
    evidence = tmp_path/Path(s.EVIDENCE).name
    copied_inventory = tmp_path/Path(s.STEP41).name/'recomputed-comparisons.json'
    copied_inventory.parent.mkdir()
    shutil.copyfile(inventory, copied_inventory)
    row = rows[0]
    source = root/s.EVIDENCE/'github-hosted'/row['run']
    target = evidence/'github-hosted'/row['run']
    target.mkdir(parents=True)
    shutil.copyfile(source/'artifact-index.json', target/'artifact-index.json')
    index = s.transport.load(source/'artifact-index.json')['artifacts']
    artifact = next(a for a in index if a['name'] ==
                    f"step33-replay-{row['worker']}-{row['run']}-1")
    relative = Path(f"artifact-{artifact['id']}")/row['origin']
    (target/relative).mkdir(parents=True)
    for name in ('inputs.json', 'result.json'):
        shutil.copyfile(source/relative/name, target/relative/name)
    file = target/relative/'result.json'
    file.write_bytes(file.read_bytes()+b' ')
    with pytest.raises(ValueError, match='fingerprint'):
        s.bind_comparisons(rows, evidence)
    copied_inventory.write_bytes(copied_inventory.read_bytes()+b' ')
    with pytest.raises(ValueError, match='SHA256'):
        s.bind_comparisons(rows, evidence)
    record_property('historical_authentication', 'Extracted binding verified; archives INCOMPLETE')
    print('Historical extracted-byte binding verified; original archive authentication INCOMPLETE')
    assert s.policy()['evidence_authentication'] == 'INCOMPLETE'
