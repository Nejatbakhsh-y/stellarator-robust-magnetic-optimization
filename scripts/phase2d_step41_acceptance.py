"""Offline final acceptance audit; never modifies production or historical evidence.

Explicit inputs are STEP38 evidence and the complete STEP39/40 output roots.
Exit 2 means incomplete diagnostics; exit 1 means retained scientific failure.
The numerical backend is the separately identified STEP40 independent diagnostic,
not a production solver. No historical failure can be promoted by this protocol.
"""
import argparse
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import phase2d_step38_verify as transport

RTOL, ATOL, GUARD = D('1e-11'), D('1e-13'), D('1e-15')
SOURCE_COMMIT = '57d7652db63a81240f4234a9752b06888b471e72'
STEP41_OUTPUT_ROOT = (Path(__file__).resolve().parents[1]/'results'/'phase2d'/
                      'step41-final-acceptance-20261101-110323-7fe7248c')


def scalar(value):
    """Preserve exact binary64 inputs; decimal strings are explicit references."""
    if type(value) is bool or not isinstance(value, (int, float, str, D)):
        raise ValueError('Invalid numerical value')
    try:
        result = D.from_float(value) if type(value) is float else D(value)
    except ArithmeticError as exc:
        raise ValueError('Invalid numerical value') from exc
    if not result.is_finite():
        raise ValueError('Nonfinite numerical value')
    return result


def agrees(candidate, reference):
    # Exact rational comparison avoids dependence on the caller's Decimal context.
    a, b = F(scalar(candidate)), F(scalar(reference))
    return abs(a-b) <= F(ATOL)+F(RTOL)*abs(b)


def recovery(B, L, P, digits=90):
    if digits not in (60, 90):
        raise ValueError('Require 60/90 significant digits')
    with localcontext() as ctx:
        ctx.prec = digits
        B, L, P = map(scalar, (B, L, P))
        gap, gain = L-B, L-P
        if abs(gap) <= GUARD:
            raise ValueError('Original denominator guard')
        gradient = [gain/gap**2, (P-B)/gap**2, -1/gap]
        h = abs(gap)*D('1e-15')
        fd = []
        for j in range(3):
            plus, minus = [B,L,P], [B,L,P]
            plus[j] += h
            minus[j] -= h
            ratio = lambda z: (z[1]-z[2])/(z[1]-z[0])
            fd.append((ratio(plus)-ratio(minus))/(2*h))
        return dict(ratio=str(gain/gap), denominator=str(gap), numerator=str(gain),
                    derivatives_B_L_P=list(map(str,gradient)), finite_difference_B_L_P=list(map(str,fd)),
                    denominator_condition=str((abs(L)+abs(B))/abs(gap)),
                    numerator_condition=str((abs(L)+abs(P))/abs(gain)) if gain else None)


def mathematics():
    """Coefficient-wise exact quotient rule plus independent rational differences."""
    cases = [('1','3','2'), ('0','2','3'), ('-2','-5','1'),
             ('0.000025914425556311052','0.000025914480221164456','0.000025914502890077691')]
    records = []
    for values in cases:
        B,L,P = map(F,values)
        gap, gain = L-B,L-P
        # Differentiate numerator and denominator basis coefficients independently.
        quotient = [((dl-dp)*gap-gain*(dl-db))/gap**2
                    for db,dl,dp in [(1,0,0),(0,1,0),(0,0,1)]]
        correct = [gain/gap**2,(P-B)/gap**2,-1/gap]
        if quotient != correct:
            raise ValueError('Symbolic quotient-rule coefficients disagree')
        r = recovery(*values)
        rational_fd = []
        h = abs(gap)*F(1,10**15)
        for j in range(3):
            u,v = [B,L,P],[B,L,P]
            u[j] += h
            v[j] -= h
            ratio = lambda z:(z[1]-z[2])/(z[1]-z[0])
            difference = (ratio(u)-ratio(v))/(2*h)
            if abs(difference-correct[j]) > max(F(1),abs(correct[j]))*F(2,10**30):
                raise ValueError('Rational central difference disagrees')
            rational_fd.append(str(difference))
        for g,fd in zip(r['derivatives_B_L_P'],r['finite_difference_B_L_P']):
            if abs(F(D(g))-F(D(fd))) > max(F(1),abs(F(D(g))))*F(2,10**30):
                raise ValueError('High precision derivative disagrees')
        r.update(inputs=values, exact_derivatives=list(map(str,correct)), rational_finite_differences=rational_fd)
        records.append(r)
    return dict(status='VERIFIED', method='Exact rational coefficient extraction and central differences; Decimal 90 digits',cases=records)


