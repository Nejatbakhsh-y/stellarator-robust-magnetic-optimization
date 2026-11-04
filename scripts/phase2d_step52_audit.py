"""Offline final acceptance audit. No archived code, network, or publication actions.

STEP50 ZIP/source checks, STEP38 seals, STEP40 reconstruction, STEP46 Decimal
QR and STEP51 numerical/field routines are explicitly reused and re-executed.
New arithmetic checks classifications; reuse is not a second implementation.
Exit 2 means a completed adverse/incomplete assessment, not successful science.
"""
import argparse
from decimal import Decimal as D, localcontext, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

sys.dont_write_bytecode = True
import phase2d_step51_numerical as previous

archive_tools = previous.archive_tools
ROOT = Path(__file__).resolve().parents[1]
RTOL, ATOL, REFINEMENT, GUARD = D('1e-11'), D('1e-13'), D('1e-4'), D('1e-15')
SOURCE = 'bb89294ff817f66f88ec64812ce7fa6b8256eb2f'
OUTPUTS = ('decision.json', 'evidence-audit.json', 'numerical-audit.json',
           'acceptance-gates.json', 'remaining-blockers.json')


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def number(value):
    if isinstance(value, bool):
        raise ValueError('Boolean numerical evidence')
    value = D.from_float(value) if isinstance(value, float) else D(value)
    if not value.is_finite():
        raise ValueError('Nonfinite numerical evidence')
    return value


def close(candidate, reference):
    with localcontext() as ctx:
        ctx.prec = 100
        a, b = number(candidate), number(reference)
        return abs(a-b) <= ATOL+RTOL*abs(b)


def quotient(values):
    """Independent scalar classification on the original B,L,P values, in tesla."""
    with localcontext() as ctx:
        ctx.prec = 100
        B, L, P = map(number, values)
        denominator, numerator = L-B, L-P
        guarded = abs(denominator) <= GUARD
        return dict(numerator_T=str(numerator), denominator_T=str(denominator),
                    denominator_guard_pass=not guarded,
                    ratio=None if guarded else str(numerator/denominator))


def walk(value, path=''):
    yield path, value
    if isinstance(value, dict):
        for k, child in sorted(value.items()):
            yield from walk(child, path+'/'+k)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, path+'/'+str(i))


def classifications(value):
    """Never trust scalar PASS or a zero failure count over the supplied operands."""
    rows = []
    for path, record in walk(value):
        if not isinstance(record, dict):
            continue
        a, b = record.get('candidate'), record.get('reference')
        if isinstance(a, (int, float, str)) and isinstance(b, (int, float, str)):
            try:
                passed = close(a, b)
            except (ValueError, InvalidOperation):
                continue
            claims = [record[k] for k in ('pass', 'pass_original_tolerance') if k in record]
            if 'status' in record and record['status'] in ('PASS', 'FAIL'):
                claims.append(record['status'] == 'PASS')
            rows.append(dict(path=path, reference=b, candidate=a, recomputed_pass=passed,
                             contradictory=any(type(c) is not bool or c != passed for c in claims)))
        if isinstance(record.get('failures'), int) and record['failures'] > 0 and record.get('status') == 'PASS':
            rows.append(dict(path=path, recomputed_pass=False, contradictory=True))
    return rows


def compare_tree(saved, fresh, path=''):
    """Compare all saved quantitative values and classifications to an executed replay.

    Floating-point byte hashes may differ with the runtime. They are retained as
    differences, never used as a tolerance test. Input hashes are checked exactly
    by the caller. Structural omissions, status/boolean changes and altered
    numbers are rejected; missing evidence cannot produce an empty success.
    """
    problems = []
    if isinstance(fresh, dict):
        if not isinstance(saved, dict) or set(saved) != set(fresh):
            return [path+': missing or extra keys']
        for k in sorted(fresh):
            problems += compare_tree(saved[k], fresh[k], path+'/'+k)
    elif isinstance(fresh, list):
        if not isinstance(saved, list) or len(saved) != len(fresh):
            return [path+': dimensions']
        for i, (a, b) in enumerate(zip(saved, fresh)):
            problems += compare_tree(a, b, path+'/'+str(i))
    elif type(fresh) is bool or fresh is None:
        if type(saved) is not type(fresh) or saved != fresh:
            problems.append(path+': classification mismatch')
    else:
        try:
            numeric = not isinstance(fresh, str) or bool(re.fullmatch(r'[+-]?[0-9.]+([eE][+-]?[0-9]+)?', fresh))
            if numeric:
                if not close(saved, fresh):
                    problems.append(path+': numerical disagreement')
            elif saved != fresh:
                problems.append(path+': text/fingerprint differs')
        except (ValueError, TypeError, InvalidOperation):
            problems.append(path+': malformed numerical value')
    return problems


