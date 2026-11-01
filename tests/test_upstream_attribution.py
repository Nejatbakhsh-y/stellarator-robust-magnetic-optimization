"""Attribution contracts, independent references, and failure integrity."""
import numpy as np
import pytest
from stellarator_robust.upstream_attribution import pack, unpack, reference, close, write


def test_exact_binary64_serialization():
    x = np.array([0., -0., np.nextafter(1., 2.), np.finfo(float).tiny])
    assert x.tobytes() == unpack(pack(x)).tobytes()
    assert pack(x) == pack(unpack(pack(x)))
    with pytest.raises(ValueError):
        pack([np.nan])


def test_independent_interior_reference_and_rank_failure():
    M = np.array([[1., 0.], [0., 2.], [1., 1.]])
    x = np.array([.25, -.125])
    low, high = [reference(M, M@x, n) for n in (60, 90)]
    assert low['status'] == high['status'] == 'PASS'
    assert close(x, [float(v) for v in high['x']])['status'] == 'PASS'
    assert reference(np.zeros((3, 2)), np.zeros(3), 60)['status'] == 'INCONCLUSIVE'


def test_active_bounds_are_not_unconstrained_reference_pass():
    r = reference(np.eye(2), np.array([2., -.5]), 60)
    assert r['status'] == 'INCONCLUSIVE'
    assert 'Active bounds' in r['reason']


def test_failure_reporting_and_no_overwrite(tmp_path):
    path = tmp_path/'evidence.json'
    write(path, {'status': 'FAIL'})
    old = path.read_bytes()
    with pytest.raises(FileExistsError):
        write(path, {'status': 'PASS'})
    assert path.read_bytes() == old
    assert close([0.], [1e-12])['status'] == 'FAIL'
    assert close([1.], [1., 2.])['status'] == 'FAIL'


def test_frozen_current_field_linearity_and_analytic_center():
    from stellarator_robust.model import circle, field, MU0
    n, radius = 512, .16
    coil = circle([0., 0., 0.], [0., 0., 1.], radius, n, 'householder-v2')
    points = np.array([[0., 0., 0.], [.01, .02, .03]])
    B = field(points, coil, 1.)
    assert close(field(points, coil, -3.), -3*B)['status'] == 'PASS'
    expected = MU0*n*np.tan(np.pi/n)/(2*np.pi*radius)
    assert close(B[0], [0., 0., expected])['status'] == 'PASS'
    from stellarator_robust.upstream_attribution import decimal_field
    independent = np.array(decimal_field(points, coil.vertices, 1., 60), float)
    assert close(independent, B)['status'] == 'PASS'


def test_production_fault_capture_and_repeated_currents():
    from pathlib import Path
    import json
    from stellarator_robust.upstream_attribution import capture
    config = json.loads(Path('configs/phase2c_quick.json').read_text())
    assert config['segments'] == 512
    assert config['ridge'] == 1e-6
    assert config['imax_A'] == 3000
    first, second = capture(config), capture(config)
    for row, failed in ((3, 3), (4, 6)):
        name = 'row'+str(row)
        assert first['cases'][name]['failed'] == failed
        x = unpack(first['arrays'][name+'_x'])
        assert x[failed] == 0 and max(abs(x)) <= 1
        assert close(x, unpack(second['arrays'][name+'_x']))['status'] == 'PASS'
    assert first['arrays'] == second['arrays']


def test_worker_missing_empty_and_altered_manifest_rejected(tmp_path):
    from stellarator_robust.upstream_attribution import verify_worker, WORKER_FILES, sha
    with pytest.raises(FileNotFoundError):
        verify_worker(tmp_path, '0'*64)
    write(tmp_path/'manifest.json', {})
    with pytest.raises(ValueError, match='inventory'):
        verify_worker(tmp_path, '0'*64)
    (tmp_path/'manifest.json').unlink()
    for name in WORKER_FILES:
        write(tmp_path/name, {})
    entries = {name: sha(tmp_path/name) for name in WORKER_FILES}
    write(tmp_path/'manifest.json', entries)
    (tmp_path/'frozen-solve.json').write_text('{"altered":true}')
    with pytest.raises(ValueError, match='manifest mismatch'):
        verify_worker(tmp_path, '0'*64)


