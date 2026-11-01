"""STEP 33 extensions to the explicitly reused STEP 32 reciprocal engine.

No production physics or acceptance settings are changed.
"""
import argparse
from decimal import Decimal, localcontext
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import lsq_linear
import phase2d_step32 as s
from stellarator_robust.model import Coil, field


def decimal_kkt(M, y, x, digits=90):
    """Evaluate box feasibility and KKT directly from residuals, not normal equations.

    This checks a supplied candidate; it is not an interval optimality certificate.
    Bound signs are determined exactly from binary64 candidate values.
    """
    s.optimality(M, y, x)  # dimension and finite-value validation
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: Decimal.from_float(float(v))
        rows = [list(map(cv, row)) for row in M]
        xx, yy = list(map(cv, x)), list(map(cv, y))
        residual = [sum((a*b for a, b in zip(row, xx)), Decimal(0))-v
                    for row, v in zip(rows, yy)]
        gradient = [sum((row[j]*r for row, r in zip(rows, residual)), Decimal(0))
                    for j in range(len(xx))]
        kkt = [min(g, Decimal(0)) if v == -1 else max(g, Decimal(0)) if v == 1 else g
               for v, g in zip(xx, gradient)]
        violation = max(Decimal(0), max(abs(v)-1 for v in xx))
        return dict(precision=digits, objective=str(sum((r*r for r in residual), Decimal(0))/2),
                    kkt_max=str(max(abs(g) for g in kkt)), constraint_violation=str(violation),
                    status='PASS' if violation == 0 and max(abs(g) for g in kkt) <= Decimal('1e-12') else 'FAIL')


