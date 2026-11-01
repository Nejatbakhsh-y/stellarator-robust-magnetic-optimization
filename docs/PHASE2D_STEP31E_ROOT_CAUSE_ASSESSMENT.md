# Phase 2D Step 31E numerical assessment

## 1. Executive scientific conclusion

Overall **PARTIAL**; production acceptance **FAIL**; precise numerical attribution
**INCONCLUSIVE**. The immediate current-to-recovery pathway is supported by the
supplied Step 31 analysis and its controlled Decimal swaps. No production change
is justified. Fresh Python replay and regression execution were attempted but
failed before interpreter startup (missing Python311 base executable). This is
an evidence assessment and prepared implementation, not a verified checkpoint.

## 2. Evidence inventory and fingerprints

Only the supplied current Phase 2D raw bundle supplies numerical evidence.
The historical Step 31 review records 361 source files and 18 matching manifests;
those counts have not been independently replayed in this turn. The new tool
requires exact inventory coverage and validates manifests before numerical work.
PowerShell SHA256 independently measured:

* analysis.json: `49f4ddea773b54698aa3ed5162bb892a0e24918de34c587d29ad8b18ad9863b2`
* STEP31D_scientific_summary.json: `03223fbf5640b097e5ef809e714c071ca9b840f7da847275ddabea27bec0b49a`

The analysis hash matches its manifest and the summary's recorded analysis hash.
The summary has no separately authenticated external fingerprint. Its measured
hash establishes a local identity only. Full analysis is 47,113,625 bytes; the
453,982-byte summary is explicitly abbreviated and cannot replace full records.

## 3. Source and worker provenance

Local branch is `codex/phase2d-upstream-attribution`, HEAD and supplied reference
`11c2b1347c7b5359bec0a56e95cc2aa46f03660c`. Existing untracked work was retained.
The worker/seal environment records instead name
`3a747c1b6535d8b34c5a152650e8fe169515fb14`; that object is unavailable locally.
The previous review reports ten file fingerprint differences, covering a workflow,
four configs, requirements-tested.txt, three Phase 2C scripts and a CI test.
Semantic equivalence is unresolved. The new replay checks recorded source hashes
against Git object bytes rather than interpreting a worker label as proof.

Read-only GitHub connector queries authenticated run 41231422708 metadata:
seven artifacts, seal success, four worker successes, compare failure. All six
compare steps failed. Artifact metadata records the supplied reference SHA.
Worker jobs are Windows NumPy 2.4.6/SciPy 1.17.1, Linux 2.4.6/1.17.1,
Linux NumPy sensitivity 2.3.5/1.17.1, Linux SciPy sensitivity 2.4.6/1.16.3.
Responses are retained under the new output root as hosted-workflow_run_*.json.
No ZIP download/digest-to-extraction comparison was performed. Hosted run identity
is verified; authenticity of these particular local extracted bytes remains
INCONCLUSIVE. Local hashes cannot bridge that gap.

## 4. Exact solver inputs

Recorded sealed input SHA256 is
`4faec908829e36e67415e6cf56c7326f6b64149864c5f8cc3ad39404fba05fed`.
The supplied analysis reports all four frozen copies byte-identical, covering
M/y, distinct D/d, weights, support, bounds and configuration. Regenerated inputs
differ in binary64 geometry, field and matrix values while passing tolerance.
Recorded maximum differences include M 5.551115123125783e-17,
D 9.43689570931383e-16 and A 3.1763735522036263e-22 T/A.
Bitwise equality is distinct from numerical tolerance agreement and signed-zero
numerical equality. The tool uses case-sensitive Python JSON parsing throughout.

## 5. Current vectors

Recorded frozen reference/Linux maximum differences are dense
6.092903959142859e-13 A and row 3 1.3642420526593924e-12 A;
NumPy sensitivity dense 5.684341886080801e-13 A and row 3
1.4779288903810084e-12 A. These pass current-vector tolerance but are not bitwise
equal. The tool prepares all 24 solve records and computes maximum absolute and
relative current errors, treating zero reference currents separately. Fresh
row-4 current maxima and relative differences are unexecuted, not invented.

## 6. Constraints and optimality