def test_sealed_input_fingerprint_and_source_provenance(tmp_path):
    from stellarator_robust.upstream_attribution import verify_worker, WORKER_FILES, sha, source_fingerprints
    for name in WORKER_FILES:
        write(tmp_path/name, {})
    def reseal():
        (tmp_path/'manifest.json').unlink(missing_ok=True)
        write(tmp_path/'manifest.json', {name: sha(tmp_path/name) for name in WORKER_FILES})
    reseal()
    with pytest.raises(ValueError, match='fingerprint'):
        verify_worker(tmp_path, '0'*64)
    digest = sha(tmp_path/'sealed-inputs.json')
    (tmp_path/'status.json').write_text(__import__('json').dumps({'input_sha256': digest}))
    reseal()
    with pytest.raises(ValueError, match='source differs'):
        verify_worker(tmp_path, digest)
    assert 'src/stellarator_robust/model.py' in source_fingerprints()
    assert '.github/workflows/phase2d-upstream-attribution.yml' in source_fingerprints()


def test_incomplete_cli_comparison_retains_failure(tmp_path):
    import subprocess
    import sys
    import json
    result = subprocess.run([sys.executable, 'scripts/phase2d_upstream.py', 'compare',
        '--input-sha256', '0'*64, '--reference', str(tmp_path/'missing'),
        '--current', str(tmp_path/'missing2'), '--output', str(tmp_path/'comparison')],
        capture_output=True, text=True)
    assert result.returncode != 0
    state = json.loads((tmp_path/'comparison/status.json').read_text())
    assert state['status'] == 'FAIL'
    assert (tmp_path/'comparison/manifest.json').is_file()


def test_hosted_validation_workflow_contract():
    from pathlib import Path
    yaml = pytest.importorskip('yaml', reason='Hosted pinned setup includes PyYAML')
    # BaseLoader preserves the GitHub key "on" rather than YAML 1.1 boolean conversion.
    doc = yaml.load(Path('.github/workflows/phase2d-upstream-attribution.yml').read_text(), Loader=yaml.BaseLoader)
    assert doc['permissions'] == {'contents': 'read'}
    assert 'pull_request_target' not in doc['on']
    assert doc['on']['pull_request']['branches'] == ['codex/phase2d-cross-platform-reproducibility']
    workers = doc['jobs']['workers']
    cohorts = workers['strategy']['matrix']['include']
    assert [(c['os'], c['numpy'], c['scipy']) for c in cohorts] == [
        ('windows-latest', '2.4.6', '1.17.1'), ('ubuntu-latest', '2.4.6', '1.17.1'),
        ('ubuntu-latest', '2.3.5', '1.17.1'), ('ubuntu-latest', '2.4.6', '1.16.3')]
    commands = [s['run'] for s in workers['steps'] if 'run' in s]
    required = [
        'python scripts/phase2c_verify.py --output results/ci/upstream-production',
        'python scripts/phase2c_fault_audit.py --root results/ci/upstream-production',
        'python scripts/phase2c_legacy_compare.py --root results/ci/upstream-production',
        'python scripts/phase2b_investigate.py --output results/ci/upstream-production/investigation --corrected results/ci/upstream-production',
        'python scripts/phase2c_finalize.py --output results/ci/upstream-production']
    assert [command for command in commands if command in required] == required
    for job in doc['jobs'].values():
        for step in job['steps']:
            if step.get('uses') == 'actions/checkout@v4':
                assert step['with']['fetch-depth'] == '0'
                assert step['with']['persist-credentials'] == 'false'
            if step.get('uses') == 'actions/upload-artifact@v4':
                assert step['if'] == 'always()'
                assert step['with']['if-no-files-found'] == 'error'
            if step.get('uses') == 'actions/setup-python@v5':
                assert step['with']['python-version'] == '3.11'