def step51_files(status_path, output):
    errors, payloads, hashes = [], {}, {}
    status = archive_tools.decode(status_path.read_bytes())
    expected = status.get('output_sha256', {})
    if set(expected) != set(previous.FILES):
        errors.append('STEP51 output SHA256 inventory is incomplete or unexpected')
    for name in previous.FILES:
        path = output/name
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(output):
                raise ValueError('Output evidence path escape')
            raw = path.read_bytes()
            hashes[name] = archive_tools.digest(raw)
            if hashes[name] != expected.get(name):
                errors.append('STEP51 output SHA256 mismatch: '+name)
            payloads[name] = archive_tools.decode(raw)
            for location, record in walk(payloads[name]):
                if isinstance(record, dict):
                    for key in ('scientific_comparison','production_acceptance','overall_scientific_status'):
                        if record.get(key) in ('PASS','ACCEPTED','COMPLETE'):
                            errors.append('Unsupported scientific PASS in incomplete STEP51 evidence: '+name+location+'/'+key)
            if any(r['contradictory'] for r in classifications(payloads[name])):
                errors.append('Contradictory scalar classifications in '+name)
        except (OSError, ValueError) as exc:
            errors.append(name+': '+str(exc))
    actual = archive_tools.digest((ROOT/'scripts/phase2d_step51_numerical.py').read_bytes())
    if status.get('implementation_sha256') != actual:
        errors.append('STEP51 implementation source identity mismatch')
    for key, expected_value in dict(rtol=1e-11, atol=1e-13, refinement_limit=1e-4, denominator_guard_T=1e-15).items():
        if status.get(key) != expected_value:
            errors.append('Changed original threshold: '+key)
    if status.get('scientific_comparison') != 'FAIL' or status.get('production_acceptance') != 'FAIL' or status.get('exit_code') != 2 or status.get('overall_scientific_status') != 'INCOMPLETE':
        errors.append('Contradictory/forged scientific acceptance on incomplete STEP51 baseline')
    if status.get('assessment') != 'COMPLETED_WITH_UNRESOLVED_REQUIREMENTS':
        errors.append('STEP51 assessment did not complete normally')
    return status, payloads, hashes, errors


