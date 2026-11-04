**STEP 40 — controlled numerical correction and independent validation**

2026-11-01. Fresh independent .NET numerical experiments completed; the new
Python validator and regression tests remain runtime-unverified. The existing
`.venv` cannot locate its configured Python 3.11 base executable. This is **not
a verified research checkpoint**. Scientific comparison **FAIL**, production
acceptance **FAIL**, overall scientific status **PARTIAL**, upstream numerical
root cause **INCONCLUSIVE**. No corrected production experiment is claimed.

**Research objective and evidence boundaries.** Establish which STEP 39
conclusions survive independent arithmetic, resolve demonstrable diagnostic
defects, and distinguish current-to-ratio sensitivity from the originating
solver mechanism. AGENTS.md, both requested reports, their implementations and
tests, README, execution/refinement status, the original Phase 2D methods,
STEP 34/35/36 records, production capture/solve, field and fault-metric code were
reviewed. Work stayed on `codex/phase2d-upstream-attribution`, starting HEAD
`cc0602b43ed455005672625e75588e080f572b80`. Only the three authorized STEP 40
deliverables were created outside the supplied output root. Production source,
historical evidence, existing tests, documentation and workflows were preserved.
Nothing was staged, committed, pushed, merged or dispatched. No GitHub CLI
configuration was accessed; no environment was replaced.

