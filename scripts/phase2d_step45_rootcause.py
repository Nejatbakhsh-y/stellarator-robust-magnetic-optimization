"""STEP45 investigation coordinator; never promotes historical failures to PASS.

Exit 2: incomplete execution/invalid evidence. Exit 1: completed diagnostics,
historical scientific acceptance still FAIL. Reuses STEP38/40/42/44 explicitly.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import inspect
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
BASELINE = '3025749c1107acf8989231c91a4ed291d4cc81be'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def archive_identity(archive, expected_sha256, extracted):
    """Byte/coverage check only. Caller-supplied hashes do not prove GitHub origin."""
    if not re.fullmatch('[0-9a-f]{64}',expected_sha256) or sha(archive) != expected_sha256:
        raise ValueError('Incorrect original archive SHA256')
    members = {}
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename or ':' in entry.filename:
                raise ValueError('Unsafe archive member')
            if entry.is_dir():
                continue
            name = path.as_posix()
            if name in members:
                raise ValueError('Duplicate archive member')
            members[name] = hashlib.sha256(z.read(entry)).hexdigest()
    if not members or members != snapshot(extracted):
        raise ValueError('Original archive/extracted-file coverage or SHA256 mismatch')
    return dict(archive_sha256=expected_sha256,extracted_members=members,byte_identity='MATCH',
                github_origin='NOT_ESTABLISHED_BY_THIS_CHECK')


def policy(head, errors, blockers):
    return dict(diagnostic_status='INCOMPLETE' if errors else 'COMPLETE',
                scientific_comparison='FAIL', causal_root_cause='INCONCLUSIVE',
                evidence_authentication='INCOMPLETE', production_acceptance='FAIL',
                scientific_status='PARTIAL', remaining_blockers=list(blockers)+list(errors),
                source_commit=head, baseline_source_commit=BASELINE)


def output_path(root, output, sources):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root/'results') or output.exists():
        raise ValueError('Output must be a new isolated directory beneath repository results')
    for source in sources:
        source = source.resolve()
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError('Input/output overlap')
    return output


def kernels(M, y):
    """Diagnostic LAPACK interventions only; never replaces production TRF."""
    import numpy as np
    from scipy.linalg import lstsq, get_lapack_funcs
    import phase2d_step40_validation as v
    import phase2d_step42_replay as r
    refs = {str(d): v.qr_reference(M, y, d) for d in (60, 90)}
    initial = np.linalg.lstsq(M,y,rcond=-1)[0]
    records = {}
    for driver in ('gelsd', 'gelss', 'gelsy'):
        x, residual, rank, singular = lstsq(M, y, lapack_driver=driver)
        records[driver] = dict(x_binary64_le=x.astype('<f8').tobytes().hex(),
            x=x.tolist(), rank=int(rank), certificate=r.certificate(M,y,x),
            lapack_type=get_lapack_funcs(driver,(M,y)).typecode,
            singular_values=None if singular is None else singular.tolist())
        if 'x' in refs['90']:
            with localcontext() as ctx:
                ctx.prec = 90
                records[driver]['max_error_vs_decimal_qr'] = str(max(
                    abs(Decimal.from_float(float(z))-Decimal(q)) for z,q in zip(x,refs['90']['x'])))
    source = inspect.getsource(__import__('scipy.optimize', fromlist=['lsq_linear']).lsq_linear)
    # Retain the actual implementation, rather than assuming a particular dispatch.
    dispatch = [line.strip() for line in source.splitlines() if 'lstsq(' in line or 'lsq_solver ==' in line]
    return dict(decimal_qr=refs, conditioning=v.conditioning(M), lapack=records,
                numpy_lstsq_rcond_minus_one_binary64_le=initial.astype('<f8').tobytes().hex(),
                scipy_dispatch_lines=dispatch, scipy_solver_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                numpy_lstsq_signature=str(inspect.signature(np.linalg.lstsq)),
                scope='Same captured M/y; driver is the sole explicit intervention; kernel/CPU causality not established')


def array_identity(value):
    import phase2d_step40_validation as v
    import numpy as np
    array = np.asarray(value)
    array = v.numeric(array,array.ndim).astype('<f8')
    return dict(shape=list(array.shape),binary64_le_sha256=hashlib.sha256(array.tobytes(order='C')).hexdigest())


def recovery_controls(a, dense, recovered, candidate_dense, candidate_recovered, failed):
    """Exact-input current swap, independent Decimal RMS and binary64 reduction."""
    import numpy as np
    import phase2d_step42_replay as r
    base = r.metric(a,dense,recovered,failed)
    candidate = r.metric(a,candidate_dense,candidate_recovered,failed)
    with localcontext() as ctx:
        ctx.prec = 90
        delta = Decimal(candidate['ratio'])-Decimal(base['ratio'])
        def binary_metric(dense_vector,recovered_vector):
            rms = []
            frozen = dense_vector.copy(); frozen[failed] = 0
            for x in (dense_vector,frozen,recovered_vector):
                residual = a['fine_b']+a['fine_A']@x
                rms.append(float(np.sqrt(np.sum(a['fine_weights']*residual**2))))
            checked = r.recovery(*rms)
            checked['native_binary64_ratio'] = (rms[1]-rms[2])/(rms[1]-rms[0])
            return checked
        binary = binary_metric(candidate_dense,candidate_recovered)
        binary_base = binary_metric(dense,recovered)
        observed = Decimal.from_float(binary['native_binary64_ratio'])-Decimal.from_float(binary_base['native_binary64_ratio'])
        arithmetic = observed-delta
        effect = r.differential(base,candidate)
        return dict(reference=base,candidate=candidate,
            dense_only=r.metric(a,candidate_dense,recovered,failed),
            recovered_only=r.metric(a,dense,candidate_recovered,failed),
            controlled_current_contribution=str(delta), field_matrix_contribution='0',
            disturbance_contribution='0', weight_contribution='0',
            reduction_contribution='NOT_ISOLATED: field products, reductions, roots and quotient evaluated together',
            binary64_evaluation_contribution=str(arithmetic), observed_binary64_delta=str(observed),
            exact_intervention_closure_remainder=str(observed-delta-arithmetic),
            binary64_reduction=binary,binary64_reference_reduction=binary_base,differential=effect,
            remaining_nonlinear_contribution=effect['nonlinear_remainder'],
            scope='Exact current intervention plus aggregate binary64 evaluation closes observed delta; nonlinear remainder belongs only to the separate first-order model. Pure reduction-order causality not isolated. A,b,w identical.')


def investigate(capture):
    import numpy as np
    import phase2d_step42_replay as r
    data,a,identity = r.load_capture(capture)
    if data['cases']['row3']['failed'] != 3 or data['cases']['row4']['failed'] != 6:
        raise ValueError('Unexpected independent fault identities')
    result = r.replay(capture,identity['input_sha256'])
    independent = {case:kernels(a[case+'_M'],a[case+'_y']) for case in r.CASES}
    construction = {'D':a['A']*data['config']['imax_A']/data['config']['bref_T'],
                    'd':a['b']/data['config']['bref_T']}
    construction_identity = {name:dict(saved=array_identity(a[name]),reconstructed=array_identity(value),
                            equal_bytes=array_identity(a[name]) == array_identity(value))
                             for name,value in construction.items()}
    for case in r.CASES:
        old = np.asarray(a[case+'_x'])[result['cases'][case]['support']].astype('<f8')
        fresh = np.asarray(result['cases'][case]['x'],dtype='<f8')
        different = np.flatnonzero(old.view('<u8') != fresh.view('<u8'))
        independent[case]['first_saved_fresh_current_byte_divergence'] = (
            None if not len(different) else dict(support_coordinate=int(different[0]),
                saved_hex=float(old[different[0]]).hex(),fresh_hex=float(fresh[different[0]]).hex()))
        independent[case]['scope'] = 'M/y exact identity precedes this observed output divergence; internal kernel operation not localized'
        independent[case]['numpy_initial_equals_trf_bytes'] = (
            independent[case]['numpy_lstsq_rcond_minus_one_binary64_le'] == result['cases'][case]['x_binary64_le'])
        independent[case]['driver_equals_trf_bytes'] = {
            driver:record['x_binary64_le'] == result['cases'][case]['x_binary64_le']
            for driver,record in independent[case]['lapack'].items()}
    recovery = {}
    for case in ('row3','row4'):
        recovery[case] = recovery_controls(a,a['dense_x']*3000,a[case+'_x']*3000,
            np.asarray(result['cases']['dense']['currents_A']),
            np.asarray(result['cases'][case]['currents_A']),data['cases'][case]['failed'])
    return dict(identity=identity,replay=result,independent=independent,
                array_construction=construction_identity,
                arrays={name:array_identity(value) for name,value in a.items()}), recovery


def reciprocal(source, root, head):
    """Bind complete worker manifests/environment before inherited comparisons."""
    import phase2d_step38_verify as t
    import phase2d_step42_replay as r
    import phase2d_step44_acceptance as h
    for cohort in t.COHORTS:
        folder = source/('step42-'+cohort)
        seal = h.manifest_check(folder/'manifest.json')
        if not seal['complete']:
            raise ValueError('Incomplete worker manifest: '+cohort)
        env = t.load(folder/'environment.json')
        if not env['python'].startswith('3.11.') or env['head'] != head:
            raise ValueError('Worker Python/source identity mismatch: '+cohort)
        for name,digest in env['source_sha256'].items():
            if sha(t.safe(root,name)) != digest:
                raise ValueError('Worker runtime source fingerprint mismatch: '+name)
    result = r.compare(source)
    workers = {}
    for cohort in t.COHORTS:
        folder = source/('step42-'+cohort)
        workers[cohort] = {row['origin']:t.load(t.safe(folder,row['result']))
                           for row in t.load(folder/'status.json')['results']}
    interventions = []
    import numpy as np
    for origin in t.COHORTS:
        key = 'step42-capture-'+origin
        capture = source/'captures'/key
        data,a,identity = r.load_capture(capture)
        for worker in t.COHORTS:
            if workers[worker][key]['identity'] != identity:
                raise ValueError('Comparison capture/worker identity mismatch')
        # All directed contrasts also compare the two Linux sensitivity cohorts.
        for reference in t.COHORTS:
            for worker in t.COHORTS:
                base,candidate = workers[reference][key],workers[worker][key]
                for case in ('row3','row4'):
                    amps = lambda record,k: np.asarray(record['cases'][k]['currents_A'])
                    controls = recovery_controls(a,amps(base,'dense'),amps(base,case),
                        amps(candidate,'dense'),amps(candidate,case),data['cases'][case]['failed'])
                    controls.update(origin=origin,reference_worker=reference,worker=worker,case=case,
                        input_sha256=identity['input_sha256'],
                        pass_unchanged_tolerance=r.validation.agrees(Decimal(controls['candidate']['ratio']),
                                                                   Decimal(controls['reference']['ratio'])))
                    interventions.append(controls)
    result['directed_recovery_interventions'] = interventions
    return result


def historical(root):
    import phase2d_step44_acceptance as h
    import phase2d_step38_verify as t
    evidence, inventory = root/h.EVIDENCE, root/h.STEP41
    rows,corrections = h.bind_comparisons(t.load(inventory/'recomputed-comparisons.json'),evidence)
    counts = [sum(not row['pass'] for row in rows if row['run']==run) for run in t.RUNS[2:]]
    if counts != [21,11]:
        raise ValueError('Historical failure classifications changed')
    early = h.early_records(t.load(inventory/'early-failures.json'),evidence)
    integrity = {}
    for name,base in (('downloaded-files.sha256',evidence),('historical-before.sha256',root)):
        checks = t.hash_list(evidence/name,base)
        if not all(c['match'] for c in checks):
            raise ValueError('Historical file integrity mismatch')
        integrity[name] = checks
    return dict(comparisons=rows,serialization_corrections=corrections,
                preceding_failures=21,latest_failures=11,earlier_scalar_paths=early,
                integrity=integrity,original_zip_authentication='MISSING_EVIDENCE',
                metadata_scope='Retained local records; not a fresh GitHub metadata verification')


def report(status,env,solvers,recoveries,cause):
    """Standalone verdict with explicit pointers to sealed numerical records."""
    sections = [
        ('SOURCE COMMIT',status['source_commit']+'; baseline '+BASELINE),
        ('EXECUTION ENVIRONMENT',json.dumps(env,sort_keys=True)),
        ('ORIGINAL EVIDENCE INVENTORY','See input-manifest.json and causal-attribution.json; original ZIP authentication remains incomplete.'),
        ('INPUT IDENTITY VERIFICATION','Capture file/problem/source seals and exact reconstructed M/y are required before solving. See solver-comparisons.json. No approximate inputs are substituted.'),
        ('FOUR-ENVIRONMENT NUMERICAL COMPARISON',
         str(solvers.get('reciprocal',{}).get('fresh_comparison','MISSING_EVIDENCE: complete reciprocal hosted matrix'))),
        ('INDEPENDENT HIGH-PRECISION SOLVER REFERENCE','Reused twice-orthogonalized Decimal QR, 60/90 digits; driver-specific records and uncertified-boundary limitations in solver-comparisons.json.'),
        ('FAULT ROW 3 ANALYSIS','Failed coil 3; separate original/fresh current, QR, KKT and recovery records in solver-comparisons.json and recovery-comparisons.json. Unexecuted cases provide no new numerical evidence.'),
        ('FAULT ROW 4 ANALYSIS','Failed coil 6; independent records in the same two files. Row3 agreement cannot confer row4 acceptance.'),
        ('RECOVERY-RATIO SENSITIVITY','90-digit direct field/RMS quotients, exact current swaps, derivative terms and nonlinear remainder retained separately. Pure reduction-order effect NOT_ISOLATED.'),
        ('NUMERICAL KERNEL ATTRIBUTION','INCONCLUSIVE. Same-input LAPACK SVD/QR controls are diagnostic; no isolated CPU/FMA/BLAS root cause established.'),
        ('INDEPENDENT FIELD VALIDATION','No fresh independent geometry integral in this coordinator; retained STEP40 checks do not replace final-source README gates.'),
        ('HISTORICAL FAILURE PRESERVATION','11 latest, 21 preceding, 22 earlier scalar paths remain distinct. Original SHA inventories and pre/post snapshots are checked where available; see causal-attribution.json.'),
        ('REGRESSION RESULTS','Not inferred from this assessment. Separate final-source pytest/compile/dependency and README hash-bound records are mandatory.'),
        ('HOSTED EXPERIMENT STATUS','Fresh matrix is required; locally replayed captures do not create missing hosted cohorts.'),
        ('CAUSAL ROOT-CAUSE VERDICT',status['causal_root_cause']),
        ('SCIENTIFIC COMPARISON VERDICT',status['scientific_comparison']),
        ('PRODUCTION ACCEPTANCE',status['production_acceptance']),
        ('OVERALL SCIENTIFIC STATUS',status['scientific_status']),
        ('REMAINING SCIENTIFIC BLOCKERS','\n'.join('- '+v for v in status['remaining_blockers'])),
    ]
    return '# STEP45 independent causal investigation\n\n'+'\n\n'.join('## '+title+'\n\n'+body for title,body in sections)+'\n'


def main(argv=None):
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--input',type=Path,help='Optional fresh sealed captures or STEP42 worker root')
    p.add_argument('--compare',action='store_true',help='Validate fresh reciprocal STEP42 worker evidence')
    args = p.parse_args(argv)
    root = args.root.resolve()
    if not (root/'AGENTS.md').is_file() or root != Path(__file__).resolve().parents[1]:
        raise ValueError('Root must identify this research checkout')
    source = args.input.resolve() if args.input else root/'results/phase2d/step38-independent-verification-20261101-084216-7bda80b7'
    protected = [source,root/'results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c']
    out = output_path(root,args.output,protected)
    out.mkdir(parents=True,exist_ok=False)
    errors,solvers,recoveries = [],{},{}
    blockers = ['MISSING_EVIDENCE: original authenticated historical ZIP bytes',
                'Unique upstream numerical kernel causality not established',
                'Historical scientific FAIL remains; fresh comparisons cannot replace it',
                'Final-source README gates and clean-checkout execution required',
                'No physical-model or confinement validation']
    env = dict(python=sys.version,execution='NOT_EXECUTED')
    head = subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
    before = {str(folder):snapshot(folder) for folder in protected}
    inputs = {str(folder):files for folder,files in before.items()}
    cause = dict(kernel_causality='INCONCLUSIVE',first_divergence='NOT_ESTABLISHED',
                 legitimate_floating_point_variation='Not proven or excluded',
                 historical_failure_inventories='11 latest, 21 preceding, 22 earlier: separate inventories')
    try:
        if subprocess.run(['git','merge-base','--is-ancestor',BASELINE,head],cwd=root).returncode != 0:
            raise ValueError('Source does not descend from requested baseline commit')
        import phase2d_step42_replay as r
        if sys.version_info[:2] != (3,11):
            raise ValueError('Python 3.11 required')
        with r.threadpool_limits(limits=1):
            env = dict(r.environment(),execution='EXECUTED',utc=datetime.now(timezone.utc).isoformat())
            import contextlib
            import io
            import numpy as np
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                np.show_runtime()
            env['numpy_runtime_cpu_features'] = stream.getvalue()
            if args.compare:
                solvers['reciprocal'] = reciprocal(source,root,head)
                recoveries['reciprocal'] = solvers['reciprocal']['directed_recovery_interventions']
            else:
                captures = sorted(p.parent for p in source.rglob('problem-sha256.json') if (p.parent/'input-sha256.json').is_file())
                if not captures:
                    raise FileNotFoundError('MISSING_EVIDENCE: sealed captured inputs')
                for i,capture in enumerate(captures):
                    try:
                        solvers[str(i)],recoveries[str(i)] = investigate(capture)
                    except Exception as exc:
                        errors.append(str(capture)+': '+repr(exc))
                blockers.append('MISSING_EVIDENCE: fresh four-cohort reciprocal comparisons')
            if not args.input:
                cause['historical'] = historical(root)
    except (Exception,SystemExit) as exc:
        errors.append(repr(exc))
    for folder in protected:
        if snapshot(folder) != before[str(folder)]:
            errors.append('Historical/input evidence changed during assessment: '+str(folder))
    status = policy(head,errors,blockers)
    status['experiment_utc'] = datetime.now(timezone.utc).isoformat()
    status['errors'] = errors
    for name,value in [('status',status),('environment',env),('input-manifest',inputs),
                       ('solver-comparisons',solvers),('recovery-comparisons',recoveries),('causal-attribution',cause)]:
        write(out/(name+'.json'),value)
    (out/'scientific-report.md').write_text(report(status,env,solvers,recoveries,cause),encoding='utf-8')
    source_files = list((root/'scripts').glob('phase2d*.py'))+list((root/'src').rglob('*.py'))
    source_files += [root/'tests/test_phase2d_step45_rootcause.py',
                     root/'.github/workflows/phase2d-step45-causal.yml',root/'docs/PHASE2D_STEP45_ROOT_CAUSE.md',
                     root/'configs/phase2c_quick.json',root/'pyproject.toml',root/'requirements-tested.txt']
    write(out/'output-manifest.json',dict(schema='step45-noncircular-v1',outputs=snapshot(out),
          source_sha256={str(p.relative_to(root)):sha(p) for p in sorted(source_files)}))
    return 2 if errors else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('STEP45 rejected execution: '+repr(exc),file=sys.stderr)
        raise SystemExit(2)