def authenticate(root, manifest):
    rows, inputs, historical, errors = [], {}, [], []
    seen_ids, seen_paths, seen_hashes, seen_runs = set(), set(), set(), set()
    count = sum(len(r['artifacts']) for r in manifest['runs'])
    if count != 71:
        errors.append('Original 71-archive inventory required; received '+str(count))
    for run in manifest['runs']:
        if run['run_id'] in seen_runs:
            errors.append('Duplicate run ID')
        seen_runs.add(run['run_id'])
        for item in run['artifacts']:
            identity = dict(run_id=run['run_id'], artifact_id=item['id'], path=item['file'])
            row = dict(**identity)
            try:
                seal = item['github_sha256'].removeprefix('sha256:')
                if not re.fullmatch('[0-9a-f]{64}', seal) or seal != item['verified_sha256']:
                    raise ValueError('Conflicting original ZIP SHA256')
                path_key = archive_tools.safe(item['file']).casefold()
                if item['id'] in seen_ids or path_key in seen_paths or seal in seen_hashes:
                    raise ValueError('Duplicate archive ID/path/hash')
                seen_ids.add(item['id']); seen_paths.add(path_key); seen_hashes.add(seal)
                path = root/item['file']
                if not path.resolve().is_relative_to(root):
                    raise ValueError('Archive path escape')
                members = archive_tools.archive(path, seal)
                sources = archive_tools.source(members, run)
                seals = archive_tools.seals(members)
                row.update(zip_sha256=seal, zip_integrity='MATCH_SUPPLIED_STEP49_MANIFEST',
                           members={k:archive_tools.digest(v) for k,v in sorted(members.items())},
                           sources=sources, internal_manifests=seals)
                if any(ref['status']=='MISMATCH' for seal_record in seals for ref in seal_record['records']):
                    errors.append(str(identity)+': internal artifact manifest mismatch')
                if any(s['association'] == 'CONFLICT' or any(f['status'] == 'MISMATCH' for f in s['files']) for s in sources):
                    errors.append(str(identity)+': source identity mismatch')
                for name, raw in members.items():
                    if name.endswith('.json') and any(s in name.lower() for s in ('comparison','assessment','status','causal-attribution')):
                        original = archive_tools.decode(raw)
                        historical.append(dict(**identity, member=name, sha256=archive_tools.digest(raw),
                                               classifications=classifications(original), original=original))
                    if name.split('/')[-1] in ('inputs.json', 'sealed-inputs.json'):
                        data = archive_tools.decode(raw)
                        entry = dict(**identity, member=name, input_sha256=archive_tools.digest(raw))
                        if data.get('schema') != 'production-upstream-v1':
                            entry.update(status='INCOMPLETE', reason='Unsupported original schema')
                        else:
                            entry['seals'] = previous.input_seals(members, name, raw)
                            entry['status'] = entry['seals']['status']
                        inputs[(run['run_id'], item['id'], name)] = (entry, raw)
                row['status'] = 'BYTES_VERIFIED'
            except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
                row.update(status='REJECTED_OR_MISSING', reason=str(exc))
                errors.append(str(identity)+': '+str(exc))
            rows.append(row)
    # External seal content is matched only within its original run; digest
    # equality does not prove a missing original path association.
    index = {}
    for row in rows:
        for name, seal in row.get('members', {}).items():
            index.setdefault((row['run_id'], seal), []).append(dict(artifact_id=row['artifact_id'], member=name))
    for row in rows:
        for record in row.get('internal_manifests', []):
            for reference in record['records']:
                if reference['status'] != 'MATCH':
                    reference['same_run_content'] = index.get((row['run_id'], reference['expected']), [])
                    reference['path_association'] = 'INCOMPLETE'
    return rows, inputs, historical, errors


def keyed(payload):
    result = {}
    for row in payload.get('inputs', []):
        key = (row['run_id'], row['artifact_id'], row['path'])
        if key in result:
            raise ValueError('Duplicate STEP51 input identity')
        result[key] = row
    return result


