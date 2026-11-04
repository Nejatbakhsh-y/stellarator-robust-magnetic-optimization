"""Independent contracts; synthetic checks do not authenticate historical data."""
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step46_independent as s


def test_quotient_rule_and_finite_difference():
    r = s.ratio([1,3,2])
    assert D(r['ratio']) == D('.5')
    assert list(map(D,r['gradient'])) == [D('.25'),D('.25'),D('-.5')]
    for a,b in zip(r['gradient'],r['finite_difference']):
        assert abs(D(a)-D(b)) < D('1e-35')


@pytest.mark.parametrize('values',[[0,D('1e-15'),0],[1,1,2]])
def test_guard(values):
    with pytest.raises(ValueError):
        s.ratio(values)


def test_tolerance_is_not_relaxed():
    assert s.agrees('1.0000000000101','1')
    assert not s.agrees('1.000000000010100001','1')
    assert not s.agrees('-0.4146889971','-0.41468899708091722')


def test_bound_kkt_signs_and_infeasibility():
    assert D(s.certificate([[1]],[2],[1])['kkt_max']) == 0
    assert D(s.certificate([[1]],[-2],[-1])['kkt_max']) == 0
    assert D(s.certificate([[1]],[0],[1])['kkt_max']) == 1
    assert D(s.certificate([[1]],[2],[2])['bound_violation']) == 1


def test_householder_reference_independent_residual():
    for digits in (60,90):
        r = s.reference([[1,0],[0,2],[1,1]],[D('.25'),D('-.5'),0],digits)
        assert r['status'] == 'INTERIOR_REFERENCE'
        assert D(r['certificate']['kkt_max']) < D('1e-50')
    assert s.reference([[1]],[2])['status'] == 'NOT_CERTIFIED'
    assert s.reference([[0]],[1])['status'] == 'NOT_CERTIFIED'


def test_direct_field_and_current_intervention():
    A,b,w = [[1,2],[2,-1]],[1,0],[D('.5'),D('.5')]
    f,n = s.forward(A,b,w,[1,2])
    assert f == [D(6),D(0)]
    assert abs(n*n-D(18)) < D('1e-25')
    with localcontext() as c:
        c.prec = 90
        r = s.intervention(A,b,w,[1,2],[0,1],[1,2],[0,D('1.00000001')],0)
        assert D(r['delta_R']) != 0
        assert abs(D(r['nonlinear_residual'])) < abs(D(r['delta_R']))*D('1e-6')


def test_reject_nonfinite_and_truncated_dimensions():
    with pytest.raises(ValueError):
        s.forward([[1,2]],[0],[1],[1])
    with pytest.raises(ValueError):
        s.ratio([0,float('nan'),1])


