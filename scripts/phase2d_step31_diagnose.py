"""Read-only Step 31 diagnostics. Completion never implies scientific acceptance."""
import argparse
from decimal import Decimal, localcontext
import itertools
import math
from pathlib import Path
import subprocess

import numpy as np
from stellarator_robust.upstream_attribution import (
    load_evidence, sha, unpack, write, manifest, validate_inputs, validate_solve,
    comparison_record, close, decimal_field, numeric, WORKER_FILES)

COMMIT = '11c2b1347c7b5359bec0a56e95cc2aa46f03660c'
WORKERS = ('windows-reference', 'linux-reference', 'linux-numpy-sensitivity',
           'linux-scipy-sensitivity')
CASES = ('dense', 'row3', 'row4')
RTOL, ATOL = 1e-11, 1e-13


def inventory(root):
    """Relocate the supplied absolute Windows inventory without trusting its prefix."""
    records = load_evidence(root/'source-hashes.json')
    found = {}
    for name, digest in records.items():
        normalized = name.replace('\\', '/')
        if '/raw/' not in normalized:
            raise ValueError('Inventory entry outside raw evidence')
        relative = 'raw/'+normalized.split('/raw/', 1)[1]
        p = (root/relative).resolve()
        if not p.is_relative_to((root/'raw').resolve()) or p.is_symlink():
            raise ValueError('Unsafe inventory path')
        if relative in found or sha(p) != digest.lower():
            raise ValueError('Duplicate/modified evidence: '+relative)
        found[relative] = digest.lower()
    actual = {p.relative_to(root).as_posix() for p in (root/'raw').rglob('*') if p.is_file()}
    if not found or actual != set(found):
        raise ValueError('Incomplete evidence inventory')
    return found


def verify_manifests(root):
    result = {}
    for m in sorted((root/'raw').rglob('manifest.json')):
        entries = load_evidence(m)
        if not entries:
            raise ValueError('Empty manifest')
        if m.parent.name == 'upstream-worker':
            actual = {p.relative_to(m.parent).as_posix() for p in m.parent.rglob('*') if p.is_file()}
            if set(entries) != WORKER_FILES or actual != WORKER_FILES | {'manifest.json'}:
                raise ValueError('Incomplete worker manifest inventory')
        for name, digest in entries.items():
            p = (m.parent/name).resolve()
            if not p.is_relative_to(m.parent.resolve()) or p.is_symlink() or sha(p) != digest:
                raise ValueError('Manifest mismatch: '+str(p))
        result[m.relative_to(root).as_posix()] = len(entries)
    if not result:
        raise ValueError('Missing manifests')
    return result


def compare_array(a, b):
    x, y = unpack(a), unpack(b)
    if x.shape != y.shape:
        raise ValueError('Array shape mismatch')
    return dict(byte_equal=a == b, numerical_exact=bool(np.array_equal(x, y)),
                tolerance=close(x, y))


def verify_seal(path, expected):
    if not expected or sha(path) != expected:
        raise ValueError('Incorrect input fingerprint')


def check_classification(status, records):
    if status not in ('PASS', 'FAIL') or (status == 'PASS' and any(r['status'] == 'FAIL' for r in records)):
        raise ValueError('Incorrect PASS classification')


def scalar_comparison(reference, current):
    numeric(reference, ()); numeric(current, ())
    error = abs(current-reference)
    threshold = ATOL+RTOL*abs(current)
    with localcontext() as ctx:
        ctx.prec = 90
        cv = Decimal.from_float
        exact_error = abs(cv(float(current))-cv(float(reference)))
        exact_bound = cv(ATOL)+cv(RTOL)*abs(cv(float(current)))
        exact = dict(error=str(exact_error), threshold=str(exact_bound),
                     exceedance=str(exact_error-exact_bound))
    return dict(reference=reference, current=current, absolute_error=error,
                threshold=threshold, exceedance=error-threshold,
                status='PASS' if error <= threshold else 'FAIL', binary64_exact_decimal=exact)


def ratio(B, L, P):
    denominator = L-B
    return (L-P)/denominator if abs(denominator) > Decimal('1e-15') else None


