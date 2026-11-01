# STEP 41 final independent scientific acceptance assessment

2026-11-01. **Scientific comparison FAIL; production acceptance FAIL; scientific
status PARTIAL; upstream causal root cause INCONCLUSIVE; evidence authentication
INCOMPLETE.** Diagnostic execution is INCOMPLETE because the required existing
Python environment cannot start. This is not a verified research checkpoint.

**1. Executive verdict.** Fresh independent arithmetic reproduces all eleven
latest historical recovery failures and all 21 failures in the preceding replay
run. All 32 failures also persist in independently recomputed 90-place recovery
ratios. Successful current comparisons, field checks and small KKT residuals do
not discharge the failed ratio criterion. No historical failure is relabelled.
The evidence supports the failure classifications below, not production acceptance.

**2. Scope and repository boundaries.** AGENTS.md, README, execution/refinement
status, the complete STEP 38, 39 and 40 reports, their diagnostic implementations
and regression coverage, historical Phase 2D assessments, and relevant capture,
solver, field and factored recovery implementations were reviewed. Work stayed
in this research checkout on feature branch `codex/phase2d-upstream-attribution`.
HEAD matches supplied SOURCE_COMMIT
`57d7652db63a81240f4234a9752b06888b471e72`. The only new deliverables outside
the authorized output directory are this report, `scripts/phase2d_step41_acceptance.py`
and `tests/test_phase2d_step41_acceptance.py`. No production source, old test,
report, workflow or historical numerical record was changed. Nothing was staged,
committed, pushed, merged or dispatched. GitHub CLI configuration was not inspected.

Let O denote
`results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/`.
All fresh evidence is beneath O. E denotes the STEP 38 evidence directory
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/`.
STEP 39 and 40 input roots are the paths recorded in the CLI command below.

**3. Evidence provenance and independence.** Fresh PowerShell/.NET execution
rehashes original inputs and outputs and decodes their binary64 payloads. Fresh
numerical calculations use retained independent C# helpers copied from STEP 40,
explicitly identified by O's manifest and helper source hashes. Reusing those
independent helpers is not a third newly designed arithmetic implementation or
a fresh SciPy solve. No production numerical helper is called by those checks.
The new Python acceptance wrapper additionally performs exact-rational quotient
coefficient extraction and comparison classification, strict STEP 38 transport
validation and optional STEP 40 numerical recomputation. **That Python wrapper
and its regression tests have not executed.** Results below come from the
separately executed PowerShell/.NET checks, not the blocked Python CLI.

**4. Source/input authentication.** Fresh [integrity checks][integrity] rehash
3,599 download/historical inventory entries with zero mismatches, and 558 listed
STEP 39/40 manifest members with zero mismatches. Fresh [Git source checks][sources]
match 824 source-path/cohort records to bytes read from local Git blobs for the
two later runs. This does not extend to full source-map verification of the
two earlier runs or prove what code actually executed on hosted hardware.
Fresh [historical manifest checks][history] find 58 manifests, four with incomplete
coverage and zero listed-member hash mismatches. Those four early manifests
remain failed completeness checks; they were not repaired. Exact-byte seals
are stronger than approximate numerical agreement for transport, but do not
authenticate the supplier of a hash list. Strict Python canonical problem-seal
and complete semantic validator execution remains missing, not implicitly passed.

**5. Mathematical verification.** For N=L-P and D=L-B, dN=dL-dP and dD=dL-dB.
Coefficient-wise quotient differentiation gives

```
dR = [D(dL-dP) - N(dL-dB)] / D²
   = [(P-B)dL - (L-B)dP + (L-P)dB] / (L-B)².