def test_exact_serialized_inputs_required(tmp_path):
    from stellarator_robust.upstream_attribution import identical_solver_inputs, sha
    left, right = tmp_path/'left', tmp_path/'right'
    left.mkdir(); right.mkdir()
    (left/'sealed-inputs.json').write_bytes(b'{"value":0.0}\n')
    (right/'sealed-inputs.json').write_bytes(b'{"value":-0.0}\n')
    with pytest.raises(ValueError, match='fingerprint'):
        identical_solver_inputs(left, right, sha(left/'sealed-inputs.json'))
    (right/'sealed-inputs.json').write_bytes((left/'sealed-inputs.json').read_bytes())
    identical_solver_inputs(left, right, sha(left/'sealed-inputs.json'))


def test_historical_source_hashes_cannot_be_substituted(tmp_path, monkeypatch):
    import json
    import hashlib
    from stellarator_robust.upstream_attribution import verify_historical_sources
    (tmp_path/'quick').mkdir()
    write(tmp_path/'quick/results.json', {'metadata': {
        'source_commit': 'babc88ccd5086b5ec3a6e1c215524636d86b3580', 'source_dirty': False}})
    write(tmp_path/'source_fingerprints_at_run.json', {'src/example.py': hashlib.sha256(b'original').hexdigest()})
    def history(raw):
        def output(command, **kwargs):
            return 'src/example.py\n' if command[1] == 'ls-tree' else raw
        return output
    monkeypatch.setattr('stellarator_robust.upstream_attribution.subprocess.check_output', history(b'altered'))
    with pytest.raises(ValueError, match='Historical source hash mismatch'):
        verify_historical_sources(tmp_path)
    monkeypatch.setattr('stellarator_robust.upstream_attribution.subprocess.check_output', history(b'original'))
    result = verify_historical_sources(tmp_path)
    assert result['source_status'] == 'PASS'
    assert result['archive_authentication'] == 'INCONCLUSIVE'


def test_rehashed_incomplete_scientific_results_still_rejected(tmp_path):
    import json
    import subprocess
    from stellarator_robust.upstream_attribution import (
        WORKER_FILES, INPUT_ARRAYS, sha, source_fingerprints, verify_worker)
    payloads = {name: {} for name in WORKER_FILES}
    inputs = {'arrays': {name: pack([0.]) for name in INPUT_ARRAYS},
              'cases': {name: {} for name in ('dense', 'row3', 'row4')}}
    payloads['sealed-inputs.json'] = inputs
    payloads['regenerated-inputs.json'] = inputs
    payloads['input-comparisons.json'] = {name: {} for name in INPUT_ARRAYS}
    payloads['environment.json'] = {
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'python': '3.11.9', 'packages': {'numpy': '2.4.6'}, 'numerical_config': 'fixture',
        'numpy': '2.4.6', 'scipy': '1.17.1'}
    payloads['source_sha256.json'] = source_fingerprints()
    payloads['status.json'] = {'status': 'PASS'}
    for name, value in payloads.items():
        write(tmp_path/name, value)
    digest = sha(tmp_path/'sealed-inputs.json')
    (tmp_path/'status.json').write_text(json.dumps({'status': 'PASS', 'input_sha256': digest}))
    # Recomputing the manifest must not launder empty scientific outputs into PASS.
    write(tmp_path/'manifest.json', {name: sha(tmp_path/name) for name in WORKER_FILES})
    with pytest.raises(ValueError):
        verify_worker(tmp_path, digest)


def test_independent_references_do_not_call_production_helpers(monkeypatch):
    from stellarator_robust.model import circle, MU0
    from stellarator_robust.upstream_attribution import decimal_field
    coil = circle([0., 0., 0.], [0., 0., 1.], .16, 16, 'householder-v2')
    def forbidden(*args, **kwargs):
        raise AssertionError('Independent reference called production helper')
    monkeypatch.setattr('stellarator_robust.upstream_attribution.field', forbidden)
    monkeypatch.setattr('stellarator_robust.upstream_attribution.stable_recovery', forbidden)
    assert reference(np.eye(2), np.array([.1, .2]), 60)['status'] == 'PASS'
    value = np.array(decimal_field([[0., 0., 0.]], coil.vertices, 1., 60), float)[0]
    expected = MU0*16*np.tan(np.pi/16)/(2*np.pi*.16)
    assert close(value, [0., 0., expected])['status'] == 'PASS'