def decimal_metric(arrays, currents, failed, digits=90):
    """Independent direct RMS; every source binary64 is converted exactly."""
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: Decimal.from_float(float(v))
        A = [[cv(v) for v in row] for row in arrays['fine_A']]
        b = [cv(v) for v in arrays['fine_b']]
        w = [cv(v) for v in arrays['fine_weights']]
        frozen = currents['dense'].copy(); frozen[failed] = 0
        rms = []
        for x in (currents['dense'], frozen, currents['recovered']):
            xx = [cv(v) for v in x]
            residual = [bb+sum((v*j for v, j in zip(row, xx)), Decimal(0)) for row, bb in zip(A, b)]
            rms.append(sum((ww*r*r for ww, r in zip(w, residual)), Decimal(0)).sqrt())
        B, L, P = rms
        R = ratio(B, L, P)
        return dict(rms_T=[str(v) for v in rms], ratio=None if R is None else str(R),
                    denominator_T=str(L-B), numerator_T=str(L-P),
                    denominator_condition=None if L == B else str((abs(L)+abs(B))/abs(L-B)),
                    numerator_condition=None if L == P else str((abs(L)+abs(P))/abs(L-P)))


def compensated_metric(a, currents, failed):
    frozen = currents['dense'].copy(); frozen[failed] = 0
    rms = []
    for x in (currents['dense'], frozen, currents['recovered']):
        r = [math.fsum([float(bb), math.fsum(float(v)*float(j) for v, j in zip(row, x))])
             for row, bb in zip(a['fine_A'], a['fine_b'])]
        rms.append(math.sqrt(math.fsum(float(w)*v*v for w, v in zip(a['fine_weights'], r))))
    B, L, P = rms
    return dict(rms_T=rms, ratio=(L-P)/(L-B) if abs(L-B) > 1e-15 else None)


def differential(left, right):
    with localcontext() as ctx:
        ctx.prec = 90
        B, L, P = map(Decimal, left['rms_T'])
        b, l, p = map(Decimal, right['rms_T'])
        R = ratio(B, L, P)
        if R is None or right['ratio'] is None:
            return dict(status='INCONCLUSIVE', reason='Original denominator guard')
        terms = [(1-R)*(l-L)/(L-B), -(p-P)/(L-B), R*(b-B)/(L-B)]
        observed = Decimal(right['ratio'])-R
        return dict(dB=str(b-B), dL=str(l-L), dP=str(p-P),
                    terms_L_P_B=[str(v) for v in terms], linear_prediction=str(sum(terms)),
                    observed=str(observed), nonlinear_remainder=str(observed-sum(terms)))


def solver_metrics(data, result):
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    validate_solve(result, data, a)  # Includes independent 60/90-digit reference validation.
    out = {}
    for name in CASES:
        d = result['diagnostics'][name]
        support = data['cases'][name].get('support', list(range(a['A'].shape[1])))
        x = unpack(result['currents_A'][name])[support]/data['config']['imax_A']
        M, y = a[name+'_M'], a[name+'_y']
        r = M@x-y; g = M.T@r
        # Box KKT: free gradient zero, lower gradient >=0, upper gradient <=0.
        violation = np.where(x <= -1, np.minimum(g, 0), np.where(x >= 1, np.maximum(g, 0), g))
        out[name] = dict(termination={k: d[k] for k in ('success', 'status', 'message', 'nit', 'optimality')},
                         recorded_objective=d['cost'], objective=float(r@r/2),
                         residual_norm=float(np.linalg.norm(r)), kkt_max=float(np.max(abs(violation))),
                         projected_gradient=float(np.max(abs(x-np.clip(x-g, -1, 1)))),
                         bound_margin=float(np.min(1-abs(x))), active_mask=d['active_mask'],
                         condition=d['condition'], rank=d['rank'], reference_check=d['reference_check'])
    return out


def failure_inventory(root):
    """Retain each original report and path; group only duplicate quantity labels."""
    out = {}
    base = root/'raw/upstream-comparisons'
    for cohort in ('reference', 'numpy', 'scipy'):
        p = base/('upstream-production-'+cohort+'.json')
        production = load_evidence(p)
        if production.get('status') not in ('PASS', 'FAIL'):
            raise ValueError('Missing production comparison classification')
        frozen = load_evidence(base/('upstream-comparison-'+cohort)/'comparisons.json')
        for record in frozen.values():
            comparison_record(record)
        state = load_evidence(base/('upstream-comparison-'+cohort)/'status.json')
        check_classification(state['status'], frozen.values())
        failures = [dict(path=v['path'], **scalar_comparison(v['reference'], v['current']))
                    for v in production['failures']]
        check_classification(production['status'], failures)
        out[cohort] = dict(production=production, frozen=frozen, frozen_state=state, failure_thresholds=failures,
                           duplicate_rule='fractional_recovery and recovery_evidence/fractional_recovery at same fault row are one quantity')
    return out


