"""Read-only Step 31E assessment. Exit zero means diagnostic completion only.

Run from the repository root using the existing Python 3.11 environment.
The Step 31 numerical replay is reused explicitly, not called independent code.
"""
import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase2d_step31_diagnose as d


def attribution(commit):
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError('Missing or invalid source commit')
    return 'MATCH' if commit == d.COMMIT else 'MISMATCH'


def verify_sources(analysis_path, summary_path, raw):
    analysis = d.load_evidence(analysis_path)
    summary = d.load_evidence(summary_path)
    if summary.get('original_analysis_sha256') != d.sha(analysis_path):
        raise ValueError('Summary/analysis fingerprint mismatch')
    manifests = d.load_evidence(analysis_path.parent/'manifest.json')
    if manifests.get(analysis_path.name) != d.sha(analysis_path):
        raise ValueError('Analysis manifest fingerprint mismatch')
    for value in (analysis, summary):
        if attribution(value.get('source_commit')) != 'MATCH':
            raise ValueError('Incorrect reference commit attribution')
        if str(value.get('source_run_id')) != '41231422708':
            raise ValueError('Incorrect source run attribution')
    sources = d.inventory(raw.parent)
    d.verify_manifests(raw.parent)
    return analysis, summary, sources


def vector_metrics(left, right):
    a, b = d.unpack(left), d.unpack(right)
    if a.shape != b.shape:
        raise ValueError('Vector shape mismatch')
    delta = abs(b-a)
    nz = a != 0
    return dict(max_absolute=float(np.max(delta)),
                max_relative_on_nonzero_reference=float(np.max(delta[nz]/abs(a[nz]))) if nz.any() else None,
                changed_zero_reference_count=int(np.count_nonzero((~nz) & (delta != 0))),
                vector_difference_norm=float(np.linalg.norm(delta)),
                **d.compare_array(left, right))


def failed_nodes(value, path=''):
    """Retain all failed records, including nested/duplicate scientific paths."""
    out = []
    if isinstance(value, dict):
        if value.get('status') == 'FAIL':
            out.append(dict(path=path, record=value))
        for k, v in value.items():
            out.extend(failed_nodes(v, path+'/'+str(k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(failed_nodes(v, path+'/'+str(i)))
    return out


def classify(complete, failures):
    return 'FAIL' if failures else ('INCONCLUSIVE' if not complete else 'UNRESOLVED')


def assess(analysis_path, summary_path, raw):
    original, summary, sources = verify_sources(analysis_path, summary_path, raw)
    # Recompute KKT, 60/90-digit ratios, current/model interventions and independent
    # finite-segment references from actual binary64 records; no optimizer reruns.
    replay, checked = d.diagnose(raw.parent)
    if sources != checked:
        raise ValueError('Source inventory changed during assessment')
    extra = {}
    for worker in d.WORKERS:
        base = raw/('upstream-'+worker)/'upstream-worker'
        extra[worker] = {}
        for stage in ('frozen', 'regenerated'):
            data = d.load_evidence(base/('sealed-inputs.json' if stage == 'frozen' else 'regenerated-inputs.json'))
            result = d.load_evidence(base/(stage+'-solve.json'))
            reference = d.load_evidence(raw/'upstream-windows-reference/upstream-worker'/(stage+'-solve.json'))
            cases = {}
            for case in d.CASES:
                M = d.unpack(data['arrays'][case+'_M'])
                s = np.linalg.svd(M, compute_uv=False)
                currents = d.unpack(result['currents_A'][case])
                cases[case] = dict(currents=vector_metrics(reference['currents_A'][case], result['currents_A'][case]),
                    constraint_violation_A=float(max(0., np.max(abs(currents))-data['config']['imax_A'])),
                    effective_rank=int(np.linalg.matrix_rank(M)), condition=float(s[0]/s[-1]),
                    singular_values=s.tolist())
            extra[worker][stage] = cases
    field_vectors = {}
    fixed_reference = d.load_evidence(raw/'upstream-windows-reference/upstream-worker/frozen-fields.json')
    for worker in d.WORKERS[1:]:
        fixed = d.load_evidence(raw/('upstream-'+worker)/'upstream-worker/frozen-fields.json')
        field_vectors[worker] = {k: vector_metrics(v, fixed[k]) for k, v in fixed_reference.items()}
    failures = failed_nodes(replay['original_comparisons'])
    return dict(conclusion=dict(diagnostic_status='COMPLETE', production_acceptance=classify(True, failures),
                    evidence_integrity='PASS', hosted_artifact_byte_authentication='INCONCLUSIVE',
                    numerical_attribution='INCONCLUSIVE', scientific_status='PARTIAL'),
                source_analysis_sha256=d.sha(analysis_path), source_summary_sha256=d.sha(summary_path),
                original_source_count=len(sources), original_failed_records=failures,
                source_analysis_failed_records=failed_nodes(original), numerical_replay=replay,
                additional_solver_metrics=extra, fixed_field_vector_comparisons=field_vectors,
                limitations=['Local hashes verify bytes, not external authenticity.',
                    'Worker commit differs from reference; semantic source attribution unresolved.',
                    'Replay shares Step 31 implementation; independent Decimal references are limited to rounded inputs.',
                    'Reciprocal regenerated-input solves on all four platforms remain unavailable.',
                    'No unique BLAS/LAPACK/NumPy/SciPy mechanism established.']), sources


def markdown(result):
    lines = ['# Step 31E numerical assessment', '', str(result['conclusion']), '',
             'Diagnostic completion does not establish production acceptance.', '',
             'Full failed comparison records and numerical details are retained in assessment.json.', '',
             '| Cohort | Stage | Row | Error | Bound | Exceedance | Status |',
             '|---|---|---|---:|---:|---:|---|']
    for worker, comparison in result['numerical_replay']['comparisons'].items():
        for stage in ('frozen', 'regenerated'):
            for row, record in comparison[stage]['recovery'].items():
                lines.append('| '+' | '.join(map(str, [worker, stage, row, record['absolute_error'],
                    record['threshold'], record['exceedance'], record['status']]))+' |')
    lines += ['', *result['limitations'], '',
              'Inspect numerical_replay.interventions for 60/90-digit RMS, cancellation factors,',
              'differential terms, arithmetic residuals, current/model effects and interaction.',
              'These are reevaluations of rounded records, not extra optimizer precision.']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    for name in ('analysis', 'summary', 'raw-root', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.output.resolve()
    for source in (args.raw_root.resolve(), args.analysis.resolve().parent, args.summary.resolve().parent):
        if out.is_relative_to(source) or source.is_relative_to(out):
            raise ValueError('Output must be disjoint from evidence')
    out.mkdir(parents=True, exist_ok=False)
    try:
        result, sources = assess(args.analysis, args.summary, args.raw_root.resolve())
        d.write(out/'assessment.json', result)
        d.write(out/'status.json', result['conclusion'])
        d.write(out/'evidence-sha256.json', dict(analysis=d.sha(args.analysis), summary=d.sha(args.summary), raw=sources))
        (out/'assessment.md').write_text(markdown(result), encoding='utf-8')
        return 0
    except Exception as exc:
        state = dict(diagnostic_status='FAIL', production_acceptance='FAIL', evidence_integrity='INCONCLUSIVE',
                     scientific_status='PARTIAL', error=repr(exc))
        for name in ('assessment', 'status'):
            d.write(out/(name+'.json'), state)
        d.write(out/'evidence-sha256.json', {})
        (out/'assessment.md').write_text('Assessment failed: '+repr(exc)+'\n', encoding='utf-8')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
