# Phase 2D Step 31 root-cause report

Scientific status: **PARTIAL**. Production acceptance: **FAIL**.
New Python diagnostic execution: **BLOCKED before startup**, exit 103.
No tests or compilation passed in this continuation. This is an evidence inspection,
with a prepared independent numerical investigation; it is not a verified research checkpoint.

The sole numerical source is the supplied
`results/phase2d/step31-20261031-165725-a14c217c/raw/` bundle associated by the
user with run **41231422708**. Older Phase 2C/2D numerical results are not
substituted for this bundle. The read-only inspection is saved separately in
`results/phase2d/step31-local-review-20261031/`.

All **361** inventoried source files match their supplied SHA256 values;
all **18** discovered manifests have matching listed file hashes. The seven
top-level artifact directories are present, including four numerical workers,
the upstream seal, dependency seal and comparisons. All four worker statuses
are PASS; all three upstream comparison statuses and production comparisons
are FAIL. Worker PASS is a local diagnostic classification, not production acceptance.

There is a material provenance qualification. Local HEAD and the supplied source
commit are `11c2b1347c7b5359bec0a56e95cc2aa46f03660c`, on existing feature branch
`codex/phase2d-upstream-attribution`. Worker and seal environments instead record
`3a747c1b6535d8b34c5a152650e8fe169515fb14`. That Git object is unavailable locally.
Ten recorded source fingerprints differ from current checkout file bytes:
the Phase 2C workflow, four Phase 2B/C configs, requirements-tested.txt,
phase2c_compare.py, phase2c_finalize.py, phase2c_verify.py and test_ci_evidence.py.
These are byte differences; semantic differences have not been established.
For example, the inspected quick configuration has the same numerical values.
Local hash integrity does not independently authenticate the hosted run identity
or resolve this commit discrepancy. No network authentication was attempted.

1. **Are sealed optimization inputs exactly identical? — ESTABLISHED within the supplied bundle.**
   Direct byte comparisons of the upstream seal and all four worker copies agree.
   SHA256 is `4faec908829e36e67415e6cf56c7326f6b64149864c5f8cc3ad39404fba05fed`.
   This covers M, y, A, b, D, d, weights, bounds, ridge regularization, support
   indices and solver configuration, including signed-zero bytes. Byte identity
   is stronger than tolerance agreement. The prepared script decodes each array
   with the existing project `unpack`, records byte and numerical exactness
   separately, and checks the scientific input contract; that decoding has not
   executed locally in this continuation.

2. **Which regenerated inputs differ? — SUPPORTED by the sealed comparison records.**
   All three Linux-versus-Windows regenerated comparisons have nonexact A, b,
   D, d, points, normals, vertices, error_vertices, original_Bxyz, fine_points,
   fine_normals, fine_A, fine_b, and dense/row3/row4 M, y and saved solutions.
   Weights and fine_weights are exact. All these array comparisons pass the
   unchanged numerical tolerance. Representative maximum absolute differences:
   A `3.1763735522036263e-22 T/A`, D `9.43689570931383e-16`,
   M `5.551115123125783e-17`, vertices/points `2.220446049250313e-16 m`.
   Reference/SciPy y differs by `1.1438332919722072e-17`; NumPy y differs
   by `1.5287250632045613e-17`. A tolerance pass does not imply identical inputs.

3. **Do identical inputs produce different currents? — SUPPORTED, independently of regeneration.**
   In frozen solves the reference Linux maximum current differences are
   `6.092903959142859e-13 A` dense and `1.3642420526593924e-12 A` row 3.
   NumPy sensitivity gives `5.684341886080801e-13 A` dense and
   `1.4779288903810084e-12 A` row 3. These current comparisons pass their gate,
   yet the downstream ratios can fail. Identical fixed M/y therefore do not
   ensure bit-identical numerical optimizer output. This rules out independently
   regenerated inputs as a necessary cause of the frozen-solve differences.

4. **Are solver optimality conditions satisfied? — SUPPORTED by recorded diagnostics.**
   All 24 inspected solves (four workers, two stages, three cases) report success,
   status 3, zero iterations, and entirely zero active-bound masks. Augmented
   condition numbers are about 1.94679148044784. Recorded projected-gradient
   maxima range from `1.6263032587282567e-19` to `3.469446951953614e-18`.
   Frozen Windows costs are dense `0.00033181635382875213`,
   row 3 `0.0003318174254798817`, row 4 `0.00033182626959555776`;
   Linux costs differ in final binary64 digits. Independent 60/90-digit solver
   checks in the artifacts report PASS. A fresh KKT/residual/bound-margin
   recomputation is prepared but unexecuted. No ill-conditioning or active-set
   change is established in these cases. The actual bounded solver accepted
   its interior unconstrained initialization; unconstrained references are
   justified only where strict interior feasibility is checked. This result
   does not extend to other solves with active bounds.

5. **Are field components reproducible? — SUPPORTED, for the frozen experiment.**
   All eight frozen-field array comparisons are exact for every Linux cohort,
   including the unit-coil Cartesian response, disturbance, fixed dense and
   fault currents, and projected A. Whole-array equality covers Bx, By and Bz.
   Independent field artifacts report PASS at two coarse-grid probes for each
   of 25 polygons, at 60 and 90 digits. Those references are an independent
   finite-segment calculation; platform agreement alone is not correctness.
   Fresh componentwise replay/reference verification remains unexecuted here.
   Two probes do not validate every coordinate, smooth-coil convergence,
   confinement, or a physical device.

