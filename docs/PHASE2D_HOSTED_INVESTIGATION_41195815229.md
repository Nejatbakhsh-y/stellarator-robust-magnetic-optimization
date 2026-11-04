# Phase 2D hosted discrepancy investigation, 2026-10-31

Production cross-platform status remains **FAIL**. Upstream numerical root cause
remains **INCONCLUSIVE**. Scientific scope remains PARTIAL. No production source,
solver setting, physical constraint, acceptance tolerance, or historical result
was changed. No commit, push, PR, merge, or GitHub CLI operation was performed.

## Checkout and preservation

The verified repository origin is
`https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git`.
Branch: `codex/phase2d-cross-platform-reproducibility`.
Investigation HEAD: `ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7`.
The downloaded production artifacts record source commit
`babc88ccd5086b5ec3a6e1c215524636d86b3580`, clean at execution; these are
historical calculations, not an execution of the current HEAD.

All five supplied artifact directories were inspected. All 247 original files
were hashed before investigation and checked again afterward without changes.
Each of the four worker manifests has 59 entries; every listed hash matches.
All worker source fingerprints at run agree. Existing untracked work was left
untouched. `.venv/` remains ignored. No unrelated checkout was accessed.
This establishes internal preservation, not independent authentication of the
downloaded files against GitHub ZIP digests or the run API. The frozen workflow's
six passing jobs are user-confirmed context; its hosted artifacts are not among
the five supplied production artifact directories.

New evidence is under
`results/phase2d/hosted-attribution-readonly-41195815229/`.
The inventory and independent reference records identify the original inputs;
the evidence manifest hashes the diagnostic outputs. These records establish
diagnostic observations, not a verified research checkpoint.

## Every failed numerical comparison

`all-failed-comparisons.json` retains all 16 failed records, including reference,
current, absolute error, bound, artifact filename, and JSON path. There are four
records in each of Linux reference's committed-reference comparison, Linux SciPy
sensitivity's committed-reference comparison, cross-platform comparison, and
SciPy comparison. Windows and NumPy sensitivity comparisons pass in the supplied
records. No failed record was reclassified.

Each failing report contains the following two quantities twice: once at
`/quick/faults/{row}/fractional_recovery` and once at
`/quick/faults/{row}/recovery_evidence/fractional_recovery`.

| Fault row (zero based) | Failed coil | Reference | Current | Absolute error | Bound |
|---|---:|---:|---:|---:|---:|
| 3 | 3 | -0.414688997029067 | -0.4146889970636461 | 3.457911734727759e-11 | 4.246889970636461e-12 |
| 4 | 6 | 0.16726624849972482 | 0.16726624849716587 | 2.5589530494585233e-12 | 1.7726624849716587e-12 |

The unchanged bound is `1e-13 + 1e-11 * abs(current)`, following the existing
comparator's orientation. Errors exceed it by about 8.14 and 1.44 respectively.
These are two distinct failed quantities, not 16 independent scientific effects.

## Independent reference and conditioning

The existing `scripts/phase2d_reference.cs` was compiled locally with `Add-Type`.
It decomposes binary64 bits into BigInteger fixed-point values and evaluates
direct weighted RMS norms and their differences at 60 and 90 fractional decimal
places. It does not call NumPy, BLAS, SciPy, or the production recovery helper.
The two precisions agree far beyond binary64 accuracy. This is a precision
convergence diagnostic, not a rigorous interval certificate.

Authoritative numerical records are `binary64-references.json` and
`binary64-block-swaps.json`. Windows PowerShell initially parsed JSON numbers as
Decimal; casting those to double perturbed some values by an ulp. That preliminary
calculation is retained in `independent-references.json` and `block-swaps.json`,
but is superseded by the explicitly parsed binary64 calculations. The diagnostic
loader now parses the decimal lexical value with invariant-culture `Double.Parse`
before computing. No production calculation used that preliminary loader.

| Row | Windows high-precision reference (abridged) | Linux high-precision reference (abridged) |
|---|---:|---:|
| 3 | -0.414688997029066963270294652224927 | -0.414688997063645878793003475518803 |
| 4 | 0.167266248499724981562587894655019 | 0.167266248497165832106743301733540 |

Across all four cohorts and both rows, the maximum binary64 absolute error of
the saved metric against the independent reference is 6.106226635438361e-16.
Thus the discrepancy survives independent accurate evaluation of the recorded
inputs. The production `residual-energy-v3` scalar evaluation is already accurate
enough for these cases. Replacing it, rounding its outputs, or relaxing tolerances
would not be justified.

Let B, L, P denote pre-fault, frozen-fault, and recovered RMS fields. The metric
is R=(L-P)/(L-B). Its first variation is
`dR = ((1-R)*dL - dP + R*dB)/(L-B)`.
The small denominator amplifies perturbations even when norms are individually
accurate. The production factorization uses
`(L²-P²)/(L²-B²) * (L+B)/(L+P)` and current increments to avoid subtracting
nearly equal field vectors. That reduces arithmetic cancellation without making
R insensitive to changes in the supplied currents.

