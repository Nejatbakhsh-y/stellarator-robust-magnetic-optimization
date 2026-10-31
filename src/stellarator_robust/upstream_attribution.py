"""Investigation-only production baseline capture; never changes production settings."""
import contextlib
from decimal import Decimal, DecimalException, localcontext
import hashlib
import io
from importlib.metadata import distributions
import json
import os
from pathlib import Path
import platform
import re
import subprocess

import numpy as np
import scipy
from scipy.linalg import lstsq
from . import optimize
from .model import benchmark, surface, response, field, Coil
from .fault_metrics import stable_recovery

RTOL, ATOL = 1e-11, 1e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pack(value):
    """Canonical little-endian binary64 payload, preserving signed zero and every bit."""
    a = np.asarray(value, dtype='<f8')
    if not np.isfinite(a).all():
        raise ValueError('Nonfinite scientific input')
    return dict(shape=list(a.shape), binary64_le=a.tobytes(order='C').hex())


def unpack(value):
    if (not isinstance(value, dict) or set(value) != {'shape', 'binary64_le'}
            or not isinstance(value['shape'], list)
            or any(type(n) is not int or n < 0 for n in value['shape'])
            or not isinstance(value['binary64_le'], str)
            or re.fullmatch('[0-9a-f]*', value['binary64_le']) is None):
        raise ValueError('Invalid canonical float64 payload')
    size = 1
    for n in value['shape']:
        size *= n
    if len(value['binary64_le']) != 16*size:
        raise ValueError('Invalid float64 byte count')
    a = np.frombuffer(bytes.fromhex(value['binary64_le']), dtype='<f8').copy()
    a = a.reshape(value['shape'])
    if not np.isfinite(a).all():
        raise ValueError('Nonfinite serialized input')
    return a


