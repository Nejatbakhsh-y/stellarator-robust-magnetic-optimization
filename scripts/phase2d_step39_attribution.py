"""STEP 39: read-only frozen-input attribution; no production acceptance promotion.

Requires the existing NumPy/SciPy environment. --input is the STEP38 evidence
directory, --output a NEW directory under --output-root. Exit 2 means incomplete
evidence; exit 1 preserves historical scientific failure. Never exits scientific PASS.
"""
import argparse
from decimal import Decimal as Q, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

sys.dont_write_bytecode = True

import numpy as np
import scipy
from scipy.optimize import lsq_linear
from threadpoolctl import threadpool_info, threadpool_limits

# Reuse only strict evidence transport/schema checks, not numerical diagnostics.
import phase2d_step38_verify as transport

COHORTS = transport.COHORTS
CASES = transport.CASES
RUNS = transport.RUNS
RTOL, ATOL, GUARD = 1e-11, 1e-13, Q('1e-15')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def array(value):
    a = np.asarray(transport.unpack(value), dtype=float)
    if not np.isfinite(a).all():
        raise ValueError('Nonfinite numerical input')
    return a


def finite(value, ndim=None):
    a = np.asarray(value)
    if a.dtype.kind not in 'fi' or not np.isfinite(a).all() or (ndim is not None and a.ndim != ndim):
        raise ValueError('Invalid numerical dimensions/type')
    return a.astype(float)


def compare(candidate, reference):
    a, b = finite(candidate), finite(reference)
    if a.shape != b.shape:
        raise ValueError('Comparison dimensions')
    ok = np.abs(a-b) <= ATOL+RTOL*np.abs(b)
    return dict(passed=bool(ok.all()), exact=bool(np.array_equal(a, b)),
                failures=int((~ok).sum()), max_absolute=float(np.max(np.abs(a-b))))


def seal(path, expected):
    transport.valid_digest(expected)
    actual = transport.sha(path)
    if actual != expected:
        raise ValueError('Mismatched input fingerprint')
    return actual


def conditioning(M):
    M = finite(M, 2)
    if not min(M.shape):
        raise ValueError('Empty matrix')
    s = np.linalg.svd(M, compute_uv=False)
    cutoff = max(M.shape)*np.finfo(float).eps*s[0]
    rank = int(np.sum(s > cutoff))
    full = rank == M.shape[1]
    cond = float(s[0]/s[-1]) if full else None
    return dict(singular_values=s.tolist(), effective_rank=rank, cutoff=float(cutoff),
                condition=cond, normal_equation_condition=cond*cond if cond is not None else None,
                rank_deficient=not full)


def kkt(M, y, x):
    """90-digit independent box KKT; multipliers inferred by gradient signs.

    Bounds are exact [-1,1]. An infeasible point is never made feasible by clipping.
    """
    M, y, x = finite(M, 2), finite(y, 1), finite(x, 1)
    if M.shape != (len(y), len(x)) or not len(x):
        raise ValueError('KKT dimensions')
    with localcontext() as ctx:
        ctx.prec = 90
        cv = lambda v: Q.from_float(float(v))
        rows = [[cv(v) for v in row] for row in M]
        xx = list(map(cv, x))
        residual = [sum((a*b for a, b in zip(row, xx)), Q(0))-cv(t) for row, t in zip(rows, y)]
        g = [sum((row[j]*r for row, r in zip(rows, residual)), Q(0)) for j in range(len(x))]
        lower = [max(v, Q(0)) if a == -1 else Q(0) for a, v in zip(xx, g)]
        upper = [max(-v, Q(0)) if a == 1 else Q(0) for a, v in zip(xx, g)]
        stationarity = max(abs(v-l+u) for v, l, u in zip(g, lower, upper))
        complementarity = max([abs(l*(a+1)) for l, a in zip(lower, xx)]+
                              [abs(u*(1-a)) for u, a in zip(upper, xx)])
        primal = max([Q(0)]+[abs(a)-1 for a in xx])
        dual = max([Q(0)]+[-v for v in lower+upper])
        return dict(objective=str(sum((r*r for r in residual), Q(0))/2),
                    primal=str(primal), stationarity=str(stationarity),
                    complementarity=str(complementarity), dual=str(dual),
                    kkt_max=str(max(primal, stationarity, complementarity, dual)),
                    active_lower=[i for i, a in enumerate(xx) if a == -1],
                    active_upper=[i for i, a in enumerate(xx) if a == 1])


