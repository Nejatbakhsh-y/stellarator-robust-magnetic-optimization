"""Fresh sealed-input TRF replay. Exit 2 execution/evidence failure, 1 science FAIL.

No production code is called. Existing STEP38 transport and STEP40 input/source
validators are reused explicitly; residuals and recovery arithmetic below are new.
STEP42_OUTPUT_ROOT is mandatory. Evidence directories are never overwritten.
"""
import argparse
import contextlib
from decimal import Decimal as D, localcontext
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
try:
    import numpy as np
    import scipy
    from scipy.optimize import lsq_linear
    from threadpoolctl import threadpool_info, threadpool_limits
    import phase2d_step38_verify as transport
    import phase2d_step40_validation as validation
except ImportError as exc:
    print(json.dumps(dict(execution_status='EXECUTION_FAILURE',error=str(exc))),file=sys.stderr)
    raise SystemExit(2) from exc

CASES = ('dense', 'row3', 'row4')
OPTIONS = dict(method='trf', lsq_solver='exact', bounds=(-1, 1), tol=1e-12, max_iter=1000)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def environment():
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
        scipy.show_config()
    repo = Path(__file__).resolve().parents[1]
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    files = ['scripts/phase2d_step42_replay.py', 'scripts/phase2d_step38_verify.py',
             'scripts/phase2d_step40_validation.py', 'configs/phase2c_quick.json']
    return dict(python=sys.version, executable=sys.executable, prefix=sys.prefix,
                base_prefix=sys.base_prefix, platform=platform.platform(), system=platform.system(),
                machine=platform.machine(), processor=platform.processor(), numpy=np.__version__,
                scipy=scipy.__version__, numerical_config=stream.getvalue(),
                loaded_threadpools=threadpool_info(), thread_environment={k: os.getenv(k) for k in
                ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_CORETYPE')},
                head=head, source_sha256={f: transport.sha(repo/f) for f in files})


def dec(value):
    if isinstance(value, D):
        if not value.is_finite():
            raise ValueError('Nonfinite Decimal')
        return value
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,float,np.integer,np.floating)):
        raise ValueError('Invalid numerical scalar')
    transport.number(float(value))
    return D.from_float(float(value))


def recovery(B, L, P, digits=90):
    with localcontext() as ctx:
        ctx.prec = digits
        B, L, P = map(dec, (B, L, P))
        gap, gain = L-B, L-P
        if abs(gap) <= D('1e-15'):
            raise ValueError('Original denominator guard')
        return dict(ratio=str(gain/gap), rms_T=list(map(str, (B,L,P))),
                    numerator_T=str(gain), denominator_T=str(gap),
                    derivatives_B_L_P=list(map(str, (gain/gap**2, (P-B)/gap**2, -1/gap))),
                    numerator_cancellation=str((abs(L)+abs(P))/abs(gain)) if gain else None,
                    denominator_cancellation=str((abs(L)+abs(B))/abs(gap)))


def metric(a, dense, recovered, failed, digits=90):
    """Direct Decimal forward field, energy, square root, quotient; binary64 inputs."""
    with localcontext() as ctx:
        ctx.prec = digits
        frozen = dense.copy()
        frozen[failed] = 0
        norms = []
        for amps in (dense, frozen, recovered):
            currents = list(map(dec, amps))
            energy = D(0)
            for row, b, w in zip(a['fine_A'], a['fine_b'], a['fine_weights']):
                residual = dec(b)+sum((dec(v)*x for v,x in zip(row,currents)), D(0))
                energy += dec(w)*residual**2
            norms.append(energy.sqrt())
        return recovery(*norms, digits=digits)


