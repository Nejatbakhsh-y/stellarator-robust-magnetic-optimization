"""STEP 32 reciprocal diagnostics. No production settings are changed.

Exit 0: diagnostic gates passed; 1: scientific comparison failed; 2: evidence/error.
Historical production FAIL and overall PARTIAL are never promoted by this tool.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
from decimal import Decimal, localcontext

import numpy as np
from scipy.optimize import lsq_linear
from threadpoolctl import threadpool_limits
from stellarator_robust import optimize
from stellarator_robust.upstream_attribution import (
    capture, close, environment, field_replay, independent_field_checks, load_evidence,
    manifest, pack, sha, solve_inputs, source_fingerprints, unpack, validate_inputs,
    validate_solve, require_solve, numeric, agreement, write,
)

COHORTS = ('windows-reference', 'linux-reference', 'linux-numpy-sensitivity', 'linux-scipy-sensitivity')
CASES = ('dense', 'row3', 'row4')


def decimal_metric(arrays, currents, failed, digits=90):
    """Direct RMS with exact conversion of the complete saved binary64 inputs."""
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda x: Decimal.from_float(float(x))
        A = [[cv(x) for x in row] for row in arrays['fine_A']]
        b = list(map(cv, arrays['fine_b'])); w = list(map(cv, arrays['fine_weights']))
        frozen = currents['dense'].copy(); frozen[failed] = 0
        rms = []
        for current in (currents['dense'], frozen, currents['recovered']):
            x = list(map(cv, current))
            residual = [bb+sum((a*j for a, j in zip(row, x)), Decimal(0)) for row, bb in zip(A, b)]
            rms.append(sum((ww*r*r for ww, r in zip(w, residual)), Decimal(0)).sqrt())
        B, L, P = rms
        return dict(rms_T=list(map(str, rms)), denominator_T=str(L-B),
                    ratio=str((L-P)/(L-B)) if abs(L-B) > Decimal('1e-15') else None)


def differential(left, right):
    with localcontext() as ctx:
        ctx.prec = 90
        B, L, P = map(Decimal, left['rms_T'])
        b, l, p = map(Decimal, right['rms_T'])
        if abs(L-B) <= Decimal('1e-15') or right['ratio'] is None:
            return dict(status='INCONCLUSIVE', reason='Original denominator guard')
        R = (L-P)/(L-B)
        terms = [(1-R)*(l-L)/(L-B), -(p-P)/(L-B), R*(b-B)/(L-B)]
        observed = Decimal(right['ratio'])-R
        return dict(terms_L_P_B=list(map(str, terms)), observed=str(observed),
                    linear_prediction=str(sum(terms)), nonlinear_remainder=str(observed-sum(terms)),
                    denominator_condition=str((abs(L)+abs(B))/abs(L-B)))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def runtime_sources():
    records = {}
    root = Path.cwd().resolve()
    for name in ('optimize', 'experiments', 'model', 'fault_metrics', 'upstream_attribution'):
        module = __import__('stellarator_robust.'+name, fromlist=['__file__'])
        path = Path(module.__file__).resolve()
        expected = root/'src'/'stellarator_robust'/(name+'.py')
        if path != expected:
            raise ValueError('Scientific module imported from a different checkout: '+str(path))
        relative = path.relative_to(root).as_posix()
        blob = subprocess.run(['git', 'show', 'HEAD:'+relative], capture_output=True)
        record = dict(path=relative, loaded_sha256=sha(path), git_blob_available=blob.returncode == 0)
        record['matches_head'] = blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == sha(path)
        if os.environ.get('GITHUB_ACTIONS') == 'true' and not record['matches_head']:
            raise ValueError('Hosted scientific module does not match HEAD bytes: '+relative)
        records[name] = record
    return records


def historical(root):
    """Review supplied evidence only; never regenerate historical scientific values."""
    checks = []
    for path in sorted(root.rglob('manifest.json')):
        for name, digest in load_evidence(path).items():
            target = (path.parent/name).resolve()
            if not target.is_relative_to(path.parent.resolve()) or target.is_symlink():
                raise ValueError('Unsafe historical manifest path')
            match = sha(target) == digest
            checks.append(dict(path=str(target), sha256=digest, matches=match))
    if not checks or not all(c['matches'] for c in checks):
        raise ValueError('Missing or invalid historical manifest evidence')
    workers = {}
    for cohort in COHORTS:
        path = root/('upstream-'+cohort)/'upstream-worker'
        workers[cohort] = dict(environment=load_evidence(path/'environment.json'),
            sources=load_evidence(path/'source_sha256.json'),
            input_sha256=sha(path/'sealed-inputs.json'))
    first = workers[COHORTS[0]]
    worker_source_equal = all(w['sources'] == first['sources'] for w in workers.values())
    inputs_equal = all(w['input_sha256'] == first['input_sha256'] for w in workers.values())
    objects = {}
    for commit in {w['environment']['head'] for w in workers.values()}:
        probe = subprocess.run(['git', 'cat-file', '-e', commit+'^{commit}'], capture_output=True, text=True)
        objects[commit] = dict(available=probe.returncode == 0, stderr=probe.stderr)
    comparisons_root = root/'upstream-comparisons'
    original = {}
    for name in ('reference', 'numpy', 'scipy'):
        for path in (comparisons_root/('upstream-comparison-'+name)/'comparisons.json',
                     comparisons_root/('upstream-production-'+name+'.json')):
            original[str(path.relative_to(root))] = dict(sha256=sha(path), records=load_evidence(path))
    return dict(manifest_checks=checks, workers=workers, worker_source_fingerprints_equal=worker_source_equal,
                sealed_input_bytes_equal=inputs_equal, git_objects=objects,
                original_comparisons=original, hosted_artifact_authenticity='INCONCLUSIVE',
                production_acceptance='FAIL', overall='PARTIAL',
                limitation='Recorded worker hashes agree locally; hosted metadata and archive bytes require independent authentication. Missing commit objects prevent binding recorded source to Git.')


def problem(data):
    """Complete fixed-support problem, excluding saved solutions/termination records."""
    return dict(config=data['config'], cases={k: {
        'M': data['arrays'][k+'_M'], 'y': data['arrays'][k+'_y'],
        'arguments': v['arguments'], 'method': v['implicit_method'],
        'lsq_solver': v['implicit_lsq_solver'], 'support': v.get('support'),
        'failed': v.get('failed')} for k, v in data['cases'].items()})


def verified(root):
    root = Path(root)
    records = load_evidence(root/'manifest.json')
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*')
              if p.is_file() and p.name != 'manifest.json'}
    if actual != records:
        raise ValueError('Incomplete or changed artifact: '+str(root))
    if load_evidence(root/'status.json')['diagnostic_status'] != 'PASS':
        raise ValueError('Worker/capture diagnostic did not pass: '+str(root))
    return root


def verified_capture(root):
    root = verified(root)
    if load_evidence(root/'input-sha256.json').get('inputs.json') != sha(root/'inputs.json'):
        raise ValueError('Capture seal mismatch')
    data = load_evidence(root/'inputs.json')
    if load_evidence(root/'problem-sha256.json').get('sha256') != fingerprint(problem(data)):
        raise ValueError('Complete optimization problem fingerprint mismatch')
    return root


def optimality(M, y, x):
    M, y, x = map(np.asarray, (M, y, x))
    if (M.ndim != 2 or y.shape != (len(M),) or x.shape != (M.shape[1],)
            or not all(np.isfinite(a).all() for a in (M, y, x))):
        raise ValueError('Invalid solver arrays')
    residual = M@x-y
    gradient = M.T@residual
    kkt = np.where(x <= -1, np.minimum(gradient, 0),
                   np.where(x >= 1, np.maximum(gradient, 0), gradient))
    s = np.linalg.svd(M, compute_uv=False)
    return dict(objective=float(residual@residual/2), residual_norm=float(np.linalg.norm(residual)),
                constraint_violation=float(max(0., np.max(abs(x))-1)),
                active_lower=np.flatnonzero(x <= -1).tolist(), active_upper=np.flatnonzero(x >= 1).tolist(),
                kkt_max=float(np.max(abs(kkt))),
                projected_gradient=float(np.max(abs(x-np.clip(x-gradient, -1, 1)))),
                singular_values=s.tolist(), rank=int(np.linalg.matrix_rank(M)),
                condition=None if s[-1] == 0 else float(s[0]/s[-1]))


def coordinate_reference(M, y, start, max_sweeps=100000):
    """Independent box coordinate minimization on residuals, never normal equations.

    Diagnostic stopping 1e-14 gradient; this does not change production tolerances.
    Residual is rebuilt each sweep to avoid accumulated update drift.
    """
    x = np.clip(np.asarray(start).copy(), -1, 1)
    norms = np.sum(M*M, axis=0)
    if np.any(norms == 0):
        return dict(status='INCONCLUSIVE', reason='Zero column')
    for sweep in range(max_sweeps):
        r = M@x-y
        for j in range(len(x)):
            value = np.clip(x[j]-np.dot(M[:, j], r)/norms[j], -1, 1)
            r += M[:, j]*(value-x[j]); x[j] = value
        metrics = optimality(M, y, x)
        if metrics['kkt_max'] <= 1e-14 and metrics['constraint_violation'] == 0:
            return dict(status='PASS', x=pack(x), sweeps=sweep+1, metrics=metrics)
    return dict(status='INCONCLUSIVE', x=pack(x), sweeps=max_sweeps, metrics=metrics)


def support_trace(data):
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    c = data['config']; D, d, w = [a[k] for k in ('D', 'd', 'weights')]
    def entry(x, support):
        r = np.sqrt(w)*(D@x+d)
        return dict(support=np.asarray(support).tolist(), x=pack(x),
                    objective=float((r@r+c['ridge']*(x@x))/2))
    deletion = []; support = np.arange(D.shape[1])
    while len(support):
        x, _ = optimize.baseline(D, d, w, c['ridge'], support)
        order = support[np.argsort(abs(x[support]), kind='stable')]
        record = entry(x, support)
        record.update(removed=int(order[0]), removal_order=order.tolist(),
                      removal_scores=abs(x[order]).tolist())
        deletion.append(record); support = support[support != order[0]]
    sparse = []
    for penalty in c['l1_path']:
        x, status = optimize.sparse(D, d, w, penalty, c['ridge'])
        support = np.flatnonzero(abs(x)*c['imax_A'] > c['active_threshold_A'])
        refit, _ = optimize.baseline(D, d, w, c['ridge'], support)
        sparse.append(dict(penalty=penalty, selection=entry(x, support),
                           refit=entry(refit, support), status=status))
    return dict(deletion=deletion, sparse=sparse,
                dense_active=np.flatnonzero(abs(a['dense_x'])*c['imax_A'] > c['active_threshold_A']).tolist(),
                fault_supports={k: data['cases'][k]['support'] for k in ('row3', 'row4')})


def replay(data):
    a = validate_inputs(data)
    result = solve_inputs(data)
    try:
        require_solve(result, data, a)
    except ValueError:
        # Retain an executed failed candidate before stopping diagnostics.
        if '--output' in sys.argv:
            out = Path(sys.argv[sys.argv.index('--output')+1])
            if out.is_dir():
                failed = out/('failed-solve-'+fingerprint(result)+'.json')
                if not failed.exists():
                    write(failed, result)
        raise
    independent = {}; sensitivity = {}
    for name in CASES:
        support = data['cases'][name].get('support', list(range(a['A'].shape[1])))
        x = unpack(result['currents_A'][name])[support]/data['config']['imax_A']
        M, y = a[name+'_M'], a[name+'_y']
        independent[name] = dict(production=optimality(M, y, x),
                                coordinate=coordinate_reference(M, y, np.zeros_like(x)))
        checks = {}
        # Independent constrained BVLS and controlled thread interventions.
        bvls = lsq_linear(M, y, bounds=(-1, 1), method='bvls', tol=1e-12, max_iter=1000)
        checks['bvls'] = dict(success=bool(bvls.success), status=int(bvls.status), nit=int(bvls.nit),
                              x=pack(bvls.x), metrics=optimality(M, y, bvls.x), comparison=close(x, bvls.x))
        for label, matrix, target, reverse in (
                ('reverse_rows', M[::-1].copy(), y[::-1].copy(), False),
                ('reverse_columns', M[:, ::-1].copy(), y, True)):
            fit = lsq_linear(matrix, target, **data['cases'][name]['arguments'])
            ordered = fit.x[::-1] if reverse else fit.x
            checks[label] = dict(x=pack(ordered), success=bool(fit.success),
                                 comparison=close(x, ordered), metrics=optimality(M, y, ordered),
                                 intervention='Mathematically equivalent reordered system; input byte order deliberately changed')
        for threads in (1, 2):
            with threadpool_limits(limits=threads):
                fit = lsq_linear(M, y, **data['cases'][name]['arguments'])
                checks['threads'+str(threads)] = dict(x=pack(fit.x), success=bool(fit.success),
                    comparison=close(x, fit.x), environment=environment())
        for probe in checks.values():
            candidate = numeric(unpack(probe['x']), x.shape)
            metrics = optimality(M, y, candidate)
            for key in ('objective', 'constraint_violation', 'kkt_max'):
                numeric(metrics[key], ())
            if metrics['constraint_violation'] != 0 or metrics['kkt_max'] > 1e-12:
                raise ValueError('Invalid sensitivity candidate optimality')
        sensitivity[name] = checks
    ratios = {}
    for name in ('row3', 'row4'):
        currents = dict(dense=unpack(result['currents_A']['dense']), recovered=unpack(result['currents_A'][name]))
        ratios[name] = {str(p): decimal_metric(a, currents, data['cases'][name]['failed'], p) for p in (60, 90)}
        with localcontext() as ctx:
            ctx.prec = 90
            high = ratios[name]['90']['ratio']
            saved = result['recovery'][name]['fractional_recovery']
            ratios[name]['saved_minus_decimal'] = None if high is None or saved is None else str(Decimal.from_float(saved)-Decimal(high))
            ratios[name]['precision_difference'] = None if high is None else str(Decimal(ratios[name]['60']['ratio'])-Decimal(high))
    return dict(solve=result, optimality=independent, sensitivity=sensitivity, ratios=ratios)


def require_replay(result):
    if set(result['optimality']) != set(CASES):
        raise ValueError('Incomplete solver evidence')
    for name in CASES:
        v = result['optimality'][name]
        violation = numeric(v['production']['constraint_violation'], ())
        kkt = numeric(v['production']['kkt_max'], ())
        if (v['coordinate']['status'] != 'PASS' or v['production']['constraint_violation'] != 0
                or violation < 0 or kkt < 0 or kkt > 1e-12):
            raise ValueError('Invalid constrained optimality evidence')
        sensitivity = result['sensitivity'][name]
        if not all(sensitivity[k]['success'] is True for k in
                   ('bvls', 'threads1', 'threads2', 'reverse_rows', 'reverse_columns')):
            raise ValueError('Independent solver/sensitivity failed')
        for digits in ('60', '90'):
            if result['ratios'].keys() != {'row3', 'row4'}:
                raise ValueError('Incomplete fault ratio evidence')
            for row in ('row3', 'row4'):
                if digits not in result['ratios'][row]:
                    raise ValueError('Incomplete high precision evidence')
                ratio = result['ratios'][row][digits]
                values = [Decimal(v) for v in ratio['rms_T']]
                denominator = Decimal(ratio['denominator_T'])
                recovery = Decimal(ratio['ratio']) if ratio['ratio'] is not None else None
                if (len(values) != 3 or any(not v.is_finite() or v < 0 for v in values)
                        or not denominator.is_finite() or abs(denominator) <= Decimal('1e-15')
                        or recovery is None or not recovery.is_finite()):
                    raise ValueError('Invalid or unavailable high precision ratio')


def validate_replay(result, data, arrays):
    """Bind saved diagnostic ratios to their sealed inputs and current vectors."""
    require_solve(result['solve'], data, arrays)
    require_replay(result)
    for name in CASES:
        support = data['cases'][name].get('support', list(range(arrays['A'].shape[1])))
        x = unpack(result['solve']['currents_A'][name])[support]/data['config']['imax_A']
        expected = optimality(arrays[name+'_M'], arrays[name+'_y'], x)
        actual = result['optimality'][name]['production']
        if set(actual) != set(expected):
            raise ValueError('Incomplete production optimality evidence')
        for key, value in expected.items():
            if key in ('active_lower', 'active_upper', 'rank') or value is None:
                if actual[key] != value:
                    raise ValueError('Inconsistent production optimality evidence')
            else:
                agreement(actual[key], value)
    for row in ('row3', 'row4'):
        currents = dict(dense=unpack(result['solve']['currents_A']['dense']),
                        recovered=unpack(result['solve']['currents_A'][row]))
        for digits in (60, 90):
            expected = decimal_metric(arrays, currents, data['cases'][row]['failed'], digits)
            if result['ratios'][row][str(digits)] != expected:
                raise ValueError('Inconsistent high precision recovery evidence')


def source_check(left, right, expected):
    if not expected or not isinstance(left.get('sha256'), dict) or not left['sha256']:
        raise ValueError('Incomplete source provenance')
    if left['head'] != expected or right['head'] != expected:
        raise ValueError('Incorrect worker commit')
    if left['sha256'] != right['sha256']:
        raise ValueError('Scientific source fingerprints differ')


def support_decisions(trace):
    return dict(deletion=[(r['support'], r['removed']) for r in trace['deletion']],
                sparse=[(r['penalty'], r['selection']['support']) for r in trace['sparse']],
                faults=trace['fault_supports'], dense=trace['dense_active'])


def reciprocal_effects(A, B, C, D):
    """Paired effects only after provenance/input gates; interactions remain explicit."""
    A, B, C, D = [np.asarray(v, dtype=float) for v in (A, B, C, D)]
    if len({v.shape for v in (A, B, C, D)}) != 1 or not all(np.isfinite(v).all() for v in (A, B, C, D)):
        raise ValueError('Invalid reciprocal outputs')
    return dict(solver_on_windows_inputs=pack(B-A), solver_on_linux_inputs=pack(D-C),
                generation_on_windows_solver=pack(C-A), generation_on_linux_solver=pack(D-B),
                interaction=pack((D-C)-(B-A)))


def ratio_interventions(reference_data, current_data, reference, current, name):
    """One-block swaps plus joint effects; no additive attribution assumption."""
    a, b = [{k: unpack(v) for k, v in d['arrays'].items()} for d in (reference_data, current_data)]
    def currents(result):
        return dict(dense=unpack(result['solve']['currents_A']['dense']),
                    recovered=unpack(result['solve']['currents_A'][name]))
    r, c = currents(reference), currents(current)
    failed = reference_data['cases'][name]['failed']
    if failed != current_data['cases'][name]['failed']:
        return dict(status='INCONCLUSIVE', reason='Different fault identity')
    base = decimal_metric(a, r, failed)
    swaps = {'currents': decimal_metric(a, c, failed), 'joint': decimal_metric(b, c, failed)}
    for key in ('dense', 'recovered'):
        swapped = dict(r); swapped[key] = c[key]
        swaps[key+'_currents'] = decimal_metric(a, swapped, failed)
    for key in ('fine_A', 'fine_b', 'fine_weights'):
        swapped = dict(a); swapped[key] = b[key]
        swaps[key] = decimal_metric(swapped, r, failed)
    return dict(reference=base, interventions={k: dict(metric=v, differential=differential(base, v)) for k, v in swaps.items()},
                limitation='fine_A combines response and projection; fine_b combines disturbance and normals. Unrecorded intermediate precision cannot be recovered.')


def comparisons(root, expected):
    """Require all 4 captures and all 16 replays before any numerical comparison."""
    captures = {c: verified_capture(root/('capture-'+c)) for c in COHORTS}
    workers = {c: verified(root/('replay-'+c)) for c in COHORTS}
    source = load_evidence(captures[COHORTS[0]]/'source-sha256.json')
    for path in [*captures.values(), *workers.values()]:
        source_check(source, load_evidence(path/'source-sha256.json'), expected)
    for worker, path in workers.items():
        for origin, cap in captures.items():
            digest = sha(cap/'inputs.json')
            if load_evidence(path/'input-sha256.json').get(origin) != digest:
                raise ValueError('Replay input seal mismatch')
            if (path/origin/'inputs.json').read_bytes() != (cap/'inputs.json').read_bytes():
                raise ValueError('Replay binary64 inputs changed')
            data = load_evidence(cap/'inputs.json')
            result = load_evidence(path/origin/'result.json')
            validate_replay(result, data, validate_inputs(data))
            for name in CASES:
                metrics = result['optimality'][name]
                if (metrics['coordinate']['status'] != 'PASS' or
                        metrics['production']['constraint_violation'] != 0 or
                        metrics['production']['kkt_max'] > 1e-12):
                    raise ValueError('Invalid constrained optimality evidence')
            if load_evidence(path/origin/'independent-fields.json')['status'] != 'PASS':
                raise ValueError('Independent field evidence failed')
    records = {}; failures = []
    for origin in COHORTS:
        reference = load_evidence(workers[COHORTS[0]]/origin/'result.json')
        for worker in COHORTS[1:]:
            current = load_evidence(workers[worker]/origin/'result.json')
            key = origin+'/'+worker; rows = {}
            for name in CASES:
                r, c = [unpack(x['solve']['currents_A'][name]) for x in (reference, current)]
                record = close(r, c)
                record['max_relative_nonzero'] = float(np.max(abs((c[r != 0]-r[r != 0])/r[r != 0]), initial=0))
                record['zero_reference_max_absolute'] = float(np.max(abs(c[r == 0]), initial=0))
                record['optimality'] = [x['optimality'][name] for x in (reference, current)]
                objectives = [x['optimality'][name]['production']['objective'] for x in (reference, current)]
                record['objective_absolute_difference'] = abs(objectives[1]-objectives[0])
                record['objective_comparison'] = close(*objectives)
                record['active_bounds_equal'] = all(reference['optimality'][name]['production'][k] == current['optimality'][name]['production'][k] for k in ('active_lower', 'active_upper'))
                rows[name] = record
            for name in ('row3', 'row4'):
                rows[name+'/recovery'] = close(reference['solve']['recovery'][name]['fractional_recovery'], current['solve']['recovery'][name]['fractional_recovery'])
                rows[name+'/differential'] = differential(reference['ratios'][name]['90'], current['ratios'][name]['90'])
                rows[name+'/interventions'] = ratio_interventions(load_evidence(captures[origin]/'inputs.json'), load_evidence(captures[origin]/'inputs.json'), reference, current, name)
            support_equal = support_decisions(load_evidence(workers[COHORTS[0]]/origin/'support.json')) == support_decisions(load_evidence(workers[worker]/origin/'support.json'))
            rows['support'] = dict(exact=support_equal, status='PASS' if support_equal else 'FAIL')
            for field, value in load_evidence(workers[COHORTS[0]]/origin/'fields.json').items():
                other = load_evidence(workers[worker]/origin/'fields.json')[field]
                r, c = unpack(value), unpack(other)
                rows['field/'+field] = close(r, c)
                if r.ndim >= 2 and r.shape[-1] == 3:
                    rows['field/'+field].update(component_max=np.max(abs(c-r), axis=tuple(range(r.ndim-1))).tolist(), vector_norm_max=float(np.max(np.linalg.norm(c-r, axis=-1))))
            records[key] = rows
            failures.extend(dict(comparison=key, quantity=k, record=v) for k, v in rows.items() if v.get('status') == 'FAIL')
    generated = {}; base = load_evidence(captures[COHORTS[0]]/'inputs.json')
    for origin in COHORTS[1:]:
        data = load_evidence(captures[origin]/'inputs.json')
        generated[origin] = dict(problem_exact=problem(base) == problem(data),
            arrays={k: close(unpack(v), unpack(data['arrays'][k])) for k, v in base['arrays'].items()},
            support_equal=support_decisions(load_evidence(captures[COHORTS[0]]/'support.json')) == support_decisions(load_evidence(captures[origin]/'support.json')),
            ratio_interventions={name: ratio_interventions(base, data,
                load_evidence(workers[COHORTS[0]]/COHORTS[0]/'result.json'),
                load_evidence(workers[COHORTS[0]]/origin/'result.json'), name) for name in ('row3', 'row4')})
        failures.extend(dict(comparison='generated/'+origin, quantity=k, record=v)
                        for k, v in generated[origin]['arrays'].items() if v['status'] == 'FAIL')
    reciprocal = {}
    for linux in COHORTS[1:]:
        cells = [load_evidence(workers[worker]/origin/'result.json')
                 for worker, origin in ((COHORTS[0], COHORTS[0]), (linux, COHORTS[0]),
                                        (COHORTS[0], linux), (linux, linux))]
        reciprocal[linux] = {name: reciprocal_effects(*[unpack(cell['solve']['currents_A'][name]) for cell in cells]) for name in CASES}
    return dict(comparisons=records, generated_inputs=generated, reciprocal=reciprocal, failures=failures,
                scientific_comparison='FAIL' if failures else 'PASS',
                hosted_artifact_authenticity='INCONCLUSIVE', production_acceptance='FAIL', overall='PARTIAL')


def main(argv=None):
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('command', choices=['historical', 'capture', 'local', 'replay', 'compare'])
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--inputs', type=Path)
    p.add_argument('--expected-head')
    args = p.parse_args(argv)
    out = args.output.resolve()
    if args.inputs and (out.is_relative_to(args.inputs.resolve()) or args.inputs.resolve().is_relative_to(out)):
        raise ValueError('Output must be disjoint from evidence')
    out.mkdir(parents=True, exist_ok=False)
    state = dict(diagnostic_status='FAIL', production_acceptance='FAIL', overall='PARTIAL')
    code = 2
    try:
        if sys.version_info[:2] != (3, 11):
            raise ValueError('Python 3.11 required')
        env = environment(); write(out/'environment.json', env)
        write(out/'source-provenance.json', runtime_sources())
        write(out/'source-sha256.json', dict(head=env['head'], sha256=source_fingerprints()))
        seals = {}
        if args.command == 'historical':
            result = historical(args.inputs)
            seals = {p.relative_to(args.inputs).as_posix(): sha(p) for p in args.inputs.rglob('*') if p.is_file()}
            write(out/'assessment.json', result)
            state['scope'] = 'Local integrity review; authenticity and causal attribution remain INCONCLUSIVE'
        elif args.command == 'capture':
            data = json.loads(json.dumps(capture(json.loads(Path('configs/phase2c_quick.json').read_text()))))
            validate_inputs(data); write(out/'inputs.json', data)
            seals['inputs.json'] = sha(out/'inputs.json')
            write(out/'problem-sha256.json', dict(sha256=fingerprint(problem(data))))
            write(out/'support.json', support_trace(data))
            # Perturbation is diagnostic only and retains each selected path.
            perturbed = copy.deepcopy(data)
            D = unpack(data['arrays']['D']); perturbed['arrays']['D'] = pack(np.nextafter(D, np.inf))
            write(out/'support-nextafter.json', support_trace(perturbed))
        elif args.command == 'local':
            cap = verified_capture(args.inputs)
            source_check(load_evidence(cap/'source-sha256.json'), load_evidence(out/'source-sha256.json'), env['head'])
            data = load_evidence(cap/'inputs.json')
            result = replay(data)
            require_replay(result)
            write(out/'result.json', result)
            seals['inputs.json'] = sha(cap/'inputs.json')
            fields = independent_field_checks(data)
            write(out/'independent-fields.json', fields)
            if fields['status'] != 'PASS' or any(v['coordinate']['status'] != 'PASS' or v['production']['constraint_violation'] != 0 or v['production']['kkt_max'] > 1e-12 for v in result['optimality'].values()):
                raise ValueError('Local independent checks incomplete/failed')
            state['scope'] = 'Single host only; reciprocal cross-platform design not executed'
        elif args.command == 'replay':
            errors = []
            for origin in COHORTS:
                sub = out/origin; sub.mkdir()
                try:
                    cap = verified_capture(args.inputs/('capture-'+origin))
                    source_check(load_evidence(cap/'source-sha256.json'), load_evidence(out/'source-sha256.json'), args.expected_head)
                    data = load_evidence(cap/'inputs.json'); validate_inputs(data)
                    seals[origin] = sha(cap/'inputs.json')
                    (sub/'inputs.json').write_bytes((cap/'inputs.json').read_bytes())
                    result = replay(data); write(sub/'result.json', result)
                    write(sub/'fields.json', field_replay(data))
                    fields = independent_field_checks(data); write(sub/'independent-fields.json', fields)
                    write(sub/'support.json', support_trace(data))
                    require_replay(result)
                    if fields['status'] != 'PASS':
                        raise ValueError('Independent field validation incomplete/failed')
                except Exception as exc:
                    errors.append(dict(origin=origin, error=repr(exc)))
                    write(sub/'error.json', errors[-1])
            if errors:
                state['failures'] = errors
                raise ValueError('One or more reciprocal replays failed; all origins attempted')
        else:
            result = comparisons(args.inputs, args.expected_head)
            seals = {p.relative_to(args.inputs).as_posix(): sha(p) for p in args.inputs.rglob('manifest.json')}
            write(out/'assessment.json', result)
            code = 1 if result['failures'] else 0
        if args.command != 'compare':
            code = 0
        write(out/'input-sha256.json', seals)
        state['diagnostic_status'] = 'PASS' if code == 0 else 'FAIL'
    except Exception as exc:
        state['error'] = repr(exc)
    finally:
        write(out/'status.json', state)
        if not (out/'assessment.json').exists():
            write(out/'assessment.json', state)
        if not (out/'input-sha256.json').exists():
            write(out/'input-sha256.json', {})
        manifest(out)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