def numerical_audit(inputs, payloads):
    """Re-execute earlier implementations, then independently classify results."""
    import numpy as np
    import phase2d_step40_validation as schema
    import phase2d_step46_independent as scalar
    maps = [keyed(payloads.get(n, {})) for n in previous.FILES[:3]]
    rows, errors, cache, perturbation_cache = [], [], {}, {}
    for key, (entry, raw) in sorted(inputs.items()):
        row = dict(**entry)
        try:
            if entry['status'] != 'VERIFIED':
                raise ValueError('Original sealed numerical input unavailable')
            saved = [m.get(key) for m in maps]
            if any(r is None or r.get('input_sha256') != entry['input_sha256'] for r in saved):
                raise ValueError('Missing scientific output or input SHA256 mismatch')
            for record in saved:
                if record.get('input_seals') != entry['seals']:
                    raise ValueError('Input semantic seal mismatch')
            if entry['input_sha256'] not in cache:
                cache[entry['input_sha256']] = previous.numerical(raw)
            calculations = cache[entry['input_sha256']]
            # STEP51 file order is solver, field, recovery; numerical() returns
            # solver, recovery, field. Compare explicitly in the correct order.
            differences = []
            for i, j in ((0,0), (1,2), (2,1)):
                differences += compare_tree(saved[i].get('calculation'), calculations[j], previous.FILES[i])
            solution, recovery, field = calculations
            a = schema.reconstruct(archive_tools.decode(raw))
            certificates, ratios, ulps = {}, {}, {}
            for case, record in solution['solver'].items():
                support = record['support']
                M, y = a[case+'_M'], a[case+'_y']
                x = np.asarray(record['fresh_x_A'])[support]/record['physical_scale_A']
                residual = M@x-y
                gradient = M.T@residual
                kkt = np.where(x == -1, np.minimum(gradient,0), np.where(x == 1,np.maximum(gradient,0),gradient))
                kkt_max = float(np.max(abs(kkt)))
                certificates[case] = dict(objective=float(residual@residual/2),
                    primal_feasible=bool(np.all(abs(x) <= 1)), stationarity_max=float(np.max(abs(gradient))),
                    kkt_max=kkt_max, kkt_zero_comparison_pass=close(kkt_max, 0),
                    solver_terminated=record['success'] and record['status'] > 0,
                    saved_fresh_pass=record['current_comparison']['original_tolerance_pass'],
                    qr_60_90_pass=all(close(u,v) for u,v in zip(record['high_precision']['60'].get('x',[]),record['high_precision']['90'].get('x',[])))
                        if all(record['high_precision'][p]['status']=='INTERIOR_REFERENCE' for p in ('60','90')) else False)
            for case, record in recovery.items():
                refs = {name:quotient(record[name]['rms_B_L_P']) for name in ('reference','candidate')}
                if not all(r['denominator_guard_pass'] for r in refs.values()):
                    passed = False
                else:
                    passed = close(refs['candidate']['ratio'], refs['reference']['ratio'])
                for name, value in refs.items():
                    if value['ratio'] is None or not close(record[name]['ratio'], value['ratio']):
                        differences.append(case+'/'+name+': incorrect quotient')
                if record['pass_original_tolerance'] != passed:
                    differences.append(case+': incorrect recovery classification')
                ratios[case] = dict(**refs, saved_fresh_pass=passed,
                    high_precision_reference=record['high_precision_solver_reference'])
                dense = a['dense_x']*3000
                recovered = a[case+'_x']*3000
                failed = solution['solver'][case]['failed']
                probes = []
                # Every supported current, both directions; retain measured
                # current and field effects rather than infer them from ratios.
                cache_key = (entry['input_sha256'], case)
                for j in ([] if cache_key in perturbation_cache else solution['solver'][case]['support']):
                    for direction in (-np.inf, np.inf):
                        perturbed = recovered.copy(); perturbed[j] = np.nextafter(recovered[j], direction)
                        probe = scalar.intervention(a['fine_A'].tolist(),a['fine_b'].tolist(),a['fine_weights'].tolist(),
                            dense.tolist(), recovered.tolist(),dense.tolist(),perturbed.tolist(),failed)
                        probes.append(dict(coil=j, direction='down' if direction < 0 else 'up', calculation=probe))
                if cache_key not in perturbation_cache:
                    perturbation_cache[cache_key] = probes
                ulps[case] = perturbation_cache[cache_key]
            row.update(status='EXECUTED', reused_calculations=dict(solver=solution,recovery=recovery,field=field),
                       independent_classifications=dict(solver=certificates,recovery=ratios),
                       one_ulp_current_interventions=ulps, step51_disagreements=differences)
            errors.extend(str(key)+': '+d for d in differences)
        except (ValueError, KeyError, TypeError, InvalidOperation) as exc:
            row.update(status='INCOMPLETE_OR_INVALID', reason=str(exc))
            errors.append(str(key)+': '+str(exc))
        rows.append(row)
    original_keys = set(inputs)
    for mapping in maps:
        if set(mapping) != original_keys:
            errors.append('STEP51 scientific input inventory differs from original archives')
    if not rows:
        errors.append('No numerical inputs assessed')
    return dict(inputs=rows, errors=errors,
        execution_scope='One local environment; calculations cached by exact input SHA256',
        reuse=['STEP50 ZIP/source', 'STEP38 semantic seals', 'STEP40 reconstruction',
               'STEP46 Decimal QR/certificates/interventions', 'STEP51 SciPy solves and polygon Gauss-Legendre fields'],
        independent=['100-digit scalar quotient/classifications', 'direct NumPy objective/gradient/box KKT classifications'],
        unexecuted_requirements=['Fresh four-environment controlled experiments', 'Smooth geometry refinement',
            'Full historical worker-current and field-to-ratio binding', 'Independent high-precision Biot-Savart field perturbations'])