def differential(reference,candidate):
    with localcontext() as ctx:
        ctx.prec = 90
        B,L,P = map(D,reference['rms_T'])
        b,l,p = map(D,candidate['rms_T'])
        gap = L-B
        if abs(gap) <= D('1e-15'):
            raise ValueError('Original denominator guard')
        terms = [(L-P)*(b-B)/gap**2,(P-B)*(l-L)/gap**2,-(p-P)/gap]
        observed = D(candidate['ratio'])-D(reference['ratio'])
        return dict(terms_B_L_P=list(map(str,terms)),linear_prediction=str(sum(terms)),
                    observed=str(observed),nonlinear_remainder=str(observed-sum(terms)))


def certificate(M, y, x):
    M, y, x = validation.numeric(M,2), validation.numeric(y,1), validation.numeric(x,1)
    if M.shape != (len(y),len(x)):
        raise ValueError('Residual dimensions')
    with localcontext() as ctx:
        ctx.prec = 90
        rows = [list(map(dec,row)) for row in M]
        xx = list(map(dec,x))
        r = [sum((v*z for v,z in zip(row,xx)), D(0))-dec(b) for row,b in zip(rows,y)]
        g = [sum((row[j]*v for row,v in zip(rows,r)), D(0)) for j in range(len(x))]
        # Normal-map residual also handles TRF's strictly interior bound iterates.
        projected = [z-max(D(-1),min(D(1),z-v)) for z,v in zip(xx,g)]
        feasibility = max([D(0)]+[abs(z)-1 for z in xx])
        stationarity = max(map(abs,projected))
        return dict(objective=str(sum((v*v for v in r),D(0))/2),
                    feasibility=str(feasibility), stationarity=str(stationarity),
                    active_lower=np.flatnonzero(x == -1).tolist(), active_upper=np.flatnonzero(x == 1).tolist(),
                    verified=feasibility == 0 and stationarity <= D('1e-12'))


def load_capture(path, expected_sha=None):
    path = Path(path)
    source = path/'inputs.json'
    if expected_sha is not None and transport.sha(source) != transport.valid_digest(expected_sha):
        raise ValueError('Requested input SHA256 mismatch')
    transport.frozen_seal(transport.load(path/'input-sha256.json'), {'inputs.json':transport.sha(source)})
    data = transport.load(source)
    transport.frozen_seal(transport.load(path/'problem-sha256.json'),
                          {'sha256':transport.fingerprint(transport.problem(data))})
    sources = transport.load(path/'source-sha256.json')
    validation.source_check(sources, sources['head'], Path(__file__).resolve().parents[1])
    a = validation.reconstruct(data)
    # Check exact reconstruction separately from tolerant legacy validation.
    exact = {}
    for case in CASES:
        support = data['cases'][case].get('support',list(range(24)))
        M = np.vstack((np.sqrt(a['weights'])[:,None]*a['D'][:,support],
                       np.sqrt(data['config']['ridge'])*np.eye(len(support))))
        y = np.r_[-np.sqrt(a['weights'])*a['d'],np.zeros(len(support))]
        exact[case] = dict(M=bool(np.array_equal(M,a[case+'_M'])), y=bool(np.array_equal(y,a[case+'_y'])))
        if not all(exact[case].values()):
            raise ValueError('Exact matrix reconstruction mismatch')
    return data,a,dict(input_sha256=transport.sha(source),
                       problem_sha256=transport.fingerprint(transport.problem(data)),
                       source_head=sources['head'], source_map_sha256=transport.sha(path/'source-sha256.json'),
                       exact_reconstruction=exact)


def solve(M, y):
    # No x0 exists in lsq_linear. Saved vectors never initialize this solve.
    validation.numeric(M,2)
    validation.numeric(y,1)
    fit = lsq_linear(M, y, **OPTIONS)
    cert = certificate(M,y,fit.x)
    singular = np.linalg.svd(M,compute_uv=False)
    return fit, dict(x=fit.x.tolist(), x_binary64_le=fit.x.astype('<f8').tobytes().hex(),
                     cost=float(fit.cost), certificate=cert,
                     objective_difference=str(abs(dec(fit.cost)-D(cert['objective']))),
                     status=int(fit.status), success=bool(fit.success), nit=int(fit.nit),
                     message=str(fit.message), optimality=float(fit.optimality),
                     active_mask=fit.active_mask.tolist(), singular_values=singular.tolist(),
                     condition=float(singular[0]/singular[-1]),
                     passed=bool(fit.success) and cert['verified'] and
                     validation.agrees(fit.cost,D(cert['objective'])))


