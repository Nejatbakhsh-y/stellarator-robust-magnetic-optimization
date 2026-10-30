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


def compare(a, b, trail='', records=None, exact=False, approximate_paths=frozenset()):
    if trail in approximate_paths and (type(a) is not float or type(b) is not float):
        raise AssertionError(f'{trail}: derived clearance must be a finite float')
    if exact and type(a) is not type(b):
        raise AssertionError(f'{trail}: exact type differs')
    if isinstance(a, dict):
        if not isinstance(b, dict) or a.keys() != b.keys():
            raise AssertionError(f'{trail}: keys differ')
        for key in a:
            compare(a[key], b[key], trail+'/'+key, records, exact, approximate_paths)
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            raise AssertionError(f'{trail}: dimensions differ')
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, trail+f'/{i}', records, exact, approximate_paths)
    elif isinstance(a, float):
        if isinstance(b, bool) or not isinstance(b, (int, float)) or not math.isfinite(a) or not math.isfinite(b):
            raise AssertionError(f'{trail}: invalid numeric value')
        error = abs(a-b)
        if records is not None and error:
            records.append(dict(path=trail, absolute_error=error,
                                relative_error=error/max(abs(a), 1e-300)))
        if not (a == b if exact and trail not in approximate_paths
                else np.isclose(a, b, rtol=1e-11, atol=1e-13)):
            raise AssertionError(f'{trail}: absolute_error={error}, reference={a}, current={b}')
    elif type(a) is not type(b) or a != b:
        raise AssertionError(f'{trail}: exact value differs: {a!r} != {b!r}')


def clearance_paths(scenarios):
    """Only the derived metric in the generator's known record schema is tolerant.

    Sampled clearance is recomputed from geometry, not drawn by the RNG. This
    does not change the separate certified-clearance rejection in uncertainty.py.
    """
    if type(scenarios) is not dict or scenarios.keys() != {'holdout', 'training'}:
        raise AssertionError('invalid scenario collections')
    if type(scenarios['holdout']) is not list or type(scenarios['training']) is not dict:
        raise AssertionError('invalid scenario collection types')
    groups = [('/scenarios/holdout', scenarios['holdout'])]
    groups += [('/scenarios/training/'+key, rows)
               for key, rows in scenarios['training'].items()]
    paths = set()
    fields = {'translation_m', 'rotation_rad', 'gain', 'offset_A', 'sampled_clearance_m'}
    for prefix, rows in groups:
        if type(rows) is not list:
            raise AssertionError(prefix+': expected scenario list')
        for i, row in enumerate(rows):
            if type(row) is not dict or row.keys() != fields:
                raise AssertionError(f'{prefix}/{i}: missing or unexpected scenario fields')
            count = len(row['gain']) if type(row['gain']) is list else 0
            for key in ('gain', 'offset_A'):
                values = row[key]
                if (not count or type(values) is not list or len(values) != count
                        or any(type(v) is not float or not math.isfinite(v) for v in values)):
                    raise AssertionError(f'{prefix}/{i}/{key}: invalid scenario input')
            for key in ('translation_m', 'rotation_rad'):
                values = row[key]
                if (type(values) is not list or len(values) != count
                        or any(type(v) is not list or len(v) != 3
                               or any(type(x) is not float or not math.isfinite(x) for x in v)
                               for v in values)):
                    raise AssertionError(f'{prefix}/{i}/{key}: invalid scenario input')
            paths.add(f'{prefix}/{i}/sampled_clearance_m')
    return paths


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
    # Random draws and configuration stay exact. Only derived geometric metrics
    # at these explicitly validated record paths use the existing tolerances.
    paths = clearance_paths(left['scenarios'])
    if paths != clearance_paths(right['scenarios']):
        raise AssertionError('scenario dimensions differ')
    result['approximate_scenario_fields'] = sorted(paths)
    compare(left['scenarios'], right['scenarios'], '/scenarios', records=errors,
            exact=True, approximate_paths=paths)
    compare(left['config'], right['config'], '/config', records=errors, exact=True)
    compare({k: v for k, v in left.items() if k not in ('scenarios', 'config')},
            {k: v for k, v in right.items() if k not in ('scenarios', 'config')}, records=errors)
    result['status'] = 'PASS'
    return result


def require_link(record, digest):
    if record.get('status') != 'PASS' or record.get('study_sha256') != digest:
        raise AssertionError('missing, failed or incorrectly linked evidence')
