"""Adversarial evidence and numerical checks for the independent verifier."""
import importlib.util
import json
from pathlib import Path
import struct

import pytest

spec = importlib.util.spec_from_file_location('step38', Path(__file__).resolve().parents[1]/'scripts/phase2d_step38_verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def write(path, value):
    path.write_text(json.dumps(value), encoding='utf-8')


def test_duplicate_and_nonfinite_json(tmp_path):
    p = tmp_path/'x.json'
    for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'):
        p.write_text(text)
        with pytest.raises(ValueError): v.load(p)


def test_case_distinct_keys(tmp_path):
    p = tmp_path/'x.json'; write(p, {'D': 1, 'd': 2})
    assert v.load(p) == {'D': 1, 'd': 2}


def test_manifest_exact_coverage_and_tamper(tmp_path):
    p = tmp_path/'member'; p.write_bytes(b'original')
    m = tmp_path/'manifest.json'; write(m, {'member': v.sha(p)})
    assert v.manifest(m) == 1
    (tmp_path/'omitted').write_bytes(b'unlisted')
    with pytest.raises(ValueError, match='coverage'): v.manifest(m)
    p.write_bytes(b'tampered')
    with pytest.raises(ValueError, match='mismatching'): v.manifest(m)


@pytest.mark.parametrize('record', [{}, {'../escape': '0'*64}, {'absent': '0'*64}, {'x': 'bad'}])
def test_reject_bad_manifest(tmp_path, record):
    p = tmp_path/'manifest.json'; write(p, record)
    with pytest.raises(ValueError): v.manifest(p)


def test_hash_inventory_missing_file(tmp_path):
    p = tmp_path/'list'; p.write_text('0'*64+'  absent\n')
    assert v.hash_list(p, tmp_path)[0]['match'] is False
    p.write_text('0'*64+'  ../escape\n')
    with pytest.raises(ValueError): v.hash_list(p, tmp_path)


def test_binary64_validation():
    assert v.unpack({'shape': [2], 'binary64_le': struct.pack('<dd', 1., -2.).hex()}) == [1., -2.]
    for value in ({'shape': [2], 'binary64_le': '00'}, {'shape': [1], 'binary64_le': struct.pack('<d', float('nan')).hex()}):
        with pytest.raises(ValueError): v.unpack(value)


def test_asymmetric_original_tolerance():
    assert v.close(1.+1e-12, 1.)
    assert not v.close(1.+2e-11, 1.)
    assert not v.close(float('nan'), 1.)
    assert not v.close(2e-13, 0.)


def test_independent_ratio_and_kkt():
    arr = dict(fine_A=[[1.]], fine_b=[3.], fine_weights=[1.])
    r = v.ratio(arr, [-2.], [-1.], 0)
    assert float(r['ratio']) == .5
    assert float(r['denominator_T']) == 2.
    assert v.kkt([[1.]], [2.], [1.])['kkt_max'] == '0'
    assert float(v.kkt([[1.]], [2.], [0.])['kkt_max']) == 2.
    assert v.rounded_rms_probe([1., 3., 2.])['ratio_from_rounded_saved_rms'] == .5
    with pytest.raises(ValueError): v.rounded_rms_probe([1., 1., 2.])


def test_missing_required_evidence_fails_closed(tmp_path):
    result = v.verify(tmp_path, tmp_path)
    assert len(result['errors']) == 6
    assert result['evidence_authentication'] == 'INCOMPLETE'
    assert result['scientific_comparison'] == 'FAIL'
    assert result['production_acceptance'] == 'FAIL'


def test_fingerprint_covers_solver_and_support():
    base = dict(config={'segments': 512}, arrays={'dense_M': {}, 'dense_y': {}}, cases={
        'dense': dict(arguments={'tol': 1e-12}, implicit_method='trf', implicit_lsq_solver='exact', support=[0])})
    before = v.fingerprint(v.problem(base))
    base['cases']['dense']['arguments']['tol'] = 1e-9
    assert v.fingerprint(v.problem(base)) != before


def test_environment_rejects_library_and_missing_blas():
    record = dict(python='3.11.9', numpy='2.4.6', scipy='1.17.1', head='a', numerical_config='build',
                  loaded_threadpools=[dict(num_threads=1, architecture='Haswell', version='0.3.30')])
    assert v.environment(record, 'windows-reference', 'a') == record
    record['numpy'] = '2.3.5'
    with pytest.raises(ValueError): v.environment(record, 'windows-reference', 'a')
    record['numpy'] = '2.4.6'; record['loaded_threadpools'] = []
    with pytest.raises(ValueError): v.environment(record, 'windows-reference', 'a')


@pytest.mark.parametrize('value', ['', 'z'*64, '0'*63, None, 123])
def test_invalid_sha256(value):
    with pytest.raises(ValueError): v.valid_digest(value)


def test_duplicate_manifest_records(tmp_path):
    p = tmp_path/'manifest.json'
    p.write_text('{"member":"'+'0'*64+'","member":"'+'0'*64+'"}')
    with pytest.raises(ValueError, match='Duplicate'): v.manifest(p)


def test_duplicate_hash_records(tmp_path):
    p = tmp_path/'hashes'
    p.write_text(('0'*64+'  absent\n')*2)
    with pytest.raises(ValueError, match='duplicate'): v.hash_list(p, tmp_path)


@pytest.mark.parametrize('record', [{}, {'inputs.json': 'bad'}, {'inputs.json': '1'*64}])
def test_frozen_input_digest_rejected(record):
    with pytest.raises(ValueError): v.frozen_seal(record, {'inputs.json': '0'*64})


@pytest.mark.parametrize('record', [{}, {'dense_fixed_current_Bxyz': {}},
                                   {name: {'shape': [], 'binary64_le': ''} for name in v.FIELDS}])
def test_incomplete_field_payload(record):
    with pytest.raises(ValueError): v.fields(record)


@pytest.mark.parametrize('value', [float('inf'), float('nan'), True, '1', None])
def test_invalid_numerical_input(value):
    with pytest.raises(ValueError): v.number(value)


@pytest.mark.parametrize('value', [float('inf'), float('nan')])
def test_nonfinite_current_vectors(value):
    with pytest.raises(ValueError): v.kkt([[1.]], [0.], [value])
    with pytest.raises(ValueError): v.ratio(dict(fine_A=[[1.]], fine_b=[3.], fine_weights=[1.]), [value], [1.], 0)
    with pytest.raises(ValueError): v.unpack({'shape': [1], 'binary64_le': struct.pack('<d', value).hex()})


def diagnostic():
    return dict(cost=0., optimality=0., projected_gradient_max=0., condition=1.,
                success=True, status=3, nit=0, rank=1, message='optimal',
                active_mask=[0.], singular_values=[1.])


@pytest.mark.parametrize('key', list(diagnostic()))
def test_incomplete_solver_diagnostics(key):
    record = diagnostic(); del record[key]
    with pytest.raises((KeyError, ValueError)): v.diagnostics(record, 1)


@pytest.mark.parametrize('key,value', [('success', 'true'), ('status', 0), ('nit', -1),
                                     ('rank', 2), ('cost', -1.), ('active_mask', [2]),
                                     ('singular_values', [float('nan')])])
def test_invalid_solver_diagnostics(key, value):
    record = diagnostic(); record[key] = value
    with pytest.raises(ValueError): v.diagnostics(record, 1)


@pytest.mark.parametrize('record', [dict(reference=0., candidate=1., status='PASS'),
                                   dict(reference=0., candidate=1., **{'pass': True}),
                                   dict(failures=1, status='PASS'), dict(failures=-1),
                                   dict(reference=0., candidate='invalid'),
                                   dict(reference=float('nan'), candidate=0.)])
def test_incorrect_scientific_comparison(record):
    with pytest.raises(ValueError): v.comparison_record(record)


def test_frozen_solver_settings():
    spec = dict(arguments=dict(bounds=[-1, 1], max_iter=1000, tol=1e-12),
                implicit_method='trf', implicit_lsq_solver='exact')
    v.solver_spec(spec)
    spec['arguments']['tol'] = 1e-9
    with pytest.raises(ValueError): v.solver_spec(spec)


def test_missing_artifact_names_and_false_acceptance(tmp_path):
    for rid in v.RUNS:
        root = tmp_path/'github-hosted'/rid; root.mkdir(parents=True)
        write(root/'run-metadata.json', dict(databaseId=int(rid), status='completed', headSha='a'*40))
        write(root/'artifact-index.json', dict(total_count=0, artifacts=[]))
    result = v.verify(tmp_path, tmp_path)
    assert any('MISSING_REQUIRED_ARTIFACT' in e['error'] for e in result['errors'])
    assert result['production_acceptance'] == result['scientific_comparison'] == 'FAIL'
    assert result['causal_root_cause'] == 'INCONCLUSIVE'
    assert result['scientific_status'] == 'PARTIAL'


def test_duplicate_artifact_ids(tmp_path):
    rid = v.RUNS[0]; root = tmp_path/'github-hosted'/rid; root.mkdir(parents=True)
    write(root/'run-metadata.json', dict(databaseId=int(rid), status='completed', headSha='a'*40))
    artifacts = [dict(name=name, id=1, workflow_run=dict(id=int(rid), head_sha='a'*40))
                 for name in ('one', 'two')]
    write(root/'artifact-index.json', dict(total_count=2, artifacts=artifacts))
    result = v.verify(tmp_path, tmp_path)
    assert any('duplicate artifact ID' in e['error'] for e in result['errors'])


@pytest.mark.parametrize('name', ['a/../member', './member', 'a//member', '/absolute', ''])
def test_noncanonical_manifest_paths(tmp_path, name):
    with pytest.raises(ValueError): v.safe(tmp_path, name)


def test_valid_diagnostics_and_comparison():
    v.diagnostics(diagnostic(), 1)
    v.comparison_record(dict(reference=0., candidate=1., status='FAIL', **{'pass': False}))
    v.frozen_seal({'inputs.json': '0'*64}, {'inputs.json': '0'*64})


@pytest.mark.parametrize('record', [{}, {'comparisons': {}},
    {'comparisons': {o+'/'+w: {} for o in v.COHORTS for w in v.COHORTS[1:]}}])
def test_incomplete_scientific_assessment(record):
    with pytest.raises(ValueError): v.assessment(record)
