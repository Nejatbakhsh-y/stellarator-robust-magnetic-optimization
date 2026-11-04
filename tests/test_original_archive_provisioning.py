"""Historical retrieval is explicit, immutable, authenticated and fail-closed."""
import io
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import provision_original_archives as p


def fixture(tmp_path, monkeypatch):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        archive.writestr('value.txt', 'original')
    raw_zip = stream.getvalue()
    item = dict(id=42, name='original', file='7/artifact-42.zip',
                github_sha256='sha256:'+p.original.digest(raw_zip),
                verified_sha256=p.original.digest(raw_zip))
    run = dict(run_id=7, source_sha='a'*40, artifacts=[item])
    manifest = dict(runs=[run])
    raw = json.dumps(manifest).encode()
    monkeypatch.setattr(p, 'pinned_manifest', lambda: (raw, manifest))
    meta = dict(id=42, name='original', digest=item['github_sha256'], expired=False,
                workflow_run=dict(id=7, head_sha='a'*40))
    calls = []

    def request(path, token, binary=False):
        calls.append(path)
        return raw_zip if binary else dict(total_count=1, artifacts=[meta])
    return tmp_path/'archives', item, meta, calls, request


def test_versioned_manifest_is_exact_original_bytes():
    raw, manifest = p.pinned_manifest()
    assert p.original.digest(raw) == '4ca1db2a783f2d62295e5ec2ef623b434a03c1b5a2a485f728c0f67df3d4a26e'
    assert sum(len(r['artifacts']) for r in manifest['runs']) == 71


def test_clean_provision_then_offline_verify(tmp_path, monkeypatch):
    root, item, meta, calls, request = fixture(tmp_path, monkeypatch)
    assert p.provision(root, 'fixture-token', request)['status'] == 'PASS'
    before = {x.relative_to(root).as_posix(): x.read_bytes() for x in root.rglob('*') if x.is_file()}
    calls.clear()
    assert p.provision(root, request=request, verify_only=True)['status'] == 'PASS'
    assert calls == []
    assert before == {x.relative_to(root).as_posix(): x.read_bytes() for x in root.rglob('*') if x.is_file()}


@pytest.mark.parametrize('change', ['expired', 'digest', 'head', 'missing'])
def test_unavailable_or_wrong_origin_fails_without_manifest(tmp_path, monkeypatch, change):
    root, item, meta, calls, request = fixture(tmp_path, monkeypatch)
    if change == 'expired': meta['expired'] = True
    if change == 'digest': meta['digest'] = 'sha256:'+'0'*64
    if change == 'head': meta['workflow_run']['head_sha'] = 'b'*40
    if change == 'missing': meta['id'] = 43
    with pytest.raises(ValueError):
        p.provision(root, 'fixture-token', request)
    assert not (root/'manifest.json').exists()
    assert not any('/zip' in c for c in calls)


def test_corrupt_download_and_existing_archive_not_repaired(tmp_path, monkeypatch):
    root, item, meta, calls, request = fixture(tmp_path, monkeypatch)
    def corrupted(path, token, binary=False):
        return b'corrupt' if binary else request(path, token)
    with pytest.raises(ValueError, match='downloaded SHA256'):
        p.provision(root, 'fixture-token', corrupted)
    target = root/item['file']; target.parent.mkdir(parents=True)
    target.write_bytes(b'existing historical bytes')
    with pytest.raises(ValueError, match='ZIP SHA256'):
        p.provision(root, request=request)
    assert target.read_bytes() == b'existing historical bytes'


def test_absent_originals_never_skipped_or_regenerated(tmp_path, monkeypatch):
    root, item, meta, calls, request = fixture(tmp_path, monkeypatch)
    with pytest.raises(FileNotFoundError):
        p.provision(root, request=request, verify_only=True)
    assert not root.exists()
    assert calls == []


def test_conflicting_manifest_not_overwritten(tmp_path, monkeypatch):
    root, item, meta, calls, request = fixture(tmp_path, monkeypatch)
    root.mkdir(); (root/'manifest.json').write_bytes(b'historical')
    with pytest.raises(ValueError, match='never overwrite'):
        p.provision(root, request=request)
    assert (root/'manifest.json').read_bytes() == b'historical'


def test_explicit_root_does_not_hide_missing_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv('STELLARATOR_ORIGINAL_ARCHIVES', str(tmp_path/'explicit-originals'))
    spec = importlib.util.spec_from_file_location('isolated_archive_test',
        p.ROOT/'tests/test_phase2d_step50_reproduction.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.EVIDENCE == tmp_path/'explicit-originals'
    with pytest.raises(FileNotFoundError):
        module.test_all_71_original_archives()


def test_token_is_not_forwarded_to_artifact_storage(monkeypatch):
    class Redirect:
        def open(self, request, timeout):
            assert request.get_header('Authorization') == 'Bearer fixture-secret'
            raise p.urllib.error.HTTPError(request.full_url, 302, 'redirect',
                {'Location': 'https://example.blob.core.windows.net/original.zip'}, None)
    monkeypatch.setattr(p.urllib.request, 'build_opener', lambda *args: Redirect())
    def storage(url, timeout):
        assert url == 'https://example.blob.core.windows.net/original.zip'
        return io.BytesIO(b'original')
    monkeypatch.setattr(p.urllib.request, 'urlopen', storage)
    assert p.api('/actions/artifacts/42/zip', 'fixture-secret', binary=True) == b'original'
    with pytest.raises(ValueError, match='actions:read'):
        p.api('/actions/artifacts/42/zip', None, binary=True)


def test_all_ci_regression_and_verifier_jobs_provision_first():
    for path in (p.ROOT/'.github/workflows').glob('*.yml'):
        workflow = yaml.load(path.read_text(encoding='utf-8-sig'), Loader=yaml.BaseLoader)
        for job in workflow['jobs'].values():
            provisioned = False
            for step in job.get('steps', []):
                provisioned |= step.get('uses') == './.github/actions/provision-original-archives'
                command = step.get('run', '')
                if ('python -m pytest' in command or any('python scripts/'+s in command for s in
                    ('phase2_cloud_ci.py', 'phase2b_verify.py', 'phase2c_verify.py'))):
                    assert provisioned, (path, command)
                    assert workflow['permissions']['actions'] == 'read'