def causal_audit(payload):
    # No input to this CLI provides authenticated independently executed matched
    # experiments. Labels and runtime self-reports cannot close that gap.
    records = payload.get('controlled_configurations', {})
    claims = [k for k,v in records.items() if v.get('status') not in ('INCOMPLETE','NOT_EXECUTED')]
    return dict(status='INCONCLUSIVE',
        required={k:dict(status='INCOMPLETE', reason='No independently executed matched-input experiment authenticated') for k in previous.COHORTS},
        unsupported_execution_claims=claims,
        original_environment_evidence=payload,
        required_controls=['Exact input SHA256','Python','NumPy','SciPy','BLAS/LAPACK','CPU dispatch',
            'threads','solver options','initial conditions','optimization output','KKT','currents','fields','recovery ratios'])


def assess(status_path, step51, root, manifest_path):
    raw = manifest_path.read_bytes()
    manifest = archive_tools.decode(raw)
    status, payloads, hashes, errors = step51_files(status_path, step51)
    source_head = archive_tools.git('rev-parse','HEAD').stdout.decode().strip()
    if source_head != SOURCE:
        errors.append('STEP52 requested baseline source commit differs from checkout HEAD')
    archives, inputs, historical, archive_errors = authenticate(root, manifest)
    errors += archive_errors
    solver = payloads.get('solver-reproduction.json', {})
    if solver.get('manifest_sha256') != archive_tools.digest(raw):
        errors.append('STEP51 original manifest SHA256 mismatch')
    # Compare identities and original fingerprints rather than trusting
    # STEP51's archive status strings or requiring its presentation schema.
    original = {(a['run_id'],a['artifact_id']):a for a in archives}
    recorded = {(a['run_id'],a['artifact_id']):a for a in solver.get('archives',[])}
    if len(recorded) != len(solver.get('archives',[])) or set(recorded) != set(original):
        errors.append('STEP51 archive identity inventory mismatch')
    for key, a in recorded.items():
        b = original.get(key,{})
        if a.get('zip_sha256') != b.get('zip_sha256') or a.get('members') != b.get('members') or a.get('sources') != b.get('sources'):
            errors.append(str(key)+': STEP51 archive/source/result hashes mismatch')
    numerical = numerical_audit(inputs, payloads)
    errors += numerical['errors']
    causal = causal_audit(payloads.get('causal-attribution.json', {}))
    if causal['unsupported_execution_claims']:
        errors.append('Unexecuted controlled environment claimed executed')
    executed = [r for r in numerical['inputs'] if r['status'] == 'EXECUTED']
    quantitative_failures = []
    for row in executed:
        for path, value in walk(row['reused_calculations']):
            if isinstance(value, dict):
                for flag in ('original_tolerance_pass','pass_original_tolerance'):
                    if value.get(flag) is False:
                        quantitative_failures.append(dict(input_sha256=row['input_sha256'],path=path+'/'+flag))
        for case, cert in row['independent_classifications']['solver'].items():
            if not all(cert[k] for k in ('primal_feasible','kkt_zero_comparison_pass','solver_terminated','saved_fresh_pass','qr_60_90_pass')):
                quantitative_failures.append(dict(input_sha256=row['input_sha256'],path='solver/'+case))
    gates = dict(
        original_thresholds=dict(rtol=str(RTOL),atol=str(ATOL),refinement_limit=str(REFINEMENT),denominator_guard_T=str(GUARD)),
        evidence_integrity=dict(status='FAIL' if errors else 'PASS', findings=errors),
        local_quantitative_replay=dict(status='FAIL' if quantitative_failures else 'PASS' if executed and len(executed)==len(inputs) else 'INCOMPLETE',
            failures=quantitative_failures, executed_inputs=len(executed),required_inputs=len(inputs),
            scope='Diagnostic saved-input replay only; never a full scientific acceptance gate'),
        external_origin_attestation=dict(status='INCOMPLETE', reason='Supplied STEP49 manifest is not independent GitHub-origin attestation'),
        source_and_manifest_closure=dict(status='INCOMPLETE' if not archives or any(
            not a.get('sources') or not a.get('internal_manifests') or
            any(s['association'] != 'EXACT' or any(f['status'] != 'MATCH' for f in s['files']) for s in a.get('sources',[])) or
            any(m['status'] != 'VERIFIED' for m in a.get('internal_manifests',[]))
            for a in archives) else 'PASS',
            reason='Exact source objects and original path associations required; same-run content recovery alone is insufficient'),
        magnetic_field_validation=dict(status='INCOMPLETE', reason='Saved polygon quadrature does not certify smooth geometry/refinement or all saved Bxyz artifacts'),
        recovery_validation=dict(status='FAIL', reason='Historical 21, 11 and earlier 22 scalar-path failures retained; complete worker-result binding unresolved'),
        controlled_causal_experiments=dict(status='INCOMPLETE', reason='Four independently executed matched-input environments unavailable'),
        checkpoint_validation=dict(status='INCOMPLETE', reason='No new result-SHA256-bound complete README validation record supplied'))
    blockers = [dict(gate=k, **v) for k,v in gates.items() if isinstance(v,dict) and v.get('status') in ('FAIL','INCOMPLETE')]
    decision = dict(assessment_status='COMPLETED_WITH_UNRESOLVED_REQUIREMENTS', scientific_comparison='FAIL',
        production_acceptance='FAIL', overall_scientific_status='INCOMPLETE', numerical_root_cause='INCONCLUSIVE',
        evidence_authentication='INCOMPLETE', remaining_blockers=blockers, exit_code=2)
    evidence = dict(manifest_sha256=archive_tools.digest(raw), step51_status_sha256=archive_tools.digest(status_path.read_bytes()),
        step51_output_sha256=hashes, step51_status=status, archives=archives,
        historical_records=historical, historical_failure_cohorts=[dict(run_id=41256776296,reported_failures=21),
            dict(run_id=41257645149,reported_failures=11),dict(scope='earlier scalar paths',reported_failures=22)],
        historical_counts_scope='Prior observations, not fresh worker-current reproduction counts',
        source_commit=SOURCE, source_identity=source_head,
        errors=errors, trust_scope='Consistency with supplied manifest only; external attestation INCOMPLETE')
    numerical['causal_attribution'] = causal
    return dict(zip(OUTPUTS, (decision,evidence,numerical,gates,dict(blockers=blockers))))


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    for name in ('step51-status','step51-output','archive-root','manifest','output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args(argv)
    status, step51, root, manifest, output = (getattr(args,n).resolve() for n in ('step51_status','step51_output','archive_root','manifest','output'))
    if output.exists() or any(output.is_relative_to(p) or p.is_relative_to(output) for p in (status,step51,root,manifest)):
        print('Require fresh output disjoint from every evidence path', file=sys.stderr)
        return 1
    output.mkdir(parents=True, exist_ok=False)
    try:
        records = assess(status,step51,root,manifest)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, zipfile.BadZipFile) as exc:
        # Invalid or missing baseline is an assessed evidence gap, never PASS.
        issue = dict(gate='baseline_evidence',status='INCOMPLETE',reason=str(exc))
        records = {name:{} for name in OUTPUTS}
        records['decision.json'] = dict(assessment_status='COMPLETED_WITH_INVALID_OR_MISSING_EVIDENCE',
            scientific_comparison='FAIL',production_acceptance='FAIL',overall_scientific_status='INCOMPLETE',
            numerical_root_cause='INCONCLUSIVE',evidence_authentication='INCOMPLETE',remaining_blockers=[issue],exit_code=2)
        records['evidence-audit.json'] = dict(errors=[str(exc)])
        records['acceptance-gates.json'] = dict(baseline_evidence=issue)
        records['remaining-blockers.json'] = dict(blockers=[issue])
    except Exception as exc:
        records = {name:{} for name in OUTPUTS}
        records['decision.json'] = dict(assessment_status='UNEXPECTED_EXECUTION_FAILURE',scientific_comparison='FAIL',
            production_acceptance='FAIL',overall_scientific_status='INCOMPLETE',numerical_root_cause='INCONCLUSIVE',
            evidence_authentication='INCOMPLETE',remaining_blockers=[repr(exc)],exit_code=1)
    for name, value in records.items():
        (output/name).write_bytes(encode(value))
    seals = {name:archive_tools.digest((output/name).read_bytes()) for name in OUTPUTS}
    (output/'output-manifest.json').write_bytes(encode(dict(schema='step52-output-v1',outputs=seals,
        implementation_sha256=archive_tools.digest(Path(__file__).read_bytes()))))
    return records['decision.json']['exit_code']


if __name__ == '__main__':
    sys.exit(main())
