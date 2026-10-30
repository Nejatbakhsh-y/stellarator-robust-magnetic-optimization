"""Small evidence-contract fixtures; these are not completed physical studies."""
import copy
import json
from pathlib import Path
import pytest
from stellarator_robust.phase2b import VERSION, sha, pair, require_complete, verify_manifest


def bundle(path, commit='a'*40, python='3.11.9', current=1.):
    path.mkdir(parents=True); (path/'quick').mkdir(); (path/'study').mkdir()
    actual = dict(source_commit=commit, source_dirty=False, python=python, packages={'numpy': 'test'})
    row = dict(translation_m=[[.1, .0, .0]], rotation_rad=[[.01, .0, .0]],
               gain=[.001], offset_A=[.2], sampled_clearance_m=.4)
    metadata = dict(**actual, config={'geometry_version': 'householder-v2'}, units='m, A, T',
                    condition_number=2., rank=1, clearance_sampled_m=.4, elapsed_seconds=.1)
    quick = dict(metadata=metadata, currents_A={'dense': [current]}, summary={'rms_T':1e-5},
                 scenarios={'train':[row], 'holdout':[copy.deepcopy(row)]},
                 solver_status={'fit':dict(success=True, iterations=4, seconds=.1)})
    (path/'quick/results.json').write_text(json.dumps(quick))
    raw = (path/'quick/results.json').read_bytes()
    (path/'study/phase1_input.json').write_bytes(raw)
    study = dict(**{k:actual[k] for k in ('source_commit', 'source_dirty', 'python')},
                 config={'geometry_version':'householder-v2', 'peak_algorithm':'dyadic-pattern-v2'},
                 phase1_sha256=sha(path/'quick/results.json'), trials=[],
                 scenarios={'training':{'1/1':[row]}, 'holdout':[copy.deepcopy(row)]},
                 values=[1e-5], units='m, A, T, rad')
    (path/'study/study.json').write_text(json.dumps(study))
    record = dict(benchmark_version=VERSION, status='RUNNING',
                  quick_runtime=actual, study_runtime=actual,
                  quick_sha256=sha(path/'quick/results.json'), study_sha256=sha(path/'study/study.json'))
    (path/'execution.json').write_text(json.dumps(record))
    return path


def test_attested_dynamic_metadata_and_input_hashes(tmp_path):
    a = bundle(tmp_path/'a')
    b = bundle(tmp_path/'b', commit='b'*40, python='3.11.17')
    result = pair(a, b)
    assert result['status'] == 'PASS'
    assert any(r['path'] == '/study/phase1_sha256' and r['reference'] != r['current']
               for r in result['attested_metadata'])


def test_scientific_current_changes_are_not_metadata(tmp_path):
    a = bundle(tmp_path/'a'); b = bundle(tmp_path/'b', current=1.001)
    with pytest.raises(AssertionError, match='/quick/currents_A/dense/0'):
        pair(a, b)


def test_tampered_result_hash_fails(tmp_path):
    a = bundle(tmp_path/'a'); b = bundle(tmp_path/'b')
    (b/'study/study.json').write_text('{}')
    with pytest.raises(AssertionError, match='Result hash'):
        pair(a, b)


def test_input_copy_link_fails_closed(tmp_path):
    a = bundle(tmp_path/'a'); b = bundle(tmp_path/'b')
    (b/'study/phase1_input.json').write_text('{}')
    with pytest.raises(AssertionError, match='input hash/link'):
        pair(a, b)


def test_incomplete_workers_cannot_claim_validation(tmp_path):
    a = bundle(tmp_path/'a')
    with pytest.raises(AssertionError, match='complete all required'):
        require_complete(a)


def test_false_runtime_provenance_fails(tmp_path):
    a = bundle(tmp_path/'a'); b = bundle(tmp_path/'b')
    record = json.loads((b/'execution.json').read_text())
    record['study_runtime']['python'] = 'not-the-recorded-runtime'
    (b/'execution.json').write_text(json.dumps(record))
    with pytest.raises(AssertionError, match='provenance'):
        pair(a, b)


def test_manifest_rejects_missing_and_tampered_files(tmp_path):
    p = tmp_path/'data.json'; p.write_text('{}')
    (tmp_path/'manifest.json').write_text(json.dumps({'data.json':sha(p)}))
    verify_manifest(tmp_path)
    p.write_text('{"changed": true}')
    with pytest.raises(AssertionError, match='hash/path mismatch'):
        verify_manifest(tmp_path)
    p.unlink()
    with pytest.raises(AssertionError, match='completeness'):
        verify_manifest(tmp_path)