| Windows diagnostic | Row 3 | Row 4 |
|---|---:|---:|
| L-B, T (factored evaluation) | 5.4664853404627732e-11 | 5.22068671047435e-10 |
| RMS subtraction condition (L+B)/abs(L-B) | 948121.19 | 99276.93 |
| Numerator energy sum absolute terms / absolute sum | 50.5078 | 51.9361 |
| Denominator energy sum absolute terms / absolute sum | 24.8596 | 10.4489 |

The weighted training response is full rank 24, with recorded condition number
about 1.94735. An ill-conditioned training response is not established. A
well-conditioned least-squares fit can still produce last-bit current differences
that this sensitive downstream ratio magnifies. The negative row-3 recovery is
retained: refitting on the coarse training objective need not improve the separate
fine-grid RMS metric.

## Currents, inputs, and causal block interventions

`binary64-current-vectors.json` contains full Windows/current vectors and signed
per-coordinate differences for every reported optimizer-current method, including
both recovered vectors. The Windows/Linux maximum absolute differences are:

| Block | Linux reference and SciPy sensitivity, A | NumPy sensitivity, A |
|---|---:|---:|
| Dense | 1.47792889038101e-12 | 8.10018718766514e-13 |
| Recovered row 3 | 1.50013335087351e-12 | 1.50779388974343e-12 |
| Recovered row 4 | 1.08002495835535e-12 | 1.48636658536816e-12 |

Configuration records agree exactly: 512 segments, 10x24 training surface,
3000 A cap, 0.001 T scaling, ridge 1e-6, seeds 20261029/20261030, 8 training
and 24 holdout scenarios, householder-v2 geometry, residual-energy-v3 metric.
The source baseline uses `lsq_linear`, bounds (-1,1), tol=1e-12, max_iter=1000;
none were modified. Solver statuses remain in `training-and-settings.json`.
Scenario translations, rotations, gains and offsets match exactly across
cohorts. Sampled clearances differ; they are derived geometric diagnostics.
They do not enter the nominal dense/recovered least-squares objective. Random
scenario differences therefore do not explain these two nominal recovery rows.

The supplied fine-grid reference response differs between Windows and Linux in
21011 entries, maximum about 4.50e-22 T/A. Disturbance differs in 878 entries,
maximum about 1.91e-19 T. Weights match exactly. NumPy sensitivity has the same
maximum response difference and a maximum disturbance difference about 2.44e-19 T.
These summaries in `vector-differences.json` came from preliminary Decimal
subtraction and are descriptive to the displayed precision; use the original
hashed files for exact binary64 input comparisons.

Independent 90-digit interventions hold one complete block fixed at a time:

| Row | Windows model + Windows currents | Windows model + Linux currents | Linux model + Windows currents | Linux model + Linux currents |
|---|---:|---:|---:|---:|
| 3 | -0.41468899702906696 | -0.41468899706363146 | -0.41468899702908138 | -0.41468899706364588 |
| 4 | 0.16726624849972498 | 0.16726624849716884 | 0.16726624849972197 | 0.16726624849716583 |

Changing currents alone accounts for about 99.96% and 99.88% of the respective
full shifts. Changing the fine-grid field model alone shifts the ratios only
about 1.44e-14 and 3.01e-15. Both are below the unchanged comparison bounds.
The small interaction does not change this conclusion. This is a causal
intervention on the recorded metric inputs, not just correlation.

This establishes the dominant immediate origin as optimizer-current perturbations
amplified by recovery sensitivity. It does **not** establish whether those current
perturbations originate in generated coarse-grid geometry/field data, augmented
matrix assembly, LAPACK/BLAS, or the least-squares solve itself. The artifacts
export fine-grid audit inputs, not original coarse-grid augmented M/y. Their
training matrix cannot be recovered bit-for-bit merely by treating the fine-grid
audit matrix as the solver input. That substitution would invalidate attribution.

## Platform-sensitive operations and magnetic components

Windows used Python 3.11.9; Linux used 3.11.17/glibc 2.39. Reference packages
were NumPy 2.4.6 and SciPy 1.17.1. Sensitivities used NumPy 2.3.5 or SciPy
1.16.3. The workflow pins BLAS/OMP/MKL thread counts to one. The supplied production
records do not identify actual BLAS/LAPACK builds, CPU dispatch or compiler flags;
there is no basis to name one particular BLAS implementation as the root cause.

Geometry uses trigonometry, normal normalization, Householder products and
reductions; field evaluation uses differences, norm square roots, cross products,
dot products and segment summation. Response projection, weighted assembly and
LAPACK least squares add further platform-sensitive operations. The factored
metric uses compensated scalar sums. These are possible pathways, not proven
individual culprits. Linux reference and SciPy sensitivity have identical relevant
model/current/ratio values; this weighs against the SciPy version change being
causal. NumPy sensitivity changes the answer and passes, but that does not prove
a NumPy defect or justify selecting a dependency to make a gate green.