def recovery(B, L, P, digits=90):
    """Exact binary64 conversion, or exact Decimal inputs; derivative order B,L,P."""
    with localcontext() as ctx:
        ctx.prec = digits
        def cv(v):
            if isinstance(v, Q):
                if not v.is_finite():
                    raise ValueError('Nonfinite recovery scalar')
                return v
            transport.number(v)
            return Q.from_float(float(v))
        B, L, P = map(cv, (B, L, P))
        den, num = L-B, L-P
        if abs(den) <= GUARD:
            raise ValueError('Original denominator guard')
        deriv = (num/den**2, (P-B)/den**2, -1/den)
        # Independent central differences at two scales, entirely in Decimal.
        fd = []
        for exponent in (15, 20):
            h = min(abs(den), max(abs(B), abs(L), abs(P)))*Q(10)**(-exponent)
            vals = [B, L, P]
            approx = []
            for j in range(3):
                plus, minus = vals.copy(), vals.copy()
                plus[j] += h; minus[j] -= h
                f = lambda v: (v[1]-v[2])/(v[1]-v[0])
                approx.append((f(plus)-f(minus))/(2*h))
            fd.append(dict(step=str(h), derivatives=list(map(str, approx)),
                           max_error=str(max(abs(a-b) for a, b in zip(approx, deriv)))))
        return dict(ratio=str(num/den), numerator=str(num), denominator=str(den),
                    numerator_condition=str((abs(L)+abs(P))/abs(num)) if num else None,
                    denominator_condition=str((abs(L)+abs(B))/abs(den)),
                    derivatives_B_L_P=list(map(str, deriv)), finite_differences=fd)


def field_reference(points, vertices, current=1., digits=60):
    """Independent Decimal polygon Biot-Savart, all three components.

    Polygon reference only: does not establish smooth-circle refinement or confinement.
    """
    points, vertices = finite(points, 2), finite(vertices, 2)
    if points.shape[1] != 3 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError('Field dimensions')
    transport.number(current)
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: Q.from_float(float(v))
        vv = [[cv(v) for v in row] for row in vertices]
        output = []
        for point in points:
            p = list(map(cv, point)); total = [Q(0)]*3
            for a, b in zip(vv, vv[1:]+vv[:1]):
                u, v = [p[i]-a[i] for i in range(3)], [p[i]-b[i] for i in range(3)]
                nu, nv = sum(t*t for t in u).sqrt(), sum(t*t for t in v).sqrt()
                den = nu*nv*(nu*nv+sum(u[i]*v[i] for i in range(3)))
                cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
                if den <= 0:
                    raise ValueError('Singular/collinear reference geometry')
                for i in range(3):
                    total[i] += cross[i]*(nu+nv)/den
            output.append([str(t*Q('1e-7')*cv(current)) for t in total])
        return output


