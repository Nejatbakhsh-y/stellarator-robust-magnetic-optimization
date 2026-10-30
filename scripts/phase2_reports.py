"""Generate reports only from completed hash-linked evidence."""
import hashlib
import json
import re
from pathlib import Path
import numpy as np

out = Path('results/phase2')
d = json.loads((out/'study.json').read_text())
gate = json.loads((out/'gate.json').read_text())
digest = hashlib.sha256((out/'study.json').read_bytes()).hexdigest()
assert gate['software_status'] == 'PASS' and gate['study_sha256'] == digest
training = json.loads((out/'training_audit.json').read_text())
assert training['status'] == 'PASS' and training['study_sha256'] == digest
prefix = f'# Phase 2 {{}}\n\nScientific status: **PARTIAL**. Study SHA256: `{digest}`.\n\n'
methods = '''The synthetic vacuum-filament benchmark uses the unchanged Phase 1 geometry and currents for the peak study. Angular grids are 10x24, 20x48, 40x96, each shifted by 0, 0.5 and 0.2718281828459045 cells in both angles. Peak samples are lower bounds on each polygon model's surface supremum. Signed Nelder-Mead searches start at the largest absolute sample on each grid, with 120 iterations and 240 evaluations per search. The objective is scaled by 1 mT. Angles wrap periodically; near-filament rejection is inherited from the segment solver. Failed local searches remain recorded. None provides a global certificate.

Independent adaptive smooth-circle integrals at each best candidate separate circular-geometry error from surface sampling error. Fixed-candidate segment checks use 256, 512 and 1024 segments, refining both shaping and disturbance coils. The unchanged 1e-4 configured-segment gate is applied at these candidates; it does not certify the entire surface.

Robust fits minimize the maximum training-scenario area-weighted squared residual divided by Bref squared, plus ridge times squared dimensionless command norm. Nominal fits minimize the corresponding unperturbed quadratic. Both share Phase 1's allowed 12-coil support, 3000 A bounds, ridge=1e-6 and Bref=1e-3 T; their total currents can differ. Training seeds 20261111/20261112 and counts 4/8 form four predeclared comparisons. No tuning or winner selection is performed. A single locked, previously unseen 64-scenario IID holdout uses seed 20261110 and the shifted 20x48 metric grid. This is in-distribution synthetic uncertainty, using the unchanged componentwise uniform translation, rotation, gain and offset assumptions. All raw scenario records and paired losses are saved.

Paired differences are robust RMS minus nominal RMS in tesla. Percentile paired-bootstrap intervals use 2000 resamples with seed 20261113 and assume independent scenario draws. Common holdout data make trial conclusions dependent. These intervals describe simulated-scenario sampling error conditional on the frozen training fit; they exclude numerical error and uncertainty in the assumed manufacturing distribution. Tail quantiles with 64 observations remain imprecise. No distribution-free guarantee is implied.

The training audit regenerates every frozen training scenario and checks exact scenario-record identity. It independently solves the convex dual numerically: any nonnegative scenario weights summing to one give a lower bound by minimizing their weighted quadratic loss plus ridge under the original box and support constraints. Bounded least squares solves each inner quadratic; a separate simplex optimization improves the weights. Reported primal-dual gaps use numerical arithmetic, without interval certification. This checks the finite training objective, not population performance.
'''
limitations = '''Continuum peak convergence remains UNRESOLVED: local extrema and shifted-grid samples are observed lower bounds. No interval arithmetic or global certificate is implemented. The smooth-field reference is checked at candidate locations only; it is not independently globally optimized. Polygon error and manufacturing-scenario sampling uncertainty are separate. Holdout differences are conditional on the 512-segment numerical model; their bootstrap intervals exclude discretization error. Small paired differences need their own paired segment/grid-refinement study before interpreting their sign as a smooth-field result. The Phase 1 residual error gate is not a bound on each paired difference.

Only two training seeds, two training counts and 64 IID holdout draws were executed. Magnitude, ridge, support, common-mode/correlated and shifted-envelope sensitivities remain unfinished. Current-budget matching is unavailable. No tuning was done; a separate validation cohort must be introduced before any later tuning. The larger research preset was not executed. The full-dimensional numerical dual audit and independent scalar convex reference are additional checks; neither is an interval-arithmetic proof of optimality. External SIMSOPT comparison was not executed.

This is independent synthetic reduced-order vacuum-filament research, with no Thea Energy affiliation or proprietary geometry. No confinement, equilibrium, energy-output, force, thermal, mechanical or reactor performance claim is supported. Phase 1's negative robustness finding is preserved. New results are reported across every predeclared trial without selecting favorable seeds.
'''
lines = ['| Method | finest shifted sample [microT] | local estimate [microT] | smooth at candidate [microT] | 512 relative candidate error | successful searches |',
         '|---|---:|---:|---:|---:|---:|']