New investigation-only `scripts/phase2d_field_reference.cs` independently
integrates straight wires through a tangent/perpendicular formula at 60/90
fixed-point decimal places. Its comparison implementation uses the endpoint
cross-product formula in scalar binary64 C#, separately from production NumPy.
Exact lexical binary64 vertices from the existing sealed fixture were supplied
to both implementations. All 25 coils and eight prescribed Cartesian probes
were evaluated, including the disturbance coil at 1500 A and shaping coils at
1 A: all **600 Bx/By/Bz comparisons pass** the unchanged bounds. Both reference
precisions round to the same binary64 component in every case; maximum absolute
component error is 2.439454888092385e-19 T.
See `binary64-all-field-probes.json`. The smaller preliminary probe record is
retained separately. This is a frozen polygon/probe diagnostic, not a new hosted
NumPy replay, a full production-grid comparison, or a smooth-filament/continuum
certificate. It supports the finite-wire mathematics, while the actual hosted
field implementation still requires controlled execution on identical bytes.

## Changes and validation outcomes

There is no justified production scientific correction. Added files are a
read-only artifact attribution script, an independent C# field diagnostic, and
this report. The new PowerShell diagnostic explicitly parses binary64 inputs;
it never replaces original evidence and requires a fresh output directory.

Executed diagnostic checks passed: analytic regular-polygon center field, zero
current, current sign reversal, vertex-order reversal, near-filament rejection,
and an exact synthetic recovery ratio. Both C# diagnostic classes compiled.
The new PowerShell file parses with zero syntax errors. Its end-to-end invocation
was blocked by the host's script execution policy; policy was not changed.
The reported calculations were executed as individual tool-hosted PowerShell
commands and their records are preserved. A syntax check is not an end-to-end
regression-suite pass.

The existing `.venv` launcher fails with exit code **103** because its configured
base executable at
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`
is unavailable. This is the observed environment failure; it is not evidence that
Python tests fail scientifically, nor proof of a particular sandbox denial.
Pytest, analytical validation, fresh quick execution, output checks, independent
audit, full reproducibility script, production verify and fault audit were
attempted and blocked before Python started. No dependency replacement, environment
recreation, or alternate Python was used. Logs are in `python-attempts.json`,
`scientific-audit-attempts.json` and `attempt-*.log`.

No current-HEAD research checkpoint is verified. Original failed comparisons,
original 256-segment failure evidence, and all original artifacts remain intact.
No robustness advantage or confinement validation follows from this investigation.

## Exact host continuation and hosted verification requirements

On an authorized Windows host where the existing Python 3.11 environment works,
run these commands from this checkout. Do not bypass security policy; the host
must permit the existing scripts through its normal policy. No publication
operation is required or authorized.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m stellarator_robust.cli validate
.\scripts\phase2d_controlled_host.ps1
.\scripts\phase2d_hosted_attribution.ps1 -Evidence results/ci/phase2d-hosted-investigation-41195815229 -Output results/phase2d/hosted-attribution-host-replay-41195815229
```

Stop on nonzero native exit codes; retain each failure. Choose a fresh replay
output path if the shown path already exists. The controlled host script records
fresh regression, analytical, frozen, production quick/study, independent audit,
output and complete repeated-production checks, with result hashes. It does not
authorize overwriting legacy README outputs or regenerating historical reports.
Before any later verified checkpoint claim, the complete README quick/repeat
gates must also be executed with historical outputs preserved, in addition to
these Phase 2D gates. No such execution is claimed here.

To establish upstream cause, the next hosted investigation must retain:

1. Actual production coarse-grid points, normals, weights, vertices, A/b,
   scaled D/d, augmented M/y and support for dense and failed coils 3 and 6,
   captured before solving. Keep the fine-grid audit inputs separately.
2. Exact package versions, Python patch versions, `numpy.show_config()`,
   `scipy.show_config()`, loaded BLAS/LAPACK details, CPU dispatch, thread counts,
   complete solver arguments, termination details and source/input SHA256 values.
3. Four controlled cohorts consuming identical serialized production M/y, rather
   than independently assembling them. Independently solve each interior ridge
   system at converged high precision, verify bounds/KKT/objective, and evaluate
   the recovered ratios using identical fine-grid inputs. If bounds activate,
   an unconstrained normal-equation solution is not a valid reference.
4. Orthogonal swaps of coarse input generation, assembly, solver and fine-grid
   evaluation. Include fixed Windows currents and fixed Linux currents, and
   compare every Bx/By/Bz component on identical polygon/probe bytes. Replaying
   this sealed diagnostic alone does not identify the production coarse solve.
5. Full production jobs on Windows reference, Linux reference, NumPy sensitivity
   and SciPy sensitivity; frozen prepare/four-cohort/compare jobs; strict pairwise
   production comparisons; regression and analytical checks, quick experiment,
   independent audit, output checks, training audit and full repeated runs.
   Passing records must bind the actual result-file SHA256. Retain every failed
   comparison and all original artifacts, and do not modify `rtol=1e-11`,
   `atol=1e-13`, refinement limit 1e-4, solver settings or physical constraints.

Until those production input/solver interventions run, the precise upstream
platform mechanism remains INCONCLUSIVE and production cross-platform agreement
remains FAIL.
