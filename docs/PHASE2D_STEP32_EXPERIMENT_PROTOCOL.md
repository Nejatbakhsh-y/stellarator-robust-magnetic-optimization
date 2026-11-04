# STEP 32 experiment protocol

This is a prepared diagnostic implementation, not a verified research checkpoint.
Production acceptance remains FAIL and overall scientific status remains PARTIAL.
No production objective, constraint, current bound, solver tolerance, ratio guard,
refinement threshold, historical report or failed comparison is changed.

Use Python 3.11 in the existing `.venv`. Do not replace the environment to hide a
launcher failure. On this Codex host the launcher cannot find its Python311 base
executable. Repair that installation through ordinary host maintenance first.
The host wrapper requires PowerShell 7; publication requires authenticated GitHub CLI. Codex must
not inspect GitHub CLI configuration or bypass its access restrictions.

## Evidence contract

The source of historical numerical evidence is run 41231422708 and the supplied
STEP 31 raw bundle, full analysis and STEP 31E assessment. New output directories
must be fresh and disjoint from inputs. Every capture/replay has environment,
source-sha256, input-sha256, assessment, status and manifest JSON records. Array
encoding is canonical little-endian binary64 hexadecimal, including signed zero.
`problem-sha256.json` excludes saved solutions and includes M/y, support, bounds,
solver configuration and physical configuration. The file seal covers all
geometry, projection, disturbance, weights, scaling, evaluation and saved arrays.

Manifests require exact file coverage before numerical use. All four captures and
all four replay workers are mandatory. Worker source fingerprints and commit must
match the expected workflow SHA. A worker label is not source authentication.
Original local hashes are integrity evidence only. The host wrapper separately
retrieves all seven original artifact ZIPs, checks GitHub's SHA256 digest against
binary archive bytes, and compares every extracted file against the historical
bundle. Missing/expired archives, mismatched digests or files fail this gate.
Neither a local manifest nor a successful worker proves artifact authenticity.

## Reciprocal intervention

The push-triggered isolated-branch workflow captures independently on each of:

| Cohort | OS | NumPy | SciPy |
|---|---|---|---|
| windows-reference | Windows | 2.4.6 | 1.17.1 |
| linux-reference | Linux | 2.4.6 | 1.17.1 |
| linux-numpy-sensitivity | Linux | 2.3.5 | 1.17.1 |
| linux-scipy-sensitivity | Linux | 2.4.6 | 1.16.3 |

Each replay worker consumes all four immutable captures. Thus A is Windows input
on Windows, B Windows input on Linux, C Linux input on Windows and D Linux input
on Linux. This extends to sixteen origin/solver combinations. Exact transported
input bytes and complete problem identity are mandatory for each paired replay.
Regenerated-input differences are reported separately. No Linux result is
simulated by relabeling a Windows execution. A `local` run is explicitly single
host and cannot establish A/B/C/D.

The existing dependency installer pins the complete tested stack, verifies all
installed versions, records resolver downloads, checks pip dependencies and tests
fresh-interpreter imports. Dependency setup failures have no fallback. Full Git
history is checked out; unavailable historical objects remain missing evidence.
Artifacts have unique run-ID/attempt/stage/cohort names. All uploads run even on
failure; missing artifacts are failures. No continue-on-error is used. Comparison
records every available failed numerical comparison after the completeness gate.

## Solver and support measurements

For dense, row3 and row4 record M/y, physical current vectors, constrained solver
arguments, termination, iterations, residual, objective, bound violation, active
bounds, KKT residual, projected gradient, singular values, effective rank and
condition. Existing 60/90-digit interior references are reused only where strict
interior feasibility is demonstrated. Independent residual-based coordinate
minimization clips each scalar minimizer to the physical box and handles active
bounds. Its 1e-14 gradient stopping rule is diagnostic; production tol=1e-12 is
unchanged. BVLS is a separate constrained cross-check. These are approximate
optimality checks, not interval certificates or proof of distinct exact optima.

Record every deletion support/refit, removal score/order and objective; every L1
selection/refit, support and stopping record; dense fault-selection indices and
row3/row4 fixed supports. Repeat traces after a one-ULP positive D perturbation.
The removal rule is minimum absolute current, not trial minimization over all
possible deletions. No invented trial objective is reported. Captured refit
objectives allow candidate comparisons. Compare discrete decisions separately
from current-vector changes. The finite-scenario robust optimizer is not changed
or causally certified by these nominal/fault diagnostics.