All 24 recorded cases report success/status 3, zero iterations and zero active
masks. Recorded minimum bound margins are about 0.7806 in dimensionless current.
KKT residuals in the supplied summary are around 1e-19 to 2e-18; projected
gradients are around 1e-19 to 3.5e-18. Windows frozen objective values are
0.00033181635382875213 (dense), 0.0003318174254798817 (row 3),
0.00033182626959555776 (row 4). These support numerically equivalent approximate
interior optima, not failed optimizer convergence. Full column rank with ridge
means a unique mathematical optimum, not multiple distinct exact optima.
Unconstrained Decimal references apply only after strict interior feasibility;
they are not accepted references for an active-bound problem.

## 7. Conditioning

Recorded augmented condition estimates are about 1.94679148044784, ranks 24
(dense) and 23 (fault cases). There is no evidence of an ill-conditioned augmented
solve. The new tool recomputes singular values/rank/condition, residuals, bound
violations and KKT metrics without modifying or rerunning the production optimizer.

## 8. Independent magnetic fields

The supplied analysis reports exact frozen Bx, By and Bz comparisons for each
Linux cohort; component maximum differences and vector difference norms are zero
where arrays are exact. This establishes agreement under that control only.
Separate independent 60/90-digit finite-segment reference records report PASS at
two coarse-grid points for each of 25 polygons. The prepared replay validates
those references and preserves each component comparison. This limited probe
set does not certify all points, continuum convergence, confinement or a device.
Shared production implementation agreement alone is not mathematical validation.

## 9. Fault row 3

Let B, L, P be baseline, failed and recovered RMS and R=(L-P)/(L-B).
The first-order differential is
`dR=((1-R)dL-dP+R*dB)/(L-B)`.
Recorded denominator is about 5.46648534e-11 T, subtraction condition about
948121; B is about 2.5914425556311e-5 T. The denominator is sensitive to very
small absolute RMS changes. Numerator subtraction also cancels; stabilizing
arithmetic does not remove mathematical sensitivity to currents.

The summary's frozen NumPy differential terms (L,P,B) are approximately
(-1.9406145470e-11, 2.4716938966e-11, 5.7161033600e-12), summing to
1.10268968558017e-11, nonlinear remainder -7.33e-25. These are recorded
90-digit reevaluations, not newly executed measurements or original optimizer
precision. Negative recovery is preserved.

## 10. Fault row 4 and failure inventory

Recorded denominator is about 5.22068671e-10 T, subtraction condition about
99277. Frozen NumPy row 4 fails despite passing production row 4.
The complete distinct failed cohort/stage/row quantities are:

| Cohort | Stage/row | Absolute error | Allowed bound | Exceedance |
|---|---|---:|---:|---:|
| Reference | frozen/3 | 3.2846669828501263e-11 | 4.2468899705055136e-12 | 2.8599779857995748e-11 |
| NumPy | frozen/3 | 1.1026846102879517e-11 | 4.2468899707237116e-12 | 6.7799561321558057e-12 |
| NumPy | frozen/4 | 2.4892032879364479e-12 | 1.7726624849464509e-12 | 7.1654080298999695e-13 |
| SciPy | frozen/3 | 3.2846669828501263e-11 | 4.2468899705055136e-12 | 2.8599779857995748e-11 |
| Reference | regenerated/3 | 4.9408310776044573e-11 | 4.2468899703150892e-12 | 4.5161420805729481e-11 |
| NumPy | regenerated/3 | 1.7271128971430016e-11 | 4.2468899706364610e-12 | 1.3024239000793555e-11 |
| SciPy | regenerated/3 | 4.9408310776044573e-11 | 4.2468899703150892e-12 | 4.5161420805729481e-11 |

These values are supplied analysis/summary records. Each production comparison
repeats its regenerated row-3 quantity at fractional_recovery and
recovery_evidence/fractional_recovery; duplicate JSON paths are not extra
independent scientific failures. Every original failed record remains intact.

## 11. Controlled interventions

Recorded Decimal current/model swaps give these dimensionless ratio effects:

| Cohort/stage | Row | Current on Windows model | Model on Windows currents |
|---|---:|---:|---:|
| Reference or SciPy/frozen | 3 | 3.28469818932680e-11 | 0 |
| Reference or SciPy/frozen | 4 | 7.62787901337184e-13 | 0 |
| NumPy/frozen | 3 | 1.10268968558010e-11 | 0 |
| NumPy/frozen | 4 | -2.48923037655941e-12 | 0 |
| Reference or SciPy/regenerated | 3 | 4.94226598300596e-11 | -1.50923133248168e-14 |
| Reference or SciPy/regenerated | 4 | 9.90757317919809e-13 | -2.87542290013626e-15 |
| NumPy/regenerated | 3 | 1.72883889779211e-11 | -1.71597160323484e-14 |
| NumPy/regenerated | 4 | -3.34194568654219e-13 | -2.80122929233347e-15 |

