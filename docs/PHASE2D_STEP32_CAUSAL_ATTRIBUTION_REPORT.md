# Phase 2D STEP 32 causal attribution report

Overall scientific status: **PARTIAL**. Production acceptance: **FAIL**.
Implementation: **PREPARED / UNVERIFIED**. Local numerical validation:
**NOT EXECUTED (Python startup unavailable)**. New hosted execution:
**NOT EXECUTED**. Hosted artifact-byte authenticity: **INCONCLUSIVE**.
Numerical causal attribution: **INCONCLUSIVE**, with the immediate
current-to-recovery pathway **SUPPORTED** by preserved STEP 31 evidence.

No commit, push, dispatch, merge, production edit or historical-report edit was
performed. The branch is `codex/phase2d-upstream-attribution`, HEAD
`11c2b1347c7b5359bec0a56e95cc2aa46f03660c`, matching the supplied starting HEAD.
The index was empty. Preexisting untracked scripts, reports and evidence remain.
`.venv/` remains ignored. Production objectives, current bounds, solver settings,
rtol=1e-11, atol=1e-13, denominator guard 1e-15 T and refinement 1e-4 are unchanged.

## Executed inspection and evidence

AGENTS.md, the five requested reports/runbook, execution status and the five
requested scientific modules were inspected. Existing STEP 31 and STEP 31E
records were used without regenerating historical results. New records reside in
`results/phase2d/step32-20261031-174304-3161daf1/implementation-review/`.

PowerShell independently hashed all 361 supplied raw files and checked 340 listed
entries across the historical manifests: zero hash mismatches. All four workers
have identical sets of 86 recorded source fingerprints, with no missing or extra
entries relative to Windows. All four sealed-input copies have SHA256
`4faec908829e36e67415e6cf56c7326f6b64149864c5f8cc3ad39404fba05fed`.
These are newly executed local integrity checks, not new scientific computations
or authentication of hosted archive bytes.

Read-only GitHub connector calls independently retrieved current artifact/job
metadata for [run 41231422708](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41231422708).
The seven artifacts record source SHA `11c2b1347c7b5359bec0a56e95cc2aa46f03660c`.
Seal and four worker jobs succeeded; the compare job failed. All three diagnostic
comparison steps and all three production comparison steps failed. Exact returned
metadata, job steps and SHA256 artifact digests are retained as hosted-artifacts
and hosted-jobs JSON. No new GitHub Actions execution was initiated.

All four local worker environments instead name
`3a747c1b6535d8b34c5a152650e8fe169515fb14`. `git cat-file` confirms this object is
unavailable locally. Matching recorded fingerprints support identical recorded
scientific implementations among the four workers; they cannot establish that
these bytes were actually executed at the hosted run's named commit. Still
missing: original archive download and digest verification, exact extraction to
local-byte comparison, the worker commit object, and source-to-commit binding.
The host script implements archive authentication but has not executed it here.

The Python version probe, complete pytest command and compilation command were
attempted using `.venv/Scripts/python.exe`. Each failed before interpreter startup
because the configured Python311 base executable is absent. **Zero tests passed
in this implementation turn.** The user's prior 234-test Windows result is a
historical record, not validation of these additions. PowerShell parser inspection
reported no syntax errors; that is not execution of the host automation. Git diff
whitespace checks passed for tracked changes; new files are separately inspected.

## Prepared system

The six requested deliverables are present. The Python CLI provides historical,
capture, local, replay and compare stages. Hosted capture/replay runs the four
specified cohorts with Python 3.11 and exact tested dependency installation. Four
independent captures feed four replay workers, preserving all sixteen combinations
and the required reciprocal A/B/C/D design. Source/head and exact serialized input
equality are required before comparison. All required artifact evidence is checked
before numerical differences. Missing evidence fails, rather than becoming PASS.

Diagnostics retain constrained solver records, independent coordinate/BVLS
checks, KKT/projected gradients, conditioning, support/removal/L1 traces,
one-ULP support perturbations, thread and summation-order interventions,
60/90-digit RMS ratios, ratio differentials, block swaps, fixed-current Cartesian
comparisons and independent finite-wire probes. No unique library cause is
inferred from version correlations. The protocol documents scope and commands.

The host wrapper uses fresh outputs, inventories historical/preexisting files,
checks repository/branch/authentication, authenticates original hosted archives,
runs required local gates and the complete production verifier, and preserves
machine-readable reports. Optional publication stages only the exact six new
files, refuses unrelated staged changes and pushes only the attribution branch.
It neither creates PRs nor merges. It monitors the push-triggered workflow with a
bounded timeout, downloads actual archives, verifies GitHub SHA256 digests and
rechecks numerical evidence. This automation is prepared, not runtime verified.