def replay(path, expected_sha=None):
    data,a,identity = load_capture(path,expected_sha)
    fresh, saved, results = {}, {}, {}
    for case in CASES:
        support = data['cases'][case].get('support',list(range(24)))
        fit, result = solve(a[case+'_M'],a[case+'_y'])
        fresh[case] = np.zeros(24)
        fresh[case][support] = fit.x*data['config']['imax_A']
        saved[case] = a[case+'_x']*data['config']['imax_A']
        result.update(currents_A=fresh[case].tolist(), support=support,
                      currents_A_binary64_le=fresh[case].astype('<f8').tobytes().hex(),
                      M_sha256=hashlib.sha256(a[case+'_M'].astype('<f8').tobytes()).hexdigest(),
                      y_sha256=hashlib.sha256(a[case+'_y'].astype('<f8').tobytes()).hexdigest(),
                      saved_certificate=certificate(a[case+'_M'],a[case+'_y'],a[case+'_x'][support]),
                      saved_currents_A=saved[case].tolist(),
                      current_delta_A=(fresh[case]-saved[case]).tolist(),
                      current_delta_max_A=float(np.max(abs(fresh[case]-saved[case]))),
                      projected_field_delta_max_T=float(np.max(abs(a['fine_A']@(fresh[case]-saved[case])))))
        results[case] = result
    ratios = {}
    for case in CASES[1:]:
        failed = data['cases'][case]['failed']
        f = metric(a,fresh['dense'],fresh[case],failed)
        old = metric(a,saved['dense'],saved[case],failed)
        low = metric(a,fresh['dense'],fresh[case],failed,60)
        with localcontext() as ctx:
            ctx.prec = 90
            delta = D(f['ratio'])-D(old['ratio'])
            rounding = dec(float(f['ratio']))-D(f['ratio'])
        # Controls change currents only, holding the exact A,b,w fixed.
        swaps = {label:metric(a,d,r,failed)['ratio'] for label,d,r in
                 [('dense_only',fresh['dense'],saved[case]), ('recovered_only',saved['dense'],fresh[case])]}
        ratios[case] = dict(fresh=f, saved=old, fresh_60=low, current_swaps=swaps,
                            sensitivity=differential(old,f),
                            delta_R=str(delta), pass_unchanged_tolerance=validation.agrees(D(f['ratio']),D(old['ratio'])),
                            final_binary64_rounding_delta=str(rounding))
    return dict(identity=identity, cases=results, recovery=ratios,
                execution_status='EXECUTED', diagnostic_pass=all(v['passed'] for v in results.values()))


def historical(paths):
    if not paths:
        return dict(status='MISSING_EVIDENCE', records=[])
    records, seen = [],set()
    for path in paths:
        path = Path(path).resolve()
        if path in seen:
            raise ValueError('Duplicate historical record')
        seen.add(path)
        value = transport.load(path)
        transport.comparison_record(value)
        if isinstance(value,list):
            for row in value:
                if isinstance(row,dict) and 'high_reference' in row:
                    candidate,reference = dec(D(row['high_candidate'])),dec(D(row['high_reference']))
                    if row.get('high_pass') != validation.agrees(candidate,reference):
                        raise ValueError('False high-precision scientific acceptance')
        records.append(dict(path=str(path),sha256=transport.sha(path),original=value))
    return dict(status='PRESERVED_UNCHANGED',records=records)