_replay = s.replay
def replay(data):
    result = _replay(data)
    a = s.validate_inputs(data)
    checks = {}
    for name in s.CASES:
        M, y = a[name+'_M'], a[name+'_y']
        support = data['cases'][name].get('support', list(range(a['A'].shape[1])))
        x = s.unpack(result['solve']['currents_A'][name])[support]/data['config']['imax_A']
        baseline = lsq_linear(M, y, **data['cases'][name]['arguments'])
        require_candidate(M, y, baseline)
        # Both interventions retain the original box and production solver settings.
        perturbations = {}
        for block in ('M', 'y'):
            mm = np.nextafter(M, np.inf) if block == 'M' else M
            yy = np.nextafter(y, np.inf) if block == 'y' else y
            fit = lsq_linear(mm, yy, **data['cases'][name]['arguments'])
            require_candidate(mm, yy, fit)
            metrics = s.optimality(mm, yy, fit.x)
            delta = mm-M if block == 'M' else yy-y
            input_norm = float(np.linalg.norm(delta))
            current_norm = float(np.linalg.norm(fit.x-baseline.x))
            perturbations[block] = dict(input_delta=s.pack(delta),
                current_delta=s.pack(fit.x-baseline.x), input_delta_l2=input_norm,
                current_delta_l2=current_norm, absolute_l2_gain=current_norm/input_norm if input_norm else None,
                success=bool(fit.success), metrics=metrics,
                active_set_equal=all(metrics[k] == result['optimality'][name]['production'][k]
                                     for k in ('active_lower', 'active_upper')))
        singular = np.linalg.svd(M, compute_uv=False)
        checks[name] = dict(decimal={str(p): decimal_kkt(M, y, x, p) for p in (60, 90)},
            unperturbed_probe=dict(x=s.pack(baseline.x), success=bool(baseline.success),
                saved_current_roundtrip_difference=s.pack(baseline.x-x)),
            perturbations=perturbations, rank_threshold=float(max(M.shape)*np.finfo(float).eps*singular[0]),
            uniqueness='Full column rank implies strictly convex fixed-support objective' if
                np.linalg.matrix_rank(M) == M.shape[1] else 'Rank deficient; nonuniqueness not established',
            limitation='One-ULP probes are local sensitivity observations, not global bounds')
    result['step33'] = checks
    probes = a['points'][[0, len(a['points'])//3]]
    fields = {}
    independent_fields = s.independent_field_checks(data)
    for i, vertices in enumerate([*a['vertices'], a['error_vertices']]):
        current = 1500. if i == len(a['vertices']) else 1.
        reference = np.array(independent_fields['coils'][str(i)]['reference90'], float)
        actual = field(probes, Coil(vertices), current)
        delta = actual-reference
        fields[str(i)] = dict(component_max_T=np.max(abs(delta), axis=0).tolist(),
            vector_norm_max_T=float(np.max(np.linalg.norm(delta, axis=-1))),
            comparison=s.close(reference, actual))
    result['step33_fields'] = fields
    return result


def require_candidate(M, y, fit):
    """Reject invalid probe solutions independently of solver termination."""
    metrics = s.optimality(M, y, fit.x)
    for key in ('objective', 'constraint_violation', 'kkt_max'):
        s.numeric(metrics[key], ())
    if (fit.success is not True and not isinstance(fit.success, np.bool_)) or not fit.success:
        raise ValueError('Unsuccessful STEP 33 probe')
    if metrics['constraint_violation'] != 0 or metrics['kkt_max'] > 1e-12:
        raise ValueError('Invalid STEP 33 probe optimality')


def cohort_environment(cohort, env):
    expected_os = 'Windows' if cohort == 'windows-reference' else 'Linux'
    expected_numpy = '2.3.5' if cohort == 'linux-numpy-sensitivity' else '2.4.6'
    expected_scipy = '1.16.3' if cohort == 'linux-scipy-sensitivity' else '1.17.1'
    if (not env['platform'].startswith(expected_os) or env['numpy'] != expected_numpy
            or env['scipy'] != expected_scipy or not env['python'].startswith('3.11.')):
        raise ValueError('Cohort environment mismatch: '+cohort)


_comparisons = s.comparisons
def comparisons(root, expected):
    for stage in ('capture', 'replay'):
        for cohort in s.COHORTS:
            cohort_environment(cohort, s.load_evidence(root/(stage+'-'+cohort)/'environment.json'))
    result = _comparisons(root, expected)
    for worker in s.COHORTS:
        for origin in s.COHORTS:
            record = s.load_evidence(root/('replay-'+worker)/origin/'result.json')
            if set(record.get('step33', {})) != set(s.CASES):
                raise ValueError('Missing STEP 33 independent KKT evidence')
            data = s.load_evidence(root/('capture-'+origin)/'inputs.json')
            field_checks = record.get('step33_fields', {})
            if set(field_checks) != {str(i) for i in range(len(s.unpack(data['arrays']['vertices']))+1)}:
                raise ValueError('Missing STEP 33 component field evidence')
            for coil, check in field_checks.items():
                if check['comparison']['status'] != 'PASS':
                    result['failures'].append(dict(comparison=origin+'/'+worker,
                        quantity='field-reference/'+coil, record=check))
            for name in s.CASES:
                data = s.load_evidence(root/('capture-'+origin)/'inputs.json')
                arrays = s.validate_inputs(data)
                support = data['cases'][name].get('support', list(range(arrays['A'].shape[1])))
                x = s.unpack(record['solve']['currents_A'][name])[support]/data['config']['imax_A']
                for precision in ('60', '90'):
                    check = record['step33'][name]['decimal'][precision]
                    if check != decimal_kkt(arrays[name+'_M'], arrays[name+'_y'], x, int(precision)):
                        raise ValueError('Independent KKT record mismatch')
                    if check['status'] != 'PASS':
                        result['failures'].append(dict(comparison=origin+'/'+worker,
                            quantity=name+'/decimal-kkt/'+precision, record=check))
    result['scientific_comparison'] = 'FAIL' if result['failures'] else 'PASS'
    result['causal_root_cause'] = 'INCONCLUSIVE'
    return result


_require_replay = s.require_replay
def require_replay(result):
    _require_replay(result)
    checks = result.get('step33', {})
    failed = set(checks) != set(s.CASES)
    if not failed:
        for check in checks.values():
            if set(check['decimal']) != {'60', '90'} or set(check['perturbations']) != {'M', 'y'}:
                raise ValueError('Incomplete STEP 33 precision or perturbation evidence')
            for precision, value in check['decimal'].items():
                if value['precision'] != int(precision):
                    raise ValueError('Incorrect STEP 33 precision')
                for key in ('objective', 'kkt_max', 'constraint_violation'):
                    number = Decimal(value[key])
                    if not number.is_finite() or number < 0:
                        raise ValueError('Invalid STEP 33 Decimal diagnostic')
                if (Decimal(value['constraint_violation']) != 0 or
                        Decimal(value['kkt_max']) > Decimal('1e-12')):
                    failed = True
        failed |= any(v['status'] != 'PASS' for c in checks.values() for v in c['decimal'].values())
        failed |= any(v['success'] is not True for c in checks.values() for v in c['perturbations'].values())
        failed |= any(c['unperturbed_probe']['success'] is not True for c in checks.values())
    failed |= not result.get('step33_fields') or any(
        v['comparison']['status'] != 'PASS' for v in result.get('step33_fields', {}).values())
    if failed:
        # Preserve the complete failed candidate before the reused engine raises.
        if '--output' in sys.argv:
            out = Path(sys.argv[sys.argv.index('--output')+1])
            if out.is_dir():
                s.write(out/('failed-step33-'+s.fingerprint(result)+'.json'), result)
        raise ValueError('STEP 33 constrained or independent field diagnostics failed')


def assess(root, output):
    """Validate complete local STEP 32 bytes, then independently check saved candidates."""
    root = Path(root).resolve()
    inventory = s.load_evidence(root/'manifest.json')
    actual = {p.relative_to(root).as_posix(): s.sha(p) for p in root.rglob('*')
              if p.is_file() and p != root/'manifest.json'}
    if actual != inventory:
        raise ValueError('Incomplete or changed STEP 32 host evidence')
    cap = s.verified_capture(root/'capture')
    local = s.verified(root/'local')
    data = s.load_evidence(cap/'inputs.json'); arrays = s.validate_inputs(data)
    record = s.load_evidence(local/'result.json')
    s.validate_replay(record, data, arrays)
    if s.load_evidence(local/'input-sha256.json')['inputs.json'] != s.sha(cap/'inputs.json'):
        raise ValueError('Local worker input mismatch')
    output.mkdir(parents=True, exist_ok=False)
    checks = {}
    for name in s.CASES:
        support = data['cases'][name].get('support', list(range(arrays['A'].shape[1])))
        x = s.unpack(record['solve']['currents_A'][name])[support]/data['config']['imax_A']
        checks[name] = decimal_kkt(arrays[name+'_M'], arrays[name+'_y'], x)
    s.write(output/'assessment.json', dict(input_integrity='PASS', candidate_kkt=checks,
        evidence_manifest_sha256=s.sha(root/'manifest.json'), input_sha256=s.sha(cap/'inputs.json'),
        recorded_sources=s.load_evidence(cap/'source-sha256.json'),
        hosted_authenticity='INCONCLUSIVE', four_way='INCONCLUSIVE', root_cause='INCONCLUSIVE',
        production_acceptance='FAIL', overall='PARTIAL'))
    s.manifest(output)
    return 1 if any(v['status'] == 'FAIL' for v in checks.values()) else 0


def main():
    s.replay = replay; s.comparisons = comparisons
    # STEP 32 assessment intentionally validates its original schema separately.
    if len(sys.argv) > 1 and sys.argv[1] != 'assess':
        s.require_replay = require_replay
    if len(sys.argv) > 1 and sys.argv[1] == 'assess':
        p = argparse.ArgumentParser(); p.add_argument('command'); p.add_argument('--inputs', type=Path, required=True)
        p.add_argument('--output', type=Path, required=True); args = p.parse_args()
        if args.output.resolve().is_relative_to(args.inputs.resolve()) or args.inputs.resolve().is_relative_to(args.output.resolve()):
            raise ValueError('Evidence and output must be disjoint')
        return assess(args.inputs, args.output)
    return s.main()


if __name__ == '__main__':
    raise SystemExit(main())
