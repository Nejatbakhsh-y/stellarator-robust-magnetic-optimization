import copy
import pytest
from stellarator_robust.ci_evidence import compare_study, compare, require_link


def study():
    row = dict(translation_m=[[0.1, 0.0, 0.0]], rotation_rad=[[0.01, 0.0, 0.0]],
               gain=[0.001], offset_A=[0.2], sampled_clearance_m=0.38888759185268096)
    return dict(source_commit='a'*40, source_dirty=False, python='3.11.9',
                trials=[], config={'n': 4}, scenarios={'holdout': [copy.deepcopy(row), copy.deepcopy(row)],
                'training': {'1/1': [copy.deepcopy(row)]}}, values=[1.0], status='PARTIAL')


def test_dynamic_provenance_validated_and_recorded():
    a = study(); b = copy.deepcopy(a)
    actual = dict(source_commit='b'*40, source_dirty=True, python='3.11.14')
    b.update(actual)
    result = compare_study(a, b, actual)
    assert {r['path'] for r in result['excluded']} == {'/python', '/source_commit', '/source_dirty'}
    b['source_commit'] = 'c'*40
    with pytest.raises(AssertionError, match='provenance'):
        compare_study(a, b, actual)


@pytest.mark.parametrize('field,value', [('values', [1.0001]), ('status', 'PASS'),
    ('config', {'n': 5}), ('scenarios', {'draw': [0.10000000000001]})])
def test_scientific_mismatches_rejected(field, value):
    a = study(); b = copy.deepcopy(a); b[field] = value
    with pytest.raises(AssertionError):
        compare_study(a, b, {k: a[k] for k in ('source_commit', 'source_dirty', 'python')})


@pytest.mark.parametrize('value', [None, {}, {'values': []}])
def test_malformed_missing_evidence(value):
    with pytest.raises((AssertionError, TypeError)):
        compare(study(), value)


@pytest.mark.parametrize('record', [{}, {'status': 'PASS'},
    {'status': 'FAIL', 'study_sha256': 'abc'}, {'status': 'PASS', 'study_sha256': 'wrong'}])
def test_artifact_links_fail_closed(record):
    with pytest.raises(AssertionError):
        require_link(record, 'abc')


def test_numeric_error_and_dimensions():
    errors = []
    compare([1.0], [1.0+1e-12], records=errors)
    assert errors[0]['absolute_error'] > 0
    with pytest.raises(AssertionError, match='dimensions'):
        compare([1.0], [])



def test_only_declared_solver_timing_is_excluded():
    a = study(); a['trials'] = [{'solver': {'seconds': 1.0}, 'objective': 0.1}]
    b = copy.deepcopy(a); b['trials'][0]['solver']['seconds'] = 2.0
    actual = {k: b[k] for k in ('source_commit', 'source_dirty', 'python')}
    result = compare_study(a, b, actual)
    assert result['excluded'][-1] == dict(path='/trials/0/solver/seconds', reference=1.0, current=2.0)
    b['trials'][0]['objective'] = 0.2
    with pytest.raises(AssertionError, match='absolute_error'):
        compare_study(a, b, actual)
    b['trials'][0]['solver']['seconds'] = -1.0
    with pytest.raises(AssertionError, match='timing'):
        compare_study(a, b, actual)


def test_failed_comparison_retains_exclusions_and_error_magnitudes():
    a = study(); b = copy.deepcopy(a); b['values'] = [2.0]
    report = {}
    actual = {k: b[k] for k in ('source_commit', 'source_dirty', 'python')}
    with pytest.raises(AssertionError, match='absolute_error'):
        compare_study(a, b, actual, report=report)
    assert report['status'] == 'FAIL'
    assert len(report['excluded']) == 3
    assert report['numeric_differences'][0]['absolute_error'] == 1.0


def test_exact_scenario_mismatch_retains_numeric_magnitude():
    a = study(); b = copy.deepcopy(a)
    b['scenarios']['holdout'][0]['translation_m'][0][0] += 1e-14
    report = {}
    actual = {k: b[k] for k in ('source_commit', 'source_dirty', 'python')}
    with pytest.raises(AssertionError, match='/scenarios/holdout/0/translation_m/0/0: absolute_error'):
        compare_study(a, b, actual, report=report)
    assert report['status'] == 'FAIL'
    assert report['numeric_differences'][0]['absolute_error'] > 0


def test_reference_preflight_rejects_unlisted_source(tmp_path):
    import json
    import runpy
    from pathlib import Path
    from stellarator_robust.evidence import file_hash
    references = runpy.run_path(str(Path(__file__).parents[1]/'scripts/phase2_cloud_ci.py'))['references']
    (tmp_path/'src').mkdir()
    (tmp_path/'src/unlisted.py').write_text('x = 1\n')
    (tmp_path/'.gitattributes').write_text('results/phase2/** -text\n')
    out = tmp_path/'results/phase2'; out.mkdir(parents=True)
    (out/'manifest.json').write_text(json.dumps({'.gitattributes': file_hash(tmp_path/'.gitattributes')}))
    with pytest.raises(AssertionError, match='manifest completeness before regeneration'):
        references(tmp_path)


