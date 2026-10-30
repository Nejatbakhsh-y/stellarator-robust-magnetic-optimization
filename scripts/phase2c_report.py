"""Generate a report only from complete, hash-verified numerical records."""
from pathlib import Path
from stellarator_robust.phase2c import require_complete,verify_manifest,preserve_previous,pair
from stellarator_robust.phase2b import load,sha

root=Path('results/phase2c'); record=require_complete(root); verify_manifest(root)
pair(root,root/'repeat'); preserved=preserve_previous()
q=load(root/'quick/results.json'); old=load('results/phase2b/quick/results.json')
audit=load(root/'fault-audit.json'); study=load(root/'study/study.json')
summary=load(root/'investigation/inventory-summary.json')
lines=['# Phase 2C numerical validation report','',
       'Local Windows validation: PASS. Scientific status: PARTIAL. Hosted Phase 2C',
       'Windows/Linux and package-sensitivity outcomes are PENDING until observed.',
       'See PHASE2C_PUBLICATION.md for the authenticated stacked-PR handoff.', '',
       '## Reproducible evidence','',
       f"Quick SHA-256: `{record['quick_sha256']}`.",
       f"Study SHA-256: `{record['study_sha256']}`.",
       f"Preservation contract: {len(preserved)} hash-verified files (38 original Phase 1/2,",
       '59 Phase 2B, five original failure ZIPs, and both initial-inventory copies).',
       'Every retained new file is covered by the raw-byte manifest. Original SHA-256:',
       '`395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258`',
       '(Phase 2 study); Phase 2B study:',
       '`c8f1cf9df1cdc6fb8eb5ab8595ede2015aee4647671d98142205ec1ec8f2a960`.', '',
       '## Complete local checks','',
       '| Executed stage | Return code | Measured wall seconds |','|---|---:|---:|']
for row in record['steps']:
    lines.append(f"| {row['stage']} | {row['returncode']} | {row['seconds']:.3f} |")
lines += ['', 'The first/repeat comparisons use rtol=1e-11 and atol=1e-13, exact',
          'random draws/configuration, and the unchanged 1e-4 refinement gates.',
          'All 21 active-coil outages received independent 60/90-digit arithmetic',
          'checks. The legacy-scientific comparison passed for every unchanged',
          'scientific quantity; all intentional metric changes are enumerated.',
          'Final regression output:','', '```text',
          (root/'final-tests.log').read_text().strip(), '```','',
          'Python compilation passed; see compilation.log. The initial numerical',
          'pipeline used its recorded test snapshot; added evidence-contract tests',
          'were rerun separately and by finalization. Calculation fingerprints must',
          'remain identical to the at-run record. No production numerical code was',
          'changed after these quick/study calculations.', '',
          '## All original scientific failures','',
          'The lossless inventory retains all raw differences for all ten dataset',
          'pairs, including provenance, timing, legacy geometry and NM diagnostics.',
          'These are retained rather than hidden behind the first failing scalar.', '',
          '| Original worker versus committed Phase 2B | Failed primary paths |',
          '|---|---|']
for row in summary[:4]:
    paths=[x['path'] for x in row['primary']['quick']+row['primary']['study']]
    lines.append('| '+Path(row['current'].replace('\\','/')).name+' | '+', '.join('`'+x+'`' for x in paths)+' |')
lines += ['', 'The primary study scientific quantities have no additional out-of-tolerance',
          'differences in these four archived workers. Complete investigation',
          'diagnostics and already documented adaptive-coordinate/legacy-geometry',
          'differences remain in the inventory, including within-tolerance values.', '',
          '## Original and corrected recovery values','',
          'Row index differs from physical failed-coil ID because the original',
          'active-current threshold excludes coils 4, 5 and 23. That policy is unchanged.', '',
          '| Row | Failed coil | Original ratio | Corrected ratio | Corrected error vs 90 digits | RMS subtraction condition |',
          '|---:|---:|---:|---:|---:|---:|']
for i,(before,after,checked) in enumerate(zip(old['faults'],q['faults'],audit['faults'])):
    lines.append(f"| {i} | {after['failed']} | {before['fractional_recovery']:.17g} | {after['fractional_recovery']:.17g} | {checked['stable_absolute_error']:.4g} | {checked['rms_subtraction_condition']:.7g} |")
lines += ['', f"Maximum corrected absolute error vs the 90-digit reference: {max(x['stable_absolute_error'] for x in audit['faults']):.17g}.",
          f"Maximum recovered free-coordinate projected training gradient: {max(x['projected_gradient_dimensionless'] for x in audit['faults']):.17g} (dimensionless).", '',
          'The reference evaluates exact recorded binary64 inputs. It does not',
          'certify an exact-geometry response or exact optimizer. Full residual',
          'vectors, current outputs, energy summands, reference strings and',
          'one-ULP naive sensitivity ranges are retained in hash-linked evidence.', '',
          '## Negative robustness findings and limitations','',
          '| Training seed | Count | Mean robust-minus-nominal RMS (T) | Fraction improved |',
          '|---:|---:|---:|---:|']
for trial in study['trials']:
    paired=trial['paired']
    # Retain the full source record rather than assuming any robust advantage.
    lines.append(f"| {trial['train_seed']} | {trial['count']} | {paired['mean_T']:.17g} | {paired['fraction_improved']:.17g} |")
lines += ['', 'All four tested fits retain their negative synthetic holdout findings.',
          'There is no global peak certificate, device/confinement validation,',
          'interval arithmetic proof, or guarantee across untested libraries/hardware.',
          'Observed agreement of finite calculations is separate from scientific',
          'validation of robustness. No numerical tolerance, solver setting or',
          'physical feasibility constraint was changed. See PHASE2C_METHODS.md and',
          'the preserved Phase 2B limitations for the mathematical scope.', '',
          '## Hosted status','',
          'Original run 41044895641: all four numerical jobs and cross-platform job',
          'FAILED at comparison; their preceding pipelines/audits completed.',
          'Phase 2C hosted results: PENDING. A local Windows pass is not a hosted',
          'Linux or cross-platform pass. Final publication status is recorded',
          'separately after the commit/push/PR attempt. No PR is merged.', '']
Path('docs/PHASE2C_RESULTS.md').write_text('\n'.join(lines))
print('Phase 2C report generated from hash-verified complete evidence')
