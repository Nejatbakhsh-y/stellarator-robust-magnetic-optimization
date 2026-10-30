"""Generate a concise local report only from passing, hash-linked v2 evidence."""
import re
from pathlib import Path
from stellarator_robust.phase2b import load, require_complete, verify_manifest, sha

out = Path('results/phase2b'); record = require_complete(out); verify_manifest(out)
d = load(out/'study/study.json'); gate = load(out/'gate.json')
analysis = load(out/'investigation/analysis.json')
training = load(out/'study/training_audit.json')
count = re.search(r'(\d+) passed', (out/'final-tests.log').read_text()).group(1)
lines = ['# Phase 2B local numerical results', '',
         'Scientific status: **PARTIAL**. Hosted cross-platform status must be observed separately.', '',
         f"Benchmark: `{record['benchmark_version']}`.",
         f"Study SHA256: `{record['study_sha256']}`.",
         f"Quick SHA256: `{record['quick_sha256']}`.", '',
         f'Final local suite: {count} passed. All nine numerical pipeline commands returned 0.',
         'Two complete quick and Phase 2 studies matched at rtol=1e-11, atol=1e-13.',
         'The independent quick audit, independent training replay/dual audit and candidate smooth-circle checks pass.', '',
         '| Method | observed finite peak [T] | smooth field at candidate [T] | configured relative polygon error |',
         '|---|---:|---:|---:|']
for name, p in d['peaks'].items():
    error = gate['candidate_checks'][name]['configured_relative_error']
    lines.append(f"| {name} | {abs(p['search']['best']['field_T']):.17g} | {abs(p['smooth_reference_T']):.17g} | {error:.17g} |")
lines += ['', 'These are observed lower bounds and candidate evaluations, not continuum supremum certificates.', '',
          '| Seed / count | robust minus nominal mean RMS [T] | fraction improved |', '|---|---:|---:|']
for t in d['trials']:
    lines.append(f"| {t['train_seed']} / {t['count']} | {t['paired']['mean_T']:.17g} | {t['paired']['fraction_improved']:.17g} |")
lines += ['', 'Every tested minimax fit still worsens this synthetic holdout; no robustness superiority is inferred.', '',
          '## Preserved trace and convergence analysis', '',
          f"All {len(analysis['legacy_trace_discrepancies'])} archived peak discrepancies are retained as legacy failures.",
          'They comprise 97 coordinate fields, 46 algorithmic trace fields, and two dimensionless refinement-error fields.',
          f"Maximum common-geometry field difference from the old coordinate changes: {max(r['common_geometry_field_difference_T'] for r in analysis['conditioning']):.17g} T.", '',
          '| Method | finite / Nelder–Mead best-field gap [T] | 20 / 28 level field change [T] |', '|---|---:|---:|']
for name, item in analysis['corrected_peak_sensitivity'].items():
    change = abs(item['finite_refinements']['20']['best']['field_T']-item['finite_refinements']['28']['best']['field_T'])
    lines.append(f"| {name} | {item['best_field_gap_to_NM_T']:.17g} | {change:.17g} |")
lines += ['', f"Largest numerical dual gap: {max(t['primal_dual_gap'] for t in training['trials']):.17g}.",
          'This is a numerical finite-scenario check, not an interval certificate or population guarantee.', '',
          'All 38 original Phase 1/2 evidence files, including their command and fingerprint records, are byte-preserved.',
          'The retained original study SHA256 is 395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.',
          'Current raw data, repeated data, failed audit diagnostic, historical Linux data, command logs and manifests are under results/phase2b/.',
          'No global peak, equilibrium, confinement, engineering or device validation is established.']
Path('docs/PHASE2B_RESULTS.md').write_text('\n'.join(lines)+'\n')
print('Generated hash-linked Phase 2B local report; remote status not inferred')