def comparison(row):
    required = {'reference','candidate','pass','high_reference','high_candidate','high_pass',
                'run','origin','worker','case','input_sha256','result_sha256','reference_sha256'}
    if not isinstance(row,dict) or not required.issubset(row):
        raise ValueError('Missing comparison record')
    for key in ('input_sha256','result_sha256','reference_sha256'):
        transport.valid_digest(row[key])
    for key,a,b in [('pass','candidate','reference'),('high_pass','high_candidate','high_reference')]:
        if type(row[key]) is not bool or row[key] != agrees(row[a],row[b]):
            raise ValueError('Inconsistent comparison classification')
    return dict(row,classification='REPRODUCED' if not row['pass'] else 'VERIFIED')


def policy(errors, failures):
    # This historical acceptance protocol cannot discharge unavailable archives,
    # fresh reciprocal solver controls, or the unexecuted final-source gates.
    return dict(schema='phase2d-step41-acceptance-v1',
                diagnostic_status='INCOMPLETE' if errors else 'COMPLETE',
                scientific_comparison='FAIL' if failures else 'INCONCLUSIVE',
                causal_root_cause='INCONCLUSIVE', evidence_authentication='INCOMPLETE',
                production_acceptance='FAIL', scientific_status='PARTIAL',
                remaining_blockers=sorted(set(errors+[
                    'Unresolved historical recovery comparisons',
                    'Original GitHub archive bytes unauthenticated',
                    'Four early manifests incomplete; workflow/source provenance gaps',
                    'Fresh matched-environment reciprocal production solver experiments missing',
                    'Final-source README/test/refinement/reproducibility gates require passing SHA-bound records'])))


def reject_claims(record, expected):
    for key in ('scientific_comparison','production_acceptance','scientific_status','causal_root_cause','evidence_authentication'):
        if record.get(key) != expected[key]:
            raise ValueError('Unsupported acceptance/causal conclusion: '+key)


def bind_comparisons(rows, evidence):
    """Bind retained scalar references to the actual original saved solve bytes."""
    expected = {(run,o,w,c) for run in transport.RUNS[2:] for o in transport.COHORTS
                for w in transport.COHORTS[1:] for c in ('row3','row4')}
    seen, out, indices = set(), [], {}
    for run in transport.RUNS[2:]:
        root = evidence/'github-hosted'/run
        index = transport.load(root/'artifact-index.json')
        entries = index['artifacts']
        if len({a['id'] for a in entries}) != len(entries) or len({a['name'] for a in entries}) != len(entries):
            raise ValueError('Duplicate artifact manifest entries')
        indices[run] = {a['name']:root/('artifact-'+str(a['id'])) for a in entries}
    for raw in rows:
        row = comparison(raw)
        key = tuple(row[k] for k in ('run','origin','worker','case'))
        if key in seen or key not in expected:
            raise ValueError('Duplicate or unexpected comparison')
        seen.add(key)
        run,origin,worker,case = key
        dirs = indices[run]
        capture = dirs[f'step33-capture-{origin}-{run}-1']
        if transport.sha(capture/'inputs.json') != row['input_sha256']:
            raise ValueError('Exact input fingerprint mismatch')
        for cohort,hashkey,valuekey in [(worker,'result_sha256','candidate'),(transport.COHORTS[0],'reference_sha256','reference')]:
            sub = dirs[f'step33-replay-{cohort}-{run}-1']/origin
            if transport.sha(sub/'inputs.json') != row['input_sha256'] or transport.sha(sub/'result.json') != row[hashkey]:
                raise ValueError('Reciprocal replay fingerprint mismatch')
            actual = transport.load(sub/'result.json')['solve']['recovery'][case]['fractional_recovery']
            if scalar(actual) != scalar(row[valuekey]):
                raise ValueError('Comparison scalar differs from original result')
        out.append(row)
    if seen != expected:
        raise ValueError('Missing scientific comparison records')
    return sorted(out,key=lambda r:tuple(r[k] for k in ('run','origin','worker','case')))