def test_preserved_historical_results_against_original_git_objects():
    from stellarator_robust.phase2c import preserve_previous
    hashes = preserve_previous()
    assert hashes and 'results/phase2c/history/phase2b-cross-platform.zip' in hashes


@pytest.fixture(scope='module')
def producer_worker(tmp_path_factory):
    """Real capture/solve/field producers, never a handwritten solver schema."""
    import json
    from pathlib import Path
    from stellarator_robust import upstream_attribution as u
    root = tmp_path_factory.mktemp('producer-worker')
    data = u.capture(json.loads(Path('configs/phase2c_quick.json').read_text()))
    # Round-trip producer JSON before validating its serialized schema.
    u.write(root/'sealed-inputs.json', data)
    data = u.load_evidence(root/'sealed-inputs.json')
    u.write(root/'regenerated-inputs.json', data)
    u.write(root/'input-comparisons.json', {k: u.close(u.unpack(v), u.unpack(v)) for k, v in data['arrays'].items()})
    result = u.solve_inputs(data)
    for filename in ('frozen-solve.json', 'regenerated-solve.json'):
        u.write(root/filename, result)
    independent = u.independent_field_checks(data)
    u.write(root/'independent-fields.json', independent)
    u.write(root/'frozen-fields.json', u.field_replay(data))
    env = u.environment()
    # Test the declared hosted envelope with real numerical producer results;
    # this fixture does not assert the local installation is a hosted cohort.
    env.update(numpy='2.4.6', scipy='1.17.1')
    env['packages'].update(numpy='2.4.6', scipy='1.17.1')
    u.write(root/'environment.json', env)
    u.write(root/'source_sha256.json', u.source_fingerprints())
    checks = dict(complete_cases=True, independent_fields=independent['status'] == 'PASS')
    for stage in ('frozen', 'regenerated'):
        for name, d in result['diagnostics'].items():
            checks[stage+'/'+name] = (d['success'] and d['repeated']['status'] == 'PASS'
                and d['reference_check']['status'] == 'PASS' and d['reference_check']['solver']['status'] == 'PASS')
    incomplete = any(d['reference_check']['status'] == 'INCONCLUSIVE' for d in result['diagnostics'].values())
    status = 'INCONCLUSIVE' if incomplete else ('PASS' if all(checks.values()) else 'FAIL')
    u.write(root/'status.json', dict(status=status, scientific_status='PARTIAL', production_cross_platform='UNRESOLVED',
                                   checks=checks, input_sha256=u.sha(root/'sealed-inputs.json')))
    u.manifest(root)
    return root


def test_complete_real_producer_worker_accepted(producer_worker):
    from stellarator_robust import upstream_attribution as u
    assert u.verify_worker(producer_worker, u.sha(producer_worker/'sealed-inputs.json')) == u.load_evidence(producer_worker/'status.json')


@pytest.mark.parametrize('damage', ['termination', 'repeat'])
def test_required_solve_rejects_valid_but_failed_record(producer_worker, damage):
    from stellarator_robust import upstream_attribution as u
    data = u.load_evidence(producer_worker/'sealed-inputs.json')
    arrays = u.validate_inputs(data)
    result = u.load_evidence(producer_worker/'frozen-solve.json')
    u.require_solve(result, data, arrays)
    d = result['diagnostics']['dense']
    if damage == 'termination':
        d.update(success=False, status=0, message='Maximum iterations exceeded')
    else:
        d['repeated'].update(status='FAIL', exact=False, failures=1, max_absolute=1e-6)
    gates, _ = u.validate_solve(result, data, arrays)
    assert not gates['dense']  # valid failed evidence must remain inspectable
    with pytest.raises(ValueError, match='failed or is incomplete'):
        u.require_solve(result, data, arrays)