Recorded regenerated interaction magnitudes are at most about 5.76e-25.
Frozen swaps isolate currents under identical evaluation inputs. Regenerated
model swaps jointly alter evaluation arrays; they do not uniquely isolate which
solver-input-generation operation altered optimized currents. Saved binary64
ratios and Decimal totals differ slightly, quantifying downstream rounding only
when evaluated with complete saved inputs. The tool retains saved-minus-Decimal,
60/90 precision differences, cancellation factors and all differential terms.
No missing optimizer precision is reconstructed.

## 12. Established causes

Local analysis byte identity is independently checked against the recorded hash;
hosted comparison failure is independently confirmed. Within the supplied
controlled records, identical sealed inputs coexist with nonidentical currents,
and frozen evaluation arrays agree exactly. Regeneration and fixed-current field
disagreement are therefore unnecessary for that frozen discrepancy. Fresh replay
and artifact-byte authentication remain incomplete.

## 13. Supported explanations

Solve-stage finite arithmetic changes currents; the highly sensitive recovery
functional amplifies those changes beyond its unchanged gate. Recorded swaps
support this immediate pathway. Library version correlations do not uniquely
identify NumPy, SciPy, BLAS, LAPACK, CPU instructions or thread scheduling.

## 14. Unresolved mechanisms

Specific solver operation, source-commit discrepancy, ZIP-to-local provenance,
and the causal effect of independently regenerated optimization inputs remain
unresolved. Decimal evaluation of saved binary64 inputs cannot reveal original
unrecorded intermediate precision. Shared Step 31 replay code is explicitly
reused, so it is not a second independently implemented assessment engine.

## 15. Production correction

No correction justified. Production code, objectives, physical constraints,
bounds, rtol=1e-11, atol=1e-13, denominator guard 1e-15 T and refinement limit
1e-4 were preserved. Quick geometry remains 512 segments. Diagnostic success
cannot waive production failures.

## 16. Remaining experiments

Authenticate artifact ZIP digests and compare every extracted file against local
records; obtain worker commit object and semantic source differences. Replay
each worker's regenerated M/y on each of the four environments with identical
settings, retaining reciprocal results, exact runtime source hashes and loaded
libraries. Hold all other factors fixed when varying a solver/library operation.
Run the prepared assessment and inspect every 60/90-digit check and KKT result.

## 17. STEP 32 recommendation

Resolve provenance and reciprocal input/solver interventions before proposing a
numerical correction. Require an independently implemented rounded-input ratio
and constrained-optimality check. Retain all failures; no tolerance relaxation.

## 18. STEP 33 recommendation

After justified changes, run all README tests, analytical validation, quick
experiment, independent audit, output checks and full reproducibility check,
with passing evidence linked to exact result SHA256. Expand field probes and
separate finite-wire validation from continuum and confinement questions.
Finite-scenario minimax and small synthetic holdouts do not establish robust
outperformance.

## 19. Reproducibility commands

Execute from this checkout after ordinary host maintenance restores the existing
.venv Python 3.11 base interpreter. Do not substitute a different environment.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step31e.py
.\.venv\Scripts\python.exe scripts/phase2d_step31e_review.py --analysis results/phase2d/step31-diagnostic-17722c7081a44f1293f043288b58086c/analysis.json --summary results/phase2d/step31-diagnostic-17722c7081a44f1293f043288b58086c/STEP31D_scientific_summary.json --raw-root results/phase2d/step31-20261031-165725-a14c217c/raw --output results/phase2d/step31e-20261031-173238-bf04cf36/review
```

The output subdirectory must be fresh. Both commands were attempted here and
failed before Python startup. No tests passed in this turn. Exit 0 from the tool
means completed diagnostic; scientific FAIL remains explicit. Integrity or
execution exceptions return 2. Existing Step 31 diagnostic is a dependency and
its implementation fingerprint is retained by the replay.

## 20. Acceptance status

Implementation: **FAIL** (prepared, not execution-verified; automated assessment
outputs not generated). Local regression: **NOT EXECUTED**. Evidence integrity:
**INCONCLUSIVE** (analysis hash verified, raw inventory replay and external byte
authentication incomplete). Numerical attribution: **INCONCLUSIVE** (immediate
current sensitivity supported). Production acceptance: **FAIL**. Overall scientific
status: **PARTIAL**. No commit, push, PR, workflow dispatch or production edit.
