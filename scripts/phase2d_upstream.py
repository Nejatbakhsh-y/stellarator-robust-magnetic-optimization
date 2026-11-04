"""Fresh-output-only CLI for upstream attribution experiments."""
import argparse
import json
from pathlib import Path
from stellarator_robust.upstream_attribution import (capture, environment, write, sha, manifest,
                                                    solve_inputs, field_replay, close, unpack, independent_field_checks,
                                                    source_fingerprints, verify_worker, identical_solver_inputs,
                                                    INPUT_ARRAYS, verify_historical_sources, load_evidence, validate_inputs)


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('command', choices=['prepare', 'run', 'compare', 'historical'])
    p.add_argument('--output', required=True)
    p.add_argument('--input')
    p.add_argument('--input-sha256')
    p.add_argument('--reference')
    p.add_argument('--current')
    a = p.parse_args()
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=False)
    state = dict(status='INCONCLUSIVE', scientific_status='PARTIAL', production_cross_platform='UNRESOLVED')
    code = 0
    try:
        write(out/'environment.json', environment())
        write(out/'source_sha256.json', source_fingerprints())
        if a.command == 'prepare':
            config = json.loads(Path('configs/phase2c_quick.json').read_text())
            write(out/'inputs.json', capture(config))
            state.update(status='PASS', input_sha256=sha(out/'inputs.json'))
        elif a.command == 'run':
            if not a.input_sha256 or sha(a.input) != a.input_sha256:
                raise ValueError('Missing/mismatched sealed input SHA256')
            data = load_evidence(a.input)
            validate_inputs(data)
            (out/'sealed-inputs.json').write_bytes(Path(a.input).read_bytes())
            if set(data['cases']) != {'dense', 'row3', 'row4'} or set(data['arrays']) != INPUT_ARRAYS:
                raise ValueError('Incomplete sealed solver inputs')
            regenerated = capture(data['config'])
            write(out/'regenerated-inputs.json', regenerated)
            equality = {k: close(unpack(v), unpack(regenerated['arrays'][k])) for k, v in data['arrays'].items()}
            write(out/'input-comparisons.json', equality)
            frozen, rebuilt = solve_inputs(data), solve_inputs(regenerated)
            write(out/'frozen-solve.json', frozen)
            write(out/'regenerated-solve.json', rebuilt)
            write(out/'frozen-fields.json', field_replay(data))
            independent = independent_field_checks(data)
            write(out/'independent-fields.json', independent)
            checks = {}
            checks['complete_cases'] = all(set(r['diagnostics']) == {'dense', 'row3', 'row4'}
                                            for r in (frozen, rebuilt))
            checks['independent_fields'] = independent['status'] == 'PASS'
            for stage, result in [('frozen', frozen), ('regenerated', rebuilt)]:
                for name, d in result['diagnostics'].items():
                    checks[stage+'/'+name] = (d['success'] and d['repeated']['status'] == 'PASS' and
                                             d['reference_check']['status'] == 'PASS' and
                                             d['reference_check']['solver']['status'] == 'PASS')
            incomplete = any(d['reference_check']['status'] == 'INCONCLUSIVE'
                             for result in (frozen, rebuilt) for d in result['diagnostics'].values())
            state.update(status='INCONCLUSIVE' if incomplete else ('PASS' if all(checks.values()) else 'FAIL'), checks=checks,
                         input_sha256=a.input_sha256,
                         note='Worker gates only; production agreement requires independent completed comparisons')
            code = 0 if all(checks.values()) else 1
        elif a.command == 'historical':
            from stellarator_robust.phase2b import verify_manifest
            root = Path(a.reference)
            verify_manifest(root)
            evidence = verify_historical_sources(root)
            write(out/'historical-provenance.json', evidence)
            state.update(status='INCONCLUSIVE',
                         note='Source hashes checked; authenticated archive/run evidence unavailable')
            code = 2
        else:
            ref, cur = Path(a.reference), Path(a.current)
            # Require every artifact byte to match its manifest before using scientific results.
            states = [verify_worker(root, a.input_sha256) for root in (ref, cur)]
            identical_solver_inputs(ref, cur, a.input_sha256)
            checks = {}
            for file in ('frozen-solve.json', 'regenerated-solve.json'):
                r, c = [json.loads((root/file).read_text()) for root in (ref, cur)]
                for name in r['currents_A']:
                    checks[file+'/'+name] = close(unpack(r['currents_A'][name]), unpack(c['currents_A'][name]))
                for name in ('row3', 'row4'):
                    checks[file+'/'+name+'/ratio'] = close(r['recovery'][name]['fractional_recovery'], c['recovery'][name]['fractional_recovery'])
            r, c = [json.loads((root/'sealed-inputs.json').read_text()) for root in (ref, cur)]
            if r != c:
                raise ValueError('Workers did not consume identical inputs')
            for file, key in [('frozen-fields.json', None), ('regenerated-inputs.json', 'arrays')]:
                r, c = [json.loads((root/file).read_text()) for root in (ref, cur)]
                if key:
                    r, c = r[key], c[key]
                for name in r:
                    checks[file+'/'+name] = close(unpack(r[name]), unpack(c[name]))
            write(out/'comparisons.json', checks)
            workers_pass = all(s['status'] == 'PASS' for s in states)
            passed = workers_pass and bool(checks) and all(v['status'] == 'PASS' for v in checks.values())
            state.update(status='PASS' if passed else 'FAIL',
                         evidence_status='COMPLETE',
                         production_cross_platform='UNRESOLVED: separate full production workflow required',
                         worker_statuses_pass=workers_pass,
                         note='Input exactness recorded separately from tolerance agreement; no individual library causality inferred')
            code = 0 if passed else 1
    except Exception as exc:
        state.update(status='FAIL', evidence_status='MISSING' if isinstance(exc, FileNotFoundError) else 'INVALID',
                     error=repr(exc), note='Evidence gate failure; not an executed scientific calculation failure')
        code = 2
    finally:
        write(out/'status.json', state)
        manifest(out)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