E means the existing STEP 38 input directory
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/`.
O means the supplied fresh output root
`results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/`.
Evidence links below resolve to O. Numerical records retain input and/or original
result-file SHA256 identifiers. `manifest.json` seals generated evidence;
`source-hashes.json` identifies final deliverables and executed helper sources.
These are local consistency seals, not hosted attestations.

**Mathematical formulation and unchanged invariants.** For support S, physical
current I, x=I/3000 A, D=A·3000/Bref, d=b/Bref and Bref=0.001 T:

```
minimize f(x_S) = ||M x_S - y||² / 2,  -1 <= x_S <= 1
M = [diag(sqrt(w)) D_S; sqrt(1e-6) Identity]
y = [-diag(sqrt(w)) d; 0]
```

Unsupported currents remain zero. Production settings remain `lsq_linear`,
TRF, implicit exact least squares, tol=1e-12, max_iter=1000. The comparison bound
remains `abs(candidate-reference) <= 1e-13 + 1e-11*abs(reference)`; refinement
limit remains 1e-4; quick geometry remains 512 segments; the recovery guard
remains `abs(L-B) > 1e-15 T`. Saved settings were freshly checked, without
alteration, in [solver-diagnostic-verification.json][solver]. No new production
acceptance threshold is introduced by the diagnostic module. Interior reference solves are
not a replacement production optimizer.

The [original study formulation](PHASE2D_STEP34_FINAL_CAUSAL_ATTRIBUTION.md)
uses finite-scenario minimax with eight training and 24 holdout
scenarios, not a universal robustness certificate. This capture contains bounded
ridge cases, not complete SLSQP states/constraints. No minimax reproduction,
robust outperformance, continuum-peak, smooth-circle refinement, confinement or
device validation follows from these calculations.

**Verification of STEP 39 conclusions.** STEP 39 established a wrong dL sign in
the requested differential, cancellation amplification, saved-input identity,
small worker-current differences and historical ratio failures. It did **not**
establish a unique OS/library/BLAS/dispatch causal mechanism. Its initial
wrong-sign diagnostic was explicitly superseded; both versions remain intact.
Its Gram/Jacobi spectrum was accurately labelled an estimate rather than a fresh
SVD, and its Python high-precision calculations were accurately labelled
unexecuted. These are not demonstrated defects in the production magnetic-field
or optimization equations.

Fresh STEP 40 checks confirm the following:

| Check | Actual result | Evidence |
|---|---|---|
| Supplied download/historical inventory | 3,599 entries; zero mismatches | [integrity-before.json][integrity] |
| STEP 39 manifest members | 263 files; zero mismatches | [step39-integrity.json][prior] |
| Historical source versus Git blobs | 824 path/cohort checks; zero mismatches, later two runs only | [source-git-verification.json][source] |
| Solver reconstruction | All eight captures: maximum D, d, M, y reconstruction differences zero | [input-reconstruction.json][inputs] |
| Saved candidates | 96 direct residual/KKT evaluations, each at 60/90 fractional places | [kkt-and-solver-records.json][kkt] |
| Independent reference systems | 24 cases at both precisions; all 24 additional 90-place repeats have identical textual x | [reference-certificates.json][cert] |
| Current comparisons | All 72 nonself comparisons pass; maximum difference 2.8279600883251987e-12 A | [current-comparisons.json][currents] |
| Recovery failures | Earlier 21; latest 11; all remain failures under high precision | [high-precision-deltas.json][deltas] |

Local source/input hashes do not resolve the earlier source/head inconsistencies
or authenticate missing original archive bytes. The four early incomplete
manifests and the STEP 38 workflow-identity gap remain historical limitations;
STEP 40 has not repaired or remotely reauthenticated them. The original archive
authentication requirement remains incomplete. Python's stricter semantic
fingerprint, duplicate-key/schema and complete inventory checks are implemented
but have not executed here; the successful .NET calculations must not be described
as execution of that Python validator.

**Independent numerical experiments and solver inputs.** The executed arithmetic
uses `BigInteger` fixed-point conversion of the actual IEEE-754 mantissa/exponent,
direct residual sums, integer square roots, pivoted elimination of high-precision
normal systems, independent one-sided Jacobi column orthogonalization, and
Gauss–Legendre segment quadrature. No production numerical helper is called.
The direct-RMS reference adapts the existing independent C# investigation helper;
its source and the new calculation/certificate helpers are retained in O. Reuse
of that independent evaluator is explicit, not a claim of an entirely new
arithmetic library. The Python module separately implements twice-orthogonalized
Decimal QR, direct Decimal residuals/RMS, SVD, and a tangent/perpendicular segment
integral; those implementations remain unexecuted.

Fixed-point references truncate conversions/products/square roots at 60 or 90
fractional decimal places. Decimal uses 60/90 significant digits. Their precision
labels are not interchangeable. Precision convergence is empirical, not an
interval certificate. Normal equations are justified only for the measured
well-conditioned interior subset; no bounded optimum is asserted for an
out-of-box unconstrained reference. The Python QR returns NOT_CERTIFIED for
singular/precision-limited or noninterior problems.

Input-file seals bind all saved geometry, currents, initialization, fine-grid
arrays, support, weights and configuration. Exact byte transport for the saved
replay cells was checked before numerical evaluation. Reconstructed M/y match
the saved matrices without renormalizing weights or changing scaling. Saved
solver settings, active masks, status, iteration count, objective and optimality
are retained alongside each independent residual certificate in [KKT records][kkt]
and [diagnostic verification][solver]. `lsq_linear` has no user x0; its captured
unconstrained initialization is not a controllable supplied initial guess.

**Available four-way controlled solver experiments.**

| Required fresh production-solver experiment | STEP 40 execution |
|---|---|
| A: Windows inputs on Windows | **NOT EXECUTED** — existing Python cannot start |
| B: Windows inputs on Linux | **NOT EXECUTED** — no Linux execution performed |
| C: Linux inputs on Windows | **NOT EXECUTED** — existing Python cannot start |
| D: Linux inputs on Linux | **NOT EXECUTED** — no Linux execution performed |

See [numerical-summary.json][summary] and [attempts.json][attempts]. Historical
reciprocal worker outputs remain saved observations, never substitutes for these
fresh runs. Local high-precision arithmetic solves of frozen M/y do not execute
the historical SciPy algorithm. Their iteration/termination fields must not be
invented as `lsq_linear` records.

[execution-environment.json][env] fingerprints the executing .NET/PowerShell/OS
environment. [saved-environments.json][savedenv] retains original environment-file
hashes and full saved worker self-reports. The historical Windows/Linux Python
patch versions, library wheels, BLAS builds and dispatch architectures are
confounded; saved single-thread reports do not establish isolated interventions
or independent hardware attestation. No fresh hosted success is claimed.

**High-precision references and conditioning.** All independent reference vectors
are interior. The maximum high-precision reference stationarity residual is
4.1e-89; their 60/90-place vectors round identically to binary64. The maximum
normalized distance between saved candidate currents and a rounded independent
reference is 6.7e-16. These results test the frozen mathematical problem; they do
not identify the low-level source of differing rounded solver outputs.
[reference-certificates.json][cert], [current-comparisons.json][currents].

One-sided Jacobi operates on M's columns, avoiding Gram formation in the spectral
check. Across all captures/cases its condition estimates range from
1.9467914804478383 to 1.9467914804478437. The effective-rank cutoff is
`max(M.shape)*eps*sigma_max`; ranks are 24/23/23. Representative latest
Windows-origin values are:

| Case | Largest singular value | Smallest singular value | Rank |
|---|---:|---:|---:|
| Dense | 0.069826207928519762 | 0.035867327666986130 | 24 |
| Row 3 | 0.069826207928519873 | 0.035867327666986158 | 23 |
| Row 4 | 0.069826207928519846 | 0.035867327666986228 | 23 |

The complete spectra and cutoffs are in [independent-spectra.json][spectra].
All saved rank records agree; maximum saved singular-value difference is
4.23e-16. This does not support severe matrix ill-conditioning or nonuniqueness
as the discrepancy mechanism. [solver-diagnostic-verification.json][solver].

**KKT analysis.** For r=Mx-y and g=Mᵀr, stationarity is
`g-lambda_lower+lambda_upper=0`. At x=-1 the lower multiplier must be nonnegative;
at x=1 the upper multiplier must be nonnegative. Primal feasibility, dual
feasibility and complementarity are separate checks. Inferred multipliers at
interior points are zero. Their dual/complementarity residuals being zero is
therefore not separate proof of optimality; direct stationarity is essential.
The new module also permits explicit dual certificates so negative multipliers
and noncomplementary certificates can be tested meaningfully.

Across the 96 saved candidates, maximum 90-place stationarity is
2.1773934378973348e-18, primal violations are zero, and no bounds are active.
Inferred dual/complementarity residuals are zero. Maximum saved-objective versus
independent direct-residual objective difference is about 6e-19 in binary64.
All saved termination records have status=3, nit=0 and unconstrained-optimum
messages. Feasibility and small independent KKT residuals support these
candidates without relying on their success flags. They do not force
cross-platform ratio acceptance. [KKT records][kkt], [diagnostic verification][solver],
[reference certificates][cert]. Exact Decimal I/3000 and rounded binary64 I/3000
are different diagnostic conventions; these saved-candidate checks explicitly
include binary64 current normalization, as STEP 39 did.

**Recovery-ratio differential: justified diagnostic correction.** For
`R=(L-P)/(L-B)`, the quotient rule gives

```
dN = dL-dP, dD = dL-dB
dR = [(dL-dP)(L-B) - (L-P)(dL-dB)]/(L-B)^2
   = [(P-B)dL - (L-B)dP + (L-P)dB]/(L-B)^2.