def reconstruct(data):
    """Rebuild solver inputs from original saved physical arrays; no regeneration."""
    required = {'A', 'b', 'D', 'd', 'weights', 'fine_A', 'fine_b', 'fine_weights',
                'vertices', 'error_vertices', 'points', 'normals', 'original_Bxyz', 'fine_points', 'fine_normals'}
    required |= {case+suffix for case in CASES for suffix in ('_M', '_y', '_x', '_unconstrained_initial_x')}
    if data.get('schema') != 'production-upstream-v1' or required != data.get('arrays', {}).keys() or set(data.get('cases', {})) != set(CASES):
        raise ValueError('Incomplete input inventory')
    a = {k: array(v) for k, v in data['arrays'].items()}
    c = data['config']
    if c != transport.load(Path(__file__).resolve().parents[1]/'configs/phase2c_quick.json'):
        raise ValueError('Unexpected production configuration')
    if c['segments'] != 512 or c['imax_A'] != 3000 or c['ridge'] != 1e-6:
        raise ValueError('Changed production settings')
    n, p = a['A'].shape[1], a['A'].shape[0]
    if n != 24 or p != c['nt']*c['np'] or a['b'].shape != (p,) or a['weights'].shape != (p,) or np.any(a['weights'] < 0) or not transport.close(float(a['weights'].sum()), 1.):
        raise ValueError('Invalid design dimensions/weights')
    shapes = dict(points=(p, 3), normals=(p, 3), original_Bxyz=(p, 3),
                  vertices=(n, 512, 3), error_vertices=(512, 3),
                  fine_points=(4*p, 3), fine_normals=(4*p, 3), fine_A=(4*p, n),
                  fine_b=(4*p,), fine_weights=(4*p,))
    if any(a[k].shape != shape for k, shape in shapes.items()) or np.any(a['fine_weights'] < 0) or not transport.close(float(a['fine_weights'].sum()), 1.):
        raise ValueError('Invalid field/recovery geometry inventory')
    checks = {'D': compare(a['D'], a['A']*c['imax_A']/c['bref_T']),
              'd': compare(a['d'], a['b']/c['bref_T']),
              'projected_disturbance': compare(a['b'], np.sum(a['original_Bxyz']*a['normals'], axis=1))}
    active = np.flatnonzero(abs(a['dense_x'])*c['imax_A'] > c['active_threshold_A'])
    records = {}
    for case in CASES:
        spec = data['cases'][case]
        transport.solver_spec(spec)
        support = list(range(n)) if case == 'dense' else spec['support']
        if any(type(i) is not int for i in support) or len(set(support)) != len(support) or any(i < 0 or i >= n for i in support):
            raise ValueError('Invalid support')
        if case != 'dense':
            failed = int(active[int(case[-1])])
            if spec['failed'] != failed or support != [i for i in range(n) if i != failed]:
                raise ValueError('Inconsistent fault/support ordering')
        if not spec.get('initialization'):
            raise ValueError('Missing initialization record')
        k = len(support)
        if a[case+'_M'].shape != (p+k, k) or a[case+'_y'].shape != (p+k,) or a[case+'_x'].shape != (n,) or a[case+'_unconstrained_initial_x'].shape != (k,):
            raise ValueError('Solver array dimensions')
        if np.any(abs(a[case+'_x']) > 1) or any(a[case+'_x'][i] != 0 for i in range(n) if i not in support):
            raise ValueError('Captured current/support inconsistency')
        M = np.vstack([np.sqrt(a['weights'])[:, None]*a['D'][:, support], np.sqrt(c['ridge'])*np.eye(k)])
        y = np.r_[-np.sqrt(a['weights'])*a['d'], np.zeros(k)]
        checks[case+'_M'] = compare(a[case+'_M'], M)
        checks[case+'_y'] = compare(a[case+'_y'], y)
        input_spec = {k: spec[k] for k in ('arguments', 'implicit_method', 'implicit_lsq_solver', 'initialization')}
        records[case] = dict(input_sha256=fingerprint(dict(M=data['arrays'][case+'_M'],
            y=data['arrays'][case+'_y'], spec=input_spec, support=support, config=c,
            initial_x=data['arrays'][case+'_unconstrained_initial_x'])), support=support,
            conditioning=conditioning(a[case+'_M']),
            initialization_kkt=kkt(a[case+'_M'], a[case+'_y'], a[case+'_unconstrained_initial_x']))
        if (type(spec['success']) is not bool or type(spec['status']) is not int
                or spec['status'] not in (-1, 0, 1, 2, 3) or spec['success'] != (spec['status'] > 0)
                or type(spec['nit']) is not int or spec['nit'] < 0
                or not isinstance(spec['message'], str) or not spec['message']
                or transport.number(spec['cost']) < 0 or transport.number(spec['optimality']) < 0
                or spec['active_mask'] != [-1 if v == -1 else 1 if v == 1 else 0 for v in a[case+'_x'][support]]):
            raise ValueError('Invalid captured solver termination')
        captured_kkt = kkt(a[case+'_M'], a[case+'_y'], a[case+'_x'][support])
        if not transport.close(spec['cost'], float(captured_kkt['objective'])):
            raise ValueError('Inconsistent captured objective')
    if not all(v['passed'] for v in checks.values()):
        raise ValueError('Inconsistent reconstructed solver inputs')
    return a, dict(array_sha256={k: fingerprint(v) for k, v in data['arrays'].items()},
                   reconstruction=checks, cases=records,
                   slsqp='NOT_CAPTURED: bounded ridge subset; no minimax replay claimed',
                   sparse_deletion='NOT_CONTROLLED_BY_THIS_FROZEN_SUBSET')


