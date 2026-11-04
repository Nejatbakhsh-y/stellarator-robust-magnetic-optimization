"""Step 31E fail-closed regression coverage; requires the project environment."""
import importlib.util
from pathlib import Path
from decimal import Decimal, localcontext
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location('step31e', Path(__file__).parents[1]/'scripts/phase2d_step31e_review.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
d = e.d


def test_commits():
    assert e.attribution(d.COMMIT) == 'MATCH'
    assert e.attribution('3a747c1b6535d8b34c5a152650e8fe169515fb14') == 'MISMATCH'
    with pytest.raises(ValueError):
        e.attribution(None)


def test_case_sensitive_and_exact(tmp_path):
    p = tmp_path/'case.json'
    p.write_text('{"D": 1, "d": 2}')
    assert d.load_evidence(p) == {'D': 1, 'd': 2}
    from stellarator_robust.upstream_attribution import pack
    r = e.vector_metrics(pack([0.]), pack([-0.]))
    assert not r['byte_equal'] and r['numerical_exact']


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '1e999', '{"a":1,"a":2}'])
def test_invalid_json(tmp_path, value):
    p = tmp_path/'bad.json'; p.write_text(value)
    with pytest.raises(ValueError):
        d.load_evidence(p)


def test_missing_inputs_outputs():
    with pytest.raises((ValueError, KeyError)):
        d.validate_inputs({'arrays': {}})
    with pytest.raises((ValueError, KeyError)):
        d.solver_metrics({'arrays': {}}, {})


def test_integrity(tmp_path):
    p = tmp_path/'evidence'; p.write_bytes(b'original')
    digest = d.sha(p); d.verify_seal(p, digest)
    p.write_bytes(b'modified')
    with pytest.raises(ValueError):
        d.verify_seal(p, digest)


def test_decimal_ratio_and_guard():
    with localcontext() as ctx:
        ctx.prec = 90
        B, L, P = map(Decimal.from_float, (2.5914425556311e-5, 2.59144802211644e-5, 2.5914502889e-5))
        assert d.ratio(B, L, P) == (L-P)/(L-B)
        assert (abs(L)+abs(B))/abs(L-B) > 900000
        assert d.ratio(B, B+Decimal('1e-16'), P) is None
    a = dict(rms_T=['1', '1.0000000001', '1.00000000005'], ratio='0.5')
    b = dict(rms_T=['1', '1.0000000001', '1.000000000050000001'], ratio='0.49999999')
    assert abs(Decimal(d.differential(a, b)['nonlinear_remainder'])) < Decimal('1e-70')


@pytest.mark.parametrize('row,left,right,status', [
    (3, -.4146889970809172, -.4146889970315089, 'FAIL'),
    (4, .16726624849750296, .16726624849849056, 'PASS'),
    (4, .1672662484971343, .1672662484946451, 'FAIL')])
def test_fault_rows(row, left, right, status):
    assert d.scalar_comparison(left, right)['status'] == status


def test_failure_classification():
    failures = e.failed_nodes({'frozen': {'row4': {'status': 'FAIL'}}})
    assert failures[0]['path'] == '/frozen/row4'
    assert e.classify(True, failures) == 'FAIL'
    assert e.classify(False, []) == 'INCONCLUSIVE'
    assert e.classify(True, []) != 'PASS'
    with pytest.raises(ValueError):
        d.check_classification('PASS', [dict(status='FAIL')])


def test_source_bundle():
    root = Path('results/phase2d/step31-20261031-165725-a14c217c')
    if not root.exists():
        pytest.skip('Source bundle unavailable')
    assert len(d.inventory(root)) == 361
    assert len(d.verify_manifests(root)) == 18