def compare_fixture(a, b, report=None):
    actual = {k: study()[k] for k in ('source_commit', 'source_dirty', 'python')}
    return compare_study(a, b, actual, report=report)


def test_observed_linux_clearance_rounding_is_accepted_and_recorded():
    a = study(); b = copy.deepcopy(a)
    b['scenarios']['holdout'][1]['sampled_clearance_m'] = 0.3888875918526809
    result = compare_fixture(a, b)
    assert result['status'] == 'PASS'
    assert result['numeric_differences'] == [dict(
        path='/scenarios/holdout/1/sampled_clearance_m',
        absolute_error=5.551115123125783e-17,
        relative_error=5.551115123125783e-17/0.38888759185268096)]
    assert result['rtol'] == 1e-11 and result['atol'] == 1e-13


def test_identical_scenario_inputs_pass_without_exclusions():
    result = compare_fixture(study(), study())
    assert result['numeric_differences'] == []
    assert not any(r['path'].startswith('/scenarios') for r in result['excluded'])


def test_training_clearance_uses_the_same_narrow_rule():
    a = study(); b = copy.deepcopy(a)
    b['scenarios']['training']['1/1'][0]['sampled_clearance_m'] = 0.3888875918526809
    result = compare_fixture(a, b)
    assert result['status'] == 'PASS'
    assert result['numeric_differences'][0]['path'] == '/scenarios/training/1/1/0/sampled_clearance_m'


@pytest.mark.parametrize('cohort', ['holdout', 'training'])
@pytest.mark.parametrize('field', ['translation_m', 'rotation_rad', 'gain', 'offset_A'])
def test_perturbations_stay_exact(cohort, field):
    a = study(); b = copy.deepcopy(a)
    row = b['scenarios']['holdout'][0] if cohort == 'holdout' else b['scenarios']['training']['1/1'][0]
    target = row[field][0] if field in ('translation_m', 'rotation_rad') else row[field]
    target[0] += 1e-14  # Less than the scientific tolerance, still an invalid draw change.
    with pytest.raises(AssertionError, match='absolute_error'):
        compare_fixture(a, b)


@pytest.mark.parametrize('cohort', ['holdout', 'training'])
def test_material_clearance_difference_is_rejected_and_recorded(cohort):
    a = study(); b = copy.deepcopy(a); report = {}
    row = b['scenarios']['holdout'][0] if cohort == 'holdout' else b['scenarios']['training']['1/1'][0]
    row['sampled_clearance_m'] += 1e-8
    with pytest.raises(AssertionError, match='sampled_clearance_m: absolute_error'):
        compare_fixture(a, b, report)
    assert report['status'] == 'FAIL'
    assert report['numeric_differences'][0]['absolute_error'] > 1e-9


@pytest.mark.parametrize('field', ['sampled_clearance_m', 'translation_m', 'gain'])
def test_missing_scenario_fields_fail_even_when_both_records_omit_them(field):
    a = study(); del a['scenarios']['holdout'][0][field]
    with pytest.raises(AssertionError, match='scenario fields'):
        compare_fixture(a, copy.deepcopy(a))


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), True, 1, '0.38', None, [], {}])
@pytest.mark.parametrize('side', ['reference', 'current'])
def test_invalid_clearance_values_fail(value, side):
    a = study(); b = copy.deepcopy(a)
    (a if side == 'reference' else b)['scenarios']['holdout'][0]['sampled_clearance_m'] = value
    with pytest.raises(AssertionError):
        compare_fixture(a, b)


def test_clearance_named_configuration_field_remains_exact():
    a = study(); a['config']['sampled_clearance_m'] = 0.4
    b = copy.deepcopy(a); b['config']['sampled_clearance_m'] += 1e-14
    with pytest.raises(AssertionError, match='/config/sampled_clearance_m: absolute_error'):
        compare_fixture(a, b)


def test_additional_archived_linux_clearance_mismatch_remains_rejected():
    a = study(); b = copy.deepcopy(a); report = {}
    a['scenarios']['holdout'][0]['sampled_clearance_m'] = 0.3894433457841317
    b['scenarios']['holdout'][0]['sampled_clearance_m'] = 0.38944327335107365
    with pytest.raises(AssertionError, match='absolute_error'):
        compare_fixture(a, b, report)
    assert report['status'] == 'FAIL'
    assert report['numeric_differences'][0]['absolute_error'] == 7.243305805149092e-08


@pytest.mark.parametrize('field', ['gain', 'translation_m'])
def test_identically_malformed_inputs_are_not_valid_evidence(field):
    a = study(); a['scenarios']['holdout'][0][field] = ['invalid']
    with pytest.raises(AssertionError, match='invalid scenario input'):
        compare_fixture(a, copy.deepcopy(a))