def metric(a, dense, recovered, failed, digits=90):
    dense, recovered = finite(dense, 1), finite(recovered, 1)
    A, b, w = a['fine_A'], a['fine_b'], a['fine_weights']
    if A.shape != (len(b), len(dense)) or w.shape != b.shape or recovered.shape != dense.shape or np.any(w < 0) or not transport.close(float(w.sum()), 1.) or type(failed) is not int or not 0 <= failed < len(dense):
        raise ValueError('Recovery input dimensions/weights/fault')
    with localcontext() as ctx:
        ctx.prec = digits
        cv = lambda v: Q.from_float(float(v))
        frozen = dense.copy(); frozen[failed] = 0
        currents = [[cv(v) for v in x] for x in (dense, frozen, recovered)]
        totals = [Q(0)]*3
        for row, bb, ww in zip(A, b, w):
            row = list(map(cv, row))
            for j, x in enumerate(currents):
                r = cv(bb)+sum((u*v for u, v in zip(row, x)), Q(0))
                totals[j] += cv(ww)*r*r
        rms = [v.sqrt() for v in totals]
        result = recovery(*rms, digits=digits)
        result['rms_B_L_P'] = list(map(str, rms))
        return result


def solve_controls(M, y):
    """Fresh same-host repeats/thread controls. No OS/library isolation claim."""
    records = []
    for threads in (1, 2):
        with threadpool_limits(limits=threads):
            for repeat in range(2):
                r = lsq_linear(M, y, bounds=(-1, 1), tol=1e-12, max_iter=1000)
                records.append(dict(threads=threads, repeat=repeat, pools=threadpool_info(),
                    currents_normalized=r.x.tolist(), success=bool(r.success), status=int(r.status),
                    nit=int(r.nit), message=str(r.message), kkt=kkt(M, y, r.x)))
    return records


