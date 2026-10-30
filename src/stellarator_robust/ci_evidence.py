"""Strict CI comparison: runtime provenance is checked before exclusion."""
import copy
import math
import platform
import subprocess
import numpy as np


def runtime():
    return dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                source_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()),
                python=platform.python_version())


def compare(a, b, trail='', records=None, exact=False):
    if exact and type(a) is not type(b):
        raise AssertionError(f'{trail}: exact type differs')
    if isinstance(a, dict):
        if not isinstance(b, dict) or a.keys() != b.keys():
            raise AssertionError(f'{trail}: keys differ')
        for key in a:
            compare(a[key], b[key], trail+'/'+key, records, exact)
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            raise AssertionError(f'{trail}: dimensions differ')
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, trail+f'/{i}', records, exact)
    elif isinstance(a, float):
        if isinstance(b, bool) or not isinstance(b, (int, float)) or not math.isfinite(a) or not math.isfinite(b):
            raise AssertionError(f'{trail}: invalid numeric value')
        error = abs(a-b)
        if records is not None and error:
            records.append(dict(path=trail, absolute_error=error,
                                relative_error=error/max(abs(a), 1e-300)))
        if not (a == b if exact else np.isclose(a, b, rtol=1e-11, atol=1e-13)):
            raise AssertionError(f'{trail}: absolute_error={error}, reference={a}, current={b}')
    elif type(a) is not type(b) or a != b:
        raise AssertionError(f'{trail}: exact value differs: {a!r} != {b!r}')


def compare_study(reference, current, actual=None, report=None):
    actual = runtime() if actual is None else actual
    excluded = []
    for key in ('source_commit', 'source_dirty', 'python'):
        if key not in reference or key not in current or current[key] != actual[key] or type(current[key]) is not type(actual[key]):
            raise AssertionError('invalid runtime provenance: '+key)
        excluded.append(dict(path='/'+key, reference=reference[key], current=current[key]))
    errors = []
    result = {} if report is None else report
    result.update(status='FAIL', excluded=excluded, numeric_differences=errors, rtol=1e-11, atol=1e-13)
    left = copy.deepcopy({k: v for k, v in reference.items() if k not in ('source_commit', 'source_dirty', 'python')})
    right = copy.deepcopy({k: v for k, v in current.items() if k not in ('source_commit', 'source_dirty', 'python')})
    if len(left['trials']) != len(right['trials']):
        raise AssertionError('trial dimensions differ')
    for i, (old, new) in enumerate(zip(left['trials'], right['trials'])):
        for trial in (old, new):
            seconds = trial['solver']['seconds']
            if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or not math.isfinite(seconds) or seconds < 0:
                raise AssertionError('invalid measured solver timing')
        excluded.append(dict(path=f'/trials/{i}/solver/seconds',
                             reference=old['solver'].pop('seconds'), current=new['solver'].pop('seconds')))
    # Scenario draws and configuration are discrete reference records, even their floats.
    for key in ('scenarios', 'config'):
        compare(left[key], right[key], '/'+key, records=errors, exact=True)
    compare(left, right, records=errors)
    result['status'] = 'PASS'
    return result


def require_link(record, digest):
    if record.get('status') != 'PASS' or record.get('study_sha256') != digest:
        raise AssertionError('missing, failed or incorrectly linked evidence')
