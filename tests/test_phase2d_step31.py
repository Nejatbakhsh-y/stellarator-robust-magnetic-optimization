"""Step 31 contracts; no test converts a diagnostic success into production PASS."""
import importlib.util
import json
from decimal import Decimal
from pathlib import Path

import numpy as np
import pytest
from stellarator_robust.upstream_attribution import pack, sha, write, validate_inputs

SPEC = importlib.util.spec_from_file_location('step31', Path(__file__).parents[1]/'scripts/phase2d_step31_diagnose.py')
d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(d)


def fixture_inventory(tmp_path):
    raw = tmp_path/'raw'
    raw.mkdir()
    p = raw/'input.json'
    p.write_text('{}')
    write(tmp_path/'source-hashes.json', {'C:/old/download/raw/input.json': sha(p)})
    return p


def test_inventory_positive_and_modified(tmp_path):
    p = fixture_inventory(tmp_path)
    assert len(d.inventory(tmp_path)) == 1
    p.write_text('{"modified":true}')
    with pytest.raises(ValueError, match='modified'):
        d.inventory(tmp_path)


def test_missing_evidence(tmp_path):
    with pytest.raises(FileNotFoundError):
        d.inventory(tmp_path)
    p = fixture_inventory(tmp_path)
    p.unlink()
    with pytest.raises(FileNotFoundError):
        d.inventory(tmp_path)


def test_extra_evidence_and_wrong_fingerprint(tmp_path):
    p = fixture_inventory(tmp_path)
    d.verify_seal(p, sha(p))
    with pytest.raises(ValueError, match='fingerprint'):
        d.verify_seal(p, '0'*64)
    (p.parent/'extra').write_text('x')
    with pytest.raises(ValueError, match='Incomplete'):
        d.inventory(tmp_path)


def test_exact_bytes_differ_from_numerical_equality():
    result = d.compare_array(pack([0.]), pack([-0.]))
    assert not result['byte_equal'] and result['numerical_exact']
    assert result['tolerance']['status'] == 'PASS'


@pytest.mark.parametrize('payload', [dict(shape=[2], binary64_le='00'),
    dict(shape=[1], binary64_le='000000000000f87f'), dict(shape=[-1], binary64_le='')])
def test_invalid_numerical_arrays(payload):
    with pytest.raises(ValueError):
        d.compare_array(payload, pack([1.]))


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_values(value):
    with pytest.raises(ValueError):
        d.scalar_comparison(0., value)


def test_denominator_guard_and_amplification():
    assert d.ratio(Decimal(1), Decimal(1)+Decimal('1e-16'), Decimal(1)) is None
    a = dict(rms_T=['1', '1.0000000001', '1.00000000005'], ratio='0.5')
    b = dict(rms_T=['1', '1.0000000001', '1.000000000050000001'], ratio='0.49999999')
    result = d.differential(a, b)
    assert Decimal(result['observed']) == Decimal('-1e-8')
    assert abs(Decimal(result['nonlinear_remainder'])) < Decimal('1e-70')


@pytest.mark.parametrize('row,ref,cur,expected', [
    (3, -0.4146889970809172, -0.4146889970315089, 'FAIL'),
    (4, 0.16726624849750296, 0.16726624849849056, 'PASS'),
    (4, 0.1672662484971343, 0.1672662484946451, 'FAIL')])
def test_actual_row3_row4_classifications(row, ref, cur, expected):
    result = d.scalar_comparison(ref, cur)
    assert result['status'] == expected
    assert (result['exceedance'] > 0) == (expected == 'FAIL')


def test_incorrect_pass():
    with pytest.raises(ValueError, match='Incorrect PASS'):
        d.check_classification('PASS', [dict(status='FAIL')])
    d.check_classification('FAIL', [dict(status='FAIL')])


def test_independent_decimal_and_compensated_metric():
    a = dict(fine_A=np.eye(2), fine_b=np.array([1., 2.]), fine_weights=np.array([.5, .5]))
    currents = dict(dense=np.array([-.5, 0.]), recovered=np.array([0., -.25]))
    high, low = [d.decimal_metric(a, currents, 0, p) for p in (90, 60)]
    assert abs(float(high['ratio'])-float(low['ratio'])) == 0
    assert abs(d.compensated_metric(a, currents, 0)['ratio']-float(high['ratio'])) < 1e-14


def test_missing_solver_results():
    with pytest.raises((ValueError, KeyError)):
        d.solver_metrics({'arrays': {}}, {})


def test_invalid_scientific_inputs():
    with pytest.raises(ValueError):
        validate_inputs({'schema': 'incorrect'})


def test_latest_supplied_scientific_inputs_when_available():
    # Optional large downloaded artifact test, never substitutes Phase 2C evidence.
    root = Path('results/phase2d/step31-20261031-165725-a14c217c/raw/upstream-sealed/inputs.json')
    if not root.exists():
        pytest.skip('Latest downloaded Phase 2D evidence unavailable')
    data = d.load_evidence(root)
    validate_inputs(data)
    for row, coil in ((3, 3), (4, 6)):
        assert data['cases']['row'+str(row)]['failed'] == coil