```

Thus the requested `(B-P)dL` sign is incorrect. This is a symbolic identity,
independent of the data. At B=1, L=3, P=2 the dL derivative is +0.25, while the
requested expression predicts -0.25. The fresh 90-place finite difference
confirms the positive sign in [derivative-counterexample.json][counter]. The
new regression test includes coefficient-wise quotient-rule identities and
numerical central differences; it explicitly rejects the original wrong sign.
The correction is confined to STEP 40 diagnostics. STEP 39's already-corrected
diagnostic and its initial failed attempt remain unchanged.

For all saved RMS triples the independently evaluated derivatives agree with
90-place central differences. Largest dL absolute difference is
2.587931566676031e-20, with h=abs(L-B)·1e-15, consistent with finite-step error.
[ratio-conditioning-derivatives.json][derivatives]. The Python tests use a
separate h=abs(L-B)·1e-20 calculation and have not executed.

**Fault row 3.** Latest Windows-origin/Windows-worker result SHA256 is
`abfc4d126b001d135c49b9009f9abd1366cd67f2b9260957c6c9cdd368395537`.
From its saved rounded RMS values, L-B≈5.466485340356966e-11 T,
L-P≈-2.266891323499066e-11 T, denominator cancellation factor≈948121.1885,
numerator cancellation factor≈2286346.1770, and dR/dL≈2.587931566676031e10/T.
Both cancellation and ratio amplification are large despite a well-conditioned
least-squares matrix. One upward binary64 step in the saved L scalar changes
the rounded-RMS ratio by about 8.7682532083e-11.
[ratio-conditioning-derivatives.json][derivatives].

Direct full fine-grid 90-place recomputation at saved currents instead gives
R=-0.4146889970809171094992892896548706787…; saved production R is
-0.41468899708091722. The negative ratio is not a recovery benefit. There are
ten latest-run and twelve preceding-run row3 failures. They remain failures;
the rounded-RMS scalar calculation must not replace the factored production
metric or the high-precision field-to-R reference.
[high-precision-recovery.json][ratios], [high-precision-deltas.json][deltas].

**Fault row 4.** The same representative result gives
L-B≈5.220686710494032e-10 T, L-P≈8.732446806741898e-11 T, denominator
cancellation factor≈99276.92669, numerator cancellation factor≈593531.3329,
and dR/dL≈1.595065549179688e9/T. One upward step in saved L changes the
rounded-RMS ratio by about 5.4042922927e-12. Both row denominators remain above
the original guard; neither was regularized. [derivative/conditioning records][derivatives].
Full fine-grid 90-place evaluation gives
R=0.1672662484975028316716501674920593179…; saved production R is
0.16726624849750296. One latest-run row4 comparison and nine preceding-run
row4 comparisons still fail. [high-precision-recovery.json][ratios],
[high-precision-deltas.json][deltas].

**All eleven latest historical failures.** W=Windows reference, L=Linux
reference, N=Linux NumPy sensitivity, S=Linux SciPy sensitivity. Each candidate
is compared with the Windows worker on exactly the same origin input. The table
contains fresh high-precision candidate-minus-reference differences, not the
slightly different saved binary64 ratio differences. Every row remains FAIL
under the original comparison. Full scalars, both original result SHA256 values
and classifications are in [high-precision-deltas.json][deltas] and
[recovery-comparisons.json][comparisons].

| Origin | Worker | Fault row | Independent delta R |
|---|---|---:|---:|
| W | L | 4 | -2.717251278971e-12 |
| W | N | 3 | 3.161582080683e-11 |
| W | S | 3 | 3.161582080683e-11 |
| L | N | 3 | 3.158395253375e-11 |
| L | S | 3 | 3.158395253375e-11 |
| N | L | 3 | 1.109018376310e-11 |
| N | N | 3 | 3.555492297367e-11 |
| N | S | 3 | 3.555492297367e-11 |
| S | L | 3 | 1.109018376310e-11 |
| S | N | 3 | 3.555492297367e-11 |
| S | S | 3 | 3.555492297367e-11 |

The preceding run's 21 failures are retained in the same evidence. Duplicate
N/S origins are distinct saved comparisons, not independent physical studies.
A fresh arithmetic/hash recheck also retains all 22 earlier extracted scalar
failure paths (16 and six respectively), without pretending to have performed
a new complete extraction of those early original JSON files. Duplicated nested
metric paths are not new experiments. [early-failure-recheck.json][early].

**High-precision recovery, current and model interventions.** All 64 saved
fine-grid recovery evaluations were repeated at 60/90 fractional places.
Maximum precision difference is 8.0123492783225683e-45; maximum saved-ratio versus
reference difference after binary64 rounding is 6.106226635438361e-16. These
are far smaller than the failed worker differences. Final ratio arithmetic
alone cannot explain those failures. [precision-convergence.json][precision].
An additional exact-integer check of all 48 nonself high-precision comparisons
uses `abs(candidate-reference)*10^13 <= 1+100*abs(reference)` on the retained
90-place values. It independently retains all 32 failures, with zero
classification differences from the binary64 check of the reference values.
[exact-high-precision-classifications.json][exact].

For every same-origin nonreference worker, controlled dense-only and
recovered-only current substitutions hold A, b, w, support and failed-coil
identity fixed. The combined substitution is the independently recomputed
candidate itself. All failed classifications survive it. Maximum nonlinear
interaction after subtracting the two individual effects is
2.5964495498634933e-24. This establishes a reproducible immediate pathway from
the **saved different currents** to the ratio differences; it does not explain
how SciPy generated those currents. [current-interventions.json][swaps],
[current-effect-decomposition.json][effects].

Separately, 48 one-ULP matrix-entry, disturbance-entry and balanced-weight
interventions were actually evaluated at fixed saved currents. Largest ratio
changes are respectively 3.9061140782243914e-17, 5.2449556296600683e-17 and
3.09848855147641e-17 for these particular coordinate directions. These are not
global sensitivity bounds, not optimized perturbations and not solver reruns.
Weight transfers preserve normalization algebraically subject to binary64
rounding. No scenario was removed or reweighted in production.
[input-interventions.json][interventions]. Discrete support-path comparisons
have zero mismatches across the 32 saved cells; no active bounds are observed.
This excludes observed switching in this subset, not all possible transitions.
[support-comparisons.json][supports], [KKT records][kkt].

**Independent magnetic-field and design-matrix validation.** Fresh independent
eight-point Gauss–Legendre integration covers all 240 training points, all 960
fine-grid points and all 25 polygons per origin. Against captured projected
inputs, largest training A/b errors are 1.9058241313221758e-21 T/A and
7.589415207398531e-19 T. Fine-grid maxima are 1.0852609636695723e-21 T/A and
1.2468324983583301e-18 T. Full independent fine-grid matrices are saved, not
substituted into production. [independent-field-validation.json][field],
[independent-fine-design.json][fine].

Independent 60/90-place straight-segment reference fields cover both Cartesian
probes (training indices 0 and 80), all coils, and the disturbance. Their unit
coil components round identically at both precisions; maximum quadrature versus
90-place probe differences are 2.4352197233561135e-21 T/A for unit coils and
4.87890977618477e-19 T for disturbance. High precision is limited to those probes;
full-grid arbitrary-precision geometry integration is not claimed. [field references][field].

All 96 saved optimized-current training Bxyz vectors were freshly evaluated
with independent quadrature. Captured-current field comparisons against saved
field arrays have maximum component error 9.0801931945661e-19 T; disturbance
maximum is 7.8604657505199071e-19 T. Saved fixed-current arrays use captured
currents, not each worker's optimized currents; these checks keep the distinction
explicit. [all-current-forward-fields.json][vectors]. Small field errors and
fixed-current agreement do not imply reproducibility of a cancellation-sensitive
derived ratio, nor constitute the mandatory independent quick/refinement audit.

**Demonstrated causes and justified corrections.** The requested dL sign is a
conclusive algebraic error; the quotient and finite differences demonstrate
scalar perturbation amplification. Controlled current substitutions establish
the immediate saved-current-to-R pathway. No production optimization or magnetic
equation defect has been independently demonstrated. Therefore **no production
patch is justified or applied** at this stage. A specific rounding kernel,
LAPACK driver, operating system, dispatch choice, termination criterion or
active-set change remains an unproved upstream hypothesis.

The minimal justified diagnostic correction is the positive `(P-B)dL`
coefficient, implemented only in the new STEP 40 module. Additional diagnostic
improvements are independent QR reference solutions, direct residual KKT with
optional explicit multipliers, high-precision ratios/finite differences, strict
input/source seals, numerical versus missing-evidence classifications, actual
input/current interventions, and separate diagnostic/production verdicts. They
do not change the scientific model or thresholds. The wrong-sign regression is
the concrete counterexample B=1,L=3,P=2; the original failed evidence is preserved.

**Implementation and validation results.** The three deliverables are
`scripts/phase2d_step40_validation.py`,
`tests/test_phase2d_step40_validation.py`, and this document. The CLI requires
explicit input, new output and output-root directories, verifies containment and
hashes, uses strict STEP 38 transport/schema checks and its own independent
numerical functions, records JSON diagnostics, and never promotes historical
production acceptance. It preserves missing/corrupt-evidence errors separately
from numerical comparison failures. Exit 2 denotes incomplete evidence; completed
diagnostics still exit 1 with scientific FAIL. Known missing archives remain an
authentication limitation, even if arithmetic succeeds.

Regression tests cover quotient-rule sign/coefficients, high precision, finite
differences, guard and nonfinite rejection, singular/ill-conditioned matrices,
QR, KKT stationarity/primal/dual/complementarity, changed frozen matrices and
solver settings, missing artifacts, invalid source fingerprints, active-set
changes, both fault rows, false PASS claims, repeatability, analytical square-loop
fields, controlled field/weight interventions and diagnostic/production separation.
These are meaningful mathematical assertions, but **zero Python tests executed**.

| Requested validation | Executed outcome |
|---|---|
| STEP 40 regressions; complete pytest | BLOCKED before interpreter startup, exit 103 |
| Python compilation | BLOCKED before interpreter startup, exit 103 |
| Analytical CLI validation | BLOCKED before interpreter startup, exit 103 |
| Quick run, output checks, independent audit | Each attempted; exit 103 before startup |
| README test record and full repeat | Each attempted in a fresh source copy under O; exit 103 |
| Phase 2C full production repeat | Attempted in fresh output scope; exit 103 |
| STEP 40 Python CLI | Attempted; exit 103 |
| Independent .NET arithmetic, spectra, fields and references | Executed; evidence cited above, scientific failures retained |
| Input/source SHA256 and historical preservation | Executed; before/after records and source hashes in O |
| Git whitespace/index/ignored environment checks | Executed; see final-git-checks.json |

[attempts.json][attempts] and `final-attempts.json` retain exact command arrays,
working directories, exit codes and individual logs. No dependency installation
or alternate interpreter was used. Fixed-path README writers were attempted
only in `O/validation-copy`, never against historical results. The initial field
command was rejected at PowerShell parsing because two keys differed only by
case; no calculation ran in that attempt. The corrected command uses distinct
names. Both the failure note and executed corrected command are retained in O;
no execution-policy setting was changed.
`reviewed-final-attempts.json` binds the final post-review Python attempts to
the final validator and test SHA256 values. Final historical preservation is
recorded in `integrity-after.json` and `step39-integrity-after.json`.

**Reproducibility commands.** After the environment owner restores the existing
Python 3.11 base installation, run from this checkout, choosing a new child of
the authorized root. Check each return code; do not describe blocked commands as
passing. The historical evidence input is required locally.

```powershell
$py = Join-Path $PWD '.venv/Scripts/python.exe'
$E = Join-Path $PWD 'results/phase2d/step38-independent-verification-20261101-084216-7bda80b7'
$O = Join-Path $PWD 'results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e'
$R = Join-Path $O ('repeat-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $R
$env:PYTHONPYCACHEPREFIX = Join-Path $R 'pycache'
$env:PYTEST_ADDOPTS = '-p no:cacheprovider'
& $py -m pytest -q tests/test_phase2d_step40_validation.py --basetemp "$R/targeted"
& $py -m pytest -q --basetemp "$R/full"
& $py -m compileall -q src scripts tests
& $py scripts/phase2d_step40_validation.py --input $E --output-root $O --output "$R/validation"
& $py -m stellarator_robust.cli validate
& $py -m stellarator_robust.cli run --config configs/quick.json --output "$R/quick"
& $py scripts/check_outputs.py "$R/quick"
& $py scripts/audit_quick.py "$R/quick"
& $py scripts/phase2c_verify.py --output "$R/production"
git diff --check
```

Repeat the complete baseline README workflow, including `test_and_record.py`
and `reproduce_check.py`, in a new source/config/test/package copy beneath R
using the same existing `.venv` interpreter and recording copy hashes. The
README audit defaults to `results/quick`; pass explicit paths outside that copy.
Do not run fixed-path scripts against historical quick results. Required gates
must yield actual passing records tied to the new results.json SHA256 before
any checkpoint-verification claim. Passing software tests alone cannot change
the scientific verdict. The retained C# sources and
`executed-*-command.txt` records document the actual arithmetic checks separately;
the Python CLI is not claimed to reproduce the .NET execution transcript byte
for byte.

**Remaining uncertainty, scientific verdict and STEP 41 requirements.**
The saved current differences, sensitivity pathway and continued failures have
independent numerical support. The unique upstream mechanism remains
INCONCLUSIVE. No threshold was relaxed and no historical failure was suppressed.

```
scientific_comparison = FAIL
production_acceptance = FAIL
scientific_status = PARTIAL
causal_root_cause = INCONCLUSIVE
```

STEP 41 requires a functioning existing Python environment; executed final-source
targeted/full tests and compilation; complete README analytical/quick/output/
independent audit/full-repeat gates with result-SHA-bound passing records;
executed strict semantic/frozen/source verification; authenticated original
archives and resolution of remaining source/workflow/manifest provenance gaps;
and fresh reciprocal production solver experiments with exact serialized M/y,
support, settings, currents, objective, feasibility, KKT, active sets,
iterations/termination and environment fingerprints. Hold interpreter, BLAS build,
thread count and dispatch fixed while changing one factor at a time. Preserve
all failed interventions. Evaluate each new experiment under the unchanged
scientific thresholds; do not retroactively relabel historical results. Full-grid
arbitrary-precision geometry, broader supports/minimax and larger holdout studies
remain separate validation extensions. Hosted reproducibility requires actual
successful hosted execution and verified evidence; it is not established here.

[integrity]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/integrity-before.json
[prior]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/step39-integrity.json
[source]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/source-git-verification.json
[inputs]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/input-reconstruction.json
[kkt]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/kkt-and-solver-records.json
[cert]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/reference-certificates.json
[currents]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/current-comparisons.json
[deltas]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/high-precision-deltas.json
[summary]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/numerical-summary.json
[attempts]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/attempts.json
[env]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/execution-environment.json
[savedenv]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/saved-environments.json
[spectra]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/independent-spectra.json
[solver]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/solver-diagnostic-verification.json
[counter]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/derivative-counterexample.json
[derivatives]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/ratio-conditioning-derivatives.json
[ratios]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/high-precision-recovery.json
[comparisons]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/recovery-comparisons.json
[early]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/early-failure-recheck.json
[precision]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/precision-convergence.json
[exact]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/exact-high-precision-classifications.json
[swaps]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/current-interventions.json
[effects]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/current-effect-decomposition.json
[interventions]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/input-interventions.json
[supports]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/support-comparisons.json
[field]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/independent-field-validation.json
[fine]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/independent-fine-design.json
[vectors]: ../results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e/all-current-forward-fields.json
