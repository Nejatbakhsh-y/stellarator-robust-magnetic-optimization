import copy
import pytest
from stellarator_robust.ci_evidence import compare_study, compare, require_link


def study():
    return dict(source_commit='a'*40, source_dirty=False, python='3.11.9',
                trials=[], config={'n': 4}, scenarios={'draw': [0.1]}, values=[1.0], status='PARTIAL')


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