def audit(evidence, step39, step40, repo, numerical=True):
    errors, records = [], []
    details = dict(mathematics=mathematics(), manifests={}, errors=[], numerical_backend='NOT EXECUTED')
    for name,path in [('step39',step39),('step40',step40)]:
        try:
            details['manifests'][name] = transport.manifest(path/'manifest.json')
        except (ValueError,OSError,TypeError) as exc:
            errors.append(name+': '+str(exc))
    try:
        details['transport'] = transport.verify(evidence,repo)
        errors.extend('transport: '+str(e) for e in details['transport']['errors'])
        records = bind_comparisons(transport.load(step40/'recovery-comparisons.json'),evidence)
        details['comparisons'] = records
        details['failure_counts'] = {run:sum(not r['pass'] for r in records if r['run']==run) for run in transport.RUNS[2:]}
        # Validate high precision records against the separately retained per-cell evaluations.
        high = transport.load(step40/'high-precision-recovery.json')
        lookup = {}
        for r in high:
            key = tuple(r[k] for k in ('run','origin','worker','case'))
            if key in lookup:
                raise ValueError('Duplicate high precision record')
            scalar(r['ratio90'])
            lookup[key] = r
        if len(lookup) != 64:
            raise ValueError('Missing high precision records')
        for r in records:
            for worker,val,seal in [(r['worker'],'high_candidate','result_sha256'),(transport.COHORTS[0],'high_reference','reference_sha256')]:
                saved = lookup[(r['run'],r['origin'],worker,r['case'])]
                if scalar(saved['ratio90']) != scalar(r[val]) or saved['result_sha256'] != r[seal]:
                    raise ValueError('Inconsistent high precision comparison')
    except (ValueError,OSError,KeyError,TypeError,ArithmeticError) as exc:
        errors.append('scientific inputs: '+str(exc))
    if numerical:
        try:
            import phase2d_step40_validation as backend
            details['numerical_backend_sha256'] = transport.sha(backend.__file__)
            # Independently developed prior diagnostic: explicit reuse, no production call.
            result = backend.run(evidence,repo,controls=False)
            details['numerical_backend'] = result
            if not result.get('local_evidence_complete') or result['errors']:
                errors.append('Independent numerical backend incomplete')
            details['numerical_failures'] = result['numerical_failures']
            fresh = {tuple(r[k] for k in ('run','origin','worker','case')):r for r in result['comparisons']}
            if len(fresh) != 48:
                errors.append('Incomplete independently recomputed comparison grid')
            for row in records:
                key = tuple(row[k] for k in ('run','origin','worker','case'))
                if key not in fresh:
                    continue
                probe = fresh[key]
                with localcontext() as ctx:
                    ctx.prec = 90
                    expected_delta = scalar(row['high_candidate'])-scalar(row['high_reference'])
                    if (probe['saved_pass'] != row['pass'] or probe['high_precision_pass'] != row['high_pass']
                            or not agrees(probe['high_precision_delta'],expected_delta)):
                        errors.append('Stored versus fresh numerical comparison disagreement: '+str(key))
        except (ImportError,ValueError,OSError,KeyError,TypeError,ArithmeticError) as exc:
            errors.append('numerical backend: '+str(exc))
    else:
        errors.append('Fresh numerical recomputation explicitly omitted')
    details['errors'] = sorted(errors)
    details['implementation_sha256'] = transport.sha(__file__)
    details['requested_source_commit'] = SOURCE_COMMIT
    details['transport_sha256'] = transport.sha(transport.__file__)
    details['limits'] = dict(rtol=str(RTOL),atol=str(ATOL),refinement='1e-4',segments=512)
    return policy(errors,[r for r in records if not r['pass']]), details


def output_path(root, output, inputs):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root) or output == root:
        raise ValueError('Output must be a fresh child of STEP41_OUTPUT_ROOT')
    for path in inputs:
        path = path.resolve()
        if output.is_relative_to(path) or path.is_relative_to(output) or root.is_relative_to(path):
            raise ValueError('Output and historical evidence must be disjoint')
    if output.exists():
        raise ValueError('Refuse to overwrite existing output')
    return output


def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(__doc__)
    for key in ('evidence','step39','step40','output-root','output'):
        parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--records-only',action='store_true',help='Explicit incomplete diagnostics; no fresh numerical backend')
    args = parser.parse_args()
    inputs = [args.evidence,args.step39,args.step40]
    repo = Path(__file__).resolve().parents[1]
    if (not args.output_root.resolve().is_relative_to(STEP41_OUTPUT_ROOT.resolve())
            or not all(p.resolve().is_relative_to(repo) for p in inputs)):
        raise ValueError('Repository and authorized STEP41_OUTPUT_ROOT containment required')
    out = output_path(args.output_root,args.output,inputs)
    result,details = audit(*[p.resolve() for p in inputs],repo,not args.records_only)
    out.mkdir(parents=True,exist_ok=False)
    write(out/'acceptance.json',result)
    write(out/'diagnostics.json',details)
    write(out/'manifest.json',{p.name:transport.sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    return 2 if result['diagnostic_status']=='INCOMPLETE' else 1


if __name__ == '__main__':
    sys.exit(main())
