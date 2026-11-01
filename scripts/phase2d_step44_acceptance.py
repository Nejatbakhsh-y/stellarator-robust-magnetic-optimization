"""Read-only STEP44 acceptance of the existing, historically failed experiment.

Exit 1 is an honest completed/partial assessment; exit 2 is corrupt input or
execution failure. This historical protocol cannot promote a new local solve to
production acceptance. STEP38 transport, STEP40 diagnostics and STEP42 exact
capture/replay are explicitly reused, never called independent new arithmetic.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
import phase2d_step38_verify as transport
import phase2d_step41_acceptance as prior

SOURCE_COMMIT = 'cb4fd64da725fe35d8286f1f8842077d68e07bdb'
BASE = 'results/phase2d/'
EVIDENCE = BASE+'step38-independent-verification-20261101-084216-7bda80b7'
STEP41 = BASE+'step41-final-acceptance-20261101-110323-7fe7248c'
STEP42 = BASE+'step42-reproducibility-20261101-120046-d90ebceb'
RTOL, ATOL, GUARD = map(Fraction, ('1e-11', '1e-13', '1e-15'))
HEADS = dict(zip(transport.RUNS, (
    'ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7',
    '11c2b1347c7b5359bec0a56e95cc2aa46f03660c',
    'cf77cf5466beadec7bd273e5c72ce9732cf253a7',
    '1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9')))
BLOCKERS = [
    'Historical scientific comparisons remain FAIL (11 latest, 21 preceding; 22 earlier scalar paths separately)',
    'MISSING_EVIDENCE: authenticated original archive bytes for all historical artifacts',
    'Four early manifest coverage gaps and historical workflow/source provenance gaps',
    'MISSING_EVIDENCE: fresh exact-input reciprocal SciPy execution on both operating systems',
    'Unique upstream numerical kernel cause has not been demonstrated',
    'Final-source passing README/test/audit/reproducibility records bound to fresh results are required',
    'Physical-model/device/confinement validation is outside this synthetic benchmark',
]


def rational(value):
    """Exact binary64 or explicitly decimal reference, without ambient rounding."""
    if type(value) not in (int, float, str, Decimal, Fraction):
        raise ValueError('Invalid numerical scalar')
    try:
        return Fraction(value)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError('Nonfinite/invalid numerical scalar') from exc


def text_number(value, digits=100):
    value = rational(value)
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def agrees(candidate, reference):
    a, b = map(rational, (candidate, reference))
    return abs(a-b) <= ATOL+RTOL*abs(b)


def recovery(B, L, P):
    """New exact rational quotient/derivatives, independent of prior helpers."""
    B, L, P = map(rational, (B, L, P))
    gap, gain = L-B, L-P
    if abs(gap) <= GUARD:
        raise ValueError('Original denominator guard 1e-15 T')
    gradient = [gain/gap**2, (P-B)/gap**2, -1/gap]
    # Independently derive basis coefficients from the quotient rule.
    derived = [((dl-dp)*gap-gain*(dl-db))/gap**2
               for db, dl, dp in ((1,0,0), (0,1,0), (0,0,1))]
    if derived != gradient:
        raise ValueError('Derivative identity disagreement')
    return dict(ratio=text_number(gain/gap), exact_ratio=str(gain/gap),
                rms_B_L_P=list(map(text_number, (B,L,P))),
                numerator_T=text_number(gain), denominator_T=text_number(gap),
                derivatives_B_L_P=list(map(text_number, gradient)),
                numerator_cancellation=text_number((abs(L)+abs(P))/abs(gain)) if gain else None,
                denominator_cancellation=text_number((abs(L)+abs(B))/abs(gap)))


def mathematics():
    rows = []
    for values in ((1,3,2), (0,2,3), (-2,-5,1),
                   ('0.000025914425556311052','0.000025914480221164456','0.000025914502890077691')):
        row = recovery(*values)
        B,L,P = map(rational, values)
        h = abs(L-B)/10**20
        fd = []
        for j, g in enumerate(row['derivatives_B_L_P']):
            u,v = [B,L,P], [B,L,P]
            u[j] += h
            v[j] -= h
            f = lambda z: (z[1]-z[2])/(z[1]-z[0])
            slope = (f(u)-f(v))/(2*h)
            if abs(slope-rational(g)) > max(1,abs(rational(g)))*Fraction('2e-40'):
                raise ValueError('Independent rational finite difference failed')
            fd.append(text_number(slope))
        rows.append(dict(row, finite_difference_B_L_P=fd))
    return dict(method='New exact Fraction quotient rule and rational central differences', cases=rows)


def metric(A, b, w, dense, recovered, failed, digits=100):
    """New direct scalar Decimal RMS; no NumPy/production reduction helper.

    Binary64 observations are converted exactly. Precision is significant digits,
    not a formal interval bound. Repeated 70/100-digit results are retained.
    """
    if len(A) != len(b) or len(b) != len(w) or not len(A):
        raise ValueError('Field dimensions')
    if len(dense) != len(recovered) or not 0 <= failed < len(dense):
        raise ValueError('Current dimensions')
    def dec(v):
        if hasattr(v,'item'):
            v = v.item()
        q = rational(v)
        return Decimal(q.numerator)/Decimal(q.denominator)
    with localcontext() as ctx:
        ctx.prec = digits
        rows = [[dec(v) for v in row] for row in A]
        if any(len(row) != len(dense) for row in rows):
            raise ValueError('Matrix dimensions')
        weights = list(map(dec,w))
        if any(v < 0 for v in weights) or sum(weights) <= 0:
            raise ValueError('Invalid weights')
        disturbance = list(map(dec,b))
        frozen = list(dense)
        frozen[failed] = 0
        rms = []
        for vector in (dense, frozen, recovered):
            x = list(map(dec,vector))
            energy = sum((weight*(offset+sum((a*z for a,z in zip(row,x)),Decimal(0)))**2
                          for row,offset,weight in zip(rows,disturbance,weights)),Decimal(0))
            rms.append(energy.sqrt())
        return dict(recovery(*rms), significant_digits=digits)


def manifest_check(path):
    """Missing coverage is incomplete; false hashes/unsafe paths are corruption."""
    expected = transport.load(path)
    if not isinstance(expected,dict) or not expected:
        raise ValueError('Empty manifest')
    missing = []
    for name,digest in expected.items():
        target = transport.safe(path.parent,name)
        transport.valid_digest(digest)
        if not target.is_file():
            missing.append(name)
        elif transport.sha(target) != digest:
            raise ValueError('Incorrect SHA256: '+str(target))
    actual = {p.relative_to(path.parent).as_posix() for p in path.parent.rglob('*')
              if p.is_file() and p != path}
    omitted = sorted(actual-set(expected))
    return dict(path=str(path),sha256=transport.sha(path), missing=missing,omitted=omitted,
                complete=not missing and not omitted)


def source_identity(root):
    head = subprocess.run(['git','rev-parse','HEAD'],cwd=root,check=True,
                          capture_output=True,text=True).stdout.strip()
    if head != SOURCE_COMMIT:
        raise ValueError('Incorrect source commit: '+head)
    return head


def capture_identity(identity,run,digest):
    transport.valid_digest(digest)
    if (run not in HEADS or identity.get('source_head') != HEADS[run]
            or identity.get('input_sha256') != digest):
        raise ValueError('Incorrect solver-input/source identity')


def bind_comparisons(rows, evidence):
    """Build a separately verified record; never assert unequal scalars equal.

    Only the hash-pinned historical inventory authorizes the demonstrated
    Windows PowerShell Decimal-to-Double transcription. All source seals and
    the unchanged STEP41 binder remain mandatory.
    """
    inventory = evidence.parents[0]/Path(STEP41).name/'recomputed-comparisons.json'
    if transport.sha(inventory) != '3847225855df15864ef0a4668b15f0684b1b25847e7c0d4bc71fd9e117fac719':
        raise ValueError('Historical comparison inventory SHA256 mismatch')
    historical = transport.load(inventory)
    tokens = json.loads(inventory.read_text(encoding='utf-8-sig'), parse_float=str)
    normalized = []
    corrections = []
    for raw in rows:
        prior.comparison(raw)
        row = dict(raw)
        if (row['run'] not in transport.RUNS[2:] or row['origin'] not in transport.COHORTS
                or row['worker'] not in transport.COHORTS[1:] or row['case'] not in ('row3','row4')):
            raise ValueError('Incorrect comparison identity')
        for worker, key in ((row['worker'], 'candidate'),
                            (transport.COHORTS[0], 'reference')):
            folder = evidence/'github-hosted'/row['run']
            index = transport.load(folder/'artifact-index.json')['artifacts']
            matches = [a for a in index if a['name'] ==
                       f"step33-replay-{worker}-{row['run']}-1"]
            if len(matches) != 1:
                raise ValueError('Missing or duplicate replay artifact identity')
            file = folder/('artifact-'+str(matches[0]['id']))/row['origin']/'result.json'
            seal = 'result_sha256' if key == 'candidate' else 'reference_sha256'
            if (transport.sha(file) != row[seal] or
                    transport.sha(file.parent/'inputs.json') != row['input_sha256']):
                raise ValueError('Reciprocal replay fingerprint mismatch')
            actual = transport.load(file)['solve']['recovery'][row['case']]['fractional_recovery']
            identity = tuple(row[k] for k in ('run','origin','worker','case'))
            positions = [i for i,r in enumerate(historical)
                         if tuple(r[k] for k in ('run','origin','worker','case')) == identity]
            if len(positions) != 1:
                raise ValueError('Incorrect comparison identity')
            i = positions[0]
            saved_token = json.loads(file.read_text(encoding='utf-8-sig'), parse_float=str)['solve']['recovery'][row['case']]['fractional_recovery']
            source_token = tokens[i][key]
            unequal = prior.scalar(row[key]) != prior.scalar(actual)
            if unequal and not (raw == historical[i] and key == 'candidate'
                    and identity == ('41257645149','windows-reference','linux-reference','row3')
                    and source_token == '-0.414688997078806'
                    and saved_token == '-0.41468899707880597'):
                raise ValueError('Comparison scalar differs from original result')
            if raw == historical[i] and str(source_token) != str(saved_token):
                with localcontext() as ctx:
                    ctx.prec = 1100
                    difference = str(prior.scalar(actual)-prior.scalar(row[key]))
                    token_difference = str(Decimal(str(saved_token))-Decimal(str(source_token)))
                corrections.append(dict(run=row['run'], origin=row['origin'], worker=worker,
                    case=row['case'], scalar=key, retained=row[key], original=actual,
                    original_scalar_token=source_token, saved_scalar_token=saved_token,
                    exact_difference=difference, exact_decimal_token_difference=token_difference,
                    binary64_equal=not unequal, original_binary64=float(row[key]).hex(),
                    saved_binary64=float(actual).hex(), source_path=str(file),
                    result_sha256=transport.sha(file), input_sha256=row['input_sha256'],
                    comparison_source_path=str(inventory), comparison_source_sha256=transport.sha(inventory),
                    conversion_method='Original JSON token -> Python correctly rounded binary64',
                    reason='Derived PowerShell inventory representation; original retained separately',
                    retained_record=dict(raw)))
                row[key] = actual
        # Revalidate both retained and original classifications; no relabelling.
        prior.comparison(raw)
        normalized.append(row)
    return prior.bind_comparisons(normalized, evidence), corrections


def early_records(rows, evidence):
    if not isinstance(rows,list) or len(rows) != 22:
        raise ValueError('Incomplete early failure inventory')
    seen = set()
    for row in rows:
        key = (row['run'],row['original_file'],row['path'])
        if key in seen or row['run'] not in transport.RUNS[:2]:
            raise ValueError('Duplicate/invalid early failure')
        seen.add(key)
        # This legacy inventory alone uses Windows separators; normalize explicitly.
        name = row['original_file'].replace('\\','/')
        file = transport.safe(evidence/'github-hosted'/row['run'],name)
        if transport.sha(file) != transport.valid_digest(row['sha256']):
            raise ValueError('Early failure SHA256 mismatch')
        if row.get('fail') is not True or agrees(row['candidate'],row['reference']):
            raise ValueError('Unresolved historical failure relabelled')
    return rows


def policy(blockers=(), corrupt=(), failures=True):
    # These are immutable historical failures, not a general-purpose PASS switch.
    return dict(schema='phase2d-step44-acceptance-v1',
                diagnostic_status='INCOMPLETE' if blockers or corrupt else 'COMPLETE',
                scientific_comparison='FAIL' if failures else 'INCONCLUSIVE',
                causal_root_cause='INCONCLUSIVE', evidence_authentication='INCOMPLETE',
                production_acceptance='FAIL', scientific_status='PARTIAL',
                remaining_blockers=sorted(set(BLOCKERS+list(blockers)+list(corrupt))),
                source_commit=SOURCE_COMMIT)


def reject_claims(claim):
    for key,value in policy().items():
        if key in ('scientific_comparison','causal_root_cause','evidence_authentication',
                   'production_acceptance','scientific_status') and claim.get(key) != value:
            raise ValueError('Unsupported scientific acceptance: '+key)


def output_path(root, output):
    root, output = root.resolve(), output.resolve()
    area = root/'results/phase2d'
    if output == area or not output.is_relative_to(area):
        raise ValueError('Output must be new under repository results/phase2d')
    # Never write inside or around any pre-existing scientific directory. A new
    # child of an empty user-provided stage container is allowed.
    for child in area.iterdir() if area.is_dir() else ():
        if child.is_dir() and (output.is_relative_to(child) or child.is_relative_to(output)):
            if any(child.iterdir()) and not child.name.startswith('step44-'):
                raise ValueError('Output overlaps existing scientific evidence')
            if child.name.startswith('step44-'):
                for existing in child.iterdir():
                    if output.is_relative_to(existing.resolve()) or existing.resolve().is_relative_to(output):
                        raise ValueError('Output overlaps existing STEP44 evidence')
    if output.exists():
        raise ValueError('Output must be new')
    return output


def write(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


def report(status, data):
    headings = [
        ('EXECUTION ENVIRONMENT',data.get('environment')),
        ('SOURCE COMMIT',status['source_commit']),
        ('EVIDENCE INVENTORY',data.get('inventory')),
        ('ORIGINAL ARTIFACT AUTHENTICATION','INCOMPLETE. Offline extracted hashes and saved/live metadata do not authenticate original ZIP bytes.'),
        ('INDEPENDENT SOLVER VERIFICATION',data.get('fresh_solver')),
        ('FOUR-ENVIRONMENT COMPARISON',data.get('matrix')),
        ('INDEPENDENT MAGNETIC-FIELD VALIDATION',data.get('field_validation')),
        ('FAULT ROW 3',data.get('faults',{}).get('row3')),
        ('FAULT ROW 4',data.get('faults',{}).get('row4')),
        ('RECOVERY-RATIO SENSITIVITY',data.get('mathematics')),
        ('NUMERICAL ROOT-CAUSE ATTRIBUTION','INCONCLUSIVE. Cancellation amplifies field/current rounding; OS/library/BLAS/LAPACK factors remain confounded.'),
        ('HISTORICAL FAILURE PRESERVATION',data.get('failure_counts')),
        ('TARGETED REGRESSION RESULTS','MISSING_EVIDENCE: this command does not run or certify pytest.'),
        ('COMPLETE REGRESSION RESULTS','MISSING_EVIDENCE: successful software tests cannot establish numerical or physical acceptance.'),
        ('SCIENTIFIC COMPARISON STATUS',status['scientific_comparison']),
        ('PRODUCTION ACCEPTANCE',status['production_acceptance']),
        ('OVERALL SCIENTIFIC STATUS',status['scientific_status']),
        ('REMAINING BLOCKERS',status['remaining_blockers'])]
    result = '# STEP44 independent acceptance\n\n'
    result += 'Synthetic planar-coil benchmark; finite-scenario minimax and small holdouts establish neither general robust outperformance nor confinement/device validation.\n\n'
    result += 'Input/output byte identities are in evidence-manifest.json. Reused STEP38/40/41/42 helpers are identified there. New rational mathematics and scalar RMS do not reuse production arithmetic.\n\n'
    for title,value in headings:
        result += '## '+title+'\n\n'+('MISSING_EVIDENCE' if value is None else json.dumps(value,sort_keys=True,indent=2))+'\n\n'
    return result


def assess(root, out):
    blockers, corrupt, inputs, indices = [], [], {}, {}
    data = dict(environment=dict(python=sys.version, executable=sys.executable,
                                platform=platform.platform(),cpu=platform.processor()),
                matrix={k:'MISSING_EVIDENCE: fresh execution on required OS' for k in 'ABCD'},
                fresh_solver='MISSING_EVIDENCE',faults={},failure_counts={},inventory={})
    def record(path):
        inputs[path.relative_to(root).as_posix()] = transport.sha(path)
    try:
        source_identity(root)
        if sys.version_info[:2] != (3,11):
            raise ValueError('Existing Python 3.11 environment required')
        data['mathematics'] = mathematics()
        e, h = root/EVIDENCE, root/STEP41
        # Reuse strict source/result binding; the new exact comparison also checks
        # every scalar's classification without trusting stored PASS labels.
        rows, corrections = bind_comparisons(transport.load(h/'recomputed-comparisons.json'),e)
        data['derived_inventory_serialization_corrections'] = corrections
        for row in rows:
            if agrees(row['candidate'],row['reference']) != row['pass'] or agrees(row['high_candidate'],row['high_reference']) != row['high_pass']:
                raise ValueError('Incorrect scientific comparison label')
        data['historical_comparisons'] = rows
        record(h/'recomputed-comparisons.json')
        data['earlier_scalar_paths'] = early_records(transport.load(h/'early-failures.json'),e)
        record(h/'early-failures.json')
        data['failure_counts'] = {run:{case:sum(not r['pass'] for r in rows if r['run']==run and r['case']==case)
                                     for case in ('row3','row4')} for run in transport.RUNS[2:]}
        if [sum(data['failure_counts'][run].values()) for run in transport.RUNS[2:]] != [21,11]:
            raise ValueError('Historical failure inventory changed')
        for case in ('row3','row4'):
            data['faults'][case] = [r for r in rows if r['case']==case and not r['pass']]
        data['inventory']['early_scalar_paths'] = 22
        manifests = []
        for path in sorted((e/'github-hosted').rglob('manifest.json')):
            check = manifest_check(path)
            manifests.append(check)
            if not check['complete']:
                blockers.append('Incomplete historical manifest: '+str(path.relative_to(root)))
        data['manifests'] = manifests
        for name in ('downloaded-files.sha256','historical-before.sha256'):
            path = e/name
            checks = transport.hash_list(path,e if name=='downloaded-files.sha256' else root)
            record(path)
            if not all(c['match'] for c in checks):
                raise ValueError('Incorrect historical SHA256 inventory '+name)
            data['inventory'][name] = len(checks)
        indices = {}
        for run in transport.RUNS:
            folder = e/'github-hosted'/run
            path = folder/'artifact-index.json'
            index = transport.load(path)['artifacts']
            record(path)
            if len({a['id'] for a in index}) != len(index) or len({a['name'] for a in index}) != len(index):
                raise ValueError('Duplicate artifact identity')
            indices[run] = index
            metadata = transport.load(folder/'run-metadata.json')
            if metadata['headSha'] != HEADS[run]:
                raise ValueError('Incorrect captured source commit')
            for item in index:
                if not (folder/('artifact-'+str(item['id']))).is_dir():
                    blockers.append('MISSING_EVIDENCE: extracted artifact '+str(item['id']))
        data['inventory']['artifacts'] = {r:len(v) for r,v in indices.items()}
        # Bind every original file actually consumed and all local artifacts.
        for path in sorted(e.rglob('*')):
            if path.is_file():
                record(path)
        for folder in (root/STEP41, root/STEP42):
            for path in sorted(folder.glob('*.json')):
                record(path)
        data['field_validation'] = refinement(root)
        for name in ('audit.json','results.json'):
            record(root/'results/quick'/name)
    except FileNotFoundError as exc:
        corrupt.append('MISSING_INDISPENSABLE_INPUT: '+str(exc))
    except Exception as exc:
        corrupt.append('Invalid evidence: '+repr(exc))
    # Fresh optimization reuses the existing sealed-capture implementation.
    # Import is delayed so optional numerical libraries cannot prevent status output.
    try:
        import phase2d_step42_replay as replay
        import phase2d_step40_validation as validation
        with replay.threadpool_limits(limits=1):
            data['numerical_environment'] = replay.environment()
            captures = []
            for run in transport.RUNS[2:]:
                index = transport.load(root/EVIDENCE/'github-hosted'/run/'artifact-index.json')['artifacts']
                indices[run] = index
                for origin in transport.COHORTS:
                    name = f'step33-capture-{origin}-{run}-1'
                    item = next(a for a in index if a['name']==name)
                    capture = root/EVIDENCE/'github-hosted'/run/('artifact-'+str(item['id']))
                    dat,a,identity = replay.load_capture(capture)
                    capture_identity(identity,run,transport.sha(capture/'inputs.json'))
                    result = replay.replay(capture,identity['input_sha256'])
                    replay.require_solve_record(result)
                    # Keep every fresh field component with actual new currents.
                    result['fields'] = fresh_fields(a,result,validation)
                    result['independent_recovery'] = {}
                    for case in ('row3','row4'):
                        x = result['cases']['dense']['currents_A']
                        y = result['cases'][case]['currents_A']
                        low,high = [metric(a['fine_A'],a['fine_b'],a['fine_weights'],x,y,
                                           dat['cases'][case]['failed'],d) for d in (70,100)]
                        if not agrees(low['ratio'],high['ratio']) or not agrees(high['ratio'],result['recovery'][case]['fresh']['ratio']):
                            raise ValueError('Independent RMS/precision inconsistency')
                        result['independent_recovery'][case] = dict(low=low,high=high,
                            reused_input_interventions=validation.interventions(a,x,y,dat['cases'][case]['failed']))
                    result['independent_saved_evaluations'] = independent_saved(
                        root,run,origin,dat,a,indices[run],data.get('historical_comparisons',[]))
                    file = out/f'fresh-{run}-{origin}.json'
                    write(file,result)
                    captures.append(dict(run=run,origin=origin,file=file.name,sha256=transport.sha(file),identity=identity))
                    system = platform.system()
                    cell = ('A' if origin==transport.COHORTS[0] else 'C') if system=='Windows' else ('B' if origin==transport.COHORTS[0] else 'D')
                    data['matrix'][cell] = 'EXECUTED on current '+system+'; historical cohort not recreated'
            data['fresh_solver'] = captures
            # Independent references, saved currents, SVD and source validators
            # reuse STEP40 explicitly; they are saved evaluations, not new solves.
            backend = validation.run(root/EVIDENCE,root,controls=False)
            file = out/'reused-step40-diagnostics.json'
            write(file,backend)
            data['reused_backend'] = dict(file=file.name,sha256=transport.sha(file),
                                         errors=backend['errors'],scope='Saved current evaluation, reused STEP40 implementation')
            blockers.extend('STEP40: '+str(v) for v in backend['errors'])
            if not backend.get('local_evidence_complete'):
                blockers.append('Independent numerical reference incomplete')
    except (ImportError,SystemExit) as exc:
        corrupt.append('Required numerical execution unavailable: '+str(exc))
    except FileNotFoundError as exc:
        corrupt.append('MISSING_INDISPENSABLE_INPUT: fresh replay inputs '+str(exc))
    except Exception as exc:
        corrupt.append('Numerical execution/input failure: '+repr(exc))
    for name in ('phase2d_step38_verify.py','phase2d_step40_validation.py',
                 'phase2d_step41_acceptance.py','phase2d_step42_replay.py','phase2d_step44_acceptance.py'):
        try:
            record(root/'scripts'/name)
        except OSError as exc:
            corrupt.append('MISSING_INDISPENSABLE_INPUT: '+str(exc))
    for name,digest in inputs.items():
        try:
            if transport.sha(root/name) != digest:
                corrupt.append('Input changed during assessment: '+name)
        except OSError as exc:
            corrupt.append('Input unavailable during assessment: '+str(exc))
    for cell,value in data['matrix'].items():
        if value.startswith('MISSING_EVIDENCE'):
            blockers.append('MISSING_EVIDENCE: reciprocal cell '+cell)
    data['errors'],data['missing_evidence'] = corrupt,blockers
    status = policy(blockers,corrupt)
    return status,data,inputs,2 if corrupt else 1


def independent_saved(root,run,origin,dat,a,index,comparisons):
    """New scalar RMS on all saved vectors, bound to original result files."""
    records = []
    for worker in transport.COHORTS:
        name = f'step33-replay-{worker}-{run}-1'
        item = next(v for v in index if v['name']==name)
        folder = root/EVIDENCE/'github-hosted'/run/('artifact-'+str(item['id']))/origin
        file = folder/'result.json'
        solve = transport.load(file)['solve']
        amps = {k:transport.unpack(v) for k,v in solve['currents_A'].items()}
        for case in ('row3','row4'):
            r = metric(a['fine_A'],a['fine_b'],a['fine_weights'],amps['dense'],amps[case],dat['cases'][case]['failed'])
            expected = [row for row in comparisons if row['run']==run and row['origin']==origin and row['case']==case
                        and (worker==transport.COHORTS[0] or row['worker']==worker)]
            if not expected:
                raise ValueError('Incomplete comparison identity')
            key,seal = ('high_reference','reference_sha256') if worker==transport.COHORTS[0] else ('high_candidate','result_sha256')
            if any(row[seal]!=transport.sha(file) or abs(rational(r['ratio'])-rational(row[key]))>Fraction('1e-40') for row in expected):
                raise ValueError('Independent saved RMS/result identity disagreement')
            records.append(dict(worker=worker,case=case,result_sha256=transport.sha(file),
                                evaluation=r,scope='Saved currents; new scalar RMS; no optimizer'))
    return records


def refinement(root):
    path = root/'results/quick/audit.json'
    audit = transport.load(path)
    if audit['results_sha256'] != transport.sha(root/'results/quick/results.json'):
        raise ValueError('Incorrect refinement result SHA256')
    rows = audit['fixed_dense_segment_sensitivity']
    changes = [float(r['relative_residual_error']) for r in rows]
    orders = [math.log2(a/b) for a,b in zip(changes,changes[1:])]
    for row,order in zip(rows[1:],orders):
        if not agrees(row['observed_order'],order):
            raise ValueError('Inconsistent second-order evidence')
    selected = next(r for r in rows if r['segments']==512)
    passed = (audit['configured_segments']==512 and audit['status']=='PASS'
              and all(v is True for v in audit['gates'].values())
              and selected['relative_rms_change'] < 1e-4
              and selected['relative_residual_error'] < 1e-4
              and all(1.95 < x < 2.05 for x in orders[-3:]))
    return dict(scope='Recomputed orders from historical executed audit; not fresh quadrature/refinement',
                audit_sha256=transport.sha(path),results_sha256=audit['results_sha256'],
                observed_orders=orders,original_limit='1e-4',historical_pass=passed,
                historical_256_failure=next(r['relative_rms_change'] for r in rows if r['segments']==256)>1e-4)


def fresh_fields(a,result,validation):
    """Reused independent STEP40 segment integral; all Cartesian observations."""
    import numpy as np
    fields = {}
    for grid,points,normals in [('training',a['points'],a['normals']),
                                 ('fine',a['fine_points'],a['fine_normals'])]:
        units = np.asarray([validation.field(points,v,digits=60) for v in a['vertices']],float)
        error = np.asarray(validation.field(points,a['error_vertices'],1500.,60),float)
        fields[grid] = {}
        for case in ('dense','row3','row4'):
            amps = np.asarray(result['cases'][case]['currents_A'])
            xyz = error+np.einsum('cpi,c->pi',units,amps)
            fields[grid][case] = dict(Bx=xyz[:,0].tolist(),By=xyz[:,1].tolist(),Bz=xyz[:,2].tolist(),
                                      projected=np.sum(xyz*normals,axis=1).tolist())
    return dict(method='Explicit reuse STEP40 independent segment integral at 60 digits; rounded output binary64',values=fields)


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        raise ValueError('Invalid repository root: '+str(root))
    out = output_path(root,args.output)
    out.mkdir(parents=True,exist_ok=False)
    try:
        status,data,inputs,code = assess(root,out)
    except Exception as exc:
        status = policy(corrupt=['Assessment execution failure: '+repr(exc)])
        data,inputs,code = dict(errors=[repr(exc)]),{},2
    write(out/'status.json',status)
    write(out/'numerical-comparisons.json',data)
    (out/'acceptance-report.md').write_text(report(status,data),encoding='utf-8')
    outputs = {p.name:transport.sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    # Manifest excludes itself to avoid a circular digest; all other outputs sealed.
    write(out/'evidence-manifest.json',dict(schema='phase2d-step44-manifest-v1',
        source_commit=SOURCE_COMMIT,inputs=inputs,outputs=outputs,
        authentication='Local byte identity only; no original-archive authentication'))
    return code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('STEP44 execution failure: '+repr(exc),file=sys.stderr)
        raise SystemExit(2)