def test_undefined_recovery_marks_solve_incomplete(producer_worker):
    from stellarator_robust import upstream_attribution as u
    data = u.load_evidence(producer_worker/'sealed-inputs.json')
    arrays = u.validate_inputs(data)
    result = u.load_evidence(producer_worker/'frozen-solve.json')
    # Diagnostic synthetic evaluation: no current can change this field, so
    # L-B is zero. Training arrays and the real candidate remain untouched.
    arrays['fine_A'] = np.zeros_like(arrays['fine_A'])
    dense = u.unpack(result['currents_A']['dense'])
    for row in ('row3', 'row4'):
        frozen = dense.copy(); frozen[data['cases'][row]['failed']] = 0.
        result['recovery'][row] = u.stable_recovery(arrays['fine_A'], arrays['fine_b'],
            arrays['fine_weights'], dense, frozen, u.unpack(result['currents_A'][row]))
    gates, incomplete = u.validate_solve(result, data, arrays)
    assert all(gates.values()) and incomplete
    with pytest.raises(ValueError, match='incomplete'):
        u.require_solve(result, data, arrays)


def test_complete_executed_nonpass_evidence_retains_classification(producer_worker, tmp_path):
    import json
    import shutil
    from stellarator_robust import upstream_attribution as u
    root = tmp_path/'worker'; shutil.copytree(producer_worker, root)
    state = u.load_evidence(root/'status.json')
    # These tests require the interior benchmark references to pass first.
    assert state['status'] == 'PASS'
    result = u.load_evidence(root/'frozen-solve.json')
    d = result['diagnostics']['dense']
    d.update(success=False, status=0, message='The maximum number of iterations is exceeded.')
    state['checks']['frozen/dense'] = False
    state['status'] = 'FAIL'
    (root/'frozen-solve.json').write_text(json.dumps(result))
    (root/'status.json').write_text(json.dumps(state))
    (root/'manifest.json').unlink(); u.manifest(root)
    assert u.verify_worker(root, u.sha(root/'sealed-inputs.json'))['status'] == 'FAIL'