6. **What causes recovery-ratio amplification? — SUPPORTED mechanism; precise attribution INCONCLUSIVE.**
   For B=baseline RMS, L=failed-coil RMS and P=recovered RMS,
   `R=(L-P)/(L-B)` and
   `dR=((1-R)dL-dP+R*dB)/(L-B)`.
   Baseline RMS is about `2.5914425556311e-5 T`; recorded denominators are
   about `5.46648534e-11 T` for row 3 and `5.22068671e-10 T` for row 4.
   Denominator subtraction condition factors are approximately 948121 and
   99277. Small changes in field residuals caused by current changes can thus
   create much larger dimensionless ratio changes. Numerator subtraction also
   cancels; a stable energy formulation does not remove mathematical input
   sensitivity. Negative row-3 recovery is retained.
   The new script independently evaluates binary64 inputs through
   `Decimal.from_float` at 60/90 digits, compares compensated direct RMS and
   saved float64 ratios, records numerator/denominator cancellation, and
   resolves the differential into three terms and a nonlinear remainder.
   These new high-precision calculations have **not run**. No percentage of
   the latest ratio difference is attributed to currents or model changes yet.

7. **Which controlled interventions establish causality? — SUPPORTED immediate solver pathway.**
   Identical sealed solver inputs with differing frozen currents isolate a
   solve-stage arithmetic effect from input generation. Identical sealed
   geometry/coordinates/currents with exact Cartesian results show that field
   evaluation differences are unnecessary in that control. This supports dense
   least-squares arithmetic as the immediate source of current differences;
   it does not identify a particular LAPACK/BLAS operation. Reciprocal model/
   current swaps are implemented with four combinations at each stage and row,
   including an interaction term. They remain unexecuted. Merely comparing
   regenerated solves confounds matrix-generation and solver effects.

8. **Which differences remain unexplained? — INCONCLUSIVE.**
   The exact operation causing solver rounding differences; relative sizes of
   generation, currents and final metric arithmetic contributions in this run;
   and the source-commit discrepancy remain unresolved. Linux reference and
   SciPy sensitivity frozen ratios agree with each other but differ from
   Windows. NumPy sensitivity changes those ratios again. Version correlations
   do not establish a unique library cause or prove a defective optimizer.

9. **Is a production correction justified? — INCONCLUSIVE; no correction justified by current evidence.**
   No production objective, solver, physical constraint, setting, tolerance or
   historical evidence was changed. The gates remain rtol=1e-11, atol=1e-13,
   denominator guard 1e-15 T and refinement 1e-4. A diagnostic success cannot
   override the following failures.

10. **What additional experiments are necessary?**
    Restore the existing Python 3.11 environment through normal host maintenance,
    execute the diagnostic and tests, and inspect all 60/90-digit swaps and KKT
    checks. Obtain independently authenticated run/commit metadata and the
    recorded source object. Execute reciprocal solves of each worker's
    regenerated M/y on every platform, with identical recorded solver settings,
    and retain relevant runtime/LAPACK metadata. Revalidate all production gates
    and result SHA256 links. No hosted jobs are dispatched by this continuation.

The complete latest failure inventory follows. Errors and thresholds are
binary64 calculations on the recorded scalars, not new Decimal results.
The executable diagnostic additionally records exact binary64-derived Decimal
errors/bounds when it can run. Positive exceedance is a failure.

| Comparison | Stage/row | Absolute error | Threshold | Exceedance |
|---|---|---:|---:|---:|
| Reference | frozen/3 | 3.2846669828501263e-11 | 4.2468899705055136e-12 | 2.8599779857995748e-11 |
| NumPy | frozen/3 | 1.1026846102879517e-11 | 4.2468899707237116e-12 | 6.7799561321558057e-12 |
| NumPy | frozen/4 | 2.4892032879364479e-12 | 1.7726624849464509e-12 | 7.1654080298999695e-13 |
| SciPy | frozen/3 | 3.2846669828501263e-11 | 4.2468899705055136e-12 | 2.8599779857995748e-11 |
| Reference | regenerated/3 | 4.9408310776044573e-11 | 4.2468899703150892e-12 | 4.5161420805729481e-11 |
| NumPy | regenerated/3 | 1.7271128971430016e-11 | 4.2468899706364610e-12 | 1.3024239000793555e-11 |
| SciPy | regenerated/3 | 4.9408310776044573e-11 | 4.2468899703150892e-12 | 4.5161420805729481e-11 |

Each production comparison repeats its corresponding regenerated row-3 failure
at `/quick/faults/3/fractional_recovery` and
`/quick/faults/3/recovery_evidence/fractional_recovery`. Those are duplicate
paths for one scientific quantity, not two independent failures. The production
row-4 comparisons pass for all cohorts; frozen NumPy row 4 fails as shown.
All original comparison files remain intact. This inventory supersedes no
historical evidence and excludes no failure to manufacture acceptance.

The new diagnostic and tests are additions only. No commit, push, merge, PR
change, GitHub CLI operation or workflow dispatch occurred. Existing untracked
work is preserved. Finite-scenario minimax and small synthetic holdouts retain
their existing limitations; no robust outperformance or confinement validation
is inferred. See the companion reproducibility record for actual attempts and
remaining commands.