def saved_analysis(root):
    """Independently recompute all saved reciprocal currents, without solving them."""
    records = []
    for run in ('41256776296','41257645149'):
        folder = root/run
        index = transport.load(folder/'artifact-index.json')['artifacts']
        if len({r['id'] for r in index}) != len(index) or len({r['name'] for r in index}) != len(index):
            raise ValueError('Duplicate artifact records')
        artifacts = {r['name']:folder/('artifact-'+str(r['id'])) for r in index}
        for origin in transport.COHORTS:
            capture = artifacts[f'step33-capture-{origin}-{run}-1']
            data,a,identity = load_capture(capture)
            vectors, ratios, files = {},{},{}
            for worker in transport.COHORTS:
                replay_root = artifacts[f'step33-replay-{worker}-{run}-1']
                transport.manifest(replay_root/'manifest.json')
                sub = replay_root/origin
                if transport.sha(sub/'inputs.json') != identity['input_sha256']:
                    raise ValueError('Reciprocal input mismatch')
                file = sub/'result.json'
                files[worker] = transport.sha(file)
                value = transport.load(file)
                vectors[worker] = {case:validation.numeric(transport.unpack(value['solve']['currents_A'][case]),1) for case in CASES}
                for case,current in vectors[worker].items():
                    support = data['cases'][case].get('support',list(range(24)))
                    if current.shape != (24,) or any(current[i] != 0 for i in range(24) if i not in support):
                        raise ValueError('Invalid saved support/current vector')
                    certificate(a[case+'_M'],a[case+'_y'],current[support]/3000.)
                ratios[worker] = {case:metric(a,vectors[worker]['dense'],vectors[worker][case],data['cases'][case]['failed']) for case in CASES[1:]}
            reference = transport.COHORTS[0]
            for worker in transport.COHORTS[1:]:
                for case in CASES[1:]:
                    x,ref = vectors[worker],vectors[reference]
                    failed = data['cases'][case]['failed']
                    support = data['cases'][case]['support']
                    candidate,base = ratios[worker][case],ratios[reference][case]
                    with localcontext() as ctx:
                        ctx.prec = 90
                        delta = D(candidate['ratio'])-D(base['ratio'])
                    records.append(dict(run=run,origin=origin,worker=worker,case=case,
                        input_sha256=identity['input_sha256'],result_sha256=files[worker],reference_sha256=files[reference],
                        saved_candidate=candidate,saved_reference=base,delta_R=str(delta),
                        sensitivity=differential(base,candidate),
                        pass_unchanged_tolerance=validation.agrees(D(candidate['ratio']),D(base['ratio'])),
                        dense_current_delta_A=(x['dense']-ref['dense']).tolist(),
                        recovered_current_delta_A=(x[case]-ref[case]).tolist(),
                        projected_field_delta_max_T=float(np.max(abs(a['fine_A']@(x[case]-ref[case])))),
                        candidate_certificate=certificate(a[case+'_M'],a[case+'_y'],x[case][support]/3000.),
                        reference_certificate=certificate(a[case+'_M'],a[case+'_y'],ref[case][support]/3000.),
                        singular_values=np.linalg.svd(a[case+'_M'],compute_uv=False).tolist(),
                        dense_only_current_swap=metric(a,x['dense'],ref[case],failed),
                        recovered_only_current_swap=metric(a,ref['dense'],x[case],failed),
                        scope='Saved current evaluation; no optimizer execution'))
    return dict(records=records,failures={run:sum(not r['pass_unchanged_tolerance'] for r in records if r['run'] == run)
                                         for run in ('41256776296','41257645149')})


def verdict():
    return dict(scientific_comparison='FAIL', production_acceptance='FAIL',
                causal_root_cause='INCONCLUSIVE', scientific_status='PARTIAL')