@pytest.mark.parametrize('damage', [
    'missing_currents', 'missing_diagnostics', 'missing_case', 'empty_solver', 'truncated_current',
    'current_dimensions', 'invalid_hex', 'nonfinite_current', 'missing_termination',
    'missing_file', 'wrong_hash', 'extra_file', 'input_fingerprint', 'false_pass',
    'empty_reference', 'missing_residual', 'bad_field_shape', 'empty_comparison',
    'bad_recovery_reference', 'bad_input_shape', 'unknown_status', 'duplicate_json', 'nonfinite_json',
    'null_diagnostics', 'null_field_inventory', 'invalid_decimal', 'bad_environment_type',
    'bad_threads', 'impossible_repeat_count', 'impossible_rounding_count', 'impossible_reference_count',
])
def test_rehashed_invalid_worker_rejected(producer_worker, tmp_path, damage):
    import json
    import shutil
    from stellarator_robust import upstream_attribution as u
    root = tmp_path/'worker'
    shutil.copytree(producer_worker, root)
    filename = 'frozen-solve.json'
    result = u.load_evidence(root/filename)
    if damage == 'missing_currents': del result['currents_A']
    elif damage == 'missing_diagnostics': del result['diagnostics']
    elif damage == 'missing_case': del result['currents_A']['row4']
    elif damage == 'empty_solver': result = {}
    elif damage == 'truncated_current': result['currents_A']['dense'] = u.pack(u.unpack(result['currents_A']['dense'])[:-1])
    elif damage == 'current_dimensions': result['currents_A']['dense'] = u.pack(u.unpack(result['currents_A']['dense'])[None, :])
    elif damage == 'invalid_hex': result['currents_A']['dense']['binary64_le'] = 'xx'
    elif damage == 'nonfinite_current': result['currents_A']['dense']['binary64_le'] = '000000000000f87f'+result['currents_A']['dense']['binary64_le'][16:]
    elif damage == 'missing_termination': del result['diagnostics']['row3']['message']
    elif damage == 'null_diagnostics': result['diagnostics'] = None
    elif damage == 'impossible_repeat_count': result['diagnostics']['dense']['repeated'].update(status='FAIL', failures=25, exact=False)
    elif damage == 'impossible_rounding_count': result['diagnostics']['dense']['rounding_sensitivity']['14'].update(status='FAIL', failures=25, exact=False)
    elif damage == 'impossible_reference_count': result['diagnostics']['dense']['reference_check']['solver'].update(status='FAIL', failures=25, exact=False)
    elif damage in ('bad_environment_type', 'bad_threads'):
        filename = 'environment.json'; result = u.load_evidence(root/filename)
        result['python' if damage == 'bad_environment_type' else 'threads'] = []
    elif damage in ('null_field_inventory', 'invalid_decimal'):
        filename = 'independent-fields.json'; result = u.load_evidence(root/filename)
        if damage == 'null_field_inventory': result['coils'] = None
        else: result['coils']['0']['reference60'][0][0] = 'invalid-decimal'
    elif damage == 'empty_reference': result['diagnostics']['dense']['reference60'] = {}
    elif damage == 'missing_residual': del result['diagnostics']['dense']['residual']
    elif damage == 'bad_recovery_reference': result['recovery']['row3']['recovered_currents_A'] = [0.]
    elif damage == 'false_pass':
        result['diagnostics']['dense'].update(success=False, status=0)
        state = u.load_evidence(root/'status.json'); state['status'] = 'PASS'
        (root/'status.json').write_text(json.dumps(state))
    elif damage == 'bad_field_shape':
        filename = 'frozen-fields.json'; result = u.load_evidence(root/filename)
        result['original_Bxyz'] = u.pack([0.])
    elif damage == 'empty_comparison':
        filename = 'input-comparisons.json'; result = u.load_evidence(root/filename); result['points'] = {}
    elif damage == 'bad_input_shape':
        filename = 'regenerated-inputs.json'; result = u.load_evidence(root/filename); result['arrays']['points'] = u.pack([0.])
    elif damage in ('input_fingerprint', 'unknown_status'):
        filename = 'status.json'; result = u.load_evidence(root/filename)
        result['input_sha256' if damage == 'input_fingerprint' else 'status'] = 'invalid'
    (root/filename).write_text(json.dumps(result))
    if damage == 'missing_file': (root/'regenerated-solve.json').unlink()
    if damage == 'extra_file': (root/'unexpected.json').write_text('{}')
    if damage == 'duplicate_json': (root/'status.json').write_text('{"status":"PASS","status":"PASS"}')
    if damage == 'nonfinite_json': (root/'frozen-solve.json').write_text('{"cost":1e999}')
    # Rehash all mutations except the explicit SHA corruption case.
    (root/'manifest.json').unlink()
    u.manifest(root)
    if damage == 'wrong_hash':
        entries = u.load_evidence(root/'manifest.json'); entries['frozen-solve.json'] = '0'*64
        (root/'manifest.json').write_text(json.dumps(entries))
    with pytest.raises(ValueError):
        u.verify_worker(root, u.sha(root/'sealed-inputs.json'))


@pytest.mark.parametrize('payload', [
    {'shape': [-1], 'binary64_le': ''}, {'shape': [True], 'binary64_le': '00'*8},
    {'shape': [1.0], 'binary64_le': '00'*8}, {'shape': [1], 'binary64_le': '00'*4},
    {'shape': [1], 'binary64_le': '00 '*8}, {'shape': [1], 'binary64_le': '000000000000f07f'},
])
def test_malformed_float64_rejected(payload):
    with pytest.raises(ValueError):
        unpack(payload)


@pytest.mark.parametrize('record,size', [
    ({'status': 'FAIL', 'failures': 1, 'max_absolute': 0., 'exact': False}, 24),
    ({'status': 'FAIL', 'failures': 25, 'max_absolute': 1., 'exact': False}, 24),
])
def test_impossible_comparison_diagnostics_rejected(record, size):
    from stellarator_robust.upstream_attribution import comparison_record
    with pytest.raises(ValueError, match='comparison diagnostics'):
        comparison_record(record, size=size)
