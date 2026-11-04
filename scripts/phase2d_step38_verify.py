"""Read-only STEP 38 evidence checks. Exit 2 incomplete, 1 retained scientific failure.

Agreement never promotes historical production acceptance. Standard library only.
Output must be new and disjoint from evidence. No network or production solves.
"""
import argparse
from decimal import Decimal, DecimalException, localcontext
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess

COHORTS = ('windows-reference', 'linux-reference', 'linux-numpy-sensitivity', 'linux-scipy-sensitivity')
RUNS = ('41195815229', '41231422708', '41256776296', '41257645149')
CASES = ('dense', 'row3', 'row4')
FIELDS = {'dense_fixed_current_Bxyz', 'original_Bxyz', 'projected_A',
          'row3_fixed_current_Bxyz', 'row3_frozen_current_Bxyz',
          'row4_fixed_current_Bxyz', 'row4_frozen_current_Bxyz', 'unit_coils_Bxyz'}


def number(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError('Invalid finite numerical input')
    return value


def valid_digest(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('Invalid SHA-256 fingerprint')
    return value


def fields(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError('Missing or invalid field components')
    return {name: unpack(value) for name, value in record.items()}


def diagnostics(record, n):
    for key in ('cost', 'optimality', 'projected_gradient_max', 'condition'):
        if number(record[key]) < 0:
            raise ValueError('Invalid solver diagnostics '+key)
    if (type(record['success']) is not bool or type(record['status']) is not int
            or record['status'] not in (-1, 0, 1, 2, 3)
            or record['success'] != (record['status'] > 0)
            or type(record['nit']) is not int or record['nit'] < 0
            or type(record['rank']) is not int or not 0 <= record['rank'] <= n
            or not isinstance(record['message'], str) or not record['message']
            or len(record['active_mask']) != n
            or any(number(x) not in (-1, 0, 1) for x in record['active_mask'])
            or len(record['singular_values']) != n
            or any(number(x) < 0 for x in record['singular_values'])):
        raise ValueError('Invalid solver diagnostics')


def comparison_record(value):
    """Validate scalar comparisons recursively; never trust a saved PASS label."""
    if isinstance(value, dict):
        if 'failures' in value:
            count = value['failures']
            if type(count) is not int or count < 0:
                raise ValueError('Invalid comparison failure count')
            if count and (value.get('status') == 'PASS' or value.get('pass') is True):
                raise ValueError('Incorrect scientific acceptance claim')
        if 'reference' in value and 'candidate' in value:
            a, b = value['reference'], value['candidate']
            if (type(a) in (int, float)) != (type(b) in (int, float)):
                raise ValueError('Invalid comparison record')
            if type(a) in (int, float) and type(b) in (int, float):
                passed = close(number(b), number(a))
                if 'pass' in value and (type(value['pass']) is not bool or value['pass'] != passed):
                    raise ValueError('Incorrect scientific acceptance claim')
                if value.get('status') == 'PASS' and not passed:
                    raise ValueError('Incorrect scientific acceptance claim')
        for child in value.values(): comparison_record(child)
    elif isinstance(value, list):
        for child in value: comparison_record(child)


def assessment(record):
    required = {o+'/'+w for o in COHORTS for w in COHORTS[1:]}
    if not isinstance(record, dict) or not required.issubset(record.get('comparisons', {})):
        raise ValueError('Incomplete scientific comparison payload')
    for key in required:
        if not set(CASES).issubset(record['comparisons'][key]):
            raise ValueError('Incomplete scientific comparison cases')
    comparison_record(record)


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: '+key)
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                       parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    def finite(v):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError('Nonfinite number')
        if isinstance(v, dict):
            for x in v.values(): finite(x)
        elif isinstance(v, list):
            for x in v: finite(x)
    finite(value)
    return value


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(root, name):
    root = Path(root).resolve()
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or name.startswith('/') or any(x in ('', '.', '..') for x in name.split('/'))):
        raise ValueError('Unsafe path')
    p = root/name
    if p.is_symlink() or not p.resolve().is_relative_to(root):
        raise ValueError('Escaping evidence path')
    if any(x.is_symlink() for x in p.parents if x != root):
        raise ValueError('Symlink parent')
    return p


def manifest(path):
    path = Path(path)
    expected = load(path)
    if not isinstance(expected, dict) or not expected:
        raise ValueError('Empty or invalid manifest')
    for name, digest in expected.items():
        target = safe(path.parent, name)
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('Invalid digest')
        if not target.is_file() or sha(target) != digest:
            raise ValueError('Missing or mismatching manifest member: '+name)
    actual = {p.relative_to(path.parent).as_posix() for p in path.parent.rglob('*') if p.is_file() and p != path}
    if actual != set(expected):
        raise ValueError('Incomplete manifest coverage')
    return len(expected)


def hash_list(path, root):
    rows = []
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        m = re.fullmatch(r'([0-9a-fA-F]{64})  (.+)', line)
        if not m:
            raise ValueError('Malformed hash list')
        p = safe(root, m[2])
        rows.append(dict(path=m[2], match=p.is_file() and sha(p) == m[1].lower()))
    if not rows or len({r['path'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate hash inventory')
    return rows


def unpack(v):
    if (not isinstance(v, dict) or set(v) != {'shape', 'binary64_le'}
            or not isinstance(v['shape'], list) or not v['shape'] or any(type(n) is not int or n <= 0 for n in v['shape'])
            or not isinstance(v['binary64_le'], str)
            or re.fullmatch('[0-9a-f]*', v['binary64_le']) is None
            or len(v['binary64_le']) != 16*math.prod(v['shape'])):
        raise ValueError('Invalid binary64 array')
    flat = struct.unpack('<'+'d'*math.prod(v['shape']), bytes.fromhex(v['binary64_le']))
    if not all(math.isfinite(x) for x in flat):
        raise ValueError('Nonfinite binary64')
    def nest(a, dims):
        if not dims: return a[0]
        n = math.prod(dims[1:])
        return [nest(a[i*n:(i+1)*n], dims[1:]) for i in range(dims[0])]
    return nest(flat, v['shape'])


def close(candidate, reference):
    if type(candidate) not in (float, int) or type(reference) not in (float, int):
        raise ValueError('Invalid comparison numbers')
    return math.isfinite(candidate) and math.isfinite(reference) and abs(candidate-reference) <= 1e-13+1e-11*abs(reference)


def flatten(value):
    if isinstance(value, list):
        return [x for row in value for x in flatten(row)]
    return [value]


def environment(record, worker, head):
    expected = ('3.11.9' if worker == COHORTS[0] else '3.11.17',
                '2.3.5' if worker == COHORTS[2] else '2.4.6',
                '1.16.3' if worker == COHORTS[3] else '1.17.1')
    if tuple(record[k] for k in ('python', 'numpy', 'scipy')) != expected or record['head'] != head:
        raise ValueError('Unexpected numerical environment')
    if not record['numerical_config'] or not record['loaded_threadpools']:
        raise ValueError('Missing BLAS/LAPACK provenance')
    for pool in record['loaded_threadpools']:
        if pool['num_threads'] != 1 or not pool['architecture'] or not pool['version']:
            raise ValueError('Incomplete or inconsistent threadpool metadata')
    return record


def problem(data):
    return dict(config=data['config'], cases={k: dict(M=data['arrays'][k+'_M'], y=data['arrays'][k+'_y'],
        arguments=v['arguments'], method=v['implicit_method'], lsq_solver=v['implicit_lsq_solver'],
        support=v.get('support'), failed=v.get('failed')) for k, v in data['cases'].items()})


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def frozen_seal(record, expected):
    if not isinstance(record, dict) or not record:
        raise ValueError('Missing frozen-input seal')
    for value in record.values(): valid_digest(value)
    if record != expected:
        raise ValueError('Frozen-input digest mismatch')


def solver_spec(spec):
    if (spec['arguments'] != dict(bounds=[-1, 1], max_iter=1000, tol=1e-12)
            or spec['implicit_method'] != 'trf' or spec['implicit_lsq_solver'] != 'exact'):
        raise ValueError('Changed frozen solver settings')


def rounded_rms_probe(values):
    if len(values) != 3: raise ValueError('Invalid saved RMS probe dimensions')
    for value in values: number(value)
    B, L, P = values
    if not all(math.isfinite(x) for x in values) or abs(L-B) <= 1e-15:
        raise ValueError('Invalid saved RMS probe')
    num, den = L-P, L-B
    R = num/den; next_L = math.nextafter(L, math.inf)
    return dict(ratio_from_rounded_saved_rms=R, numerator_T=num, denominator_T=den,
        numerator_condition=(abs(L)+abs(P))/abs(num) if num else None,
        denominator_condition=(abs(L)+abs(B))/abs(den),
        L_one_ulp_T=next_L-L, ratio_delta_L_one_ulp=(next_L-P)/(next_L-B)-R)


def ratio(arr, dense, recovered, failed, digits=90):
    if type(failed) is not int or not 0 <= failed < len(dense):
        raise ValueError('Invalid failed-coil index')
    for value in flatten([dense, recovered, arr['fine_A'], arr['fine_b'], arr['fine_weights']]): number(value)
    if not arr['fine_A'] or any(w < 0 for w in arr['fine_weights']) or not close(sum(arr['fine_weights']), 1.):
        raise ValueError('Invalid recovery weights')
    with localcontext() as ctx:
        ctx.prec = digits
        cv = Decimal.from_float
        frozen = list(dense); frozen[failed] = 0.0
        rms = []
        A, b, w = (arr[k] for k in ('fine_A', 'fine_b', 'fine_weights'))
        if len(A) != len(b) or len(A) != len(w) or any(len(r) != len(dense) for r in A) or len(dense) != len(recovered):
            raise ValueError('Recovery dimensions')
        for current in (dense, frozen, recovered):
            x = list(map(cv, current))
            residual = [cv(bb)+sum((cv(a)*j for a, j in zip(row, x)), Decimal(0)) for row, bb in zip(A, b)]
            rms.append(sum((cv(ww)*r*r for ww, r in zip(w, residual)), Decimal(0)).sqrt())
        B, L, P = rms; num, den = L-P, L-B
        if abs(den) <= Decimal('1e-15'): raise ValueError('Original ratio guard')
        return dict(rms_T=list(map(str, rms)), numerator_T=str(num), denominator_T=str(den), ratio=str(num/den),
            numerator_condition=str((abs(L)+abs(P))/abs(num)) if num else None,
            denominator_condition=str((abs(L)+abs(B))/abs(den)),
            derivatives_B_L_P=list(map(str, (num/den**2, (den-num)/den**2, -1/den))))


def kkt(M, y, x):
    if len(M) != len(y) or not M or not x or any(len(row) != len(x) for row in M):
        raise ValueError('KKT dimensions')
    for value in flatten([M, y, x]): number(value)
    with localcontext() as ctx:
        ctx.prec = 90
        cv = Decimal.from_float
        rows = [list(map(cv, row)) for row in M]; xx = list(map(cv, x))
        residual = [sum((a*b for a, b in zip(row, xx)), Decimal(0))-cv(v) for row, v in zip(rows, y)]
        g = [sum((row[j]*r for row, r in zip(rows, residual)), Decimal(0)) for j in range(len(x))]
        projected = [min(v, Decimal(0)) if a == -1 else max(v, Decimal(0)) if a == 1 else v for a, v in zip(xx, g)]
        return dict(objective=str(sum((r*r for r in residual), Decimal(0))/2),
            kkt_max=str(max(map(abs, projected))), violation=str(max(Decimal(0), max(abs(v)-1 for v in xx))),
            active_lower=[i for i, v in enumerate(xx) if v == -1], active_upper=[i for i, v in enumerate(xx) if v == 1])


def verify(evidence, repo):
    evidence, repo = Path(evidence).resolve(), Path(repo).resolve()
    result = dict(schema='step38-v1', thresholds=dict(rtol=1e-11, atol=1e-13, refinement=1e-4, segments=512),
        errors=[], artifacts=[], runs={}, comparisons=[], failed_scientific_comparisons=[],
        evidence_authentication='INCOMPLETE', GITHUB_RUN_PROVENANCE='LOCAL_METADATA_ONLY',
        ORIGINAL_ARCHIVE_AUTHENTICATION='INCOMPLETE', scientific_comparison='FAIL',
        production_acceptance='FAIL', scientific_status='PARTIAL', causal_root_cause='INCONCLUSIVE')
    def attempt(label, action):
        try: return action()
        except (ValueError, KeyError, TypeError, OSError, IndexError, ArithmeticError, DecimalException) as exc:
            result['errors'].append(dict(check=label, error=str(exc)))
            return None
    result['download_hashes'] = attempt('download hashes', lambda: hash_list(evidence/'downloaded-files.sha256', evidence))
    result['historical_hashes'] = attempt('historical hashes', lambda: hash_list(evidence/'historical-before.sha256', repo))
    for rid in RUNS:
        def run_check():
            root = evidence/'github-hosted'/rid
            meta, index = load(root/'run-metadata.json'), load(root/'artifact-index.json')
            if str(meta['databaseId']) != rid or meta['status'] != 'completed': raise ValueError('Run identity/status')
            if not isinstance(meta['headSha'], str) or re.fullmatch('[0-9a-f]{40}', meta['headSha']) is None:
                raise ValueError('Invalid source commit identity')
            if index['total_count'] != len(index['artifacts']): raise ValueError('Incomplete artifact index')
            artifacts = {}
            ids = set()
            for a in index['artifacts']:
                if a['name'] in artifacts: raise ValueError('Duplicate artifact name')
                if type(a['id']) is not int or a['id'] <= 0 or a['id'] in ids: raise ValueError('Invalid or duplicate artifact ID')
                ids.add(a['id'])
                if str(a['workflow_run']['id']) != rid or a['workflow_run']['head_sha'] != meta['headSha']:
                    raise ValueError('Artifact run/commit mismatch')
                directory = root/('artifact-'+str(a['id'])); artifacts[a['name']] = directory
                result['artifacts'].append(dict(run=rid, **a, available=directory.is_dir(),
                    archive_authentication='MISSING_ORIGINAL_BYTES'))
                if not directory.is_dir(): result['errors'].append(dict(check=a['name'], error='MISSING_ARTIFACT'))
                for m in sorted(directory.rglob('manifest.json')):
                    attempt(str(m.relative_to(evidence)), lambda m=m: manifest(m))
            if rid == RUNS[0]:
                required = {'phase2d-'+c for c in COHORTS} | {'phase2d-cross-platform'}
            elif rid == RUNS[1]:
                required = {'upstream-'+c for c in COHORTS} | {'upstream-comparisons', 'upstream-sealed', 'dependency-seal'}
            else:
                required = {f'step33-{s}-{c}-{rid}-1' for s in ('capture', 'replay', 'capture-dependencies', 'replay-dependencies') for c in COHORTS} | {f'step33-comparison-{rid}-1'}
            for missing in sorted(required-set(artifacts)):
                result['errors'].append(dict(check=rid, error='MISSING_REQUIRED_ARTIFACT '+missing))
            run = dict(metadata=meta, replay_records={}, environments={}, sources={})
            result['runs'][rid] = run
            if rid in RUNS[2:]:
                comparison_root = artifacts[f'step33-comparison-{rid}-1']
                assessment(load(comparison_root/'comparison'/'assessment.json'))
            if rid in RUNS[:2]:
                run['reciprocal_replay'] = 'NOT_PRESENT_IN_THIS_PROTOCOL'
                maps = sorted(root.rglob('source_fingerprints_at_run.json')) if rid == RUNS[0] else sorted(root.rglob('source_sha256.json'))
                if not maps: raise ValueError('Missing source fingerprints')
                for source_path in maps:
                    def source_check():
                        source = load(source_path)
                        if not source: raise ValueError('Empty source fingerprints')
                        checks = {}
                        for name, digest in source.items():
                            safe(repo, name); valid_digest(digest)
                            blob = subprocess.run(['git', 'show', meta['headSha']+':'+name], cwd=repo, capture_output=True)
                            checks[name] = blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == digest
                            if not checks[name]: raise ValueError('Historical source mismatch '+name)
                        run['sources'][source_path.relative_to(root).as_posix()] = checks
                    attempt(str(source_path), source_check)
                paths = set(root.rglob('*comparison*.json')) | set(root.rglob('cross-platform.json'))
                run['saved_comparisons'] = {p.relative_to(root).as_posix(): dict(sha256=sha(p), record=load(p)) for p in sorted(paths)}
                if not paths: raise ValueError('Missing scientific comparisons')
                for saved in run['saved_comparisons'].values(): comparison_record(saved['record'])
                def saved_failures(value, path):
                    if isinstance(value, dict):
                        if value.get('status') == 'FAIL':
                            result['failed_scientific_comparisons'].append(dict(run=rid, kind='historical_failed_record', path=path))
                        for key, child in value.items(): saved_failures(child, path+'/'+key)
                    elif isinstance(value, list):
                        for i, child in enumerate(value): saved_failures(child, path+'/'+str(i))
                saved_failures(run['saved_comparisons'], '')
                return
            def stage(s, c):
                name = f'step33-{s}-{c}-{rid}-1'
                if name not in artifacts: raise ValueError('MISSING_REQUIRED_ARTIFACT '+name)
                return artifacts[name]
            records = {}
            for worker in COHORTS:
                rp = stage('replay', worker)
                for name in ('manifest.json', 'source-sha256.json', 'input-sha256.json', 'environment.json'):
                    if not (rp/name).is_file(): raise ValueError('Missing replay metadata '+name)
                run['environments'][worker] = environment(load(rp/'environment.json'), worker, meta['headSha'])
            for origin in COHORTS:
                def origin_check():
                    cap = stage('capture', origin); data = load(cap/'inputs.json')
                    manifest(cap/'manifest.json')
                    frozen_seal(load(cap/'input-sha256.json'), {'inputs.json': sha(cap/'inputs.json')})
                    frozen_seal(load(cap/'problem-sha256.json'), {'sha256': fingerprint(problem(data))})
                    if data['config']['segments'] != 512: raise ValueError('Geometry resolution')
                    if set(data['cases']) != set(CASES) or number(data['config']['imax_A']) != 3000:
                        raise ValueError('Incomplete scientific payload or current scale')
                    sources = load(cap/'source-sha256.json')
                    if sources['head'] != meta['headSha'] or not sources['sha256']: raise ValueError('Source identity')
                    for name, digest in sources['sha256'].items():
                        safe(repo, name); valid_digest(digest)
                        blob = subprocess.run(['git', 'show', sources['head']+':'+name], cwd=repo, capture_output=True)
                        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest: raise ValueError('Source blob '+name)
                    run['sources'][origin] = sources
                    arr = {k: unpack(v) for k, v in data['arrays'].items()}
                    for case in CASES: solver_spec(data['cases'][case])
                    for worker in COHORTS:
                        def replay_check():
                            rp = stage('replay', worker); sub = rp/origin
                            manifest(rp/'manifest.json')
                            if sha(sub/'inputs.json') != sha(cap/'inputs.json'): raise ValueError('Replay bytes differ')
                            frozen_seal(load(rp/'input-sha256.json'),
                                        {c: sha(stage('capture', c)/'inputs.json') for c in COHORTS})
                            if load(rp/'source-sha256.json') != sources: raise ValueError('Replay sources differ')
                            rec = load(sub/'result.json')
                            fields(load(sub/'fields.json'))
                            entry = dict(result_sha256=sha(sub/'result.json'), input_sha256=sha(sub/'inputs.json'),
                                input_bytes_equal=True, kkt={}, recovery={}, saved_diagnostics=rec['solve']['diagnostics'])
                            currents = {k: unpack(rec['solve']['currents_A'][k]) for k in CASES}
                            for case in CASES:
                                spec = data['cases'][case]; support = spec.get('support', list(range(len(currents[case]))))
                                if (len(currents[case]) != 24 or any(isinstance(x, list) for x in currents[case])
                                        or not support or any(type(i) is not int or not 0 <= i < 24 for i in support)
                                        or len(set(support)) != len(support)
                                        or any(currents[case][i] != 0 for i in range(24) if i not in support)):
                                    raise ValueError('Invalid current vector or support')
                                if case != 'dense' and (spec['failed'] in support or len(support) != 23):
                                    raise ValueError('Invalid fault support')
                                x = [currents[case][i]/data['config']['imax_A'] for i in support]
                                entry['kkt'][case] = kkt(arr[case+'_M'], arr[case+'_y'], x)
                                diag = rec['solve']['diagnostics'][case]
                                diagnostics(diag, len(support))
                                mask = [-1 if a == -1 else 1 if a == 1 else 0 for a in x]
                                if diag['active_mask'] != mask: raise ValueError('Solver active mask inconsistent with currents')
                                if not close(number(diag['cost']), float(entry['kkt'][case]['objective'])):
                                    raise ValueError('Solver objective inconsistent with frozen problem')
                                if diag['success'] is not True or Decimal(entry['kkt'][case]['violation']) != 0 or Decimal(entry['kkt'][case]['kkt_max']) > Decimal('1e-12'):
                                    result['failed_scientific_comparisons'].append(dict(run=rid, origin=origin, worker=worker, case=case, kind='solver_or_kkt'))
                                if case != 'dense':
                                    entry['recovery'][case] = {str(p): ratio(arr, currents['dense'], currents[case], spec['failed'], p) for p in (60, 90)}
                                    saved = rec['solve']['recovery'][case]['fractional_recovery']
                                    number(saved)
                                    entry['recovery'][case]['rounded_rms_probe'] = rounded_rms_probe(rec['solve']['recovery'][case]['rms_T'])
                                    high = float(entry['recovery'][case]['90']['ratio'])
                                    if not close(saved, high): result['failed_scientific_comparisons'].append(dict(run=rid, origin=origin, worker=worker, case=case, kind='saved_vs_decimal'))
                            records[origin, worker] = rec
                            run['replay_records'][origin+'/'+worker] = entry
                        attempt(rid+'/'+origin+'/'+worker, replay_check)
                attempt(rid+'/'+origin, origin_check)
            for origin in COHORTS:
                for worker in COHORTS[1:]:
                    def compare():
                        ref, cur = records[origin, COHORTS[0]], records[origin, worker]
                        provenance = dict(run=rid, origin=origin, worker=worker,
                            reference_sha256=run['replay_records'][origin+'/'+COHORTS[0]]['result_sha256'],
                            candidate_sha256=run['replay_records'][origin+'/'+worker]['result_sha256'])
                        for case in CASES:
                            a, b = [unpack(r['solve']['currents_A'][case]) for r in (ref, cur)]
                            if len(a) != len(b): raise ValueError('Current dimensions')
                            result['comparisons'].append(dict(provenance, kind='current', case=case,
                                passed=all(close(y, x) for x, y in zip(a, b))))
                            for i, (x, y) in enumerate(zip(a, b)):
                                if not close(y, x): result['failed_scientific_comparisons'].append(dict(run=rid, origin=origin, worker=worker, case=case, kind='current', index=i, reference=x, candidate=y))
                        for row in CASES[1:]:
                            a, b = [r['solve']['recovery'][row]['fractional_recovery'] for r in (ref, cur)]
                            result['comparisons'].append(dict(provenance, kind='recovery', case=row, passed=close(b, a)))
                            if not close(b, a): result['failed_scientific_comparisons'].append(dict(run=rid, origin=origin, worker=worker, case=row, kind='recovery', reference=a, candidate=b, delta=b-a))
                        field_files = [stage('replay', w)/origin/'fields.json' for w in (COHORTS[0], worker)]
                        field_records = [load(p) for p in field_files]
                        for f in field_records: fields(f)
                        for name in FIELDS:
                            if field_records[0][name]['shape'] != field_records[1][name]['shape']: raise ValueError('Field shape mismatch')
                            a, b = [flatten(unpack(f[name])) for f in field_records]
                            if len(a) != len(b): raise ValueError('Field dimensions')
                            failed = [i for i, (x, y) in enumerate(zip(a, b)) if not close(y, x)]
                            result['comparisons'].append(dict(provenance, kind='fixed_fields', component=name,
                                reference_fields_sha256=sha(field_files[0]), candidate_fields_sha256=sha(field_files[1]), passed=not failed))
                            if failed: result['failed_scientific_comparisons'].append(dict(run=rid, origin=origin, worker=worker, kind='fixed_fields', component=name, failed_indices=failed))
                    attempt(rid+'/'+origin+'/'+worker+'/comparison', compare)
            run['reciprocal_replay'] = 'COMPLETE' if len(run['replay_records']) == 16 else 'INCOMPLETE'
        attempt(rid, run_check)
    lists = [result.get(k) for k in ('download_hashes', 'historical_hashes')]
    result['LOCAL_FILE_INTEGRITY'] = 'PASS' if all(v and all(r['match'] for r in v) for v in lists) else 'INCOMPLETE_OR_FAIL'
    result['EVIDENCE_CONSISTENCY'] = 'INCOMPLETE_OR_FAIL' if result['errors'] else 'PASS'
    result['SCIENTIFIC_REPRODUCIBILITY'] = 'FAIL'
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    e, o = args.evidence.resolve(), args.output.resolve()
    if o.is_relative_to(e) or e.is_relative_to(o): raise ValueError('Output overlaps evidence')
    if not e.is_relative_to(args.repo.resolve()) or not o.is_relative_to(args.repo.resolve()):
        raise ValueError('Work only in the research checkout')
    o.mkdir(parents=True, exist_ok=False)
    result = verify(e, args.repo)
    (o/'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (o/'source.json').write_text(json.dumps({'verifier_source_sha256': sha(__file__)}, indent=2)+'\n', encoding='utf-8')
    (o/'manifest.json').write_text(json.dumps({p.name: sha(p) for p in sorted(o.iterdir()) if p.is_file()}, indent=2)+'\n', encoding='utf-8')
    return 2 if result['errors'] or result['evidence_authentication'] == 'INCOMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