def load_evidence(path):
    """JSON evidence has unique keys and finite JSON numbers, including exponents."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate evidence key: '+key)
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                       parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON: '+s)))
    def finite(v):
        if isinstance(v, float) and not np.isfinite(v):
            raise ValueError('Nonfinite JSON number')
        if isinstance(v, dict):
            for x in v.values():
                finite(x)
        if isinstance(v, list):
            for x in v:
                finite(x)
    finite(value)
    if not isinstance(value, dict):
        raise ValueError('Evidence must be a JSON object')
    return value


def require_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('Incomplete/unexpected scientific object: '+str(keys))


def numeric(value, shape=None):
    # Do not coerce strings, booleans or null into scientific numbers.
    def real(v):
        if isinstance(v, (list, tuple)):
            return all(real(x) for x in v)
        if isinstance(v, np.ndarray):
            return v.dtype.kind in 'fi'
        return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_))
    if not real(value):
        raise ValueError('Invalid scientific number type')
    a = np.asarray(value)
    if a.dtype.kind not in 'fi' or not np.isfinite(a).all() or (shape is not None and a.shape != shape):
        raise ValueError('Invalid finite numerical dimensions')
    return a


def agreement(actual, expected):
    if close(numeric(actual), numeric(expected))['status'] != 'PASS':
        raise ValueError('Inconsistent scientific numerical evidence')


def comparison_record(record, expected=None, size=None):
    require_keys(record, ('status', 'max_absolute', 'failures', 'exact'))
    if (record['status'] not in ('PASS', 'FAIL') or type(record['exact']) is not bool
            or type(record['failures']) is not int or record['failures'] < 0
            or (size is not None and record['failures'] > size)
            or numeric(record['max_absolute'], ()) < 0
            or (record['failures'] > 0 and record['max_absolute'] == 0)
            or (record['status'] == 'PASS') != (record['failures'] == 0)
            or (record['exact'] and (record['failures'] or record['max_absolute'] != 0))):
        raise ValueError('Invalid comparison diagnostics')
    if expected is not None and record != expected:
        raise ValueError('Inconsistent comparison diagnostics')


def termination(d, size):
    for key in ('success', 'status', 'message', 'nit', 'cost', 'optimality', 'active_mask'):
        if key not in d:
            raise ValueError('Missing solver termination diagnostics: '+key)
    if (type(d['success']) is not bool or type(d['status']) is not int
            or d['status'] not in (-1, 0, 1, 2, 3) or d['success'] != (d['status'] > 0)
            or not isinstance(d['message'], str) or not d['message']
            or type(d['nit']) is not int or d['nit'] < 0
            or numeric(d['cost'], ()) < 0 or numeric(d['optimality'], ()) < 0
            or not np.isin(numeric(d['active_mask'], (size,)), [-1, 0, 1]).all()):
        raise ValueError('Invalid solver termination diagnostics')


def validate_inputs(data):
    require_keys(data, ('schema', 'config', 'cases', 'arrays'))
    if data['schema'] != 'production-upstream-v1' or not isinstance(data['config'], dict):
        raise ValueError('Invalid scientific input schema')
    require_keys(data['cases'], ('dense', 'row3', 'row4'))
    require_keys(data['arrays'], INPUT_ARRAYS)
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    c = data['config']
    # This experiment is the established quick production benchmark.
    if json.dumps(c, sort_keys=True) != json.dumps(json.loads(Path('configs/phase2c_quick.json').read_text()), sort_keys=True):
        raise ValueError('Unexpected production input configuration')
    p, n, f = c['nt']*c['np'], c['nphi']*c['ntheta'], 4*c['nt']*c['np']
    shapes = dict(points=(p, 3), normals=(p, 3), weights=(p,), A=(p, n), b=(p,),
                  D=(p, n), d=(p,), vertices=(n, c['segments'], 3),
                  error_vertices=(c['segments'], 3), original_Bxyz=(p, 3),
                  fine_points=(f, 3), fine_normals=(f, 3), fine_weights=(f,), fine_A=(f, n), fine_b=(f,))
    for name, shape in shapes.items():
        numeric(a[name], shape)
    for key in ('weights', 'fine_weights'):
        if np.any(a[key] < 0):
            raise ValueError('Negative surface weight')
        agreement(a[key].sum(), 1.)
    agreement(a['D'], a['A']*c['imax_A']/c['bref_T'])
    agreement(a['d'], a['b']/c['bref_T'])
    agreement(a['b'], np.sum(a['original_Bxyz']*a['normals'], axis=1))
    active = np.flatnonzero(abs(a['dense_x'])*c['imax_A'] > c['active_threshold_A'])
    for name, case in data['cases'].items():
        extra = () if name == 'dense' else ('fault_row', 'failed', 'support')
        require_keys(case, ('arguments', 'implicit_method', 'implicit_lsq_solver', 'initialization',
                           'status', 'success', 'message', 'nit', 'cost', 'optimality', 'active_mask', *extra))
        support = np.arange(n) if name == 'dense' else np.delete(np.arange(n), int(active[int(name[-1])]))
        if name != 'dense' and (case['fault_row'] != int(name[-1]) or case['failed'] != int(active[int(name[-1])])
                                or type(case['fault_row']) is not int or type(case['failed']) is not int
                                or not isinstance(case['support'], list) or any(type(v) is not int for v in case['support'])
                                or case['support'] != support.tolist()):
            raise ValueError('Inconsistent scientific fault support')
        if (case['arguments'] != dict(bounds=[-1, 1], tol=1e-12, max_iter=1000)
                or case['implicit_method'] != 'trf' or case['implicit_lsq_solver'] != 'exact'
                or not case['initialization']):
            raise ValueError('Unexpected scientific solver settings')
        numeric(case['arguments']['bounds'], (2,))
        k = len(support)
        termination(case, k)
        numeric(a[name+'_M'], (p+k, k)); numeric(a[name+'_y'], (p+k,))
        numeric(a[name+'_unconstrained_initial_x'], (k,)); numeric(a[name+'_x'], (n,))
        if np.any(abs(a[name+'_x']) > 1) or (name != 'dense' and a[name+'_x'][case['failed']] != 0):
            raise ValueError('Invalid captured current constraints')
        agreement(a[name+'_M'], np.vstack([np.sqrt(a['weights'])[:, None]*a['D'][:, support],
                                         np.sqrt(c['ridge'])*np.eye(k)]))
        agreement(a[name+'_y'], np.r_[-np.sqrt(a['weights'])*a['d'], np.zeros(k)])
        residual = a[name+'_M']@a[name+'_x'][support]-a[name+'_y']
        agreement(case['cost'], residual@residual/2)
        initial = a[name+'_unconstrained_initial_x']
        agreement(a[name+'_M'].T@(a[name+'_M']@initial-a[name+'_y']), np.zeros(k))
    return a


def validate_reference(record, size, digits, M, y):
    # Decimal replay uses the saved binary64 inputs and no production solver.
    # A fabricated stationarity certificate or unavailable-reference reason is
    # invalid evidence, rather than an executed independent-reference failure.
    if record != reference(M, y, digits):
        raise ValueError('Inconsistent independent reference evidence')
    if record.get('status') == 'INCONCLUSIVE':
        require_keys(record, ('status', 'reason'))
        if not isinstance(record['reason'], str) or not record['reason']:
            raise ValueError('Missing independent reference reason')
        return None
    require_keys(record, ('status', 'x', 'gradient_max', 'objective', 'bound_margin', 'precision'))
    if record['status'] not in ('PASS', 'FAIL') or record['precision'] != digits:
        raise ValueError('Invalid independent reference status')
    x = numeric([float(Decimal(v)) for v in record['x']], (size,))
    values = [Decimal(record[k]) for k in ('gradient_max', 'objective', 'bound_margin')]
    if (any(not v.is_finite() for v in values) or min(values) < 0 or values[2] <= 0
            or (record['status'] == 'PASS') != (values[0] < Decimal(10)**(-(digits//2)))):
        raise ValueError('Invalid independent reference certificate')
    return x


def validate_solve(result, data, a):
    require_keys(result, ('currents_A', 'diagnostics', 'recovery', 'training_condition'))
    for key in ('currents_A', 'diagnostics'):
        require_keys(result[key], ('dense', 'row3', 'row4'))
    require_keys(result['recovery'], ('row3', 'row4'))
    n = a['A'].shape[1]
    currents = {k: numeric(unpack(v), (n,)) for k, v in result['currents_A'].items()}
    gates, incomplete = {}, False
    for name, d in result['diagnostics'].items():
        require_keys(d, ('success', 'status', 'message', 'nit', 'optimality', 'cost', 'active_mask',
                         'singular_values', 'rank', 'condition', 'residual', 'reference60', 'reference90',
                         'reference_check', 'repeated', 'driver_diagnostics', 'rounding_sensitivity',
                         'initialization_sensitivity', 'projected_gradient_max'))
        case = data['cases'][name]
        support = case.get('support', list(range(n)))
        M, y = a[name+'_M'], a[name+'_y']
        k = len(support)
        termination(d, k)
        x = currents[name]/data['config']['imax_A']
        if np.any(abs(x) > 1) or (name != 'dense' and x[case['failed']] != 0):
            raise ValueError('Invalid solver current constraints')
        residual = numeric(unpack(d['residual']), y.shape)
        agreement(residual, M@x[support]-y)
        agreement(d['cost'], residual@residual/2)
        gradient = M.T@residual
        agreement(d['projected_gradient_max'], max(abs(x[support]-np.clip(x[support]-gradient, -1, 1))))
        singular = numeric(d['singular_values'], (k,))
        if np.any(singular <= 0) or np.any(np.diff(singular) > 0) or type(d['rank']) is not int or not 0 <= d['rank'] <= k:
            raise ValueError('Invalid solver singular diagnostics')
        agreement(d['condition'], singular[0]/singular[-1])
        agreement(singular, np.linalg.svd(M, compute_uv=False))
        if d['rank'] != int(np.linalg.matrix_rank(M)):
            raise ValueError('Inconsistent solver rank')
        comparison_record(d['repeated'], size=k)
        refs = [validate_reference(d['reference'+str(digits)], k, digits, M, y) for digits in (60, 90)]
        check = d['reference_check']
        if all(d['reference'+str(digits)]['status'] == 'PASS' for digits in (60, 90)):
            require_keys(check, ('status', 'precision_convergence', 'solver'))
            comparison_record(check['precision_convergence'], close(*refs))
            comparison_record(check['solver'], size=k)
            # Imax scaling can round the saved current; do not demand bitwise
            # identity of diagnostics computed from the pre-scaling fit.x.
            expected_solver = close(refs[1], x[support])
            agreement(check['solver']['max_absolute'], expected_solver['max_absolute'])
            if check['solver']['status'] != expected_solver['status']:
                raise ValueError('Inconsistent solver reference comparison')
            if check['status'] != ('PASS' if np.array_equal(*refs) else 'FAIL'):
                raise ValueError('Inconsistent independent solver status')
        else:
            require_keys(check, ('status',))
            if check['status'] != 'INCONCLUSIVE':
                raise ValueError('Invalid unavailable reference status')
        incomplete |= check['status'] == 'INCONCLUSIVE'
        require_keys(d['driver_diagnostics'], ('gelsd', 'gelss', 'gelsy'))
        for v in d['driver_diagnostics'].values():
            driver_x = numeric(unpack(v), (k,))
            agreement(M.T@(M@driver_x-y), np.zeros(k))
        require_keys(d['rounding_sensitivity'], ('14', '15', '16'))
        for v in d['rounding_sensitivity'].values():
            comparison_record(v, size=k)
        if not isinstance(d['initialization_sensitivity'], str) or not d['initialization_sensitivity']:
            raise ValueError('Missing initialization diagnostic')
        gates[name] = (d['success'] and d['repeated']['status'] == 'PASS'
                       and check['status'] == 'PASS' and check['solver']['status'] == 'PASS')
    training = result['training_condition']
    require_keys(training, ('singular_values', 'condition', 'rank'))
    s = numeric(training['singular_values'], (n,))
    if np.any(s <= 0) or type(training['rank']) is not int or not 0 <= training['rank'] <= n:
        raise ValueError('Invalid training diagnostics')
    agreement(training['condition'], s[0]/s[-1])
    weighted = np.sqrt(a['weights'])[:, None]*a['D']
    agreement(s, np.linalg.svd(weighted, compute_uv=False))
    if training['rank'] != int(np.linalg.matrix_rank(weighted)):
        raise ValueError('Inconsistent training rank')
    for name in ('row3', 'row4'):
        frozen = currents['dense'].copy(); frozen[data['cases'][name]['failed']] = 0
        expected = stable_recovery(a['fine_A'], a['fine_b'], a['fine_weights'], currents['dense'], frozen, currents[name])
        record = result['recovery'][name]
        require_keys(record, expected)
        for key, value in expected.items():
            if isinstance(value, str) or value is None:
                if record[key] != value:
                    raise ValueError('Inconsistent recovery reference')
            else:
                numeric(record[key], np.asarray(value).shape)
                agreement(record[key], value)
    return gates, incomplete


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')


def environment():
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
        scipy.show_config()
        if hasattr(np, 'show_runtime'):
            np.show_runtime()
    try:
        from threadpoolctl import threadpool_info
        pools = threadpool_info()
    except ImportError:
        pools = 'UNAVAILABLE: optional threadpoolctl is not installed; see show_config/runtime'
    return dict(python=platform.python_version(), executable=os.sys.executable,
                packages={d.metadata['Name']: d.version for d in distributions()},
                numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(),
                machine=platform.machine(), processor=platform.processor(), cpu_count=os.cpu_count(),
                threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS',
                                                      'MKL_NUM_THREADS', 'BLIS_NUM_THREADS')},
                numerical_config=stream.getvalue(), loaded_threadpools=pools,
                source_status=subprocess.check_output(['git', 'status', '--porcelain=v1'], text=True),
                head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())


WORKER_FILES = frozenset(('environment.json', 'source_sha256.json', 'sealed-inputs.json',
    'regenerated-inputs.json', 'input-comparisons.json', 'frozen-solve.json',
    'regenerated-solve.json', 'frozen-fields.json', 'independent-fields.json', 'status.json'))
INPUT_ARRAYS = frozenset(('points', 'normals', 'weights', 'A', 'b', 'D', 'd', 'vertices',
    'error_vertices', 'original_Bxyz', 'fine_points', 'fine_normals', 'fine_weights', 'fine_A', 'fine_b')) | {
    name+suffix for name in ('dense', 'row3', 'row4')
    for suffix in ('_M', '_y', '_unconstrained_initial_x', '_x')}


def identical_solver_inputs(left, right, expected_sha256):
    paths = [Path(root)/'sealed-inputs.json' for root in (left, right)]
    if not expected_sha256 or any(sha(p) != expected_sha256 for p in paths):
        raise ValueError('Sealed solver input fingerprint mismatch')
    if paths[0].read_bytes() != paths[1].read_bytes():
        raise ValueError('Workers did not consume identical serialized solver inputs')


def verify_historical_sources(root):
    """Check recorded historical source against the required Git object, never regeneration.

    This binds source bytes to history, but does not authenticate a downloaded
    archive. External archive/run authentication remains a separate requirement.
    """
    root = Path(root)
    commit = 'babc88ccd5086b5ec3a6e1c215524636d86b3580'
    metadata = json.loads((root/'quick/results.json').read_text())['metadata']
    if metadata['source_commit'] != commit or metadata['source_dirty'] is not False:
        raise ValueError('Historical source provenance mismatch')
    sources = json.loads((root/'source_fingerprints_at_run.json').read_text())
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit], text=True).splitlines()
    expected = {name for name in names if name == '.gitattributes' or
                (name.startswith('src/') and name.endswith('.py')) or
                (name.startswith(('scripts/', 'tests/')) and name.count('/') == 1 and name.endswith('.py')) or
                (name.startswith('configs/') and name.count('/') == 1 and name.endswith('.json'))}
    if set(sources) != expected or not expected:
        raise ValueError('Historical source fingerprint inventory mismatch')
    for name, digest in sources.items():
        raw = subprocess.check_output(['git', 'show', commit+':'+name])
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('Historical source hash mismatch: '+name)
    return {'source_status': 'PASS', 'archive_authentication': 'INCONCLUSIVE',
            'note': 'Source/history equality does not authenticate artifact origin'}


def verify_worker(root, expected_input_sha256):
    """Reject malformed scientific structures through a controlled validation error.

    Missing files retain FileNotFoundError so callers can distinguish missing
    evidence from invalid evidence. Do not catch execution or system failures.
    """
    try:
        return _verify_worker(root, expected_input_sha256)
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError, DecimalException) as exc:
        raise ValueError('Malformed worker scientific evidence: '+str(exc)) from exc


def _verify_worker(root, expected_input_sha256):
    """Require complete byte-bound evidence before using any scientific values.

    The expected seal digest comes from the upstream job, not the worker itself.
    A manifest establishes integrity, not independent historical authentication.
    """
    root = Path(root)
    entries = load_evidence(root/'manifest.json')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if set(entries) != WORKER_FILES or actual != WORKER_FILES | {'manifest.json'}:
        raise ValueError('Incomplete/unexpected worker result inventory')
    for name, digest in entries.items():
        path = (root/name).resolve()
        if (not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None
                or (root/name).is_symlink() or not path.is_relative_to(root.resolve()) or sha(path) != digest):
            raise ValueError('Worker manifest mismatch: '+name)
    # Parse every file strictly, even evidence that is only diagnostic.
    payloads = {name: load_evidence(root/name) for name in WORKER_FILES}
    state = payloads['status.json']
    if not expected_input_sha256 or sha(root/'sealed-inputs.json') != expected_input_sha256:
        raise ValueError('Sealed solver input fingerprint mismatch')
    if state.get('input_sha256') != expected_input_sha256:
        raise ValueError('Worker input provenance mismatch')
    sources = payloads['source_sha256.json']
    expected = source_fingerprints()
    if sources != expected:
        raise ValueError('Worker source differs from comparison checkout')
    env = payloads['environment.json']
    require_keys(env, ('python', 'executable', 'packages', 'numpy', 'scipy', 'platform', 'machine',
                       'processor', 'cpu_count', 'threads', 'numerical_config', 'loaded_threadpools',
                       'source_status', 'head'))
    for key in ('python', 'executable', 'numpy', 'scipy', 'platform', 'machine',
                'processor', 'numerical_config', 'source_status', 'head'):
        if not isinstance(env[key], str):
            raise ValueError('Invalid environment provenance type: '+key)
    if (not isinstance(env['threads'], dict)
            or set(env['threads']) != {'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS'}
            or any(v is not None and not isinstance(v, str) for v in env['threads'].values())
            or (env['cpu_count'] is not None and (type(env['cpu_count']) is not int or env['cpu_count'] <= 0))
            or not isinstance(env['loaded_threadpools'], (list, str))):
        raise ValueError('Invalid numerical environment diagnostics')
    if env.get('head') != subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip():
        raise ValueError('Worker commit provenance mismatch')
    if not env.get('python', '').startswith('3.11.') or not env.get('packages') or not env.get('numerical_config'):
        raise ValueError('Missing environment provenance')
    if (env.get('numpy'), env.get('scipy')) not in {
            ('2.4.6', '1.17.1'), ('2.3.5', '1.17.1'), ('2.4.6', '1.16.3')}:
        raise ValueError('Unexpected numerical environment')
    if (not isinstance(env['packages'], dict) or env['packages'].get('numpy') != env['numpy']
            or env['packages'].get('scipy') != env['scipy']):
        raise ValueError('Inconsistent dependency provenance')
    data = payloads['sealed-inputs.json']
    regenerated = payloads['regenerated-inputs.json']
    arrays, rebuilt = validate_inputs(data), validate_inputs(regenerated)
    equality = payloads['input-comparisons.json']
    require_keys(equality, INPUT_ARRAYS)
    for key in INPUT_ARRAYS:
        comparison_record(equality[key], close(arrays[key], rebuilt[key]))
    checks, incomplete = {'complete_cases': True}, False
    for stage, filename, inputs, a in (
            ('frozen', 'frozen-solve.json', data, arrays),
            ('regenerated', 'regenerated-solve.json', regenerated, rebuilt)):
        gates, unavailable = validate_solve(payloads[filename], inputs, a)
        checks.update({stage+'/'+key: value for key, value in gates.items()})
        incomplete |= unavailable
    fields = payloads['frozen-fields.json']
    expected_fields = {'unit_coils_Bxyz', 'original_Bxyz', 'projected_A',
                       'dense_fixed_current_Bxyz', 'row3_fixed_current_Bxyz',
                       'row4_fixed_current_Bxyz', 'row3_frozen_current_Bxyz', 'row4_frozen_current_Bxyz'}
    if set(fields) != expected_fields:
        raise ValueError('Incomplete field comparison inventory')
    p, n = arrays['A'].shape
    components = numeric(unpack(fields['unit_coils_Bxyz']), (n, p, 3))
    original = numeric(unpack(fields['original_Bxyz']), (p, 3))
    agreement(unpack(fields['projected_A']), np.sum(components*arrays['normals'][None, :, :], axis=2).T)
    numeric(unpack(fields['projected_A']), (p, n))
    for name in ('dense', 'row3', 'row4'):
        x = arrays[name+'_x']*data['config']['imax_A']
        numeric(unpack(fields[name+'_fixed_current_Bxyz']), (p, 3))
        agreement(unpack(fields[name+'_fixed_current_Bxyz']), original+np.einsum('jpc,j->pc', components, x))
        if name != 'dense':
            x = arrays['dense_x'].copy()*data['config']['imax_A']; x[data['cases'][name]['failed']] = 0
            numeric(unpack(fields[name+'_frozen_current_Bxyz']), (p, 3))
            agreement(unpack(fields[name+'_frozen_current_Bxyz']), original+np.einsum('jpc,j->pc', components, x))
    independent = payloads['independent-fields.json']
    require_keys(independent, ('points', 'coils', 'status', 'limitation'))
    if unpack(independent['points']).shape != (2, 3) or not np.array_equal(unpack(independent['points']), arrays['points'][[0, p//3]]):
        raise ValueError('Inconsistent independent field probes')
    if set(independent['coils']) != {str(i) for i in range(len(unpack(data['arrays']['vertices']))+1)}:
        raise ValueError('Incomplete independent field inventory')
    independent_pass = True
    for index, probe in independent['coils'].items():
        require_keys(probe, ('reference60', 'reference90', 'precision_convergence', 'production'))
        for key in ('reference60', 'reference90'):
            rows = probe[key]
            if (not isinstance(rows, list) or len(rows) != 2
                    or any(not isinstance(row, list) or len(row) != 3
                           or any(not isinstance(v, str) or not Decimal(v).is_finite() for v in row) for row in rows)):
                raise ValueError('Invalid independent Decimal field payload')
        low, high = [numeric(np.asarray(probe[key], dtype=float), (2, 3)) for key in ('reference60', 'reference90')]
        comparison_record(probe['precision_convergence'], close(low, high))
        actual = components[int(index), [0, p//3]] if int(index) < n else original[[0, p//3]]
        comparison_record(probe['production'], close(high, actual))
        independent_pass &= probe['precision_convergence']['exact'] and probe['production']['status'] == 'PASS'
    if independent['status'] != ('PASS' if independent_pass else 'FAIL') or not independent['limitation']:
        raise ValueError('Inconsistent independent field status')
    checks['independent_fields'] = bool(independent_pass)
    require_keys(state.get('checks'), checks)
    if any(type(v) is not bool for v in state['checks'].values()):
        raise ValueError('Invalid worker gate types')
    expected_status = 'INCONCLUSIVE' if incomplete else ('PASS' if all(checks.values()) else 'FAIL')
    if (state.get('status') != expected_status or state.get('checks') != checks
            or state.get('scientific_status') != 'PARTIAL' or state.get('production_cross_platform') != 'UNRESOLVED'):
        raise ValueError('Worker status contradicts scientific evidence')
    return state


def source_fingerprints():
    files = [f for folder in ('src', 'scripts', 'configs', 'tests', '.github/workflows')
             for f in Path(folder).rglob('*') if f.suffix in ('.py', '.json', '.cs', '.ps1', '.yml')]
    files += [Path('pyproject.toml'), Path('requirements-tested.txt')]
    return {f.as_posix(): sha(f) for f in sorted(files)}


def capture(config):
    """Use production geometry, projection, scaling, and actual baseline assembly."""
    c = config
    p, n, w, coils, error, b = benchmark(c['nt'], c['np'], c['segments'], c['nphi'],
                                       c['ntheta'], c['geometry_version'])
    A = response(p, n, coils)
    D, d = A*c['imax_A']/c['bref_T'], b/c['bref_T']
    pv, nv, av = surface(1., .25, 2*c['nt'], 2*c['np'], .5)
    wv = av/av.sum()
    Av = response(pv, nv, coils)
    bv = np.sum(field(pv, error, 1500)*nv, axis=1)
    arrays = dict(points=p, normals=n, weights=w, A=A, b=b, D=D, d=d,
                  vertices=np.array([x.vertices for x in coils]), error_vertices=error.vertices,
                  original_Bxyz=field(p, error, 1500), fine_points=pv, fine_normals=nv,
                  fine_weights=wv, fine_A=Av, fine_b=bv)
    cases = {}
    original = optimize.lsq_linear
    def recording(M, y, **kwargs):
        arrays[label+'_M'] = M.copy()
        arrays[label+'_y'] = y.copy()
        fit = original(M, y, **kwargs)
        arrays[label+'_unconstrained_initial_x'] = np.asarray(fit.unbounded_sol[0]).copy()
        cases[label] = dict(arguments=kwargs, implicit_method='trf', implicit_lsq_solver='exact',
                            initialization='No x0 argument; SciPy starts with unconstrained least squares',
                            status=int(fit.status), success=bool(fit.success), message=str(fit.message),
                            nit=int(fit.nit), cost=float(fit.cost), optimality=float(fit.optimality),
                            active_mask=fit.active_mask.tolist())
        return fit
    optimize.lsq_linear = recording
    try:
        label = 'dense'
        dense, _ = optimize.baseline(D, d, w, c['ridge'])
        active = np.flatnonzero(abs(dense)*c['imax_A'] > c['active_threshold_A'])
        arrays['dense_x'] = dense
        for row in (3, 4):
            failed = int(active[row])
            label = 'row'+str(row)
            support = np.delete(np.arange(len(coils)), failed)
            recovered, _ = optimize.baseline(D, d, w, c['ridge'], support)
            arrays[label+'_x'] = recovered
            cases[label].update(fault_row=row, failed=failed, support=support.tolist())
    finally:
        optimize.lsq_linear = original
    return dict(schema='production-upstream-v1', config=c, cases=cases,
                arrays={k: pack(v) for k, v in arrays.items()})


def reference(M, y, digits):
    """Independent Decimal elimination; certify interior feasibility and stationarity.

    Normal equations are used ONLY if the reference is strictly inside the box.
    An active/infeasible solution returns INCONCLUSIVE, never a constrained reference pass.
    Ridge gives these augmented production matrices full column rank; precision doubling
    checks loss from squaring conditioning. This is not an interval certificate.
    """
    with localcontext() as ctx:
        ctx.prec = digits
        rows = [[Decimal.from_float(float(v)) for v in row] for row in M]
        yy = [Decimal.from_float(float(v)) for v in y]
        size = M.shape[1]
        H = [[sum((r[i]*r[j] for r in rows), Decimal(0)) for j in range(size)] for i in range(size)]
        g = [sum((r[i]*v for r, v in zip(rows, yy)), Decimal(0)) for i in range(size)]
        work = [r.copy()+[v] for r, v in zip(H, g)]
        for k in range(size):
            pivot = max(range(k, size), key=lambda j: abs(work[j][k]))
            work[k], work[pivot] = work[pivot], work[k]
            if not work[k][k]:
                return dict(status='INCONCLUSIVE', reason='Singular reference system')
            for i in range(k+1, size):
                factor = work[i][k]/work[k][k]
                for j in range(k+1, size+1):
                    work[i][j] -= factor*work[k][j]
                work[i][k] = Decimal(0)
        x = [Decimal(0)]*size
        for i in reversed(range(size)):
            x[i] = (work[i][-1]-sum((work[i][j]*x[j] for j in range(i+1, size)), Decimal(0)))/work[i][i]
        if any(abs(v) >= 1 for v in x):
            return dict(status='INCONCLUSIVE', reason='Active bounds require independent constrained solver')
        gradient = max(abs(sum((H[i][j]*x[j] for j in range(size)), Decimal(0))-g[i]) for i in range(size))
        threshold = Decimal(10)**(-(digits//2))
        objective = sum(((sum((a*v for a, v in zip(r, x)), Decimal(0))-b)**2 for r, b in zip(rows, yy)), Decimal(0))/2
        return dict(status='PASS' if gradient < threshold else 'FAIL', x=[str(v) for v in x],
                    gradient_max=str(gradient), objective=str(objective),
                    bound_margin=str(1-max(abs(v) for v in x)), precision=digits)


def close(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        return dict(status='FAIL', reason='Shape mismatch')
    diff = abs(a-b)
    bound = ATOL+RTOL*abs(b)
    return dict(status='PASS' if np.all(diff <= bound) else 'FAIL',
                max_absolute=float(np.max(diff, initial=0)),
                failures=int(np.count_nonzero(diff > bound)), exact=pack(a) == pack(b))


def decimal_field(points, vertices, current, digits):
    """Independent tangent/perpendicular straight-wire integral, Decimal arithmetic."""
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: Decimal.from_float(float(v))
        vv = [[cv(v) for v in r] for r in vertices]
        result = []
        for point in points:
            p = [cv(v) for v in point]
            total = [Decimal(0)]*3
            for a, b in zip(vv, vv[1:]+vv[:1]):
                delta = [v-u for u, v in zip(a, b)]
                length = sum(v*v for v in delta).sqrt()
                u = [v/length for v in delta]
                r = [v-w for v, w in zip(p, a)]
                s = sum(v*w for v, w in zip(r, u))
                perpendicular = [v-s*w for v, w in zip(r, u)]
                h2 = sum(v*v for v in perpendicular)
                if not h2:
                    raise ValueError('Collinear reference probe requires separate limit')
                factor = (s/(h2+s*s).sqrt()-(s-length)/(h2+(s-length)**2).sqrt())/h2
                cross = [u[1]*perpendicular[2]-u[2]*perpendicular[1],
                         u[2]*perpendicular[0]-u[0]*perpendicular[2],
                         u[0]*perpendicular[1]-u[1]*perpendicular[0]]
                total = [v+w*factor for v, w in zip(total, cross)]
            result.append([str(v*Decimal('1e-7')*cv(current)) for v in total])
        return result


def solve_inputs(data):
    arrays = {k: unpack(v) for k, v in data['arrays'].items()}
    c = data['config']
    diagnostics, currents = {}, {}
    for name, case in data['cases'].items():
        M, y = arrays[name+'_M'], arrays[name+'_y']
        fit = optimize.lsq_linear(M, y, **case['arguments'])
        repeat = optimize.lsq_linear(M, y, **case['arguments'])
        singular = np.linalg.svd(M, compute_uv=False)
        low, high = reference(M, y, 60), reference(M, y, 90)
        refcheck = dict(status='INCONCLUSIVE')
        if low['status'] == high['status'] == 'PASS':
            lo = np.array([float(v) for v in low['x']])
            hi = np.array([float(v) for v in high['x']])
            refcheck = dict(precision_convergence=close(lo, hi), solver=close(hi, fit.x),
                            status='PASS' if np.array_equal(lo, hi) else 'FAIL')
        x = np.zeros(arrays['A'].shape[1])
        support = case.get('support', list(range(len(x))))
        x[support] = fit.x
        currents[name] = x*c['imax_A']
        drivers = {driver: pack(lstsq(M, y, lapack_driver=driver)[0])
                   for driver in ('gelsd', 'gelss', 'gelsy')}
        rounding = {}
        for digits in (14, 15, 16):
            rounded = np.array([[float(format(v, '.'+str(digits)+'g')) for v in r] for r in M])
            rr = optimize.lsq_linear(rounded, y, **case['arguments'])
            rounding[str(digits)] = close(fit.x, rr.x)
        diagnostics[name] = dict(success=bool(fit.success), status=int(fit.status), message=fit.message,
                                 nit=int(fit.nit), optimality=float(fit.optimality), cost=float(fit.cost),
                                 active_mask=fit.active_mask.tolist(), singular_values=singular.tolist(),
                                 rank=int(np.linalg.matrix_rank(M)), condition=float(singular[0]/singular[-1]),
                                 residual=pack(M@fit.x-y), reference60=low, reference90=high,
                                 reference_check=refcheck, repeated=close(fit.x, repeat.x),
                                 driver_diagnostics=drivers, rounding_sensitivity=rounding,
                                 initialization_sensitivity='Not applicable: lsq_linear has no x0; no settings changed')
        gradient = M.T@(M@fit.x-y)
        projected = fit.x-np.clip(fit.x-gradient, -1, 1)
        diagnostics[name]['projected_gradient_max'] = float(max(abs(projected)))
    recovery = {}
    for name in ('row3', 'row4'):
        frozen = currents['dense'].copy()
        frozen[data['cases'][name]['failed']] = 0
        recovery[name] = stable_recovery(arrays['fine_A'], arrays['fine_b'], arrays['fine_weights'],
                                         currents['dense'], frozen, currents[name])
    weighted = np.sqrt(arrays['weights'])[:, None]*arrays['D']
    s = np.linalg.svd(weighted, compute_uv=False)
    return dict(diagnostics=diagnostics, currents_A={k: pack(v) for k, v in currents.items()}, recovery=recovery,
                training_condition=dict(singular_values=s.tolist(), condition=float(s[0]/s[-1]),
                                        rank=int(np.linalg.matrix_rank(weighted))))


def field_replay(data):
    """Re-evaluate Cartesian components on identical polygon and point bytes."""
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    components = np.array([field(a['points'], Coil(v)) for v in a['vertices']])
    original = field(a['points'], Coil(a['error_vertices']), 1500.)
    result = dict(unit_coils_Bxyz=pack(components), original_Bxyz=pack(original),
                  projected_A=pack(np.sum(components*a['normals'][None, :, :], axis=2).T))
    for name in ('dense', 'row3', 'row4'):
        current = a[name+'_x']*data['config']['imax_A']
        result[name+'_fixed_current_Bxyz'] = pack(original+np.einsum('jpc,j->pc', components, current))
        if name != 'dense':
            frozen = a['dense_x'].copy()*data['config']['imax_A']
            frozen[data['cases'][name]['failed']] = 0
            result[name+'_frozen_current_Bxyz'] = pack(original+np.einsum('jpc,j->pc', components, frozen))
    return result


def independent_field_checks(data):
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    # Deterministic production-grid subset, all coils, all Cartesian components.
    points = a['points'][[0, len(a['points'])//3]]
    checks = {}
    for i, vertices in enumerate([*a['vertices'], a['error_vertices']]):
        current = 1500. if i == len(a['vertices']) else 1.
        low, high = [decimal_field(points, vertices, current, n) for n in (60, 90)]
        lowf, highf = np.array(low, float), np.array(high, float)
        actual = field(points, Coil(vertices), current)
        checks[str(i)] = dict(reference60=low, reference90=high,
                              precision_convergence=close(lowf, highf), production=close(highf, actual))
    return dict(points=pack(points), coils=checks,
                status='PASS' if all(c['precision_convergence']['exact'] and c['production']['status'] == 'PASS'
                                     for c in checks.values()) else 'FAIL',
                limitation='Two production-grid probes per polygon; finite wires, no continuum certificate')


def manifest(root):
    write(root/'manifest.json', {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()})
