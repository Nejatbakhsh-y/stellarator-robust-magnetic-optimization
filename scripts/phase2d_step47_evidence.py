"""STEP47 read-only evidence assessment; 2 incomplete, 1 retained science FAIL.

No production numerical helpers. STEP46 scalar Decimal Householder, residual,
field-matrix and quotient implementations are explicitly reused as independent
diagnostics. Original ZIP authentication is a separate, never inferred claim.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
SOURCE = '4177d52f1ac68f869147c2e3e02e1f8b876546d0'
EVIDENCE = 'results/phase2d/step47-20261102-100432-7e05bcf1'
CASES = ('dense', 'row3', 'row4')
RTOL, ATOL, GUARD = D('1e-11'), D('1e-13'), D('1e-15')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('Duplicate JSON key: '+k)
            out[k] = v
        return out
    value = json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                       parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    def finite(v):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError('Nonfinite JSON')
        if isinstance(v, dict):
            for x in v.values():
                finite(x)
        if isinstance(v, list):
            for x in v:
                finite(x)
    finite(value)
    return value


def safe(root, name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Unsafe evidence path')
    root = Path(root).resolve()
    target = root/name
    if (Path(name).is_absolute() or '..' in Path(name).parts or
            target.is_symlink() or not target.resolve().is_relative_to(root)):
        raise ValueError('Unsafe evidence path')
    return target


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file()}


def seals(root):
    """Authenticate every available manifest target, including numerical results.

    Input inventories in comparison bundles reference absent relative files;
    these remain missing, never silently rebound to a similarly named artifact.
    """
    records = []
    for p in sorted(root.rglob('*.json')):
        if p.name not in ('manifest.json', 'input-sha256.json', 'output-manifest.json'):
            continue
        inventory = load(p)
        if p.name == 'output-manifest.json':
            if inventory.get('schema') != 'step45-noncircular-v1':
                raise ValueError('Unknown output manifest schema')
            inventory = inventory['outputs']
        for name, expected in inventory.items():
            if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected):
                raise ValueError('Malformed digest inventory: '+str(p))
            target = safe(p.parent, name)
            actual = sha(target) if target.is_file() else None
            records.append(dict(inventory=str(p.relative_to(root)), file=name,
                                expected=expected, actual=actual,
                                status='MISSING' if actual is None else
                                'MATCH' if actual == expected else 'MISMATCH'))
    return records


def source_check(record, repo, expected=SOURCE):
    if record.get('head') != expected or not record.get('sha256'):
        raise ValueError('Exact source-commit identity mismatch')
    for name, digest in record['sha256'].items():
        safe(repo, name)
        if not re.fullmatch('[a-f0-9]{64}', digest):
            raise ValueError('Invalid source digest')
        blob = subprocess.run(['git', 'show', expected+':'+name], cwd=repo, capture_output=True)
        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:
            raise ValueError('Git source blob mismatch: '+name)
    return dict(head=expected, verified_git_blobs=len(record['sha256']))


def unpack(value):
    import numpy as np
    if set(value) != {'shape', 'binary64_le'}:
        raise ValueError('Array schema')
    shape, raw = value['shape'], value['binary64_le']
    if (not isinstance(shape, list) or any(type(v) is not int or v < 1 for v in shape)
            or not isinstance(raw, str) or not re.fullmatch('[0-9a-f]*', raw)
            or len(raw) != 16*math.prod(shape)):
        raise ValueError('Array bytes/dimensions')
    a = np.frombuffer(bytes.fromhex(raw), dtype='<f8').reshape(shape).copy()
    if not np.isfinite(a).all():
        raise ValueError('Nonfinite array')
    return a


def reconstruct(data, repo):
    import numpy as np
    if data['schema'] != 'production-upstream-v1' or set(data['cases']) != set(CASES):
        raise ValueError('Problem schema')
    config = load(repo/'configs/phase2c_quick.json')
    if data['config'] != config or config['segments'] != 512:
        raise ValueError('Original geometry/configuration mismatch')
    a = {k: unpack(v) for k, v in data['arrays'].items()}
    if not np.array_equal(a['D'], a['A']*config['imax_A']/config['bref_T']):
        raise ValueError('D scaling')
    if not np.array_equal(a['d'], a['b']/config['bref_T']):
        raise ValueError('d scaling')
    for key in ('weights', 'fine_weights'):
        w = a[key]
        if w.ndim != 1 or np.any(w < 0) or abs(float(w.sum())-1) > 1e-13+1e-11:
            raise ValueError('Weights')
    active = np.flatnonzero(abs(a['dense_x'])*config['imax_A'] > config['active_threshold_A'])
    for case in CASES:
        spec = data['cases'][case]
        if (spec['arguments'] != dict(bounds=[-1, 1], tol=1e-12, max_iter=1000)
                or spec['implicit_method'] != 'trf' or spec['implicit_lsq_solver'] != 'exact'):
            raise ValueError('Original solver settings mismatch')
        support = spec.get('support', list(range(24)))
        expected = list(range(24))
        if case != 'dense':
            failed = int(active[int(case[-1])])
            if spec['failed'] != failed or failed != {'row3': 3, 'row4': 6}[case]:
                raise ValueError('Fault row identity mismatch')
            expected.remove(failed)
        if support != expected:
            raise ValueError('Support identity mismatch')
        M = np.vstack((np.sqrt(a['weights'])[:, None]*a['D'][:, support],
                       np.sqrt(config['ridge'])*np.eye(len(support))))
        y = np.r_[-np.sqrt(a['weights'])*a['d'], np.zeros(len(support))]
        if not np.array_equal(M, a[case+'_M']) or not np.array_equal(y, a[case+'_y']):
            raise ValueError('Exact solver matrix reconstruction mismatch')
        x = a[case+'_x']
        if x.shape != (24,) or np.any(abs(x) > 1) or any(x[j] != 0 for j in set(range(24))-set(support)):
            raise ValueError('Physical current feasibility')
    return a


def polygon_field(point, vertices, current=1, digits=90):
    """Independent scalar exact straight-segment Biot-Savart equation.

    Exact binary64 input coordinates, original 1e-4 m wire clearance rejection.
    No geometry regeneration, smoothing or altered physical equations.
    """
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: D.from_float(float(v))
        p = list(map(cv, point))
        vv = [list(map(cv, v)) for v in vertices]
        out = [D(0)]*3
        dot = lambda u, v: sum((x*y for x, y in zip(u, v)), D(0))
        for a, b in zip(vv, vv[1:]+vv[:1]):
            u, v = [[x-y for x, y in zip(p, z)] for z in (a, b)]
            edge = [y-x for x, y in zip(a, b)]
            length2 = dot(edge, edge)
            if length2 == 0:
                raise ValueError('Degenerate segment')
            t = max(D(0), min(D(1), dot(u, edge)/length2))
            offset = [x-t*y for x, y in zip(u, edge)]
            if dot(offset, offset) <= D('1e-8'):
                raise ValueError('Original wire clearance')
            n1, n2 = dot(u, u).sqrt(), dot(v, v).sqrt()
            den = n1*n2*(n1*n2+dot(u, v))
            cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            if den > 0:
                out = [s+c*(n1+n2)/den for s, c in zip(out, cross)]
        return [v*D('1e-7')*cv(current) for v in out]


def numerical(path, repo):
    import numpy as np
    import scipy
    from scipy.optimize import lsq_linear
    import phase2d_step46_independent as scalar
    data = load(path/'inputs.json')
    if load(path/'input-sha256.json') != {'inputs.json': sha(path/'inputs.json')}:
        raise ValueError('Input authentication mismatch')
    problem = dict(config=data['config'], cases={k: dict(M=data['arrays'][k+'_M'],
        y=data['arrays'][k+'_y'], arguments=v['arguments'], method=v['implicit_method'],
        lsq_solver=v['implicit_lsq_solver'], support=v.get('support'), failed=v.get('failed'))
        for k, v in data['cases'].items()})
    digest = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(',', ':'),
                                       allow_nan=False).encode()).hexdigest()
    if load(path/'problem-sha256.json') != {'sha256': digest}:
        raise ValueError('Original problem SHA256 mismatch')
    source_check(load(path/'source-sha256.json'), repo)
    a = reconstruct(data, repo)
    saved, fresh, solved = {}, {}, {}
    for case in CASES:
        M, y = a[case+'_M'], a[case+'_y']
        support = data['cases'][case].get('support', list(range(24)))
        fit = lsq_linear(M, y, method='trf', lsq_solver='exact', tol=1e-12,
                         max_iter=1000, bounds=(-1, 1))
        fresh[case] = np.zeros(24)
        fresh[case][support] = fit.x*3000
        saved[case] = a[case+'_x']*3000
        solved[case] = dict(success=bool(fit.success), currents_A=fresh[case].tolist(),
            saved_currents_A=saved[case].tolist(),
            saved_certificate=scalar.certificate(M.tolist(), y.tolist(), a[case+'_x'][support].tolist()),
            fresh_certificate=scalar.certificate(M.tolist(), y.tolist(), fit.x.tolist()),
            decimal_QR={str(d): scalar.reference(M.tolist(), y.tolist(), d) for d in (60, 90)},
            M_sha256=hashlib.sha256(M.astype('<f8').tobytes()).hexdigest(),
            y_sha256=hashlib.sha256(y.astype('<f8').tobytes()).hexdigest())
    recovery = {}
    A, b, w = [a[k].tolist() for k in ('fine_A', 'fine_b', 'fine_weights')]
    for case in CASES[1:]:
        recovery[case] = scalar.intervention(A, b, w, saved['dense'], saved[case],
                                            fresh['dense'], fresh[case], data['cases'][case]['failed'])
    probes = []
    for grid in ('', 'fine_'):
        for i in (0, len(a[grid+'points'])//3):
            for j, vertices in enumerate([*a['vertices'], a['error_vertices']]):
                fields = {str(d): polygon_field(a[grid+'points'][i], vertices, 1500 if j == 24 else 1, d)
                          for d in (60, 90)}
                normal = a[grid+'normals'][i]
                with localcontext() as ctx:
                    ctx.prec = 90
                    projected = sum((v*D.from_float(float(n)) for v, n in zip(fields['90'], normal)), D(0))
                expected = a[grid+'b'][i] if j == 24 else a[grid+'A'][i, j]
                probes.append(dict(grid=grid or 'training', point=i, coil=j,
                    reference60=list(map(str, fields['60'])), reference90=list(map(str, fields['90'])),
                    projected_T=str(projected), captured_T=float(expected),
                    agrees=scalar.agrees(projected, float(expected))))
    return dict(input_sha256=sha(path/'inputs.json'), solver=solved, recovery=recovery,
                environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__),
                independent_geometry_probes=probes,
                scope='Two points on each grid, all 25 polygons; not full-grid geometry validation')


def cross_capture(left, right, repo):
    """Separate current interventions from field-matrix interventions.

    Both captures must already have passed source, seal and matrix validation.
    This does not substitute a new quotient for an original saved result.
    """
    import numpy as np
    import phase2d_step46_independent as scalar
    ldata, rdata = load(left/'inputs.json'), load(right/'inputs.json')
    la, ra = reconstruct(ldata, repo), reconstruct(rdata, repo)
    out = dict(current_vectors={}, recovery={},
               original_saved_result_binding='INCOMPLETE: original result records must be compared separately')
    for case in CASES:
        x, y = [a[case+'_x']*3000 for a in (la, ra)]
        out['current_vectors'][case] = dict(max_absolute_A=float(np.max(abs(x-y))),
            agrees=bool(np.all(abs(x-y) <= 1e-13+1e-11*abs(x))),
            identical_M=bool(np.array_equal(la[case+'_M'], ra[case+'_M'])),
            identical_y=bool(np.array_equal(la[case+'_y'], ra[case+'_y'])))
    for case in CASES[1:]:
        failed = ldata['cases'][case]['failed']
        dense, recovered = la['dense_x']*3000, la[case+'_x']*3000
        A, b, w = [la[k].tolist() for k in ('fine_A', 'fine_b', 'fine_weights')]
        out['recovery'][case] = scalar.intervention(A, b, w, dense, recovered,
            ra['dense_x']*3000, ra[case+'_x']*3000, failed)
        fixed_left = scalar.metric(A, b, w, dense, recovered, failed)[0]
        fixed_right = scalar.metric(*[ra[k].tolist() for k in ('fine_A', 'fine_b', 'fine_weights')],
                                    dense, recovered, failed)[0]
        with localcontext() as ctx:
            ctx.prec = 90
            out['recovery'][case]['fixed_current_matrix_delta_R'] = str(
                D(fixed_right['ratio'])-D(fixed_left['ratio']))
    return out


def verdict(blockers):
    return dict(diagnostic_status='INCOMPLETE', source_authentication='INCOMPLETE',
        artifact_authentication='INCOMPLETE', solver_reproducibility='INCOMPLETE',
        field_validation='INCOMPLETE', recovery_ratio_validation='INCOMPLETE',
        numerical_root_cause='INCONCLUSIVE', scientific_comparison='FAIL',
        production_acceptance='FAIL', overall_scientific_status='INCOMPLETE',
        remaining_blockers=blockers)


def main(argv=None):
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--evidence', type=Path, default=Path(EVIDENCE))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--numerical', action='store_true')
    args = p.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    evidence, output = args.evidence.resolve(), args.output.resolve()
    allowed = (repo/EVIDENCE).resolve()
    if (evidence != allowed or not output.is_relative_to(allowed) or output == allowed
            or output.exists() or output.is_symlink()):
        raise ValueError('Require specified evidence directory and fresh child output')
    runs = sorted(evidence.glob('run-*'))
    if any(output.is_relative_to(r) for r in runs):
        raise ValueError('Output overlaps original evidence')
    before = {r.name: snapshot(r) for r in runs}
    result = verdict(['Original ZIP bytes unavailable: extracted seals do not prove ZIP authenticity',
                      'Full original scientific acceptance and final-source README gates remain required',
                      'Unique numerical implementation root cause not established'])
    result['source_commit'] = SOURCE
    result['runs'], result['seals'], result['sources'], result['numerical'] = [], [], [], {}
    errors = []
    authenticated = []
    for run in runs:
        try:
            identity = load(run/'run.json')
            if identity['head_sha'] != SOURCE:
                raise ValueError('Run source mismatch')
            result['runs'].append({k: identity.get(k) for k in ('id', 'head_sha', 'run_attempt', 'conclusion')})
            result['seals'].extend(dict(run=run.name, **r) for r in seals(run))
            for capture in sorted([*run.rglob('source-sha256.json'), *run.rglob('source_sha256.json')]):
                try:
                    rec = load(capture)
                    if capture.name == 'source_sha256.json':
                        rec = dict(head=load(capture.parent/'environment.json')['head'], sha256=rec)
                    # The upstream bundle contains older evidence. Bind its own
                    # source without relabelling it as the requested experiment.
                    historical = run.name == 'run-41465460206'
                    expected = '8d87244eb07b7ff6e811596728441aee8b2fd618' if historical else SOURCE
                    result['sources'].append(dict(file=str(capture.relative_to(evidence)),
                        scope='historical' if historical else 'requested_source',
                        **source_check(rec, repo, expected)))
                except (ValueError, KeyError, FileNotFoundError) as exc:
                    errors.append(str(capture.relative_to(evidence))+': '+str(exc))
            if args.numerical:
                for capture in sorted(run.rglob('inputs.json')):
                    if (capture.parent/'input-sha256.json').is_file() and (capture.parent/'problem-sha256.json').is_file():
                        key = str(capture.parent.relative_to(evidence))
                        try:
                            result['numerical'][key] = numerical(capture.parent, repo)
                            authenticated.append(capture.parent)
                        except (ValueError, KeyError, FileNotFoundError, ImportError) as exc:
                            errors.append(key+': '+str(exc))
        except (ValueError, KeyError, FileNotFoundError) as exc:
            errors.append(run.name+': '+str(exc))
    if not runs:
        errors.append('Missing original run evidence')
    if result['sources'] and not errors:
        result['source_authentication'] = 'VERIFIED_RECORDED_GIT_BLOBS'
    if not args.numerical:
        errors.append('Independent numerical execution not requested')
    result['cross_capture'] = {}
    for left in authenticated:
        if 'windows-reference' not in left.name:
            continue
        for right in authenticated:
            if left.parent == right.parent and 'linux-' in right.name:
                key = str(left.relative_to(evidence))+' / '+right.name
                result['cross_capture'][key] = cross_capture(left, right, repo)
    result['remaining_blockers'] += errors
    result['historical_preserved'] = before == {r.name: snapshot(r) for r in runs}
    if not result['historical_preserved']:
        raise RuntimeError('Historical evidence changed')
    output.mkdir(parents=True)
    target = output/'assessment.json'
    target.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (output/'manifest.json').write_text(json.dumps({'assessment.json': sha(target),
        'diagnostic_source_sha256': sha(__file__)}, indent=2)+'\n', encoding='utf-8')
    return 2  # Incomplete archive/full-field/acceptance evidence cannot become PASS.


if __name__ == '__main__':
    sys.exit(main())
