"""Portable provenance fixtures do not establish research acceptance."""
import importlib.util
from pathlib import Path
import subprocess

import pytest

SPEC = importlib.util.spec_from_file_location('step48', Path(__file__).resolve().parents[1]/
                                             'scripts/phase2d_step48_provenance.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


@pytest.fixture
def repo(tmp_path):
    def run(*args):
        return subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True).stdout.decode().strip()
    run('init')
    run('config', 'user.email', 'fixture@example.invalid')
    run('config', 'user.name', 'Fixture')
    run('config', 'core.autocrlf', 'false')
    (tmp_path/'source.py').write_bytes(b'first\n')
    run('add', 'source.py')
    run('commit', '-m', 'first')
    first = run('rev-parse', 'HEAD')
    (tmp_path/'source.py').write_bytes(b'second\r\n')
    run('add', 'source.py')
    run('commit', '-m', 'second')
    return tmp_path, first, run('rev-parse', 'HEAD')


def test_exact_blob_and_different_commits(repo):
    root, first, second = repo
    a = m.check_source(root, first, 'source.py', m.sha(b'first\n'))
    b = m.check_source(root, second, 'source.py', m.sha(b'second\r\n'))
    assert a['status'] == b['status'] == 'VERIFIED_MATCH'
    assert a['object'] != b['object']
    assert a['actual_sha256'] == m.sha(b'first\n')


def test_stale_manifest_preserves_record(repo):
    root, first, second = repo
    digest = m.sha(b'first\n')
    r = m.check_source(root, second, 'source.py', digest, candidates=[first])
    assert r['status'] == 'VERIFIED_MISMATCH'
    assert r['recorded_sha256'] == digest and r['recorded_commit'] == second
    assert r['matching_other_commits'][0]['commit'] == first
    assert r['stale_manifest'] == 'SUPPORTED_BY_OTHER_COMMIT'


def test_missing_object_is_not_hash_of_empty_stdout(repo):
    root, _, _ = repo
    r = m.blob(root, '0'*40, 'source.py')
    assert r['status'] == 'SOURCE_COMMIT_UNAVAILABLE'
    assert 'actual_sha256' not in r


@pytest.mark.parametrize('name', ['absent.py', '../source.py', 'C:/source.py', '/source.py', 'a\\b'])
def test_incorrect_paths(repo, name):
    root, first, _ = repo
    assert m.blob(root, first, name)['status'] == 'MISSING_EVIDENCE'


def test_conflicting_source_identity(repo):
    root, first, second = repo
    r = m.check_source(root, first, 'source.py', m.sha(b'first\n'), second)
    assert r['status'] == 'VERIFIED_MATCH'
    assert r['identity_status'] == 'SOURCE_IDENTITY_INCONSISTENT'


def test_untrusted_metadata_and_missing_zip():
    assert m.archive_status([], {'expired': False, 'digest': 'sha256:'+'a'*64}) == 'MISSING_EVIDENCE'
    assert m.archive_status(['unbound.zip']) != 'VERIFIED_MATCH'


def test_incomplete_numerical_is_not_completed():
    r = m.classify_numerical({'solver': {'dense': {'success': True}}})
    assert r['independent_calculation'] == 'INCOMPLETE'
    assert r['geometry'] == 'INCOMPLETE'


def test_geometry_failure_and_failed_recovery():
    r = m.classify_numerical({'independent_geometry_probes': [{'agrees': False}],
                             'recovery': {'row3': {'pass_original_tolerance': False}}})
    assert r['geometry'] == 'FAIL' and r['recovery']['row3'] == 'FAIL'


def test_no_false_scientific_pass():
    r = m.final_status()
    assert r['scientific_comparison'] == r['production_acceptance'] == 'FAIL'
    assert r['overall_scientific_status'] == 'INCOMPLETE'
    assert r['unique_numerical_root_cause'] == 'INCONCLUSIVE'


def test_historical_bytes_preserved(repo):
    root, first, _ = repo
    before = m.snapshot(root)
    m.check_source(root, first, 'source.py', 'a'*64)
    assert m.snapshot(root) == before


def test_encoding_variation_is_not_silent_match(repo):
    root, first, _ = repo
    r = m.check_source(root, first, 'source.py', m.sha(b'first\r\n'))
    assert r['status'] == 'VERIFIED_MISMATCH' and r['encoding_only_match']
