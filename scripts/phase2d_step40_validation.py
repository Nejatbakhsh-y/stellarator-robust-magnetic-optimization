"""Independent STEP 40 diagnostics; production code and evidence are read only.

--input is STEP38's evidence directory. Output must be a fresh child of the
explicit --output-root. Exit 2: incomplete evidence; exit 1: scientific failure.
Decimal QR, residuals and direct RMS do not call production numerical helpers.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
import numpy as np
import scipy
from scipy.optimize import lsq_linear
from threadpoolctl import threadpool_info, threadpool_limits
import phase2d_step38_verify as transport

RTOL, ATOL, GUARD = D('1e-11'), D('1e-13'), D('1e-15')
CASES, COHORTS = transport.CASES, transport.COHORTS


def decimal(v):
    if isinstance(v, D):
        if not v.is_finite():
            raise ValueError('Nonfinite scalar')
        return v
    if isinstance(v,(np.floating,np.integer)):
        v = v.item()
    transport.number(v)
    return D.from_float(float(v))


def numeric(v, ndim):
    a = np.asarray(v)
    if a.dtype.kind not in 'fi' or a.ndim != ndim or not a.size or not np.isfinite(a).all():
        raise ValueError('Invalid finite numerical array')
    return a.astype(float)


def agrees(candidate, reference):
    with localcontext() as c:
        c.prec = 90
        return abs(decimal(candidate)-decimal(reference)) <= ATOL+RTOL*abs(decimal(reference))


def recovery(B, L, P, digits=90):
    """Quotient rule, independently checked central differences; B,L,P order."""
    if digits not in (60, 90):
        raise ValueError('Use independently repeated 60/90 precision')
    with localcontext() as c:
        c.prec = digits
        B, L, P = map(decimal, (B, L, P))
        gap, gain = L-B, L-P
        if abs(gap) <= GUARD:
            raise ValueError('Original denominator guard')
        gradient = [gain/gap**2, (P-B)/gap**2, -1/gap]
        h = abs(gap)*D('1e-20')
        fd = []
        for j in range(3):
            u, v = [B,L,P], [B,L,P]
            u[j] += h
            v[j] -= h
            f = lambda z: (z[1]-z[2])/(z[1]-z[0])
            fd.append((f(u)-f(v))/(2*h))
        return dict(ratio=str(gain/gap), numerator=str(gain), denominator=str(gap),
                    rms_B_L_P=list(map(str, (B,L,P))), derivatives_B_L_P=list(map(str, gradient)),
                    finite_difference_B_L_P=list(map(str, fd)), step=str(h),
                    numerator_condition=str((abs(L)+abs(P))/abs(gain)) if gain else None,
                    denominator_condition=str((abs(L)+abs(B))/abs(gap)))


def kkt(M, y, x, lower=None, upper=None, digits=90):
    """Separate feasibility and stationarity; optional supplied dual certificates.

    Without supplied multipliers infer the best nonnegative exact-bound ones.
    Thus dual/complementarity zero alone never establishes optimality.
    """
    M, y, x = numeric(M,2), numeric(y,1), numeric(x,1)
    if M.shape != (len(y),len(x)) or (lower is None) != (upper is None):
        raise ValueError('KKT dimensions/certificate')
    with localcontext() as c:
        c.prec = digits
        rows = [[decimal(v) for v in row] for row in M]
        xx = list(map(decimal,x))
        r = [sum((a*b for a,b in zip(row,xx)),D(0))-decimal(b) for row,b in zip(rows,y)]
        g = [sum((row[j]*v for row,v in zip(rows,r)),D(0)) for j in range(len(x))]
        if lower is None:
            lo = [max(v,D(0)) if a == -1 else D(0) for a,v in zip(xx,g)]
            hi = [max(-v,D(0)) if a == 1 else D(0) for a,v in zip(xx,g)]
        else:
            lo,hi = [list(map(decimal,numeric(z,1))) for z in (lower,upper)]
            if len(lo) != len(x) or len(hi) != len(x):
                raise ValueError('Dual dimensions')
        stat = max(abs(v-l+u) for v,l,u in zip(g,lo,hi))
        primal = max([D(0)]+[abs(v)-1 for v in xx])
        dual = max([D(0)]+[-v for v in lo+hi])
        comp = max([abs(l*(v+1)) for l,v in zip(lo,xx)]+[abs(u*(1-v)) for u,v in zip(hi,xx)])
        return dict(objective=str(sum((v*v for v in r),D(0))/2), residual=list(map(str,r)),
                    gradient=list(map(str,g)), stationarity=str(stat), primal=str(primal),
                    dual=str(dual), complementarity=str(comp), kkt_max=str(max(stat,primal,dual,comp)),
                    active_lower=[i for i,v in enumerate(xx) if v == -1],
                    active_upper=[i for i,v in enumerate(xx) if v == 1])


def conditioning(M):
    M = numeric(M,2)
    s = np.linalg.svd(M,compute_uv=False)
    cutoff = max(M.shape)*np.finfo(float).eps*s[0]
    rank = int(np.count_nonzero(s > cutoff))
    full = rank == M.shape[1]
    cond = float(s[0]/s[-1]) if full else None
    return dict(singular_values=s.tolist(), effective_rank=rank, cutoff=float(cutoff),
                condition=cond, rank_deficient=not full)


def qr_reference(M,y,digits=90):
    """Twice orthogonalized Decimal QR, independent of LAPACK/normal equations.

    Only an interior solution is a bounded reference. Singular or boundary
    problems return a limitation, never a fabricated bounded optimum.
    """
    M,y = numeric(M,2),numeric(y,1)
    if M.shape[0] != len(y) or M.shape[0] < M.shape[1]:
        raise ValueError('QR dimensions')
    with localcontext() as c:
        c.prec = digits
        n = M.shape[1]
        q, r = [], [[D(0)]*n for _ in range(n)]
        dot = lambda a,b: sum((v*w for v,w in zip(a,b)),D(0))
        for j in range(n):
            v = [decimal(t) for t in M[:,j]]
            for _ in range(2):
                for i,col in enumerate(q):
                    t = dot(col,v)
                    r[i][j] += t
                    v = [a-t*b for a,b in zip(v,col)]
            length = dot(v,v).sqrt()
            if length <= D(10)**(-(digits-10)):
                return dict(status='NOT_CERTIFIED',reason='Singular/precision-limited QR')
            r[j][j] = length
            q.append([t/length for t in v])
        rhs = [dot(col,list(map(decimal,y))) for col in q]
        x = [D(0)]*n
        for j in reversed(range(n)):
            x[j] = (rhs[j]-sum((r[j][i]*x[i] for i in range(j+1,n)),D(0)))/r[j][j]
        residual = [sum((decimal(a)*b for a,b in zip(row,x)),D(0))-decimal(t) for row,t in zip(M,y)]
        gradient = [sum((decimal(row[j])*v for row,v in zip(M,residual)),D(0)) for j in range(n)]
        interior = max(map(abs,x)) < 1
        return dict(status='INTERIOR_REFERENCE' if interior else 'NOT_CERTIFIED',
                    reason='Unconstrained QR; bounded reference only if interior',x=list(map(str,x)),
                    gradient_max=str(max(map(abs,gradient))),
                    objective=str(dot(residual,residual)/2), bound_margin=str(1-max(map(abs,x))))


def metric(a,dense,recovered,failed,digits=90):
    A,b,w = (numeric(a[k],n) for k,n in [('fine_A',2),('fine_b',1),('fine_weights',1)])
    dense,recovered = numeric(dense,1),numeric(recovered,1)
    if (A.shape != (len(b),len(dense)) or w.shape != b.shape or recovered.shape != dense.shape
            or np.any(w < 0) or not agrees(float(w.sum()),1.) or type(failed) is not int
            or not 0 <= failed < len(dense)):
        raise ValueError('Metric dimensions/weights/fault')
    frozen = dense.copy()
    frozen[failed] = 0
    with localcontext() as c:
        c.prec = digits
        norms = []
        for amps in (dense,frozen,recovered):
            xx = list(map(decimal,amps))
            energy = D(0)
            for row,bb,ww in zip(A,b,w):
                v = decimal(bb)+sum((decimal(t)*x for t,x in zip(row,xx)),D(0))
                energy += decimal(ww)*v*v
            norms.append(energy.sqrt())
        return recovery(*norms,digits=digits)


def field(points,vertices,current=1.,digits=90):
    """Independent tangent/perpendicular integral of each straight segment."""
    points,vertices = numeric(points,2),numeric(vertices,2)
    if points.shape[1] != 3 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError('Field dimensions')
    with localcontext() as c:
        c.prec = digits
        vv = [[decimal(x) for x in row] for row in vertices]
        output = []
        for point in points:
            p = list(map(decimal,point))
            total = [D(0)]*3
            for a,b in zip(vv,vv[1:]+vv[:1]):
                dl = [v-u for u,v in zip(a,b)]
                length = sum(v*v for v in dl).sqrt()
                if not length:
                    raise ValueError('Zero-length segment')
                tangent = [v/length for v in dl]
                r = [v-u for u,v in zip(a,p)]
                s = sum(v*u for v,u in zip(r,tangent))
                h = [v-s*u for v,u in zip(r,tangent)]
                h2 = sum(v*v for v in h)
                if not h2:
                    raise ValueError('Collinear field probe')
                factor = (s/(h2+s*s).sqrt()-(s-length)/(h2+(s-length)**2).sqrt())/h2
                cross = [tangent[1]*h[2]-tangent[2]*h[1],tangent[2]*h[0]-tangent[0]*h[2],tangent[0]*h[1]-tangent[1]*h[0]]
                total = [u+v*factor for u,v in zip(total,cross)]
            output.append([str(v*D('1e-7')*decimal(current)) for v in total])
        return output


def seal(path,expected):
    transport.valid_digest(expected)
    if transport.sha(path) != expected:
        raise ValueError('Frozen input fingerprint mismatch')
    return expected


def source_check(record,head,repo):
    if record.get('head') != head or not record.get('sha256'):
        raise ValueError('Invalid source fingerprint inventory')
    for name,digest in record['sha256'].items():
        transport.safe(repo,name)
        transport.valid_digest(digest)
        blob = subprocess.run(['git','show',head+':'+name],cwd=repo,capture_output=True)
        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:
            raise ValueError('Invalid source fingerprint '+name)


def reconstruct(data):
    required = {'A','b','D','d','weights','fine_A','fine_b','fine_weights','points','normals',
                'vertices','error_vertices','original_Bxyz','fine_points','fine_normals'}
    required |= {k+s for k in CASES for s in ('_M','_y','_x','_unconstrained_initial_x')}
    if data.get('schema') != 'production-upstream-v1' or set(data.get('arrays',{})) != required or set(data.get('cases',{})) != set(CASES):
        raise ValueError('Incomplete numerical artifacts')
    a = {k:np.asarray(transport.unpack(v),float) for k,v in data['arrays'].items()}
    config = transport.load(Path(__file__).resolve().parents[1]/'configs/phase2c_quick.json')
    if data['config'] != config or config['segments'] != 512:
        raise ValueError('Solver input configuration mismatch')
    p,n = config['nt']*config['np'],24
    shapes = dict(A=(p,n),b=(p,),D=(p,n),d=(p,),weights=(p,),points=(p,3),normals=(p,3),
                  vertices=(n,512,3),error_vertices=(512,3),original_Bxyz=(p,3),
                  fine_A=(4*p,n),fine_b=(4*p,),fine_weights=(4*p,),fine_points=(4*p,3),fine_normals=(4*p,3))
    for k,shape in shapes.items():
        if a[k].shape != shape:
            raise ValueError('Input dimensions '+k)
    for key in ('weights','fine_weights'):
        if np.any(a[key] < 0) or not agrees(float(a[key].sum()),1.):
            raise ValueError('Invalid scenario weights')
    def check(u,v):
        if u.shape != v.shape or not np.all(abs(u-v) <= float(ATOL)+float(RTOL)*abs(v)):
            raise ValueError('Solver input reconstruction mismatch')
    check(a['D'],a['A']*config['imax_A']/config['bref_T'])
    check(a['d'],a['b']/config['bref_T'])
    check(a['b'],np.sum(a['original_Bxyz']*a['normals'],axis=1))
    active = np.flatnonzero(abs(a['dense_x'])*config['imax_A'] > config['active_threshold_A'])
    for case in CASES:
        spec = data['cases'][case]
        transport.solver_spec(spec)
        support = spec.get('support',list(range(n)))
        if not support or any(type(i) is not int or not 0 <= i < n for i in support) or len(set(support)) != len(support):
            raise ValueError('Invalid support')
        if case != 'dense':
            failed = int(active[int(case[-1])])
            if spec['failed'] != failed or support != [i for i in range(n) if i != failed]:
                raise ValueError('Fault support mismatch')
        elif support != list(range(n)):
            raise ValueError('Dense support mismatch')
        size = len(support)
        check(a[case+'_M'],np.vstack((np.sqrt(a['weights'])[:,None]*a['D'][:,support],np.sqrt(config['ridge'])*np.eye(size))))
        check(a[case+'_y'],np.r_[-np.sqrt(a['weights'])*a['d'],np.zeros(size)])
        if a[case+'_x'].shape != (n,) or a[case+'_unconstrained_initial_x'].shape != (size,):
            raise ValueError('Missing saved current/initialization')
        if np.any(abs(a[case+'_x']) > 1) or any(a[case+'_x'][i] != 0 for i in range(n) if i not in support):
            raise ValueError('Captured current infeasible')
        if not spec.get('initialization'):
            raise ValueError('Missing solver initialization provenance')
    return a


def active_change(first,second):
    return any(first[k] != second[k] for k in ('active_lower','active_upper'))


def supports(record):
    def indices(v):
        if not isinstance(v,list) or any(type(i) is not int or not 0 <= i < 24 for i in v) or len(set(v)) != len(v):
            raise ValueError('Invalid support indices')
        return v
    if not record.get('deletion') or not record.get('sparse') or not record.get('dense_active') or 'fault_supports' not in record:
        raise ValueError('Missing support paths')
    previous = list(range(24))
    deletion = []
    for row in record['deletion']:
        current = indices(row['support'])
        order = indices(row['removal_order'])
        if current != previous or sorted(order) != sorted(current) or row['removed'] != order[0]:
            raise ValueError('Inconsistent deletion active-set path')
        deletion.append(dict(support=current,order=order,removed=row['removed']))
        previous = [i for i in current if i != row['removed']]
    if previous:
        raise ValueError('Incomplete deletion path')
    return dict(dense=indices(record['dense_active']),deletion=deletion,
                sparse=[dict(penalty=transport.number(r['penalty']),selection=indices(r['selection']['support']),
                             refit=indices(r['refit']['support'])) for r in record['sparse']],fault=record['fault_supports'])


def interventions(a,dense,recovered,failed):
    """Actual one-ULP input interventions; no inferred upstream solver cause.

    Weight transfers preserve the sum algebraically, but their independently
    rounded binary64 realization may change it. Record that change explicitly.
    """
    baseline = metric(a,dense,recovered,failed)
    probes = {}
    for key in ('fine_A','fine_b','fine_weights'):
        changed = {k:np.array(v,copy=True) for k,v in a.items() if k.startswith('fine_')}
        target = changed[key]
        original = float(target.flat[0])
        target.flat[0] = np.nextafter(original,np.inf)
        if key == 'fine_weights':
            target.flat[1] -= target.flat[0]-original
        record = metric(changed,dense,recovered,failed)
        record['perturbed_index'] = 0
        record['binary64_change'] = float(target.flat[0]-original)
        if key == 'fine_weights':
            record['weight_sum_change'] = float(target.sum()-np.asarray(a[key]).sum())
        probes[key] = record
    xx = numeric(dense,1).copy()
    index = int(np.argmax(abs(xx)))
    old = float(xx[index])
    xx[index] = np.nextafter(old,np.inf)
    probes['dense_current'] = dict(index=index,change_A=float(xx[index]-old),
                                   evaluation=metric(a,xx,recovered,failed))
    return dict(baseline=baseline,probes=probes,
                scope='Fixed support/current evaluation; interventions are not optimizer reruns')


def verdict(diagnostics_pass=False):
    return dict(diagnostic_acceptance='PASS' if diagnostics_pass else 'INCOMPLETE_OR_FAIL',
                scientific_comparison='FAIL',production_acceptance='FAIL',
                scientific_status='PARTIAL',causal_root_cause='INCONCLUSIVE')


def run(evidence,repo,controls=True):
    result = dict(schema='step40-v1',**verdict(),errors=[],numerical_failures=[],origins={},cells=[],comparisons=[],
                  environment=dict(platform=platform.platform(),python=sys.version,numpy=np.__version__,scipy=scipy.__version__,pools=threadpool_info()),
                  experiments={k:'NOT EXECUTED' for k in ('A','B','C','D')},
                  limits=dict(rtol=str(RTOL),atol=str(ATOL),refinement=1e-4,segments=512,denominator_guard=str(GUARD)))
    result['inventory'] = transport.verify(evidence,repo)
    inv = result['inventory']
    for key in ('download_hashes','historical_hashes'):
        if not inv.get(key) or not all(r['match'] for r in inv[key]):
            result['errors'].append(dict(kind='MISSING_OR_CORRUPT_EVIDENCE',check=key))
            result['evidence_complete'] = False
            return result
    for rid in transport.RUNS[2:]:
        root = evidence/'github-hosted'/rid
        index = transport.load(root/'artifact-index.json')
        head = transport.load(root/'run-metadata.json')['headSha']
        dirs = {v['name']:root/('artifact-'+str(v['id'])) for v in index['artifacts']}
        stage = lambda kind,cohort: dirs[f'step33-{kind}-{cohort}-{rid}-1']
        for origin in COHORTS:
            try:
                cap = stage('capture',origin)
                transport.manifest(cap/'manifest.json')
                digest = seal(cap/'inputs.json',transport.load(cap/'input-sha256.json')['inputs.json'])
                data = transport.load(cap/'inputs.json')
                sources = transport.load(cap/'source-sha256.json')
                source_check(sources,head,repo)
                transport.frozen_seal(transport.load(cap/'problem-sha256.json'),{'sha256':transport.fingerprint(transport.problem(data))})
                a = reconstruct(data)
                origin_report = dict(input_sha256=digest,cases={},independent_design={})
                result['origins'][rid+'/'+origin] = origin_report
                # Every training design-matrix entry: independent 60-digit geometry.
                units = np.array([field(a['points'],v,digits=60) for v in a['vertices']],float)
                design = np.einsum('cpi,pi->pc',units,a['normals'])
                disturbance = np.sum(np.array(field(a['points'],a['error_vertices'],1500.,60),float)*a['normals'],axis=1)
                origin_report['independent_design'] = dict(A=design.tolist(),b=disturbance.tolist(),precision=60,
                    max_A_error=float(np.max(abs(design-a['A']))),max_b_error=float(np.max(abs(disturbance-a['b']))),
                    all_entries_agree=bool(np.all(abs(design-a['A']) <= float(ATOL)+float(RTOL)*abs(a['A'])) and np.all(abs(disturbance-a['b']) <= float(ATOL)+float(RTOL)*abs(a['b']))))
                probes = [0,len(a['points'])//3]
                origin_report['field_precision_probes'] = {str(d):[field(a['points'][probes],v,digits=d) for v in a['vertices']] for d in (60,90)}
                if not origin_report['independent_design']['all_entries_agree']:
                    result['numerical_failures'].append(dict(kind='INDEPENDENT_DESIGN',run=rid,origin=origin))
                low,high = [np.asarray(origin_report['field_precision_probes'][str(d)],float) for d in (60,90)]
                origin_report['field_precision_rounds_identically'] = bool(np.array_equal(low,high))
                if not origin_report['field_precision_rounds_identically']:
                    result['numerical_failures'].append(dict(kind='FIELD_PRECISION',run=rid,origin=origin))
                for case in CASES:
                    M,y = a[case+'_M'],a[case+'_y']
                    origin_report['cases'][case] = dict(conditioning=conditioning(M),qr={str(d):qr_reference(M,y,d) for d in (60,90)},
                        captured_normalized=kkt(M,y,a[case+'_x'][data['cases'][case].get('support',list(range(24)))]),
                        saved_initialization=kkt(M,y,a[case+'_unconstrained_initial_x']))
                    qr = origin_report['cases'][case]['qr']
                    if any(qr[str(d)]['status'] != 'INTERIOR_REFERENCE' or D(qr[str(d)].get('gradient_max','1')) > D('1e-12') for d in (60,90)):
                        result['numerical_failures'].append(dict(kind='QR_NOT_CERTIFIED',run=rid,origin=origin,case=case))
                    if controls:
                        fresh = []
                        with threadpool_limits(limits=1):
                            for repeat in range(2):
                                fit = lsq_linear(M,y,**data['cases'][case]['arguments'])
                                fresh.append(dict(repeat=repeat,x=fit.x.tolist(),objective=float(fit.cost),optimality=float(fit.optimality),
                                    active_mask=fit.active_mask.tolist(),nit=int(fit.nit),status=int(fit.status),success=bool(fit.success),message=fit.message,
                                    kkt=kkt(M,y,fit.x),environment=result['environment'],pools=threadpool_info(),input_sha256=digest,
                                    solver_settings=data['cases'][case],execution='FRESH_SAME_HOST'))
                        origin_report['cases'][case]['fresh'] = fresh
                        for probe in fresh:
                            if not probe['success'] or D(probe['kkt']['primal']) != 0 or D(probe['kkt']['kkt_max']) > D('1e-12'):
                                result['numerical_failures'].append(dict(kind='FRESH_SOLVER_KKT',run=rid,origin=origin,case=case))
                        if platform.system() == 'Windows':
                            result['experiments']['A' if origin == COHORTS[0] else 'C'] = 'EXECUTED: current Windows environment; not historical worker recreation'
                        elif platform.system() == 'Linux':
                            result['experiments']['B' if origin == COHORTS[0] else 'D'] = 'EXECUTED: current Linux environment; not historical worker recreation'
                reference = None
                for worker in COHORTS:
                    sub = stage('replay',worker)/origin
                    transport.manifest(stage('replay',worker)/'manifest.json')
                    seal(sub/'inputs.json',digest)
                    replay_root = stage('replay',worker)
                    if transport.load(replay_root/'source-sha256.json') != sources:
                        raise ValueError('Replay source fingerprints mismatch')
                    transport.environment(transport.load(replay_root/'environment.json'),worker,head)
                    record = transport.load(sub/'result.json')
                    solve = record['solve']
                    amps = {k:np.asarray(transport.unpack(solve['currents_A'][k]),float) for k in CASES}
                    entry = dict(run=rid,origin=origin,worker=worker,input_sha256=digest,result_sha256=transport.sha(sub/'result.json'),cases={},execution='SAVED_SOLVE_FRESH_DIAGNOSTICS')
                    entry['support_signature'] = supports(transport.load(sub/'support.json'))
                    entry['support_sha256'] = transport.sha(sub/'support.json')
                    if reference is not None and entry['support_signature'] != reference[0]['support_signature']:
                        result['numerical_failures'].append(dict(kind='SUPPORT_TRANSITION',run=rid,origin=origin,worker=worker))
                    for case in CASES:
                        support = data['cases'][case].get('support',list(range(24)))
                        if amps[case].shape != (24,) or any(amps[case][i] != 0 for i in range(24) if i not in support):
                            raise ValueError('Invalid saved currents/support')
                        diag = kkt(a[case+'_M'],a[case+'_y'],amps[case][support]/3000.)
                        saved = solve['diagnostics'][case]
                        transport.diagnostics(saved,len(support))
                        spectrum = origin_report['cases'][case]['conditioning']
                        if saved['rank'] != spectrum['effective_rank'] or any(not agrees(v,w) for v,w in zip(saved['singular_values'],spectrum['singular_values'])):
                            result['numerical_failures'].append(dict(kind='SAVED_SPECTRUM',run=rid,origin=origin,worker=worker,case=case))
                        if not agrees(saved['cost'],D(diag['objective'])):
                            raise ValueError('Corrupted saved objective')
                        mask = [-1 if v == -1 else 1 if v == 1 else 0 for v in amps[case][support]/3000.]
                        if saved['active_mask'] != mask:
                            raise ValueError('Corrupted active constraints')
                        entry['cases'][case] = dict(kkt=diag,saved_diagnostics=saved)
                        reference_qr = origin_report['cases'][case]['qr']['90']
                        if reference_qr['status'] == 'INTERIOR_REFERENCE':
                            with localcontext() as c:
                                c.prec = 90
                                entry['cases'][case]['normalized_distance_to_qr_reference'] = str(max(
                                    abs(decimal(v)-D(w)) for v,w in zip(amps[case][support]/3000.,reference_qr['x'])))
                        if D(diag['primal']) != 0 or D(diag['kkt_max']) > D('1e-12') or saved['success'] is not True:
                            result['numerical_failures'].append(dict(kind='KKT_OR_SOLVER',run=rid,origin=origin,worker=worker,case=case))
                        if case != 'dense':
                            failed = data['cases'][case]['failed']
                            entry['cases'][case]['recovery'] = {str(d):metric(a,amps['dense'],amps[case],failed,d) for d in (60,90)}
                            highratio = D(entry['cases'][case]['recovery']['90']['ratio'])
                            lowratio = D(entry['cases'][case]['recovery']['60']['ratio'])
                            with localcontext() as c:
                                c.prec = 90
                                entry['cases'][case]['precision_difference_60_minus_90'] = str(lowratio-highratio)
                            if not agrees(lowratio,highratio):
                                result['numerical_failures'].append(dict(kind='RECOVERY_PRECISION',run=rid,origin=origin,worker=worker,case=case))
                            if not agrees(solve['recovery'][case]['fractional_recovery'],highratio):
                                result['numerical_failures'].append(dict(kind='SAVED_VS_REFERENCE_RATIO',run=rid,origin=origin,worker=worker,case=case))
                            if worker == COHORTS[0]:
                                entry['cases'][case]['input_interventions'] = interventions(a,amps['dense'],amps[case],failed)
                            if reference is not None:
                                refentry,refamps,refsolve = reference
                                refvalue = refsolve['recovery'][case]['fractional_recovery']
                                curvalue = solve['recovery'][case]['fractional_recovery']
                                high = D(entry['cases'][case]['recovery']['90']['ratio'])
                                refhigh = D(refentry['cases'][case]['recovery']['90']['ratio'])
                                with localcontext() as c:
                                    c.prec = 90
                                    comparison = dict(run=rid,origin=origin,worker=worker,case=case,reference=refvalue,candidate=curvalue,
                                        saved_pass=agrees(curvalue,refvalue),high_precision_pass=agrees(high,refhigh),high_precision_delta=str(high-refhigh),
                                        result_sha256=entry['result_sha256'],reference_sha256=refentry['result_sha256'])
                                comparison['swaps'] = {label:metric(a,dd,pp,failed) for label,dd,pp in
                                    [('reference',refamps['dense'],refamps[case]),('dense_only',amps['dense'],refamps[case]),
                                     ('recovered_only',refamps['dense'],amps[case]),('both',amps['dense'],amps[case])]}
                                comparison['active_set_changed'] = active_change(diag,refentry['cases'][case]['kkt'])
                                result['comparisons'].append(comparison)
                    if reference is None:
                        reference = entry,amps,solve
                    result['cells'].append(entry)
            except (ValueError,KeyError,OSError,TypeError,ArithmeticError,IndexError) as exc:
                result['errors'].append(dict(kind='MISSING_OR_CORRUPT_EVIDENCE',run=rid,origin=origin,error=str(exc)))
    result['local_evidence_complete'] = not result['errors'] and not inv['errors'] and len(result['cells']) == 32
    result['archive_authentication'] = 'INCOMPLETE: original archive bytes unavailable'
    result['evidence_complete'] = False  # This offline protocol cannot authenticate unavailable ZIP bytes.
    result.update(verdict(result['local_evidence_complete'] and not result['numerical_failures']))
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    for name in ('input','output','output-root'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--saved-only',action='store_true')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    evidence,out,root = [p.resolve() for p in (args.input,args.output,args.output_root)]
    if (not all(p.is_relative_to(repo) for p in (evidence,out,root)) or out == root or not out.is_relative_to(root)
            or evidence.is_relative_to(out) or out.is_relative_to(evidence) or root.is_relative_to(evidence)):
        raise ValueError('Output containment/disjointness')
    out.mkdir(parents=True,exist_ok=False)
    try:
        result = run(evidence,repo,not args.saved_only)
    except (ValueError,KeyError,OSError,TypeError,ArithmeticError) as exc:
        result = dict(**verdict(),evidence_complete=False,errors=[str(exc)])
    result['implementation_sha256'] = transport.sha(__file__)
    result['transport_sha256'] = transport.sha(transport.__file__)
    path = out/'validation.json'
    path.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({'validation.json':transport.sha(path)},indent=2)+'\n',encoding='utf-8')
    return 2 if not result['evidence_complete'] else 1


if __name__ == '__main__':
    sys.exit(main())