```

Thus in B,L,P order the gradient is
`[(L-P)/(L-B)², (P-B)/(L-B)², -1/(L-B)]`.
At B=1,L=3,P=2 it is exactly `[1/4,1/4,-1/2]`.
Fresh [90-place central differences][math] cover that case, (0,2,3), (-2,-5,1),
and a nonsingular row3-scale case; signs agree for every coordinate. Fresh
[saved-triple derivatives][derivatives] cover all 64 saved fault triples.
The step is `abs(L-B)*1e-15`; finite-step error is expected, not set to zero.
The new Python implementation independently checks exact rational quotient
coefficients and rational central differences, with 60/90-significant-digit
Decimal regressions; those runtime checks are blocked. No symbolic algebra
package execution is claimed; the symbolic identity above is explicit algebra.
The original denominator guard `abs(L-B)>1e-15 T` is preserved.

**6. Historical derivative correction and consequences.** The demonstrable wrong
implementation is the retained STEP 39 output
`initial-wrong-requested-dL-sign.json`: all 64 dL derivatives are negative where
the corrected derivatives are positive. Its SHA256 is
`cb2b9bf9c0d5a76fbe71434d6d1173e110897626a87c8b0ac046c9934ecc59d0`.
It implements the incorrect B-P coefficient. The corrected historical output
`recovery-sensitivity.json` has SHA256
`02d602550a8172b806920e050c3c1df09c435861e471ad596126a994790aa067`.
Both remain untouched. STEP 39's final report explicitly rejects B-P, STEP 40
also uses P-B, and STEP 38's `(1-R)/(L-B)` dL expression is equivalent to P-B.
They are not incorrectly accused of retaining the erroneous final formula.

Fresh [paired consequences][sign] establish that all 64 derivative magnitudes,
saved ratios, independently evaluated binary64 ratios and denominator condition
factors are unchanged between those two STEP 39 records. The initial signed L
response was therefore wrong and reverses direction; magnitude-only sensitivity
and cancellation statements survive. Historical directly computed recovery
comparisons are unaffected by this derivative correction. No evidence shows
that this diagnostic sign error caused the worker-current differences. No
production derivative or metric was patched.

**7. Solver-input reproducibility.** Fresh [reciprocal input checks][inputs]
establish 32/32 replay input-file SHA256 matches to the corresponding capture.
Full input bytes include geometry, M/y, weights, current bounds, support,
regularization, saved currents and internal initialization arrays. Captured
origins are distinct inputs, not interchangeable references. Fresh
[reconstruction][reconstruction] obtains zero maximum differences for D, d,
M and y in all eight captures and all 24 dense/row3/row4 systems.

The problem is `0.5*||Mx-y||²`, normalized currents x=I/3000, bounds [-1,1],
D=A*3000/0.001, d=b/0.001, and augmented ridge 1e-6.
`M=[sqrt(w)*D_S; sqrt(1e-6)*I]`, `y=[-sqrt(w)*d;0]`.
Weights are retained, not renormalized. `lsq_linear` uses TRF, implicit exact
least squares, tol=1e-12 and max_iter=1000. It has no user x0 argument; the saved
unconstrained solution describes internal initialization. A byte-bound saved
initialization is not evidence of independently rerunning that initialization.
Complete SLSQP/minimax initial states and constraints are outside this subset.

**8. Four-environment assessment.** Both later runs retain all four origins on
all four workers, including A Windows inputs/Windows, B Windows inputs/Linux,
C Linux inputs/Windows and D Linux inputs/Linux. Fresh STEP 41 SciPy execution
for **every A/B/C/D cell is NOT EXECUTED**. Windows execution is blocked by the
existing environment; no Linux runtime/host experiment was performed. Recalculating
saved vectors on this host does not recreate the hosted solver environments.

[Environment records][env] retain original environment-file SHA256 values and
saved self-reports: Windows Python 3.11.9 versus Linux 3.11.17; reference NumPy
2.4.6/SciPy 1.17.1; sensitivity NumPy 2.3.5 or SciPy 1.16.3. Bundled OpenBLAS
versions and Haswell/SkylakeX dispatch differ; saved pools report one thread.
These are confounded cohorts, not a controlled isolation of OS, NumPy, SciPy,
BLAS/LAPACK or dispatch. Hardware self-report is not hardware attestation.

**9. Independent magnetic-field validation.** Fresh independent eight-point
Gauss-Legendre integration evaluates all Cartesian components on the 240-point
training grid, all 25 polygons and all 96 saved optimized-current vectors.
Fresh 960-point fine-grid projected evaluations also complete. Maximum errors:

| Comparison | Maximum absolute error |
|---|---:|
| Training projected unit-coil A | 1.9058241313221758e-21 T/A |
| Training projected disturbance b | 7.589415207398531e-19 T |
| Fine projected unit-coil A | 1.0852609636695723e-21 T/A |
| Fine projected disturbance b | 1.2468324983583301e-18 T |
| Captured-current Bxyz versus saved fields | 9.0801931945661e-19 T |
| Disturbance Bxyz versus saved fields | 7.8604657505199071e-19 T |

[Full field evidence][fields] preserves independent matrices and Bxyz vectors.
Independent 60/90-fractional-place segment references at training indices 0/80
cover every coil and disturbance; unit-coil references round identically.
Largest quadrature/probe errors are 2.4352197233561135e-21 T/A and
4.87890977618477e-19 T. High precision geometry is limited to those probes.
Fresh [fixed-field checks][fixed] find 192/192 nonself component payloads with
identical shapes and exact binary64 bytes. These checks distinguish fixed-current
field reproducibility, approximate optimized-current agreement and failed ratio
reproducibility. Full-grid arbitrary-precision geometry and the mandatory fresh
quick smooth-circle/refinement audit remain unexecuted.

**10. KKT and conditioning.** Fresh [spectra][spectra] use one-sided Jacobi column
orthogonalization on M, not Gram eigenvalues. Conditions range from
1.9467914804478383 to 1.9467914804478437; effective ranks are dense 24 and faults
23 with dimension-scaled binary64 epsilon cutoff. Representative largest and
smallest singular values are approximately 0.06982620792852 and 0.03586732766699.
These results do not support severe matrix ill-conditioning or nonuniqueness.

Fresh [96 direct residual certificates][kkt] yield maximum stationarity
2.1773934378973348e-18 and zero primal violation. No bounds are active. Inferred
interior dual multipliers and complementarity are zero; their zeros alone do
not prove optimality. The existing KKT diagnostic gate is 1e-12. Fresh inspection
of all 96 saved termination records finds success=true, status=3, nit=0; maximum
saved optimality is 2.1700355451389634e-18 and maximum direct objective discrepancy
is 6e-19. No fresh solver termination is invented. [Termination summary][termination].
All 32 saved support signatures agree within origin; no active-set change is
observed. These observations cannot rule out transitions in other problems.

**11. Fault row 3.** FAIL: ten latest and twelve preceding comparisons.
For latest Windows/Windows, L-B≈5.466485340356966e-11 T and
L-P≈-2.266891323499066e-11 T. Denominator/numerator cancellation factors are
about 948121/2286346; dR/dL≈2.587931566676031e10/T. The negative recovery ratio
is not a recovery benefit. Fresh full fine-grid 90-place R is
`-0.4146889970809171094992892896548706787…`, reproducing STEP 40.
The result SHA256 is
`abfc4d126b001d135c49b9009f9abd1366cd67f2b9260957c6c9cdd368395537`.
[Recovery evidence][ratios]. Cancellation in rounded RMS subtraction must not
be confused with a defect demonstrated in the factored production metric.

**12. Fault row 4.** FAIL: one latest and nine preceding comparisons.
For that same representative result, L-B≈5.220686710494032e-10 T,
L-P≈8.732446806741898e-11 T, cancellation factors≈99277/593531 and
dR/dL≈1.595065549179688e9/T. Fresh full fine-grid 90-place R is
`0.1672662484975028316716501674920593179…`. Both rows' denominators exceed
the unchanged guard. Neither is regularized or relabelled. [Derivatives][derivatives],
[recovery evidence][ratios].

**13. All outstanding historical failures.** W=Windows reference, L=Linux
reference, N=Linux NumPy sensitivity, S=Linux SciPy sensitivity. Fresh 90-place
candidate-minus-Windows-reference differences for all eleven latest failures:

| Origin | Worker | Row | Delta R | Result |
|---|---|---:|---:|---|
| W | L | 4 | -2.717251278971e-12 | FAIL |
| W | N | 3 | 3.161582080683e-11 | FAIL |
| W | S | 3 | 3.161582080683e-11 | FAIL |
| L | N | 3 | 3.158395253375e-11 | FAIL |
| L | S | 3 | 3.158395253375e-11 | FAIL |
| N | L | 3 | 1.109018376310e-11 | FAIL |
| N | N | 3 | 3.555492297367e-11 | FAIL |
| N | S | 3 | 3.555492297367e-11 | FAIL |
| S | L | 3 | 1.109018376310e-11 | FAIL |
| S | N | 3 | 3.555492297367e-11 | FAIL |
| S | S | 3 | 3.555492297367e-11 | FAIL |

[All 48 comparisons][comparisons] retain scalars, both original result-file
SHA256 identifiers, input SHA256 and exact high-precision classifications.
Run 41256776296 retains its separate 21 failures (12 row3, nine row4).
Fresh [early failure checks][early] reclassify all 22 earlier extracted scalar
paths: 16 from 41195815229 and six from 41231422708, all FAIL, with zero original
comparison-file hash mismatches. This is not a fresh exhaustive extraction of
those earlier JSON documents. Duplicated paths/files or N/S origins are not
independent physical experiments. The original 256-segment refinement failure
and its diagnosis also remain; the 1e-4 acceptance limit was not relaxed.

**14. Demonstrated numerical causes.** The B-P diagnostic sign is conclusively
an algebraic error. Small denominators and cancellation amplify RMS perturbations,
as the derivative identity and finite differences demonstrate. Fresh deterministic
fine-grid evaluations holding each origin's A,b,w fixed reproduce the differences
from its workers' differing saved currents. All 64 90-place texts match STEP 40;
the failed comparisons survive exact-integer tolerance evaluation. Final scalar
ratio rounding alone therefore cannot explain the historical failures.
STEP 40's hash-checked current-swap controls support that immediate pathway;
STEP 41 does not present those old individual swaps as newly executed optimizer
experiments. Fresh 48 fixed-current one-ULP input evaluations are in O; they
are coordinate probes, not global sensitivity bounds or optimizer reruns.

**15. Unresolved causal hypotheses.** The specific upstream floating-point
kernel, least-squares initialization/driver, BLAS/LAPACK build, NumPy/SciPy version,
interpreter patch, OS and dispatch remain INCONCLUSIVE. Fixed-input replay
localizes differences to numerical solution generation before recovery evaluation;
it does not isolate which of these confounded factors causes them. Independent
field agreement does not justify assigning all error to the solver, because
cross-origin input generation also differs. No new production defect or justified
production patch has been demonstrated.

**16. Missing original evidence.** Zero original ZIP files were found in E;
46 extracted indexed artifacts cannot authenticate missing archive bytes.
The saved workflow-identity gap for run 41256776296, earlier source/head
inconsistencies and four incomplete early manifests remain. No new remote
authentication was attempted. Original GitHub archive authentication is
MISSING_EVIDENCE, not VERIFIED merely because extracted-file hashes agree.

**17. Quantitative acceptance classifications.**

| Question | Classification | Evidence/limit |
|---|---|---|
| Correct quotient derivative | VERIFIED | Explicit coefficient algebra; fresh 90-place differences |
| Local inventory/source consistency | VERIFIED | 3599 and 824 fresh matches; not hosted attestation |
| Saved reciprocal input byte identity | VERIFIED | 32/32 within origin |
| Fixed-current fields | REPRODUCED | 192 identical saved payloads; independent field checks |
| Current tolerance agreement | REPRODUCED | 72/72 nonself vectors pass; max 2.8279600883251987e-12 A |
| Latest/preceding recovery criterion | FAILED | 11/21 failures retained at high precision |
| Earlier scalar-path criterion | FAILED | 22/22 extracted paths still fail |
| Fresh four-way solver causality | INCONCLUSIVE | No new SciPy/host-controlled cells |
| Original archives/final Python gates | MISSING_EVIDENCE | No archives; interpreter fails before startup |
| Production scientific acceptance | FAILED | Applicable requirements unresolved |

All comparisons retain `rtol=1e-11`, `atol=1e-13`, refinement limit `1e-4` and
512-segment quick geometry. No equations, objectives, bounds, constraints,
solver settings or acceptance criteria were changed.

**18. Regression and execution results.** [Attempts][attempts] record twelve
commands: targeted STEP 41 pytest, complete pytest, compilation, analytical CLI,
quick experiment, output checks, independent audit, physics/refinement tests,
Phase 2C production verification, STEP 41 CLI, README test_and_record and full
reproduce_check. **All exit 103 before Python startup: zero Python tests execute.**
The .venv launcher cannot locate its configured Python311 base executable.
No alternative interpreter, dependency installation or environment replacement
was used. Fixed-path README commands were attempted only in O/validation-copy.

The new tests cover all twenty requested categories: derivative signs, finite
differences, high precision, denominator guard, missing records, corrupt hashes,
duplicate manifests, invalid numbers, singularity, conditioning, KKT, feasibility,
optimality, active-set change, inconsistent comparisons, missing artifacts,
unsupported causality, unsupported PASS, historical failures and repeatability.
Additional tests exercise exact input identity, output containment and analytical
square-loop fields. They remain runtime-unverified; no pytest pass count is claimed.

Fresh .NET arithmetic, source/input/historical checks and field evaluations
completed as recorded above. A separate repeated .NET recheck is retained under
O/independent-repeat: all 64 recovery texts agree exactly at both 60 and 90
fractional places, with zero differences. `repeated-summary.json` records this;
Python deterministic execution remains untested. Initial
copied field/source helper execution failed on read-only PowerShell `$Error`;
the copied command was corrected to `$errorVertices`. Two initial fixed-field
command strings failed parsing; a multiline corrected command completed.
Failure notes are preserved. No machine execution-policy setting was changed.
Git whitespace checks and `git fsck --full --no-reflogs` succeed; staging remains
empty and .venv remains ignored. Final preservation and source hashes are in O.

**19. Production acceptance decision.** `production_acceptance=FAIL`.
Passing numerical subsets or future pytest success cannot override failed
scientific comparisons, absent archive authentication and missing final-source
result-SHA-bound gates. The machine-readable [acceptance.json][acceptance] was
written by the executed PowerShell assessment because Python cannot start;
it is not misrepresented as successful execution of the Python implementation.

**20. Final scientific status.** `scientific_status=PARTIAL`,
`scientific_comparison=FAIL`, `causal_root_cause=INCONCLUSIVE`,
`evidence_authentication=INCOMPLETE`, `diagnostic_status=INCOMPLETE`.
Finite-scenario minimax with eight training and 24 holdout scenarios does not
establish general robust outperformance. No confinement, equilibrium, continuum
peak-field or device validation is claimed.

**21. Remaining work.** Restore the existing environment externally and execute
the final source's focused/full regression, compilation and complete README
analytical/quick/output/independent-refinement/full-repeat gates with passing
records bound to exact result SHA256. Execute strict canonical semantic seals
and complete numerical validation; retain their expected failures. Acquire and
authenticate original archive bytes and resolve manifest/workflow/source gaps.
Run fresh reciprocal production solves with identical serialized inputs,
matched interpreter/BLAS/dispatch and one-factor controls; retain currents,
initialization, objectives, feasibility, KKT, singular values, support, termination,
fields and recovery metrics. Resolve new comparisons under the unchanged gates
while preserving every historical FAIL. Broader minimax/holdout, full-grid
arbitrary-precision geometry and physical validation remain separate extensions.

After restoration, independent repeated Python execution uses explicit inputs
and a fresh child output directory (substitute another fresh child for repeats):

```powershell
$O = Join-Path $PWD 'results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c'
$env:PYTHONPYCACHEPREFIX = Join-Path $O 'pycache-fresh'
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step41_acceptance.py -p no:cacheprovider --basetemp "$O/tests-fresh"
.\.venv\Scripts\python.exe scripts/phase2d_step41_acceptance.py --evidence results/phase2d/step38-independent-verification-20261101-084216-7bda80b7 --step39 results/phase2d/step39-independent-attribution-20261101-095118-07af8f3a --step40 results/phase2d/step40-controlled-validation-20261101-102305-2ce5ec9e --output-root $O --output "$O/python-repeat-fresh"
```

The CLI refuses existing output directories and emits sorted deterministic JSON.
`--records-only` explicitly leaves diagnostics INCOMPLETE. The full numerical
path reuses the identified independent STEP 40 backend and runs no fresh
production solver. It does not discharge the four-host causal experiment.

[integrity]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/integrity-summary.json
[sources]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/source-git-verification.json
[history]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/historical-manifests.json
[math]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/mathematical-validation.json
[derivatives]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/derivatives.json
[sign]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/sign-consequences.json
[inputs]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/reciprocal-inputs.json
[reconstruction]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/input-reconstruction.json
[env]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/saved-environments.json
[fields]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/all-current-forward-fields.json
[fixed]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/fixed-field-checks.json
[spectra]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/independent-spectra.json
[kkt]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/recomputed-kkt.json
[termination]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/termination-summary.json
[ratios]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/recomputed-recovery.json
[comparisons]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/recomputed-comparisons.json
[early]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/early-failures.json
[attempts]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/attempts.json
[acceptance]: ../results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/acceptance.json