def require_solve_record(value):
    if set(value.get('cases',{})) != set(CASES):
        raise ValueError('Missing solver cases')
    for row in value['cases'].values():
        cert = row['certificate']
        objective,primal,stationarity = (dec(D(cert[k])) for k in ('objective','feasibility','stationarity'))
        if (row['success'] is not True or row['passed'] is not True or cert['verified'] is not True
                or type(row['status']) is not int or row['status'] not in (1,2,3)
                or type(row['nit']) is not int or row['nit'] < 0 or not row['message']
                or primal != 0 or stationarity < 0 or stationarity > D('1e-12') or objective < 0
                or not validation.agrees(dec(row['cost']),objective)):
            raise ValueError('Invalid solver certificate/termination')
        currents = validation.numeric(row['currents_A'],1)
        if currents.shape != (24,) or np.any(abs(currents) > 3000):
            raise ValueError('Invalid bounded current vector')
        if currents.astype('<f8').tobytes().hex() != row['currents_A_binary64_le']:
            raise ValueError('Corrupt current binary64 transport')


def compare(root):
    """Require four complete workers and identical input sets before comparing."""
    workers = {}
    for worker in transport.COHORTS:
        folder = root/('step42-'+worker)
        status = transport.load(folder/'status.json')
        if status['errors'] or status['execution_status'] != 'EXECUTED' or len(status['results']) != 4:
            raise ValueError('Missing/incomplete worker '+worker)
        env = transport.load(folder/'environment.json')
        expected = ('2.3.5' if worker == transport.COHORTS[2] else '2.4.6',
                    '1.16.3' if worker == transport.COHORTS[3] else '1.17.1')
        if (env['numpy'],env['scipy']) != expected or env['system'] != ('Windows' if worker == transport.COHORTS[0] else 'Linux'):
            raise ValueError('Unexpected worker environment')
        if not env['loaded_threadpools'] or any(p['num_threads'] != 1 for p in env['loaded_threadpools']):
            raise ValueError('Missing one-thread numerical provenance')
        cells = {}
        for row in status['results']:
            file = transport.safe(folder,row['result'])
            if transport.sha(file) != row['sha256']:
                raise ValueError('Corrupt worker result')
            value = transport.load(file)
            require_solve_record(value)
            if value['identity']['source_head'] != env['head']:
                raise ValueError('Hosted runtime/capture source identity mismatch')
            # Origin labels are serialized separately: Windows path syntax must
            # never be interpreted using a Linux comparator's pathlib rules.
            key = row['origin']
            if key in cells or not value['diagnostic_pass']:
                raise ValueError('Duplicate origin or failed solver certificate')
            cells[key] = value
        workers[worker] = cells
    reference = workers[transport.COHORTS[0]]
    if set(reference) != {'step42-capture-'+c for c in transport.COHORTS}:
        raise ValueError('Missing required capture origins')
    comparisons = []
    for worker,cells in workers.items():
        if set(cells) != set(reference):
            raise ValueError('Missing origin')
        for origin,value in cells.items():
            ref = reference[origin]
            if value['identity'] != ref['identity']:
                raise ValueError('Reciprocal input/source identity mismatch')
            for case in CASES:
                candidate,base = value['cases'][case],ref['cases'][case]
                xx,yy = candidate['currents_A'],base['currents_A']
                if len(xx) != 24 or len(yy) != 24:
                    raise ValueError('Incomplete current vector')
                with localcontext() as ctx:
                    ctx.prec = 90
                    objective_delta = D(candidate['certificate']['objective'])-D(base['certificate']['objective'])
                comparisons.append(dict(worker=worker,origin=origin,case=case,kind='currents',
                    max_delta_A=max(abs(a-b) for a,b in zip(xx,yy)),objective_delta=str(objective_delta),
                    reference_stationarity=base['certificate']['stationarity'],
                    candidate_stationarity=candidate['certificate']['stationarity'],
                    pass_unchanged_tolerance=all(validation.agrees(a,b) for a,b in zip(xx,yy))))
            for case in CASES[1:]:
                x,y = D(value['recovery'][case]['fresh']['ratio']),D(ref['recovery'][case]['fresh']['ratio'])
                comparisons.append(dict(worker=worker,origin=origin,case=case,kind='recovery',reference=str(y),candidate=str(x),
                                        pass_unchanged_tolerance=validation.agrees(x,y)))
    return dict(**verdict(),comparisons=comparisons,
                fresh_comparison='FAIL' if any(not r['pass_unchanged_tolerance'] for r in comparisons) else 'PASS',
                scope='Fresh four-cohort experiment; historical production failure remains unchanged')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True,help='Capture directory, or root containing sealed captures')
    parser.add_argument('--input-sha256',help='Required identity for a single capture; seal always checked')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--history',type=Path,action='append',default=[])
    parser.add_argument('--compare',action='store_true')
    parser.add_argument('--expected-captures',type=int)
    args = parser.parse_args()
    root = Path(os.environ['STEP42_OUTPUT_ROOT']).resolve()
    out, source = args.output.resolve(),args.input.resolve()
    if (out == root or not out.is_relative_to(root) or out.is_relative_to(source)
            or source.is_relative_to(out) or any(p.resolve().is_relative_to(out) for p in args.history)):
        raise ValueError('Output must be a fresh child of STEP42_OUTPUT_ROOT, disjoint from inputs')
    out.mkdir(parents=True,exist_ok=False)
    state = dict(**verdict(),execution_status='EXECUTION_FAILURE',results=[],errors=[])
    try:
        with threadpool_limits(limits=1):
            write(out/'environment.json',environment())
            if sys.version_info[:2] != (3,11):
                raise ValueError('Existing Python 3.11 required')
            history = historical(args.history)
            write(out/'historical.json',history)
            if args.compare:
                write(out/'comparison.json',compare(source))
                state['execution_status'] = 'EXECUTED'
                state['results'].append(dict(result='comparison.json',sha256=transport.sha(out/'comparison.json')))
                captures = []
            else:
                captures = [source] if (source/'problem-sha256.json').is_file() else sorted(p.parent for p in source.rglob('problem-sha256.json'))
            if not args.compare and (not captures or (args.input_sha256 and len(captures) != 1)):
                raise ValueError('Missing captures or ambiguous input SHA256')
            if args.expected_captures is not None and len(captures) != args.expected_captures:
                raise ValueError('Missing required capture artifacts')
            for i,capture in enumerate(captures):
                try:
                    result = replay(capture,args.input_sha256)
                    name = f'replay-{i:02d}.json'
                    write(out/name,result)
                    state['results'].append(dict(capture=str(capture),origin=capture.name,result=name,sha256=transport.sha(out/name),
                                                 diagnostic_pass=result['diagnostic_pass']))
                except Exception as exc:
                    state['errors'].append(dict(capture=str(capture),error=repr(exc)))
            state['execution_status'] = 'EXECUTED' if not state['errors'] else 'INCOMPLETE'
            state['history_status'] = history['status']
            if not args.compare and all((source/run/'artifact-index.json').is_file() for run in ('41256776296','41257645149')):
                write(out/'saved-current-analysis.json',saved_analysis(source))
    except Exception as exc:
        state['errors'].append(dict(error=repr(exc)))
        state['execution_status'] = 'INCOMPLETE'
    write(out/'status.json',state)
    write(out/'manifest.json',{p.name:transport.sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    return 2 if state['errors'] or not state['results'] else 1


if __name__ == '__main__':
    try:
        code = main()
    except Exception as exc:
        # Rejected output paths are never written, even to record a failure.
        print(json.dumps(dict(**verdict(),execution_status='EXECUTION_FAILURE',error=repr(exc)),
                         sort_keys=True),file=sys.stderr)
        code = 2
    raise SystemExit(code)