def test_missing_evidence_cannot_pass(tmp_path,monkeypatch):
    monkeypatch.setattr(s,'__file__',str(tmp_path/'scripts'/'phase2d_step46_independent.py'))
    out = tmp_path/'results/phase2d/step46'
    assert s.main(['--output',str(out)]) == 2
    import json
    r = json.loads((out/'assessment.json').read_text())
    assert r['artifact_authentication'] == 'MISSING_EVIDENCE'
    assert r['production_acceptance'] == r['step32'] == r['step33'] == r['step45'] == 'FAIL'
    assert r['independent_calculation'] == 'INCOMPLETE'
    assert r['overall_scientific_status'] == 'PARTIAL'
    manifest = json.loads((out/'manifest.json').read_text())
    assert manifest['diagnostic_source_sha256'] is None
    assert manifest['result_sha256'] == hashlib.sha256((out/'assessment.json').read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        s.main(['--output',str(out)])


def isolated_source(tmp_path, monkeypatch):
    source = tmp_path/'scripts'/'phase2d_step46_independent.py'
    source.parent.mkdir()
    source.write_bytes(Path(s.__file__).read_bytes())
    monkeypatch.setattr(s, '__file__', str(source))
    return source


def assert_fail_closed(out):
    r = json.loads((out/'assessment.json').read_text())
    assert r['artifact_authentication'] == 'MISSING_EVIDENCE'
    assert r['production_acceptance'] == r['step32'] == r['step33'] == r['step45'] == 'FAIL'
    assert r['overall_scientific_status'] == 'PARTIAL'
    return r


def test_existing_source_exact_bytes_and_missing_history(tmp_path, monkeypatch):
    source = isolated_source(tmp_path, monkeypatch)
    historical = tmp_path/'historical.json'
    historical.write_bytes(b'{"scientific_comparison":"FAIL"}\n')
    original = historical.read_bytes()
    out = tmp_path/'results/phase2d/new/nested'
    assert not out.parent.exists()
    assert s.main(['--output',str(out)]) == 2
    assert_fail_closed(out)
    manifest = json.loads((out/'manifest.json').read_text())
    assert set(manifest) == {'result_sha256','diagnostic_source_sha256'}
    assert manifest['diagnostic_source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert historical.read_bytes() == original


def test_source_digest_no_substitute_and_exact_sha256(tmp_path):
    source = tmp_path/'diagnostic.py'
    assert s.diagnostic_source_digest(source) is None
    source.write_bytes(b'abc')
    assert s.diagnostic_source_digest(source) == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    source.write_bytes(b'abc\r\n')
    assert s.diagnostic_source_digest(source) == hashlib.sha256(b'abc\r\n').hexdigest()


def test_source_disappears_after_check(tmp_path, monkeypatch):
    source = tmp_path/'diagnostic.py'
    source.write_bytes(b'abc')
    def disappeared(path):
        raise FileNotFoundError(path)
    monkeypatch.setattr(Path, 'read_bytes', disappeared)
    assert s.diagnostic_source_digest(source) is None


def test_unrelated_source_read_failure_propagates(tmp_path, monkeypatch):
    source = tmp_path/'diagnostic.py'
    source.touch()
    def denied(path):
        raise PermissionError(path)
    monkeypatch.setattr(Path, 'read_bytes', denied)
    with pytest.raises(PermissionError):
        s.diagnostic_source_digest(source)


def test_missing_authenticated_input_writes_incomplete(tmp_path, monkeypatch):
    isolated_source(tmp_path, monkeypatch)
    out = tmp_path/'results/phase2d/missing-input'
    assert s.main(['--capture',str(tmp_path/'missing-capture'),
                   '--input-sha256','0'*64,'--output',str(out)]) == 2
    r = assert_fail_closed(out)
    assert r['independent_calculation'] == r['recovery_ratio_validation'] == 'INCOMPLETE'
    assert (out/'manifest.json').is_file()


def test_missing_source_blocks_even_successful_local_calculation(tmp_path, monkeypatch):
    monkeypatch.setattr(s, '__file__', str(tmp_path/'scripts/absent.py'))
    monkeypatch.setattr(s, 'investigate', lambda *args: {
        'recovery': {'row3': {'pass_original_tolerance': True}}})
    out = tmp_path/'results/phase2d/no-source'
    assert s.main(['--capture',str(tmp_path/'capture'),
                   '--input-sha256','0'*64,'--output',str(out)]) == 2
    r = assert_fail_closed(out)
    assert r['independent_calculation'] == r['recovery_ratio_validation'] == 'INCOMPLETE'


def test_incorrect_authenticated_source_identity_is_not_swallowed(tmp_path, monkeypatch):
    import phase2d_step42_replay as transport
    isolated_source(tmp_path, monkeypatch)
    def invalid(*args):
        transport.validation.source_check(
            dict(head='0'*40,sha256={'missing.py':'0'*64}), '0'*40, tmp_path)
    monkeypatch.setattr(transport, 'load_capture', invalid)
    with pytest.raises(ValueError, match='source'):
        s.main(['--capture',str(tmp_path/'capture'),'--input-sha256','0'*64,
                '--output',str(tmp_path/'results/phase2d/invalid-source')])


def test_local_success_never_promotes_historical_acceptance(tmp_path, monkeypatch):
    isolated_source(tmp_path, monkeypatch)
    monkeypatch.setattr(s, 'investigate', lambda *args: {
        'recovery': {'row3': {'pass_original_tolerance': True}}})
    out = tmp_path/'results/phase2d/local-only'
    assert s.main(['--capture',str(tmp_path/'capture'),'--input-sha256','0'*64,
                   '--output',str(out)]) == 1
    assert_fail_closed(out)