def diagnose(root):
    sources = inventory(root)
    expected_artifacts = {'dependency-seal', 'upstream-sealed', 'upstream-comparisons'} | {
        'upstream-'+w for w in WORKERS}
    if {p.name for p in (root/'raw').iterdir() if p.is_dir()} != expected_artifacts:
        raise ValueError('Incomplete/unexpected seven-artifact bundle')
    manifests = verify_manifests(root)
    raw = root/'raw'
    seal = load_evidence(raw/'upstream-sealed/status.json')['input_sha256']
    verify_seal(raw/'upstream-sealed/inputs.json', seal)
    workers, inputs, solves = {}, {}, {}
    for w in WORKERS:
        base = raw/('upstream-'+w)/'upstream-worker'
        state = load_evidence(base/'status.json')
        if state.get('input_sha256') != seal or sha(base/'sealed-inputs.json') != seal:
            raise ValueError('Incorrect worker input fingerprint')
        env = load_evidence(base/'environment.json')
        if not isinstance(env.get('head'), str) or len(env['head']) != 40:
            raise ValueError('Missing worker source commit')
        # Compare historical source to the specified Git object, not newly added files.
        source_differences = []
        for name, digest in load_evidence(base/'source_sha256.json').items():
            import hashlib
            content = subprocess.check_output(['git', 'show', COMMIT+':'+name])
            if hashlib.sha256(content).hexdigest() != digest:
                source_differences.append(name)
        inputs[w] = {stage: load_evidence(base/file) for stage, file in
                     [('frozen', 'sealed-inputs.json'), ('regenerated', 'regenerated-inputs.json')]}
        solves[w] = {stage: load_evidence(base/(stage+'-solve.json')) for stage in ('frozen', 'regenerated')}
        metrics = {}
        solver_gates = []
        for stage, data in inputs[w].items():
            validate_inputs(data)
            metrics[stage] = solver_metrics(data, solves[w][stage])
            solver_gates.extend(dict(status='PASS' if v['reference_check']['status'] == 'PASS'
                and v['reference_check']['solver']['status'] == 'PASS' and v['termination']['success']
                else 'FAIL') for v in metrics[stage].values())
        independent = load_evidence(base/'independent-fields.json')
        a = {k: unpack(v) for k, v in inputs[w]['frozen']['arrays'].items()}
        fields = load_evidence(base/'frozen-fields.json')
        points = a['points'][[0, len(a['points'])//3]]
        if not np.array_equal(unpack(independent['points']), points):
            raise ValueError('Independent reference coordinates mismatch')
        if set(independent['coils']) != {str(i) for i in range(len(a['vertices'])+1)}:
            raise ValueError('Missing independent component references')
        for i, vertices in enumerate([*a['vertices'], a['error_vertices']]):
            probe = independent['coils'][str(i)]
            current = 1500. if i == len(a['vertices']) else 1.
            for digits in (60, 90):
                if probe['reference'+str(digits)] != decimal_field(points, vertices, current, digits):
                    raise ValueError('Independent component reference mismatch')
            high = np.array(probe['reference90'], float)
            actual = (unpack(fields['unit_coils_Bxyz'])[i] if i < len(a['vertices'])
                      else unpack(fields['original_Bxyz']))[[0, len(a['points'])//3]]
            comparison_record(probe['production'], close(high, actual))
            comparison_record(probe['precision_convergence'], close(np.array(probe['reference60'], float), high))
        check_classification(state['status'], [*solver_gates, dict(status=independent['status'])])
        workers[w] = dict(status=state, environment=env, solver=metrics,
                          independent_fields=independent,
                          provenance=dict(supplied_commit=COMMIT, recorded_commit=env['head'],
                              commit_equal=env['head'] == COMMIT,
                              fingerprints_differing_from_supplied_commit=source_differences,
                              archive_authentication='INCONCLUSIVE: local integrity does not authenticate run identity'))
    comparisons = {}
    ref = WORKERS[0]
    for w in WORKERS[1:]:
        record = {}
        for stage in ('frozen', 'regenerated'):
            left, right = inputs[ref][stage], inputs[w][stage]
            record[stage] = dict(arrays={k: compare_array(v, right['arrays'][k]) for k, v in left['arrays'].items()},
                config_exact=left['config'] == right['config'],
                solver_and_support={n: {k: left['cases'][n].get(k) == right['cases'][n].get(k)
                    for k in ('arguments', 'support', 'failed', 'implicit_method', 'implicit_lsq_solver')}
                    for n in CASES},
                currents={n: compare_array(solves[ref][stage]['currents_A'][n], solves[w][stage]['currents_A'][n]) for n in CASES},
                recovery={n: scalar_comparison(solves[ref][stage]['recovery'][n]['fractional_recovery'],
                    solves[w][stage]['recovery'][n]['fractional_recovery']) for n in ('row3', 'row4')})
        paths = [raw/('upstream-'+v)/'upstream-worker/frozen-fields.json' for v in (ref, w)]
        l, r = map(load_evidence, paths)
        record['fixed_current_fields'] = {k: {axis: close(unpack(l[k])[..., j], unpack(r[k])[..., j])
            for j, axis in enumerate(('Bx', 'By', 'Bz'))} for k in l if k != 'projected_A'}
        record['interventions'] = {}
        for stage in ('frozen', 'regenerated'):
            for name in ('row3', 'row4'):
                experiments = {}
                for model, current in itertools.product((ref, w), repeat=2):
                    data = inputs[model][stage]
                    a = {k: unpack(v) for k, v in data['arrays'].items()}
                    currents = dict(dense=unpack(solves[current][stage]['currents_A']['dense']),
                                    recovered=unpack(solves[current][stage]['currents_A'][name]))
                    failed = data['cases'][name]['failed']
                    high = decimal_metric(a, currents, failed, 90)
                    low = decimal_metric(a, currents, failed, 60)
                    with localcontext() as ctx:
                        ctx.prec = 90
                        precision_delta = (None if high['ratio'] is None else
                            str(Decimal(high['ratio'])-Decimal(low['ratio'])))
                    experiments[model+'|'+current] = dict(decimal90=high, decimal60=low,
                        precision_delta=precision_delta,
                        compensated=compensated_metric(a, currents, failed))
                    if model == current:
                        saved = solves[model][stage]['recovery'][name]['fractional_recovery']
                        with localcontext() as ctx:
                            ctx.prec = 90
                            experiments[model+'|'+current]['saved_float64_minus_decimal'] = (
                                None if high['ratio'] is None else str(Decimal.from_float(saved)-Decimal(high['ratio'])))
                ll = experiments[ref+'|'+ref]['decimal90']; rr = experiments[w+'|'+w]['decimal90']
                with localcontext() as ctx:
                    ctx.prec = 90
                    values = [Decimal(experiments[m+'|'+c]['decimal90']['ratio'])
                              for m, c in ((ref, ref), (ref, w), (w, ref), (w, w))]
                    v00, v01, v10, v11 = values
                    effects = dict(current_on_reference=str(v01-v00), model_on_reference=str(v10-v00),
                                   interaction=str(v11-v10-v01+v00), total=str(v11-v00))
                    effects['current_fraction_of_total'] = None if v11 == v00 else str((v01-v00)/(v11-v00))
                record['interventions'][stage+'/'+name] = dict(experiments=experiments,
                    differential=differential(ll, rr), effects=effects)
        comparisons[w] = record
    return dict(source_run_id='41231422708', source_commit=COMMIT, seal_sha256=seal,
                diagnostic_implementation_sha256={str(p).replace('\\', '/'): sha(p) for p in
                    (Path(__file__), Path('src/stellarator_robust/upstream_attribution.py'),
                     Path('src/stellarator_robust/fault_metrics.py'))},
                manifest_checks=manifests, workers=workers, comparisons=comparisons,
                original_comparisons=failure_inventory(root),
                limitation='Reciprocal cross-platform solves of each regenerated matrix are unavailable; no unique library/BLAS cause established'), sources


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    root, out = args.evidence_root.resolve(), args.output.resolve()
    if out.is_relative_to(root) or root.is_relative_to(out):
        raise ValueError('Output must be disjoint from source evidence')
    out.mkdir(parents=True, exist_ok=False)
    state = dict(diagnostic_status='FAIL', scientific_status='PARTIAL', production_acceptance='UNRESOLVED')
    code = 2
    try:
        analysis, sources = diagnose(root)
        write(out/'source-sha256.json', sources)
        write(out/'analysis.json', analysis)
        state.update(diagnostic_status='COMPLETE', production_acceptance='FAIL')
        code = 1  # Original scientific failures remain failures.
    except Exception as exc:
        write(out/'analysis.json', dict(error=repr(exc), numerical_analysis_executed=False))
        write(out/'source-sha256.json', {p.relative_to(root).as_posix(): sha(p)
              for p in root.rglob('*') if p.is_file()})
        state['error'] = repr(exc)
    finally:
        write(out/'status.json', state)
        manifest(out)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
