"""Archive rejection and conservative scientific status regression coverage."""
import importlib.util
import json
from pathlib import Path
import stat
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('step50', ROOT/'scripts/phase2d_step50_reproduction.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
EVIDENCE = ROOT/'results/phase2d/step49-original-archives-20261102-120255-a1314650'


def make(tmp_path, names=None):
    path = tmp_path/'test.zip'
    names = names or [('value.txt', b'original')]
    # ZipInfo converts backslashes on Windows. Serialize a portable spelling,
    # then restore the literal unsafe spelling in both ZIP filename records.
    literal_name = None
    if len(names) == 1 and isinstance(names[0][0], str) and chr(92) in names[0][0]:
        literal_name, content = names[0]
        serialized_name = literal_name.replace(chr(92), '/')
        names = [(serialized_name, content)]
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as z:
        for name, content in names:
            z.writestr(zipfile.ZipInfo(name) if isinstance(name, str) else name, content)
    if literal_name is not None:
        before = serialized_name.encode('utf-8')
        after = literal_name.encode('utf-8')
        assert len(before) == len(after)
        raw = path.read_bytes()
        assert raw.count(before) == 2  # Local header and central directory.
        assert after not in raw
        raw = raw.replace(before, after)
        assert raw.count(after) == 2
        assert before not in raw
        path.write_bytes(raw)
        with zipfile.ZipFile(path) as z:
            assert len(z.infolist()) == 1
            assert z.infolist()[0].orig_filename == literal_name
            assert z.testzip() is None
            assert z.read(z.infolist()[0]) == content
    return path


def test_all_71_original_archives():
    manifest = s.decode((EVIDENCE/'manifest.json').read_bytes())
    artifacts = [a for r in manifest['runs'] for a in r['artifacts']]
    assert len(artifacts) == 71
    assert len({a['id'] for a in artifacts}) == 71
    assert len(manifest['runs'][2]['artifacts']) == 17
    for a in artifacts:
        members = s.archive(EVIDENCE/a['file'], a['github_sha256'].removeprefix('sha256:'))
        assert members
        for seal in s.seals(members):
            assert all(r['status'] != 'MISMATCH' for r in seal['records'])


def test_missing_archive(tmp_path):
    with pytest.raises(FileNotFoundError):
        s.archive(tmp_path/'absent.zip', '0'*64)


def test_incorrect_sha(tmp_path):
    with pytest.raises(ValueError, match='SHA256'):
        s.archive(make(tmp_path), '0'*64)


def test_crc_failure(tmp_path):
    path = make(tmp_path)
    raw = path.read_bytes().replace(b'original', b'corrupt!')
    path.write_bytes(raw)
    with pytest.raises(zipfile.BadZipFile):
        s.archive(path, s.digest(raw))


def test_truncated(tmp_path):
    path = make(tmp_path)
    raw = path.read_bytes()[:-24]
    path.write_bytes(raw)
    with pytest.raises(zipfile.BadZipFile):
        s.archive(path, s.digest(raw))


@pytest.mark.parametrize('name', ['../x', '/x', 'a/../x', 'C:/x', 'a\\x',
                                  'a//b', 'a/./b', 'NUL.txt', 'a.', 'a/./x', 'a//x',
                                  'C:x', '//server/share/x', '\\\\server\\share\\x',
                                  'a:x', 'a\x01x', 'a\x7fx', 'a\x85x', 'a ',
                                  'a/COM1.txt', 'LPT¹', 'CONOUT$', 'a/.../x',
                                  'a//', 'a/../', 'a?x', 'a|x'] )
def test_unsafe_paths(tmp_path, name):
    path = make(tmp_path, [(name, b'x')])
    with zipfile.ZipFile(path) as z:
        assert z.infolist()[0].orig_filename == name
    if chr(92) in name:
        assert path.read_bytes().count(name.encode('utf-8')) == 2
    with pytest.raises(ValueError, match='Unsafe'):
        s.archive(path, s.digest(path.read_bytes()))


@pytest.mark.parametrize('name', ['a\\x', 'a\\nested\\x', 'a\\directory/',
                                  '\\\\server\\share\\x'])
def test_backslash_fixture_with_normalizing_zipinfo(tmp_path, monkeypatch, name):
    original_writestr = zipfile.ZipFile.writestr

    def normalizing_writestr(self, entry, data, *args, **kwargs):
        if isinstance(entry, str):
            entry = zipfile.ZipInfo(entry)
        entry.filename = entry.filename.replace(chr(92), '/')
        return original_writestr(self, entry, data, *args, **kwargs)

    # Exercise the Windows writer behavior on either operating system.
    with monkeypatch.context() as patch:
        patch.setattr(zipfile.ZipFile, 'writestr', normalizing_writestr)
        probe = tmp_path/'normalizing-writer.zip'
        with zipfile.ZipFile(probe, 'w') as z:
            z.writestr(zipfile.ZipInfo(name), b'x')
        with zipfile.ZipFile(probe) as z:
            assert z.infolist()[0].orig_filename == name.replace(chr(92), '/')
        path = make(tmp_path, [(name, b'x')])
    with zipfile.ZipFile(path) as z:
        assert z.infolist()[0].orig_filename == name
        assert z.testzip() is None
    assert path.read_bytes().count(name.encode('utf-8')) == 2
    with pytest.raises(ValueError, match='^Unsafe ZIP member path$'):
        s.archive(path, s.digest(path.read_bytes()))


def test_duplicate_member(tmp_path):
    path = make(tmp_path, [('A', b'1'), ('a', b'2')])
    with pytest.raises(ValueError, match='Duplicate'):
        s.archive(path, s.digest(path.read_bytes()))


@pytest.mark.parametrize('name', ['', 'a\x00x', 'a\\x', 'a//', '/'])
def test_original_name_validation(name):
    with pytest.raises(ValueError, match='Unsafe'):
        s.safe(name, directory=name.endswith('/'))


def test_embedded_nul_archive(tmp_path):
    path = make(tmp_path, [('aQx', b'x')])
    raw = path.read_bytes().replace(b'aQx', b'a\x00x')
    path.write_bytes(raw)
    with pytest.raises(ValueError, match='Unsafe'):
        s.archive(path, s.digest(raw))


@pytest.mark.parametrize('names', [ [('a/', b''), ('a/', b'')],
                                    [('a', b'x'), ('a/', b'')],
                                    [('a/', b''), ('A/', b'')],
                                    [('a/x', b'x'), ('A/y', b'y')] ])
def test_duplicate_normalized_paths(tmp_path, names):
    path = make(tmp_path, names)
    with pytest.raises(ValueError, match='Duplicate'):
        s.archive(path, s.digest(path.read_bytes()))


def test_nested_directories_and_original_sha(tmp_path):
    path = make(tmp_path, [('a/', b''), ('a/b/', b''), ('a/b/x', b'original')])
    original = path.read_bytes()
    expected = s.digest(original)
    assert s.archive(path, expected) == {'a/b/x': b'original'}
    assert path.read_bytes() == original
    assert s.digest(path.read_bytes()) == expected


@pytest.mark.parametrize('names', [[('a', b'x'), ('a/b/', b'')],
                                    [('a/', b'payload')]])
def test_malformed_directories(tmp_path, names):
    path = make(tmp_path, names)
    with pytest.raises(ValueError):
        s.archive(path, s.digest(path.read_bytes()))


def test_invalid_zip(tmp_path):
    path = tmp_path/'invalid.zip'
    path.write_bytes(b'not a ZIP')
    with pytest.raises(zipfile.BadZipFile):
        s.archive(path, s.digest(path.read_bytes()))


def test_extraction_boundary(tmp_path, monkeypatch):
    destination = tmp_path/'destination'
    target = destination/'nested'/'x'
    resolve = Path.resolve
    monkeypatch.setattr(Path, 'resolve', lambda self: tmp_path/'outside' if self == target
                        else resolve(self))
    with pytest.raises(ValueError, match='Unsafe'):
        s.extraction_target(destination, 'nested/x')


def test_symlink(tmp_path):
    entry = zipfile.ZipInfo('link')
    entry.external_attr = (stat.S_IFLNK | 0o777) << 16
    path = make(tmp_path, [(entry, b'../elsewhere')])
    with pytest.raises(ValueError, match='link'):
        s.archive(path, s.digest(path.read_bytes()))


def test_missing_internal_manifest():
    assert s.seals({'inputs.json': b'{}'}) == []


def test_bad_internal_manifest():
    rows = s.seals({'manifest.json': json.dumps({'x': '0'*64}).encode(), 'x': b'x'})
    assert rows[0]['records'][0]['status'] == 'MISMATCH'


def test_incorrect_source_commit():
    rows = s.source({'source-sha256.json': json.dumps(
        {'head': 'incorrect', 'sha256': {'x': '0'*64}}).encode()}, {'source_sha': s.COMMITS[0]})
    assert rows[0]['association'] == 'CONFLICT'
    assert rows[0]['files'][0]['status'] == 'UNAVAILABLE'


def test_historical_merge_association():
    rows = s.source({'source-sha256.json': json.dumps(
        {'head': s.COMMITS[1], 'sha256': {}}).encode()}, {'source_sha': s.COMMITS[0]})
    assert rows[0]['association'] == 'HISTORICAL_MERGE_ASSOCIATION'
    assert rows[0]['recorded_commit'] != rows[0]['run_commit']


def test_duplicate_archive_identities(tmp_path):
    a = dict(id=1, file='x.zip', name='x', github_sha256='sha256:'+'0'*64, verified_sha256='0'*64)
    rows, _, _ = s.assess(tmp_path, {'runs': [dict(run_id=1, source_sha=s.COMMITS[0], artifacts=[a, a])]}, tmp_path/'out')
    assert 'Duplicate archive identity' in rows[1]['error']


def test_missing_numerical_inputs():
    assert s.numerical({}) == []


def test_no_false_scientific_acceptance_and_fail_preservation(tmp_path, monkeypatch):
    monkeypatch.setattr(s, 'recover_objects', lambda output: [])
    manifest = tmp_path/'manifest.json'
    manifest.write_text('{"runs": []}')
    output = tmp_path/'output'
    assert s.main(['--archive-root', str(tmp_path/'archives'), '--manifest', str(manifest),
                   '--output', str(output)]) == 2
    status = json.loads((output/'status.json').read_text())
    assert status['scientific_comparison'] == status['production_acceptance'] == 'FAIL'
    assert status['overall_scientific_status'] != 'PASS'


def test_existing_output_is_preserved(tmp_path):
    assert s.main(['--archive-root', str(tmp_path/'archives'), '--manifest', str(tmp_path/'missing'),
                   '--output', str(tmp_path)]) == 1


def test_incorrect_solver_and_failed_ratio():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    import phase2d_step46_independent as independent
    cert = independent.certificate([[1.0]], [0.0], [0.5])
    assert float(cert['kkt_max']) == 0.5
    assert not independent.agrees('0.99', '1.0')
    with pytest.raises(ValueError, match='guard'):
        independent.ratio([1e-16, 1e-16, 0.0])