for name, p in d['peaks'].items():
    sample = next(r for r in p['grids'] if r['nt'] == 40 and r['shift'] == .5)
    segment = next(r for r in p['segment_refinement'] if r['segments'] == 512)
    successes = sum(r['success'] for r in p['search']['searches'])
    lines.append(f"| {name} | {sample['sampled_peak_T']*1e6:.10f} | {abs(p['search']['best']['field_T'])*1e6:.10f} | {abs(p['smooth_reference_T'])*1e6:.10f} | {segment['relative_error']:.10g} | {successes}/{len(p['search']['searches'])} |")
lines += ['', 'Each smooth-circle number is evaluated at the polygon-search candidate. It is not a certified smooth-circle global extremum.', '',
          '| Training seed/count | mean delta [microT] | paired bootstrap 95% [microT] | fraction improved | nominal / robust sum abs current [A] |',
          '|---|---:|---:|---:|---:|']
for t in d['trials']:
    s = t['paired']; lo, hi = s['mean_bootstrap_95_T']
    lines.append(f"| {t['train_seed']}/{t['count']} | {s['mean_T']*1e6:.10f} | [{lo*1e6:.10f}, {hi*1e6:.10f}] | {s['fraction_improved']:.6f} | {t['nominal_l1_A']:.6f} / {t['robust_l1_A']:.6f} |")
lines += ['', f"Preserved Phase 1 paired mean delta: {d['phase1_paired']['mean_T']*1e6:.10f} microT (24 samples; positive is worse). Its original output has not been edited.", '',
          'Peak-location heatmaps, peak_refinement.png and paired_difference.png are computed from this study. Unrounded data and all trials are in results/phase2/study.json. Raw observations use tesla; figures and these tables convert by 1e6.']
lines += ['', '| Method | finest half-cell sample to local change [microT] | relative change |',
          '|---|---:|---:|']
for name, p in d['peaks'].items():
    sampled = next(r['sampled_peak_T'] for r in p['grids'] if r['nt'] == 40 and r['shift'] == .5)
    delta = abs(p['search']['best']['field_T'])-sampled
    lines.append(f'| {name} | {delta*1e6:.10f} | {delta/sampled:.10g} |')
lines += ['', '| Seed/count | nominal / robust q95 [microT] | nominal / robust max [microT] |',
          '|---|---:|---:|']
for t in d['trials']:
    a, b = np.array(t['nominal_rms_T'])*1e6, np.array(t['robust_rms_T'])*1e6
    lines.append(f"| {t['train_seed']}/{t['count']} | {np.quantile(a,.95):.10f} / {np.quantile(b,.95):.10f} | {a.max():.10f} / {b.max():.10f} |")
lines += ['', 'Tail estimates have only 64 independent scenario draws; these descriptive maxima and quantiles do not establish population-tail superiority.']
lines += ['', '| Seed/count | nominal training objective | robust training objective | numerical primal-dual gap |',
          '|---|---:|---:|---:|']
for t in training['trials']:
    lines.append(f"| {t['seed']}/{t['count']} | {t['nominal_training_objective']:.14g} | {t['robust_training_objective']:.14g} | {t['primal_dual_gap']:.10g} |")
