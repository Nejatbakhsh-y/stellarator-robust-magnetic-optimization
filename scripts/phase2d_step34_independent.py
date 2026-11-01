"""Standard-library forensic recomputation, independent of NumPy/SciPy.

This can inspect evidence on a maintenance interpreter; it does not replace the
required Python 3.11 production/regression gates or authenticate hosted archives.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import struct
import subprocess

COHORTS = ('windows-reference', 'linux-reference', 'linux-numpy-sensitivity', 'linux-scipy-sensitivity')


def load(p):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('Duplicate key')
            out[k] = v
        return out
    def finite_float(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('Nonfinite JSON number')
        return value
    return json.loads(p.read_text(encoding='utf-8-sig'), object_pairs_hook=pairs, parse_float=finite_float,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def unpack(v):
    if (not isinstance(v, dict) or set(v) != {'shape', 'binary64_le'}
            or not isinstance(v['shape'], list)
            or any(type(n) is not int or n < 0 for n in v['shape'])
            or not isinstance(v['binary64_le'], str)
            or re.fullmatch('[0-9a-f]*', v['binary64_le']) is None
            or len(v['binary64_le']) != 16*math.prod(v['shape'])):
        raise ValueError('Invalid canonical float64 payload')
    shape = v['shape']
    flat = list(struct.unpack('<'+'d'*math.prod(shape), bytes.fromhex(v['binary64_le'])))
    if not all(math.isfinite(x) for x in flat):
        raise ValueError('Nonfinite payload')
    def nest(values, dims):
        if not dims:
            return values[0]
        size = math.prod(dims[1:])
        return [nest(values[i*size:(i+1)*size], dims[1:]) for i in range(dims[0])]
    return nest(flat, shape)


def dec(v):
    return D.from_float(v) if isinstance(v, float) else D(v)


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('Mismatched scientific vector dimensions')
    return sum((x*y for x, y in zip(a, b)), D(0))


def close(a, b):
    return abs(a-b) <= 1e-13+1e-11*abs(b)


def ratio(arr, dense, recovered, failed, precision):
    rows = arr['fine_A']
    if (len(rows) != len(arr['fine_b']) or len(rows) != len(arr['fine_weights'])
            or not rows or len(dense) != len(recovered)
            or any(len(row) != len(dense) for row in rows)
            or type(failed) is not int or not 0 <= failed < len(dense)):
        raise ValueError('Invalid recovery dimensions or fault index')
    with localcontext() as ctx:
        ctx.prec = precision
        frozen = dense.copy(); frozen[failed] = 0.
        currents = [list(map(dec, x)) for x in (dense, frozen, recovered)]
        totals = [D(0)]*3
        for row, b, w in zip(arr['fine_A'], arr['fine_b'], arr['fine_weights']):
            row = list(map(dec, row)); b, w = dec(b), dec(w)
            for i, x in enumerate(currents):
                totals[i] += w*(b+dot(row, x))**2
        B, L, P = [t.sqrt() for t in totals]
        den, num = L-B, L-P
        return dict(rms_T=list(map(str, (B, L, P))), numerator_T=str(num), denominator_T=str(den),
                    ratio=str(num/den) if abs(den) > D('1e-15') else None,
                    numerator_condition=str((abs(L)+abs(P))/abs(num)) if num else None,
                    denominator_condition=str((abs(L)+abs(B))/abs(den)) if den else None,
                    derivatives_B_L_P=list(map(str, (num/den**2, (den-num)/den**2, -1/den))) if den else None)


def kkt(M, y, x):
    if not M or len(M) != len(y) or not x or any(len(row) != len(x) for row in M):
        raise ValueError('Invalid KKT dimensions')
    with localcontext() as ctx:
        ctx.prec = 90
        mm = [list(map(dec, row)) for row in M]; xx = list(map(dec, x))
        r = [dot(row, xx)-dec(b) for row, b in zip(mm, y)]
        g = [dot([row[j] for row in mm], r) for j in range(len(x))]
        kk = [min(v, D(0)) if a == -1 else max(v, D(0)) if a == 1 else v for a, v in zip(xx, g)]
        return dict(objective=str(dot(r, r)/2), kkt_max=str(max(map(abs, kk))),
                    bound_violation=str(max(D(0), max(abs(v)-1 for v in xx))),
                    active_lower=[i for i, v in enumerate(xx) if v == -1],
                    active_upper=[i for i, v in enumerate(xx) if v == 1])


def singular_values(M):
    # Independent symmetric Jacobi diagonalization of the Gram matrix. Diagnostic
    # only: normal equations square conditioning; no production solve is replaced.
    n = len(M[0])
    g = [[math.fsum(row[i]*row[j] for row in M) for j in range(n)] for i in range(n)]
    for _ in range(100*n*n):
        p, q = max(((i, j) for i in range(n) for j in range(i+1, n)), key=lambda ij: abs(g[ij[0]][ij[1]]))
        if abs(g[p][q]) <= 1e-16*max(abs(g[i][i]) for i in range(n)):
            break
        angle = .5*math.atan2(2*g[p][q], g[q][q]-g[p][p])
        c, s = math.cos(angle), math.sin(angle)
        app, aqq, apq = g[p][p], g[q][q], g[p][q]
        for i in range(n):
            if i not in (p, q):
                a, b = g[i][p], g[i][q]
                g[i][p] = g[p][i] = c*a-s*b
                g[i][q] = g[q][i] = s*a+c*b
        g[p][p] = c*c*app-2*c*s*apq+s*s*aqq
        g[q][q] = s*s*app+2*c*s*apq+c*c*aqq
        g[p][q] = g[q][p] = 0.
    return sorted((math.sqrt(max(0., g[i][i])) for i in range(n)), reverse=True)


def field(points, vertices, current):
    # Finite segment integral from endpoint vectors, Decimal throughout.
    with localcontext() as ctx:
        ctx.prec = 90
        vv = [list(map(dec, v)) for v in vertices]; out = []
        for point in points:
            pp = list(map(dec, point)); total = [D(0)]*3
            for a, b in zip(vv, vv[1:]+vv[:1]):
                r, t = [[p-v for p, v in zip(pp, v)] for v in (a, b)]
                nr, nt = dot(r, r).sqrt(), dot(t, t).sqrt()
                denominator = nr*nt*(nr*nt+dot(r, t))
                if denominator <= 0:
                    raise ValueError('Singular finite-segment field reference')
                factor = (nr+nt)/denominator
                cross = [r[1]*t[2]-r[2]*t[1], r[2]*t[0]-r[0]*t[2], r[0]*t[1]-r[1]*t[0]]
                total = [v+c*factor for v, c in zip(total, cross)]
            out.append([str(v*D('1e-7')*dec(current)) for v in total])
        return out


def analyze(root, output):
    runs = sorted(root.glob('run-*'))
    if not runs:
        raise ValueError('Missing historical runs')
    if output.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(output.resolve()):
        raise ValueError('Evidence and output must be disjoint')
    output.mkdir(parents=True, exist_ok=False)
    report = dict(interpreter=platform.python_version(), scope='stdlib forensic recomputation; not Python 3.11 production validation', runs={})
    source_cache = {}
    for run in runs:
        print('Reviewing', run.name, flush=True)
        artifacts = run/'artifacts'; rid = run.name[4:]
        path = lambda stage, cohort: artifacts/f'step33-{stage}-{cohort}-{rid}-1'
        inventory = {p.relative_to(run).as_posix(): sha(p) for p in run.rglob('*') if p.is_file()}
        checks = []
        for manifest in artifacts.rglob('manifest.json'):
            expected = load(manifest)
            actual = {p.relative_to(manifest.parent).as_posix(): sha(p) for p in manifest.parent.rglob('*') if p.is_file() and p != manifest}
            checks.append(dict(path=manifest.relative_to(run).as_posix(), exact=expected == actual))
        downloaded = load(run/'downloaded-file-hashes.json')
        download_checks = []
        for v in downloaded:
            target = (artifacts/Path(v['path'].replace('\\', '/'))).resolve()
            if not target.is_relative_to(artifacts.resolve()):
                raise ValueError('Unsafe download inventory path')
            download_checks.append(dict(path=v['path'], match=sha(target) == v['sha256']))
        assessment = load(artifacts/f'step33-comparison-{rid}-1/comparison/assessment.json')
        result = dict(inventory=inventory, manifests=checks, download_hashes=download_checks,
                      historical_failures=assessment['failures'], environments={}, sources={}, captures={}, replays={}, comparisons={})
        caps, records = {}, {}
        for cohort in COHORTS:
            cap = path('capture', cohort); data = load(cap/'inputs.json')
            arr = {k: unpack(v) for k, v in data['arrays'].items()}; caps[cohort] = (data, arr)
            result['environments'][cohort] = load(path('replay', cohort)/'environment.json')
            provenance = load(cap/'source-sha256.json'); source_records = {}
            for name, digest in provenance['sha256'].items():
                key = (provenance['head'], name)
                if key not in source_cache:
                    blob = subprocess.run(['git', 'show', key[0]+':'+name], capture_output=True)
                    source_cache[key] = dict(git_available=blob.returncode == 0,
                                            git_sha256=hashlib.sha256(blob.stdout).hexdigest() if blob.returncode == 0 else None)
                source_records[name] = dict(recorded=digest, **source_cache[key],
                    matches_git=source_cache[key]['git_sha256'] == digest,
                    working_sha256=sha(Path(name)) if Path(name).is_file() else None)
            result['sources'][cohort] = dict(head=provenance['head'], paths=source_records,
                replay_source_equal=load(path('replay', cohort)/'source-sha256.json') == provenance)
            result['captures'][cohort] = dict(input_sha256=sha(cap/'inputs.json'),
                seal_match=load(cap/'input-sha256.json')['inputs.json'] == sha(cap/'inputs.json'), cases=data['cases'], conditioning={})
            for case in ('dense', 'row3', 'row4'):
                sv = singular_values(arr[case+'_M'])
                result['captures'][cohort]['conditioning'][case] = dict(singular_values=sv, condition=sv[0]/sv[-1])
            probes = [arr['points'][i] for i in (0, len(arr['points'])//3)]
            fields = [field(probes, v, 1500. if i == len(arr['vertices']) else 1.) for i, v in enumerate([*arr['vertices'], arr['error_vertices']])]
            for worker in COHORTS:
                sub = path('replay', worker)/cohort; rec = load(sub/'result.json'); records[cohort, worker] = rec
                entry = dict(result_sha256=sha(sub/'result.json'), input_bytes_equal=(sub/'inputs.json').read_bytes() == (cap/'inputs.json').read_bytes(),
                             input_seal_match=load(path('replay', worker)/'input-sha256.json')[cohort] == sha(cap/'inputs.json'), ratios={}, kkt={}, fields={})
                for case in ('dense', 'row3', 'row4'):
                    support = data['cases'][case].get('support', list(range(len(arr['dense_x']))))
                    current = unpack(rec['solve']['currents_A'][case]); x = [current[i]/data['config']['imax_A'] for i in support]
                    entry['kkt'][case] = kkt(arr[case+'_M'], arr[case+'_y'], x)
                    if case != 'dense':
                        dense = unpack(rec['solve']['currents_A']['dense'])
                        entry['ratios'][case] = {str(p): ratio(arr, dense, current, data['cases'][case]['failed'], p) for p in (60, 90)}
                        high = entry['ratios'][case]['90']['ratio']
                        entry['ratios'][case]['saved_minus_reference'] = str(dec(rec['solve']['recovery'][case]['fractional_recovery'])-D(high)) if high else None
                saved_fields = load(sub/'independent-fields.json')
                for i, computed in enumerate(fields):
                    saved = saved_fields['coils'][str(i)]['reference90']
                    entry['fields'][str(i)] = dict(max_decimal_difference=str(max(abs(D(a)-D(b)) for aa, bb in zip(saved, computed) for a, b in zip(aa, bb))),
                        binary64_equal=all(float(a) == float(b) for aa, bb in zip(saved, computed) for a, b in zip(aa, bb)))
                result['replays'][cohort+'/'+worker] = entry
        for origin in COHORTS:
            for worker in COHORTS[1:]:
                left, right = [records[origin, w] for w in (COHORTS[0], worker)]
                comp = {}
                for case in ('dense', 'row3', 'row4'):
                    a, b = [unpack(r['solve']['currents_A'][case]) for r in (left, right)]
                    comp[case] = dict(max_current_difference_A=max(abs(x-y) for x, y in zip(a, b)),
                                     fails=sum(not close(x, y) for x, y in zip(a, b)))
                for row in ('row3', 'row4'):
                    a, b = [r['solve']['recovery'][row]['fractional_recovery'] for r in (left, right)]
                    comp[row+'/recovery'] = dict(reference=a, current=b, passes=close(a, b))
                result['comparisons'][origin+'/'+worker] = comp
        # Controlled substitutions: same saved current, change one field/weight block.
        base, aa = caps[COHORTS[0]]
        result['controlled_substitutions'] = {}
        for cohort in COHORTS[1:]:
            other, bb = caps[cohort]; interventions = {}
            for row in ('row3', 'row4'):
                dense = unpack(records[COHORTS[0], COHORTS[0]]['solve']['currents_A']['dense'])
                recovered = unpack(records[COHORTS[0], COHORTS[0]]['solve']['currents_A'][row])
                interventions[row] = {'baseline': ratio(aa, dense, recovered, base['cases'][row]['failed'], 90)}
                for block in ('fine_A', 'fine_b', 'fine_weights'):
                    hybrid = dict(aa); hybrid[block] = bb[block]
                    interventions[row][block] = ratio(hybrid, dense, recovered, base['cases'][row]['failed'], 90)
            result['controlled_substitutions'][cohort] = interventions
        report['runs'][run.name] = result
        (output/(run.name+'.json')).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (output/'summary.json').write_text(json.dumps(dict(interpreter=report['interpreter'], scope=report['scope'], runs=list(report['runs'])), indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps({p.name: sha(p) for p in output.iterdir() if p.is_file()}, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.evidence.resolve()):
        raise ValueError('Keep original evidence disjoint from analysis outputs')
    analyze(args.evidence, args.output)
