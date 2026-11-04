"""Portable deterministic software checks; no historical archive substitutes."""
import importlib.util
import json
from pathlib import Path
import sys
from decimal import Decimal as D, localcontext

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('step47', SCRIPTS/'phase2d_step47_evidence.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def test_known_hash_and_manifest_tamper(tmp_path):
    p = tmp_path/'result.json'
    p.write_bytes(b'abc')
    digest = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    (tmp_path/'manifest.json').write_text(json.dumps({'result.json': digest}))
    before = e.snapshot(tmp_path)
    assert e.sha(p) == digest
    assert e.seals(tmp_path)[0]['status'] == 'MATCH'
    assert e.snapshot(tmp_path) == before
    p.write_bytes(b'abd')
    assert e.seals(tmp_path)[0]['status'] == 'MISMATCH'
    p.unlink()
    assert e.seals(tmp_path)[0]['status'] == 'MISSING'


@pytest.mark.parametrize('name', ['../outside', '/outside', 'C:/outside', 'x\\y'])
def test_manifest_path_rejection(tmp_path, name):
    (tmp_path/'manifest.json').write_text(json.dumps({name: '0'*64}))
    with pytest.raises(ValueError, match='Unsafe'):
        e.seals(tmp_path)


@pytest.mark.parametrize('text', ['{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'])
def test_invalid_json(tmp_path, text):
    p = tmp_path/'bad.json'
    p.write_text(text)
    with pytest.raises(ValueError):
        e.load(p)


def test_missing_evidence_never_passes():
    v = e.verdict(['missing original evidence'])
    assert v['overall_scientific_status'] == 'INCOMPLETE'
    assert v['scientific_comparison'] == v['production_acceptance'] == 'FAIL'
    assert v['numerical_root_cause'] == 'INCONCLUSIVE'
    assert v['remaining_blockers']


def test_exact_source_required(tmp_path):
    with pytest.raises(ValueError, match='source-commit'):
        e.source_check({'head': '0'*40, 'sha256': {'x': '0'*64}}, tmp_path)


def test_noncircular_output_manifest(tmp_path):
    p = tmp_path/'recovery.json'
    p.write_bytes(b'abc')
    record = {'schema': 'step45-noncircular-v1', 'outputs': {'recovery.json': e.sha(p)},
              'source_sha256': {'scripts/example.py': '0'*64}}
    (tmp_path/'output-manifest.json').write_text(json.dumps(record))
    checks = e.seals(tmp_path)
    assert len(checks) == 1
    assert checks[0]['status'] == 'MATCH'
    p.write_bytes(b'different')
    assert e.seals(tmp_path)[0]['status'] == 'MISMATCH'


def test_field_known_finite_wire_and_precision():
    # Oriented square, side 2, observation at center: 4 sqrt(2)*1e-7 T.
    vertices = [[-1., -1., 0.], [1., -1., 0.], [1., 1., 0.], [-1., 1., 0.]]
    low = e.polygon_field([0., 0., 0.], vertices, digits=60)
    high = e.polygon_field([0., 0., 0.], vertices, digits=90)
    assert high[0] == high[1] == 0
    assert abs(high[2]-D(4)*D(2).sqrt()*D('1e-7')) < D('1e-33')
    assert abs(high[2]-low[2]) < D('1e-60')
    reverse = e.polygon_field([0., 0., 0.], vertices[::-1])
    with localcontext() as ctx:
        ctx.prec = 90
        assert abs(reverse[2]+high[2]) < D('1e-85')
    with pytest.raises(ValueError, match='clearance'):
        e.polygon_field([0., -1., 0.], vertices)


def test_reused_scalar_qr_kkt_and_guard():
    import phase2d_step46_independent as scalar
    M, y = [[1., 0.], [0., 2.], [1., 0.]], [0.25, -1., 0.25]
    reference = scalar.reference(M, y)
    assert reference['status'] == 'INTERIOR_REFERENCE'
    assert abs(D(reference['x'][0])-D('.25')) < D('1e-80')
    assert abs(D(reference['x'][1])+D('.5')) < D('1e-80')
    assert D(scalar.certificate([[1]], [2], [1])['kkt_max']) == 0
    assert D(scalar.certificate([[1]], [2], [1.1])['bound_violation']) > 0
    assert scalar.ratio([1, 3, 2])['ratio'] == '0.5'
    with pytest.raises(ValueError, match='guard'):
        scalar.ratio(['1', '1.000000000000001', '1'])


def test_payload_preserves_signed_zero_and_rejects_truncation():
    a = e.unpack({'shape': [2], 'binary64_le': '00000000000000000000000000000080'})
    assert a.tobytes().hex() == '00000000000000000000000000000080'
    with pytest.raises(ValueError):
        e.unpack({'shape': [2], 'binary64_le': '00'})