## Final scientific decisions

The classifications below apply to the stated evidence scope. No statement
promotes supplied numerical records into a fresh independent STEP 32 execution.

| Question | Classification | Decision and limitation |
|---|---|---|
| 1. Complete solver inputs identical? | ESTABLISHED locally; hosted INCONCLUSIVE | Four sealed files have identical SHA256. STEP 31's contract covers M/y, support, bounds and configuration. Original hosted-byte binding remains absent. |
| 2. Numerical source implementations identical? | SUPPORTED | All four recorded 86-file maps agree. Executed source identity remains unproven because of the commit discrepancy and unauthenticated extracted bytes. |
| 3. Identical inputs produce different currents? | SUPPORTED | STEP 31 frozen solves record nonidentical currents, e.g. dense Linux difference 6.09e-13 A and row3 1.36e-12 A. Fresh reciprocal replay is unexecuted. |
| 4. Regenerated optimization inputs differ? | SUPPORTED | Historical binary64 A/b, D/d and M/y differences are retained; tolerance agreement is not exact equality. New independent captures remain unexecuted. |
| 5. Coil-support decisions differ? | INCONCLUSIVE | Historical fault supports agree in the recorded cases; a complete cross-platform support/removal trace and perturbation experiment has not run. |
| 6. Solver optimality conditions differ? | SUPPORTED: no material defect demonstrated | Recorded success/status 3, zero iterations, interior bounds and small KKT residuals support approximate optimality. Independent new constrained checks have not run. |
| 7. Distinct vectors both optimal? | SUPPORTED as approximate optima | Historical interior reference agreement supports numerically equivalent approximate solutions. Full-rank ridge implies a unique exact mathematical optimum, not multiple distinct exact optima. |
| 8. Conditioning explains sensitivity? | INCONCLUSIVE; no evidence of ill-conditioned augmented solve | Historical augmented condition about 1.94679 and full column rank do not support ill-conditioning as the cause. New singular-value checks remain unexecuted. |
| 9. Recovery amplification explains failures? | SUPPORTED | Historical denominators about 5.4665e-11 T (row3) and 5.2207e-10 T (row4), with cancellation factors about 948121 and 99277, amplify small current effects. Decimal swaps support the immediate pathway. They do not identify the original LAPACK/BLAS operation. |
| 10. Fixed-current fields independently valid? | SUPPORTED within limited probe scope | Historical frozen component agreement and independent 60/90-digit finite-segment probes support those coordinates only. No fresh STEP 32 reference run, continuum or confinement certification. |
| 11. Which mechanism established? | ESTABLISHED only as local evidence fact | Sealed local byte equality, recorded source-map equality and actual hosted comparison-job failure. No unique numerical implementation mechanism is independently established. |
| 12. Which mechanisms unproven? | INCONCLUSIVE | Specific BLAS/LAPACK operation, CPU/thread/summation effect, source-object discrepancy, full reciprocal regenerated-input effects, support and active-bound perturbations. |
| 13. Production correction justified? | INCONCLUSIVE | No correction is scientifically justified by these records; production optimizer is unchanged. |
| 14. Additional verification? | ESTABLISHED requirement | Restore Python, run all new/full tests and gates, authenticate original artifacts, obtain/bind worker source object, execute hosted reciprocal design and independent constrained/field checks, then separately satisfy original production criteria. |

## Preserved numerical failures and limits

The historical STEP 31 failure table remains authoritative. It includes frozen
row3 failures in reference/NumPy/SciPy, frozen row4 failure in NumPy, regenerated
row3 failures in all three Linux cohorts, and the corresponding production row3
failures. New evidence includes references and SHA256 fingerprints of every
original comparison, the full analysis and STEP 31E assessment. The executable
historical command retains complete original comparison records in its output.
No failing comparison is removed or replaced with a diagnostic success.

The prepared interventions separate continuous current changes from discrete
support changes and single-block changes from joint effects. fine_A combines
field response/projection and fine_b combines disturbance/normals; these records
do not isolate every unrecorded intermediate arithmetic operation. Baseline-field
contribution is resolved through dB in the recovery differential, not an
independent geometry perturbation. Two probes per polygon cannot certify every
field point. Diagnostic stopping rules and alternate methods do not modify
production solver settings. These limits prevent an exhaustive causal claim.

Implementation remains unverified until executable checks pass. The original
production comparison failure is retained even if the diagnostic completes.
Finite-scenario minimax and small synthetic holdouts cannot establish robust
outperformance, plasma confinement or physical device validation.
