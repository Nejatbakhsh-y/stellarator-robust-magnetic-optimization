# Phase 2D upstream numerical attribution

Overall scientific validation: **PARTIAL**. Historical production cross-platform
reproducibility: **FAIL**. Precise upstream platform mechanism: **INCONCLUSIVE**.
New attribution experiments: prepared, **not executed**. No numerical correction
is justified by the available evidence.

## Verified checkout and preservation

On 2026-10-31 the origin was verified as
`https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git`,
branch `codex/phase2d-cross-platform-reproducibility`, HEAD
`ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7`.
The complete initial working-tree status and 439 preexisting tracked/untracked
file hashes are retained in
`results/phase2d/upstream-preflight-20261031-091816/`.
The preexisting report, scripts, snapshot, and investigation records were inspected
before additions. All 439 inventoried files remain unchanged. Separately, all
247 historical supplied evidence files match the earlier inventory in both
length and SHA256; see `historical-preservation.json`. `.venv/` remains ignored.
All implementation changes are new files; no production source was edited.
No GitHub CLI, publication, commit, push, or PR operation was performed.

## Findings supported by existing scientific evidence

The prior report `PHASE2D_HOSTED_INVESTIGATION_41195815229.md` and its hashed
records remain the source for these observations; these are not fresh executions
of current HEAD. Historical worker source commit was
`babc88ccd5086b5ec3a6e1c215524636d86b3580`.

| Zero-based fault row | Failed coil | Windows recovery | Linux recovery | Absolute difference | Existing comparison bound |
|---|---:|---:|---:|---:|---:|
| 3 | 3 | -0.414688997029067 | -0.4146889970636461 | 3.457911734727759e-11 | 4.246889970636461e-12 |
| 4 | 6 | 0.16726624849972482 | 0.16726624849716587 | 2.5589530494585233e-12 | 1.7726624849716587e-12 |

Both violate `atol + rtol*abs(current)` with unchanged `rtol=1e-11`,
`atol=1e-13`. Duplicate report paths do not represent independent effects.
Windows/Linux dense currents differ by at most 1.47792889038101e-12 A;
row-3 and row-4 recovered currents differ by at most
1.50013335087351e-12 A and 1.08002495835535e-12 A, respectively.
Independent high-precision block swaps attribute approximately 99.96% and
99.88% of the ratio shifts to current changes. This is an intervention on
recorded evaluation inputs. It establishes the immediate current-to-metric
pathway, not the operation that originally changed those currents.

Independent 60/90-decimal scalar evaluations agree with saved metrics within
6.106226635438361e-16. Independently integrated frozen polygon probes passed
600 component comparisons with maximum error 2.439454888092385e-19 T.
These are existing finite-wire diagnostics, not new hosted NumPy executions.
Model-only ratio interventions shift rows 3 and 4 by approximately 1.44e-14
and 3.01e-15, below their comparison bounds.

The recorded weighted training response has rank 24 and condition approximately
1.94735. Ill-conditioning of that matrix has not been established.
For R=(L-P)/(L-B),
`dR=((1-R)*dL-dP+R*dB)/(L-B)`.
The Windows denominators are approximately 5.4664853404627732e-11 T and
5.22068671047435e-10 T; subtraction condition factors are approximately
948121.19 and 99276.93. Consequently small current perturbations can cause
failed fractional-recovery comparisons despite accurate field arithmetic.
Negative recovery in row 3 is retained: coarse-objective refitting need not
improve fine-grid RMS.

## Exact production input pathway and new capture contract

The relevant nominal solves are in `experiments.run`, `optimize.baseline`,
and `model.benchmark`. Configuration is `configs/phase2c_quick.json`:
10 by 24 unshifted toroidal samples, major/minor radii 1/.25 m, 24 coils
in 8 toroidal by 3 poloidal locations, 512 segments, householder-v2 geometry.
The separate disturbance polygon carries 1500 A. Fine evaluation uses
20 by 48 half-cell-shifted samples. Weights are normalized surface areas.

Let A be the normal projection of shaping-coil fields in T/A, b the normal
disturbance field in T, D=A*3000/.001 and d=b/.001. On the permitted support S:

```
M = vstack([sqrt(w)[:,None]*D[:,S], sqrt(1e-6)*eye(len(S))])
y = concatenate([-sqrt(w)*d, zeros(len(S))])
minimize 0.5*||M*x-y||², -1 <= x <= 1; I = 3000*x A
```