Threadpool limits 1 and 2, loaded libraries, environment settings, BVLS and
reversed row/column ordering are explicit interventions. Row/column ordering
changes binary input order and is never classified as an identical-byte replay.
The existing driver and M-rounding probes remain sensitivity diagnostics.
lsq_linear has no x0 argument; initialization intervention uses the independent
coordinate method, not a production parameter change. Library versions alone
cannot identify BLAS/LAPACK causality.

## Recovery and fields

Keep rtol=1e-11, atol=1e-13 and absolute denominator guard 1e-15 T. Calculate
B=pre-failure RMS, L=frozen-failure RMS, P=recovered RMS and R=(L-P)/(L-B).
Evaluate each complete binary64 input directly at 60/90 Decimal digits. Record
saved-minus-Decimal arithmetic error, precision difference and
`dR=((1-R)dL-dP+R*dB)/(L-B)`, including its nonlinear remainder.

One-block swaps isolate currents, fine_A, fine_b and fine_weights, with a joint
swap to expose interactions. fine_A combines Cartesian response and projection;
fine_b combines disturbance and normals. Baseline-field influence is measured by
the dB term, not an independent source perturbation. This does not uniquely
attribute unrecorded geometry/projection intermediate arithmetic. Do not sum
one-block effects into a claimed exhaustive causal partition.

Fixed geometry/coordinates/currents use all Cartesian components; report
component maxima and vector-norm maxima independently of ratio comparisons.
Independent tangent/perpendicular Decimal finite-segment integration checks two
coarse-grid probes per polygon at 60/90 digits. This limited subset is not a
continuum, confinement or device validation. Cross-platform agreement alone is
not mathematical correctness.

## Host execution and publication

From this checkout, after restoring the existing Python installation:

```powershell
$run = 'results/phase2d/step32-host-' + [guid]::NewGuid().ToString('N')
.\scripts\phase2d_step32_host.ps1 -EvidenceRoot results/phase2d/step31-20261031-165725-a14c217c -OutputRoot $run
```

The wrapper inventories evidence and preexisting changes, authenticates original
archives, runs the full regression suite, compilation, analytical validation,
historical review, capture and local controlled checks. It then runs the existing
full phase2c verifier with fresh outputs: quick, output checks, independent audit,
study, full repeat, training audit and exact result-SHA256 links, followed by
fault/legacy audits, investigation and finalization. Historical paths are
preserved. A failure stops publication and retains logs/status/manifests.
Without GitHub CLI authentication, a nonpublishing run continues local checks
and records original hosted authenticity as INCONCLUSIVE. Publication requires
successful original archive authentication. A fully recorded hosted scientific
comparison FAIL may complete the diagnostic wrapper, while production stays FAIL.

A later, explicitly chosen publication run must use a new output path:

```powershell
$run = 'results/phase2d/step32-publish-' + [guid]::NewGuid().ToString('N')
.\scripts\phase2d_step32_host.ps1 -EvidenceRoot results/phase2d/step31-20261031-165725-a14c217c -OutputRoot $run -Publish
```

Only the six STEP 32 deliverable files are staged. Unrelated staged changes block
publication. Preexisting file hashes and historical hashes must match before
commit/push. Push targets only codex/phase2d-upstream-attribution. No PR creation,
merge, force push, main modification or workflow dispatch occurs. The wrapper
polls the commit's push-triggered workflow for at most 210 minutes and records
run ID, commit, jobs, artifact names and digests. It authenticates downloaded ZIPs
and reruns comparison on extracted captures/replays. Pending, missing or failed
results cannot pass. Diagnostic completion never promotes production acceptance.

## Interpretation

Exit 0 means the command's diagnostic gates completed; exit 1 means a completed
scientific comparison failed; exit 2 means execution/evidence failure. All scopes
retain production FAIL and overall PARTIAL until a separate independently accepted
production checkpoint. A full new regression run and all README verification
stages with passing result-hash-bound evidence are required before any research
checkpoint is described as verified. Finite-scenario minimax and small synthetic
holdouts do not establish robust outperformance or confinement.