lines += ['', 'Every tested minimax fit reduced its sampled training objective while worsening every paired holdout RMS. This supports objective mismatch and finite training coverage as explanations; it does not identify a unique cause or establish behavior outside the tested synthetic distribution. Training seed/count sensitivity is visible, and shared support did not match total current. No robust mean or tail superiority is established.']
validation = '''The initial 11-test Phase 1 baseline and analytical validation passed. The final expanded suite passed 17 tests. The completed regression command record contains pytest, analytical validation, full quick run, output checks and independent audit, all with actual exit code zero. Regression outputs were written separately; historical Phase 1 outputs were preserved. The independent peak gate re-evaluates candidate smooth-circle fields and recomputes paired summaries from raw saved losses. Source/evidence SHA256 entries are in manifest.json; the gate rejects changed records. Source/config fingerprints normalize CRLF to LF; numerical evidence retains exact byte hashes and is pinned against Git newline conversion. An exact Phase 1 input copy is preserved and checked against the historical input's parsed content. Staging exposed this portability issue before commit. A dedicated test was added and pytest rerun; numerical outputs were unchanged, so their completed full repeats remain applicable. The deliberate missing-evidence/corrupt-hash test returned the expected nonzero exit, retained in failure_sensitivity.json. The numerical training replay/dual audit passed; see training_audit.json and the results tables.

Full Phase 1 and Phase 2 repeated runs matched at rtol=1e-11, atol=1e-13, excluding runtime and dirty-state metadata. The fresh Phase 1 run also matched historical numerical groups. See commands.json, regression/audit.json, reproducibility.json and gate.json for executed evidence. Existing numerical tolerances were retained. CI includes the new bounded unit tests through its existing pytest step; remote CI was not observed. Research-scale experiments are not default CI jobs.
'''
# Report the executed suite count, rather than freezing the original checkpoint count.
commands = json.loads((out/'commands.json').read_text())
match = re.search(r'(\d+) passed\b', commands[0]['stdout'])
assert commands[0]['returncode'] == 0 and match, 'Missing passing pytest count'
validation = validation.replace('final expanded suite passed 17 tests',
                                f'final expanded suite passed {match.group(1)} tests')
status = '''Completed: isolated feature branch; fixed-current multi-shift grids; periodic continuous-angle searches; independent smooth-circle and segment checks at candidates; paired 64-scenario holdout across four training configurations; bootstrap intervals; six added tests; separate historical-regression audit; full repeated studies; numerical dual audit; failure-sensitive and portable evidence gate; hash-linked reports.

Unfinished: global peak certification, broader uncertainty/sensitivity matrix, explicit current-budget matching, formal arithmetic certification, paired holdout discretization refinement, external cross-code comparison and large preset. The independent full-dimensional numerical dual audit passed, as distinct from formal certification. See PHASE2_LIMITATIONS.md. No complete Phase 2 scientific verification is claimed.

Environment note: sandboxed Python initially reported a missing base executable and Git branch creation was denied. Approved execution reached the existing Python 3.11.9 environment; no environment replacement or security bypass was used. GitHub CLI configuration remains prohibited and was not inspected. No network publication was attempted; PR #1 and Phase 1 branch were left unchanged. No website repository was accessed.
'''
publication = '''Investigate remaining peak sampling error and finite-scenario minimax behavior in the synthetic planar-coil benchmark. Add periodic surface evaluation, multistart signed extrema searches, independent smooth-circle candidate checks, and four frozen-training paired holdout comparisons with bootstrap uncertainty. Preserve Phase 1 outputs and negative results.

Scientific status is PARTIAL: observed peak extrema have no global certificate; correlated/magnitude/current-budget studies remain pending. Local regression, independent gate and full repeated experiments pass; remote CI and publication are unverified.

Base: codex/stellarator-research-v1 at ad96ee2ac9e6265ca0b97caa5d0b88f13454f6b2. Do not merge PR #1 or this PR automatically.

After reviewing the local commit, run in ordinary Windows PowerShell:

```powershell
Set-Location 'C:\\Users\\nejat\\TheaResearchWorkspace\\stellarator-robust-magnetic-optimization'
git remote get-url origin
git branch --show-current
git log -1 --oneline
git status --short
git push -u origin codex/phase2-peak-robustness-uq
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/stellarator-research-v1 --head codex/phase2-peak-robustness-uq --title 'Phase 2: peak diagnostics and paired robustness uncertainty (PARTIAL)' --body-file docs/PHASE2_PR_DESCRIPTION.md
```
'''
for title, body in [('METHODS', methods), ('RESULTS', '\n'.join(lines)), ('VALIDATION', validation),
                    ('LIMITATIONS', limitations), ('EXECUTION_STATUS', status), ('PR_DESCRIPTION', publication)]:
    Path(f'docs/PHASE2_{title}.md').write_text(prefix.format(title.replace('_', ' ').lower())+body)
print('Generated six hash-linked Phase 2 reports')
