"""Integrity and independent-reference tests; do not assert a scientific pass."""
import csv
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('phase2d_investigate', Path(__file__).parents[1]/'scripts/phase2d_investigate.py')
investigation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(investigation)


def test_direct_reference_guard_and_negative_value():
    data = investigation.decimal_inputs(dict(response_T_per_A=[[1.]], disturbance_T=[0.], weights=[1.]))
    assert float(investigation.reference(data, [[1.], [2.], [1.5]], 60)['ratio']) == .5
    assert float(investigation.reference(data, [[1.], [2.], [3.]], 90)['ratio']) == -1.
    assert investigation.reference(data, [[1.], [1.], [1.]], 90)['ratio'] is None


def test_inventory_retains_all_fields_and_extra_elements():
    rows = list(investigation.differing_leaves(
        {'x': 1., 'seconds': 2., 'extra': [0]}, {'x': 2., 'seconds': 3., 'extra': [0, 4], 'new': 9}))
    assert {r['path'] for r in rows} == {'/x', '/seconds', '/extra', '/extra/1', '/new'}
    assert next(r for r in rows if r['path'] == '/x')['reason'] == 'outside-tolerance'


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity', '1e999'])
def test_nonfinite_json_is_rejected(tmp_path, value):
    path = tmp_path/'bad.json'; path.write_text('{"a":' + value + '}')
    with pytest.raises(ValueError):
        investigation.load(path)


def test_evidence_tampering_and_missing_inventory_coverage(tmp_path):
    path = tmp_path/'data'; path.write_bytes(b'original')
    with (tmp_path/'sha256_inventory.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Path', 'SHA256', 'Bytes']); writer.writeheader()
        writer.writerow(dict(Path='data', SHA256=investigation.sha(path), Bytes=8))
    assert investigation.verify_inventory(tmp_path, expected_count=1)['entries'] == 1
    (tmp_path/'unexpected').write_bytes(b'x')
    with pytest.raises(ValueError, match='cover exactly'):
        investigation.verify_inventory(tmp_path, expected_count=1)
    (tmp_path/'unexpected').unlink(); path.write_bytes(b'modified')
    with pytest.raises(ValueError, match='mismatch'):
        investigation.verify_inventory(tmp_path, expected_count=1)


@pytest.mark.parametrize('name', ['../escape', 'C:/escape', '/escape'])
def test_escaping_paths_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        investigation.contained(tmp_path, name)


def test_invalid_reference_dimensions_and_weights_rejected():
    with pytest.raises(ValueError):
        investigation.decimal_inputs(dict(response_T_per_A=[[1.]], disturbance_T=[0.], weights=[-1.]))


def test_output_directory_contract(tmp_path):
    root = tmp_path/'evidence'
    root.mkdir()
    investigation.validate_output(root, tmp_path/'fresh-directory')
    for target in (root, root/'child', tmp_path/'investigation.json'):
        with pytest.raises(ValueError):
            investigation.validate_output(root, target)
    target = tmp_path/'existing-file'
    target.write_bytes(b'preserve')
    with pytest.raises(ValueError):
        investigation.validate_output(root, target)
    assert target.read_bytes() == b'preserve'


def test_atomic_write_collision_and_permission_denial(tmp_path, monkeypatch):
    target = tmp_path/'record.json'
    investigation.write(target, {'status': 'original'})
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        investigation.write(target, {'status': 'replacement'})
    assert target.read_bytes() == original
    def denied(*args, **kwargs):
        raise PermissionError('simulated publication denial')
    monkeypatch.setattr(investigation.os, 'link', denied)
    with pytest.raises(PermissionError):
        investigation.write(tmp_path/'denied.json', {})
    assert list(tmp_path.iterdir()) == [target]


def test_incomplete_manifest_and_inventory_count(tmp_path):
    (tmp_path/'manifest.json').write_text('{}')
    with pytest.raises(ValueError, match='completeness'):
        investigation.verify_manifest(tmp_path)
    (tmp_path/'sha256_inventory.csv').write_text('Path,SHA256,Bytes\n')
    with pytest.raises(ValueError, match='count'):
        investigation.verify_inventory(tmp_path)


def test_unknown_inventory_schema(tmp_path):
    (tmp_path/'sha256_inventory.csv').write_text('Path,SHA256,Bytes,unknown\n')
    with pytest.raises(ValueError, match='schema'):
        investigation.verify_inventory(tmp_path)