def reference_basis(a):
    indices = [0, len(a['points'])//3]
    result = {'point_indices': indices, 'precision': {}, 'scope': 'Two points, all polygons and Bx/By/Bz; not full-grid certification'}
    for digits in (60, 90):
        unit = [field_reference(a['points'][indices], v, digits=digits) for v in a['vertices']]
        original = field_reference(a['points'][indices], a['error_vertices'], 1500., digits)
        result['precision'][str(digits)] = dict(unit=unit, original=original)
    return result


def reference_currents(basis, currents):
    output = {}
    for digits, values in basis['precision'].items():
        with localcontext() as ctx:
            ctx.prec = int(digits)
            output[digits] = {case: [[str(Q(values['original'][p][c])+sum(
                (Q(unit[p][c])*Q.from_float(float(amp)) for unit, amp in zip(values['unit'], amps)), Q(0)))
                for c in range(3)] for p in range(len(basis['point_indices']))]
                for case, amps in currents.items()}
    return dict(fields=output, precision_convergence={case: compare(
        np.array(output['60'][case], float), np.array(output['90'][case], float)) for case in currents})


def support_signature(record):
    if not isinstance(record, dict) or not record.get('deletion') or not record.get('sparse') or not record.get('dense_active'):
        raise ValueError('Incomplete support trace')
    def support(values):
        if not isinstance(values, list) or any(type(v) is not int or not 0 <= v < 24 for v in values) or len(set(values)) != len(values):
            raise ValueError('Invalid support trace indices')
        return values
    previous = list(range(24)); deletion = []
    for row in record['deletion']:
        current = support(row['support'])
        if current != previous or row['removed'] not in current:
            raise ValueError('Invalid deletion transition')
        deletion.append(dict(support=current, removed=row['removed']))
        previous = [i for i in current if i != row['removed']]
    if previous:
        raise ValueError('Incomplete deletion path')
    sparse = [dict(penalty=transport.number(row['penalty']),
                   selection=support(row['selection']['support']), refit=support(row['refit']['support']))
              for row in record['sparse']]
    return dict(dense=support(record['dense_active']), deletion=deletion, sparse=sparse)


def sensitivities(a, dense, recovered, failed):
    """Chain rule on frozen fine-grid arrays; physical currents are in amperes.

    Array/weight gradients are local derivatives, not rerun optimization results.
    """
    A, b, w = a['fine_A'], a['fine_b'], a['fine_weights']
    frozen = dense.copy(); frozen[failed] = 0
    xx = (dense, frozen, recovered)
    residual = [b+A@x for x in xx]
    rms = [float(np.sqrt(np.sum(w*r*r))) for r in residual]
    if min(rms) <= 0:
        raise ValueError('RMS derivative undefined at zero')
    rr = recovery(*rms)
    coeff = np.array([float(v) for v in rr['derivatives_B_L_P']])
    gradients = [A.T@(w*r)/v for r, v in zip(residual, rms)]
    frozen_gradient = gradients[1].copy(); frozen_gradient[failed] = 0
    gd = coeff[0]*gradients[0]+coeff[1]*frozen_gradient
    gp = coeff[2]*gradients[2]
    gw = sum(c*r*r/(2*v) for c, r, v in zip(coeff, residual, rms))
    gA = sum(c*(w*r/v)[:, None]*x[None, :] for c, r, v, x in zip(coeff, residual, rms, xx))
    gb = sum(c*w*r/v for c, r, v in zip(coeff, residual, rms))
    return dict(dR_d_dense_current=gd.tolist(), dR_d_recovered_current=gp.tolist(),
                dR_d_A_frobenius_norm=float(np.linalg.norm(gA)), dR_d_b_l2=float(np.linalg.norm(gb)),
                dR_d_weights_l2=float(np.linalg.norm(gw)),
                weight_constraint='Only zero-sum weight directions preserve normalized weights',
                support_constraint='Continuous fixed-support derivative; cannot establish discrete selection causality')


def investigate(evidence, repo, controls=True):
    # Full inherited inventory check includes early failures, source Git blobs,
    # exact seals, incomplete historical manifests and all reference records.
    inventory = transport.verify(evidence, repo)
    result = dict(schema='step39-v1', scientific_comparison='FAIL', production_acceptance='FAIL',
        scientific_status='PARTIAL', causal_root_cause='INCONCLUSIVE',
        thresholds=dict(rtol=RTOL, atol=ATOL, refinement=1e-4, segments=512, denominator_guard_T='1e-15'),
        inventory=inventory, origins={}, replay=[], failures=[], errors=[],
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                         pools=threadpool_info()), fresh_optimizer_controls=controls)
    for name in ('download_hashes', 'historical_hashes'):
        rows = inventory.get(name)
        if not rows or any(not row['match'] for row in rows):
            result.update(evidence_complete=False, archive_authentication='INCOMPLETE')
            result['errors'].append(dict(check=name, error='Missing or corrupt required hash inventory; numerical execution rejected'))
            return result
    for rid in RUNS[2:]:
        root = evidence/'github-hosted'/rid
        try:
            index = transport.load(root/'artifact-index.json')
            artifacts = {r['name']: root/('artifact-'+str(r['id'])) for r in index['artifacts']}
            def stage(kind, cohort):
                return artifacts[f'step33-{kind}-{cohort}-{rid}-1']
            for origin in COHORTS:
                cap = stage('capture', origin)
                transport.manifest(cap/'manifest.json')
                path = cap/'inputs.json'
                digest = seal(path, transport.load(cap/'input-sha256.json')['inputs.json'])
                data = transport.load(path)
                a, report = reconstruct(data)
                basis = reference_basis(a)
                report['independent_field_basis'] = basis
                result['origins'][rid+'/'+origin] = dict(input_file_sha256=digest, **report)
                reference = None
                reference_support = None
                for worker in COHORTS:
                    sub = stage('replay', worker)/origin
                    seal(sub/'inputs.json', digest)
                    # A historical run's unrelated incomplete early manifest does
                    # not erase this cell, but this cell's own inventory must pass.
                    transport.manifest(stage('replay', worker)/'manifest.json')
                    rec = transport.load(sub/'result.json')
                    currents = {k: array(rec['solve']['currents_A'][k]) for k in CASES}
                    entry = dict(run=rid, origin=origin, worker=worker, result_sha256=transport.sha(sub/'result.json'),
                                 input_sha256=digest, execution='SAVED_SOLVE_FRESH_DIAGNOSTICS', cases={})
                    entry['independent_fields'] = reference_currents(basis, currents)
                    saved_fields = transport.fields(transport.load(sub/'fields.json'))
                    indices = basis['point_indices']
                    entry['independent_fields']['saved_unit_comparison'] = compare(
                        np.array(saved_fields['unit_coils_Bxyz'])[:, indices, :], np.array(basis['precision']['90']['unit'], float))
                    entry['independent_fields']['saved_original_comparison'] = compare(
                        np.array(saved_fields['original_Bxyz'])[indices], np.array(basis['precision']['90']['original'], float))
                    entry['support_trace'] = support_signature(transport.load(sub/'support.json'))
                    entry['support_trace_sha256'] = transport.sha(sub/'support.json')
                    if reference_support is None:
                        reference_support = entry['support_trace']
                    entry['support_trace_matches_reference'] = entry['support_trace'] == reference_support
                    if not entry['support_trace_matches_reference']:
                        result['failures'].append(dict(run=rid, origin=origin, worker=worker, kind='support_transition'))
                    field_checks = entry['independent_fields']
                    if not field_checks['saved_unit_comparison']['passed'] or not field_checks['saved_original_comparison']['passed'] or not all(v['passed'] for v in field_checks['precision_convergence'].values()):
                        result['failures'].append(dict(run=rid, origin=origin, worker=worker, kind='independent_field_reference'))
                    for case in CASES:
                        support = report['cases'][case]['support']
                        transport.diagnostics(rec['solve']['diagnostics'][case], len(support))
                        if currents[case].shape != (24,) or any(currents[case][i] != 0 for i in range(24) if i not in support):
                            raise ValueError('Invalid current vector/support')
                        x = currents[case][support]/data['config']['imax_A']
                        entry['cases'][case] = kkt(a[case+'_M'], a[case+'_y'], x)
                        diag = rec['solve']['diagnostics'][case]
                        expected_mask = [-1 if v == -1 else 1 if v == 1 else 0 for v in x]
                        if diag['active_mask'] != expected_mask or not transport.close(diag['cost'], float(entry['cases'][case]['objective'])):
                            raise ValueError('Inconsistent solver diagnostics')
                        if diag['success'] is not True or Q(entry['cases'][case]['kkt_max']) > Q('1e-12'):
                            result['failures'].append(dict(run=rid, origin=origin, worker=worker, case=case, kind='solver_kkt'))
                        if case != 'dense':
                            entry['cases'][case]['decimal'] = {str(d): metric(a, currents['dense'], currents[case],
                                data['cases'][case]['failed'], d) for d in (60, 90)}
                            entry['cases'][case]['local_sensitivity'] = sensitivities(a, currents['dense'], currents[case], data['cases'][case]['failed'])
                        if controls and worker == COHORTS[0]:
                            entry['cases'][case]['fresh_controls'] = solve_controls(a[case+'_M'], a[case+'_y'])
                            for probe in entry['cases'][case]['fresh_controls']:
                                if not probe['success'] or Q(probe['kkt']['kkt_max']) > Q('1e-12'):
                                    result['failures'].append(dict(run=rid, origin=origin, worker=worker, case=case, kind='fresh_control_solver_or_kkt'))
                    if reference is None:
                        reference = rec
                    else:
                        ref_currents = {k: array(reference['solve']['currents_A'][k]) for k in CASES}
                        entry['controlled_current_swaps'] = {case: {
                            label: metric(a, dd, pp, data['cases'][case]['failed'])
                            for label, dd, pp in (
                                ('reference', ref_currents['dense'], ref_currents[case]),
                                ('dense_only', currents['dense'], ref_currents[case]),
                                ('recovered_only', ref_currents['dense'], currents[case]),
                                ('both', currents['dense'], currents[case]))} for case in CASES[1:]}
                        for case in CASES[1:]:
                            ref = reference['solve']['recovery'][case]['fractional_recovery']
                            cur = rec['solve']['recovery'][case]['fractional_recovery']
                            if not transport.close(cur, ref):
                                result['failures'].append(dict(run=rid, origin=origin, worker=worker, case=case,
                                    reference=ref, candidate=cur, delta=cur-ref, result_sha256=entry['result_sha256']))
                    result['replay'].append(entry)
        except (ValueError, KeyError, OSError, TypeError, IndexError, ArithmeticError) as exc:
            result['errors'].append(dict(run=rid, error=str(exc)))
    result['evidence_complete'] = not (inventory['errors'] or result['errors']) and len(result['replay']) == 32
    # Missing original ZIP bytes independently prevents authentication, even if
    # all extracted-file and numerical semantic checks succeed.
    result['archive_authentication'] = 'INCOMPLETE'
    return result


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--output-root', type=Path, required=True)
    p.add_argument('--saved-only', action='store_true', help='Skip fresh optimizer controls; record this limitation')
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    evidence, out, root = (v.resolve() for v in (args.input, args.output, args.output_root))
    if not all(v.is_relative_to(repo) for v in (evidence, out, root)) or not out.is_relative_to(root) or out == root or out.is_relative_to(evidence) or evidence.is_relative_to(out):
        raise ValueError('Output must be new, within explicit output root, and disjoint from evidence')
    out.mkdir(parents=True, exist_ok=False)
    try:
        result = investigate(evidence, repo, not args.saved_only)
    except (ValueError, KeyError, OSError, TypeError, ArithmeticError) as exc:
        result = dict(errors=[str(exc)], evidence_complete=False, scientific_comparison='FAIL',
                      production_acceptance='FAIL', scientific_status='PARTIAL', causal_root_cause='INCONCLUSIVE')
    result['implementation_sha256'] = transport.sha(__file__)
    result['transport_validator_sha256'] = transport.sha(Path(transport.__file__))
    (out/'attribution.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({'attribution.json': transport.sha(out/'attribution.json')}, indent=2)+'\n', encoding='utf-8')
    return 2 if not result['evidence_complete'] or result.get('archive_authentication') != 'COMPLETE' else 1


if __name__ == '__main__':
    sys.exit(main())