Dense support contains all coils. Fault supports omit the actually selected
failed coil; row mapping is derived from the dense active set and tested
against the historical mapping. Failed-coil current is exactly zero.
The global output current vector starts at zero; SciPy `lsq_linear` has no x0
argument and internally starts with unconstrained least squares. Existing
arguments are bounds (-1,1), tol 1e-12, max_iter 1000; implicit defaults are
TRF and the exact dense least-squares solver. No solver arguments are changed.
Termination message, status, iterations, cost, optimality, active mask and
unconstrained initialization are captured. Initialization sensitivity is
explicitly unavailable for this API rather than fabricated by switching methods.

`upstream_attribution.capture` calls the production baseline and temporarily
records its actual lsq_linear arguments, matrices and outputs, restoring the
function in a finally block. This is an isolated diagnostic process. It retains
coordinates, normals, normalized weights, polygon vertices, disturbance Bx/By/Bz,
A/b, D/d, M/y, initial and optimized currents, fine-grid data and configuration.
Array records contain shape and canonical little-endian binary64 bytes in hex,
preserving signed zero. Input-file SHA256 is checked before replay; source and
output SHA256 manifests are separate. Historical coarse inputs were not saved
and cannot be recovered bit-for-bit by this new capture.

## Four prepared experiments and attribution logic

1. Seal one Windows production capture. Four workers consume the same input
   SHA256 and solve its identical M/y. Differences here arise during solving
   or subsequent evaluation, not independent input generation.
2. Each worker independently regenerates production geometry and captures
   A/b, D/d, M/y and currents. Every array comparison records exact equality,
   tolerance failures and maximum absolute error. Inspect the earliest differing
   stage; a geometry difference alone does not prove it dominates the currents.
3. Every worker recomputes all coarse-grid shaping and disturbance Cartesian
   components using identical sealed polygon/point bytes. Projection is retained
   separately. Currents and recovery are compared separately from components.
4. Independent Decimal elimination at 60 and 90 digits evaluates each actual
   augmented system. A reference is accepted only with strictly interior bounds,
   stationarity and precision convergence. Active/infeasible bounds return
   INCONCLUSIVE; no unconstrained answer is presented as a constrained reference.
   Independent tangent/perpendicular Decimal wire integration at both precisions
   checks two actual coarse-grid probes for every polygon and all components.

The solve reports singular values, rank, augmented and weighted-training
conditioning, residuals, projected gradients and repeated runs. Alternate LAPACK
drivers and 14/15/16-significant-digit M rounding are explicitly sensitivity
diagnostics; they neither replace the production solver nor establish causality.
They do not vary y, all input stages, or every BLAS build. Actual loaded BLAS
details are recorded when threadpoolctl/runtime exposes them; missing metadata
is stated. CPU, platform, Python, packages, thread environment, NumPy/SciPy
configuration and runtime dispatch are retained. Version-result correlation
alone never identifies a causal dependency.

## Actual validation in this continuation

| Gate | Outcome |
|---|---|
| Repository, branch, HEAD and complete initial status | Verified |
| 439 preexisting file hashes | PASS, zero changes |
| 247 historical evidence hashes and lengths | PASS, zero changes |
| New PowerShell automation syntax | PASS, zero parser errors |
| Existing Python 3.11 launcher | Unavailable, exit 103 |
| Full pytest, compileall, analytical validation | INCONCLUSIVE; blocked before Python startup |
| New production-input preparation | INCONCLUSIVE; blocked before Python startup |
| Fresh quick/audit/output/full-repeat pipeline | INCONCLUSIVE; verifier blocked before Python startup |
| New four-worker hosted results | Not executed |

The launcher reports that its configured base executable
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe` is unavailable.
No alternate Python, environment recreation, policy change or security bypass
was attempted. Logs and native exit codes are in the preflight directory.
The new Python code and tests have not been compiled or executed here and may
need corrections after ordinary-host execution. Syntax review is not a test pass.

## Remaining limitations and corrections

There is no verified current-HEAD research checkpoint and no fresh result SHA256
with complete passing gates. The exact upstream cause remains INCONCLUSIVE.
New diagnostics cover the nominal dense and two fault refits, not every sparse
or finite-scenario minimax solver. The full production workflow remains required.
Two high-precision field probes per coil do not certify an entire grid; Decimal
precision convergence is not interval certification. Active-bound independent
optimization needs a separately validated constrained reference if encountered.
The historical 256-segment failure and 1e-4 refinement gate remain unchanged.
No robustness advantage or confinement validation is claimed; finite-scenario
minimax and small synthetic holdouts retain their existing scope.

The companion [runbook](PHASE2D_ATTRIBUTION_RUNBOOK.md) gives exact remaining
commands. No solver, constraint, objective, numerical gate or dependency was
changed to obtain agreement.
