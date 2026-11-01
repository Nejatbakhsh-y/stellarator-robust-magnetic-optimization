# STEP 44 independent scientific acceptance

2026-11-01. **Scientific comparison FAIL; production acceptance FAIL; overall
scientific status PARTIAL.** Causal root cause INCONCLUSIVE; original artifact
authentication INCOMPLETE. The assessment adds executed evidence but does not
certify a research checkpoint. The new Python assessment and regressions are
prepared and **not executed**: the required existing `.venv` launcher exits 103
before Python startup. No successful test count is claimed.

## EXECUTION ENVIRONMENT

Work remained in this research checkout on
`codex/phase2d-upstream-attribution`. The existing Python environment was neither
replaced nor repaired. Its configured base interpreter is inaccessible here.
Managed .NET calculations executed on Windows NT 10.0.26300.0, AMD64,
CLR 4.0.30319.42000, Intel64 Family 6 Model 126 Stepping 5. Numerical-library,
BLAS/LAPACK and threadpool information from historical workers is preserved in
`saved-environments.json`; it is self-reported historical provenance, not a
new recreation of those workers. New QR uses managed scalar loops without
NumPy, SciPy, BLAS or LAPACK.

The user-confirmed scientific-validation run 41337449349 succeeded. This stage
does not reopen its resolved Linux CI/dependency investigation. That software
regression result does not establish numerical reproducibility, scientific
comparison acceptance or physical-model validation.

## SOURCE COMMIT

`cb4fd64da725fe35d8286f1f8842077d68e07bdb`.

Only the new Step 44 script, tests and this report were added to source. No
production code, prior report, workflow, original evidence, threshold or solver
setting was changed. Nothing was staged, committed, pushed, dispatched or merged;
PR #7 was untouched. `.venv/` remains ignored. GitHub CLI configuration was not
inspected or bypassed, as required by AGENTS.md.

## EVIDENCE INVENTORY

All paths below refer to actual local files. Let O be:

`results/phase2d/step44-independent-acceptance-20261101-135031-d0336767/local-assessment/`.

The Python command could not start. O's `status.json`, `evidence-manifest.json`,
`numerical-comparisons.json` and `acceptance-report.md` are an explicitly labelled
**PowerShell/.NET executed fallback assessment**, not outputs falsely attributed
to the Python program. Its command-attempt record retains exit 103. Final-source
hashes and execution logs distinguish implementation from executed calculation.

| Fresh local check | Executed observation |
|---|---|
| Supplied extracted/download and historical hash inventories | 3,599 entries, zero mismatches |
| Historical manifests | 58 inspected; four incomplete coverage maps; no listed-member hash mismatches |
| Original artifact directories | 46 present; original ZIP bytes unavailable |
| Captured source maps vs local Git blobs | 824 records, zero mismatches |
| Solver matrix/target reconstruction | 24 systems; zero maximum reconstruction differences |
| Saved reciprocal inputs | 32 cells, exact corresponding input-file SHA256 matches |
| Saved-current direct KKT | 96 candidate evaluations |
| Saved-current fine-grid recovery | 64 evaluations at both 60 and 90 fractional places |
| Nonself recovery comparisons | 48; 21 preceding failures and 11 latest failures |
| Earlier extracted failures | 22 scalar paths rechecked separately |
| New independent QR | 48 solves: eight captures Ã— three cases Ã— two row orders |
| Fresh QR field vectors | 96: eight captures Ã— three cases Ã— two orders Ã— two grids |

`integrity-before.json`, `integrity-after.json`, `historical-manifests.json`,
`archive-authentication.json`, `source-git-verification.json`,
`input-reconstruction.json`, `input-identities.json`,
`sealed-historical-comparisons.json` and `earlier-22-paths.json` retain identities.
The final manifest seals inputs and all diagnostic outputs except itself, avoiding
a circular digest. SHA256 establishes byte identity, not external authenticity.
Original numerical JSON is never overwritten. New scalar comparison seals and
QR current payloads retain exact little-endian binary64 hex; ordinary numeric
JSON values are convenient displays and must not replace the exact payloads.

## ORIGINAL ARTIFACT AUTHENTICATION

Fresh connected GitHub artifact API calls returned the following historical
inventories. All 46 ID/name/digest/size/date/expiration metadata records agree with
the supplied indexes. All are advertised unexpired at observation time.

| Run | Artifacts | Advertised source commit |
|---|---:|---|
| 41195815229 | 5 | ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 |
| 41231422708 | 7 | 11c2b1347c7b5359bec0a56e95cc2aa46f03660c |
| 41256776296 | 17 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 |
| 41257645149 | 17 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 |

The authenticated connector returned an original ZIP transfer reference for
artifact 13063239980. Transfer into this checkout was attempted and failed:
**Unable to connect to the remote server**. The advertised SHA256 is
`15ee0f5083d98f3445f3a96ba4400bbf5bd5dac7795664d1bd62effe2e18dfe1`;
there is no measured original archive SHA256. No replacement ZIP was generated.
Other downloads were not executed after that shared transport failure. None of
the 46 original ZIPs is locally authenticated. No expiration is inferred from
the transfer failure. Signed download URLs are not retained in the deliverable.

Metadata corroboration, original archive-byte authentication, extracted-file
hash verification and numerical reproducibility are four different results.
The prior run/workflow identity gap for 41256776296, earlier source discrepancies
and four incomplete manifests remain unresolved. Fresh artifact listings do not
close those gaps or attest runner execution. Evidence authentication remains
**INCOMPLETE**.

## INDEPENDENT SOLVER VERIFICATION

Fresh QR reuses the Step 42 Householder implementation and Step 40 fixed-point
KKT/recovery helpers. Reuse is explicit; this is a new execution of an existing
independently developed reference, not a newly invented third numerical method.
Helper files, their SHA256 and runtime information are in `qr-environment.json`.
It solves the exact captured binary64 M/y systems, with original and reversed
row order applied to both M and y. It never initializes from saved currents.
This reference accepts interior solutions only; it is not a general bounded TRF
replacement. All solutions here are inside the original box.

| Fresh QR observation | Value |
|---|---:|
| Maximum forward stationarity | 1.1108140766165024e-18 |
| Maximum QR-versus-captured physical current difference | 2.20001794559721e-12 A |
| Forward QR versus captured recovery failures | 6/16, all row 3 |
| Reversed versus forward QR recovery failures | 0/16 |
| Bitwise current disagreements with retained Step 42 repeat | 0 across 24 forward/reverse case pairs |

All fresh current components have authoritative binary64 payloads in
`fresh-qr.json`. `qr-comparisons.json` uses high-precision text and an integer
implementation of the original asymmetric comparison. These six QR failures are
a separate diagnostic inventory, not additional independent historical trials.
Reexecuting the same algorithm on the same host supports repeatability of that
reference only. It does not identify the historical SciPy floating-point kernel.

`recomputed-kkt.json` retains objective, feasibility, stationarity, active-bound
information and original status/iterations/termination/singular-value records
for all 96 saved candidates. The saved termination path is success, status 3,
nit=0, unconstrained solution optimal. It localizes the discrepancy to that
initial least-squares path rather than an observed iterative TRF bound transition.
`independent-spectra.json` contains fresh one-sided Jacobi column-orthogonalization
spectra, without forming a Gram matrix. The maximum condition estimate is
1.9467914804478437. Severe matrix ill-conditioning is not demonstrated here.
Tiny KKT residuals and objective differences do not certify the recovery ratio.

## FOUR-ENVIRONMENT COMPARISON

| Exact input origin â†’ execution platform | Saved reciprocal evidence | Fresh required SciPy execution |
|---|---|---|
| Windows â†’ Windows | Present in both reciprocal runs | MISSING_EVIDENCE; Python blocked |
| Windows â†’ Linux | Present in both reciprocal runs | MISSING_EVIDENCE; Linux worker unavailable |
| Linux â†’ Windows | Present in both reciprocal runs | MISSING_EVIDENCE; Python blocked |
| Linux â†’ Linux | Present in both reciprocal runs | MISSING_EVIDENCE; Linux worker unavailable |

The eight captured origins and 32 saved cells are actual files. Every cell's
input bytes match its specified capture; regenerated approximate inputs are not
substituted. New Windows QR calculations cover both origin types but do not fill
any missing SciPy matrix cell. No workflow was dispatched. Library/OS/hardware
causality requires matched controlled executions beyond the available evidence.

## INDEPENDENT MAGNETIC-FIELD VALIDATION

Fresh execution reuses the independently coded eight-point Gaussâ€“Legendre segment
quadrature and 60/90-fractional-place segment-integral references from Step 40/41.
It does not call production Biotâ€“Savart. Training has 240 points; fine grids have
960 points. Full unit-coil projected matrices and disturbance vectors were checked.
Bx, By, Bz and projections for new QR currents are in `fresh-qr-fields.json`.
The 96 saved-current training vectors are separately retained in
`all-current-forward-fields.json`; their calculations are not fresh optimization.

| Fresh independent field observation | Maximum absolute difference |
|---|---:|
| Training projected unit design | 1.9058241313221758e-21 T/A |
| Training projected disturbance | 7.589415207398531e-19 T |
| Fine projected unit design | 1.0852609636695723e-21 T/A |
| Fine projected disturbance | 1.2468324983583301e-18 T |
| Captured-current Cartesian field vs saved fields | 9.0801931945661e-19 T |
| 60/90-place reference difference after binary64 rounding at two training probes | 0 |

Direct current scaling at two points is retained in `linearity-check.json`.
Superposition is also used in full-field evaluations. High-precision Cartesian
reference coverage is two training points across all coils, not a full-grid
arbitrary-precision field certificate. Fine-grid quadrature remains binary64.
Quadrature estimates and precision repeats are not rigorous interval bounds.

`refinement-recheck.json` binds the original executed quick audit to result SHA256
`83162de245bfa5f64fad773f0c8212ccb04d2ae8af8287c03589fd8ee8374889`.
Recomputed last three orders are 1.999967421919967, 1.999991858540794 and
1.999997963518389. The historical configured 512-segment relative RMS change is
6.162644549068119e-5, below unchanged 1e-4. The 256-segment change is
2.465605004877691e-4 and remains a failure. This verifies consistency of actual
historically executed convergence evidence; a fresh full smooth-circle/refinement
audit was attempted through Python and blocked. Neither RMS convergence nor a
synthetic coil model establishes continuum peak convergence or confinement.

## FAULT ROW 3

Row 3 removes zero-based coil 3. There are **12 preceding** and **10 latest**
historical failing comparisons. Direct fine-grid high-precision evaluation at
saved currents retains those failures. For the latest Windows capture, R from
saved currents is -0.414688997080917109499289289654â€¦; fresh forward QR gives
-0.414688997065892692181324006934â€¦ and fails the unchanged ratio comparison.
Negative recovery is not described as an improvement.

The saved-RMS denominator is about 5.46649e-11 T; numerator cancellation factor
about 2.28635e6 and denominator factor about 9.48121e5. The local derivative
dR/dL is about +2.58793e10/T. An isolated one-ULP L intervention at fixed B/P
changes the ratio by about 8.76825e-11. This is an executed sensitivity control,
not evidence that the historical worker changed only L.

## FAULT ROW 4

Row 4 removes zero-based coil 6. There are **nine preceding** and **one latest**
historical failures. The latest Windows-origin/Linux-reference comparison remains
FAIL even though row 4 is less sensitive than row 3 in this example. For the
latest Windows capture, saved-current high-precision R is
0.167266248497502831671650167492â€¦; fresh forward QR gives
0.167266248497875657541817677264â€¦ and passes this particular comparison.

The saved-RMS denominator is about 5.22069e-10 T; numerator cancellation factor
about 5.93531e5 and denominator factor about 9.92769e4. The local derivative
dR/dL is about +1.59507e9/T. The corresponding isolated one-ULP L control changes
R by about 5.40429e-12. Both rows exceed the original 1e-15 T denominator guard.
Quotients of rounded saved RMS values differ from direct high-precision
field-to-R calculations; these two arithmetic pathways are labelled separately.

## RECOVERY-RATIO SENSITIVITY

For unchanged R=(L-P)/(L-B), independently applying the quotient rule yields

```
dR = [(P-B)dL - (L-B)dP + (L-P)dB] / (L-B)^2.
```

In B,L,P order, the derivatives are [(L-P)/(L-B)^2, (P-B)/(L-B)^2,
-1/(L-B)]. At (1,3,2), they are [+1/4,+1/4,-1/2]. Fresh PowerShell decimal
central differences independently check this example. New Python exact-rational
coefficient and finite-difference checks are implemented but unexecuted. The
historical wrong-sign diagnostic remains preserved and is not reused as truth.

`recomputed-recovery.json` repeats full fine-grid field/energy/square-root/ratio
evaluation at 60/90 fractional places for all 64 saved-current fault records.
`derivatives.json` separately computes exact-binary64 saved-RMS sensitivities.
`input-interventions.json` contains 48 matrix, disturbance and weight one-ULP
controls at fixed currents. Weight changes transfer mass algebraically; their
binary64 realization is not an exact sum-preservation certificate.
`support-comparisons.json` records 32 matching saved support-selection paths,
including deletion order, sparse selections and fault supports. No observed
support transition explains these contrasts. Sensitivity across arbitrary support
changes and fresh L1/minimax solver reruns remains unmeasured in this captured
fixed-support subset. Tiny solver residuals are not treated as error bounds on R.

## NUMERICAL ROOT-CAUSE ATTRIBUTION

Proven in the available subset: captured bytes arrive unchanged; mathematically
equivalent floating-point least-squares executions can differ in currents;
independent fields agree closely; cancellation amplifies the downstream ratio;
failures persist in high-precision field-to-ratio calculations before final
scalar rounding. New QR row reversal changes arithmetic but does not create a
failed ratio pair here. It therefore does not prove row order caused the
historical SciPy failures. Saved numerical-library/BLAS/interpreter/CPU-dispatch
differences remain confounded. No unique NumPy, SciPy, BLAS, LAPACK, OS or hardware
kernel has been isolated. **causal_root_cause=INCONCLUSIVE**.

## HISTORICAL FAILURE PRESERVATION

The 11 latest failures, 21 preceding failures, 22 earlier extracted scalar paths,
and six new QR-versus-capture failures are separate inventories. They are not
summed as independent experiments. Duplicate/nested scalar paths and repeated
inputs remain identified. Original refinement failures, failed archive transfers,
incomplete manifests and scratch calculation errors are retained. Final integrity
checks rehash original supplied inventories after work; no scientific records
were overwritten or relabelled PASS.

## TARGETED REGRESSION RESULTS

Attempted Step 44 plus Step 42 pytest: **BLOCKED, exit 103 before startup**.
New tests cover analytical recovery, correct signs, independent finite differences,
the exact denominator guard and tolerance boundary, cancellation, nonfinite data,
missing/corrupt evidence, incorrect hashes, incomplete manifests, unsupported
authentication, incorrect input/source identities, objective/KKT inconsistencies,
false scientific PASS, retained failures, report completeness and repeatability.
They are implementation coverage, not passing test evidence.

## COMPLETE REGRESSION RESULTS

Complete pytest, compilation, Step 44 command, sealed SciPy replay, analytical
validation, quick experiment, output checks, independent audit, README recording,
full reproducibility and physics/refinement tests were attempted. All 12 attempts
exit 103 before Python startup. Fixed-path README writes were isolated in a source
copy under O. `python-attempts.json` and per-command logs retain actual arguments,
working directories, return codes and hashes. Final-source targeted/compilation
attempts are separately retained. Git whitespace verification passes; new files
are also explicitly checked because ordinary `git diff --check` excludes untracked
files. Passing whitespace checks is not scientific or regression acceptance.

## SCIENTIFIC COMPARISON STATUS

**FAIL.** All original tolerance limits remain unchanged: rtol=1e-11,
atol=1e-13, refinement=1e-4, recovery denominator guard=1e-15 T.

## PRODUCTION ACCEPTANCE

**FAIL.** Software success does not replace the missing numerical acceptance
matrix, final-source validation or authenticated original evidence.

## OVERALL SCIENTIFIC STATUS

**PARTIAL.** Synthetic finite-scenario minimax and small holdouts do not establish
general robust outperformance, experimental stellarator confinement, or device
validation.

## REMAINING BLOCKERS

- Execute the prepared final Python source and all required gates in the existing
  working host environment; bind passing records to actual fresh result SHA256.
- Acquire and hash original historical archives, verify complete extraction and
  resolve manifest/source/workflow gaps. Metadata alone cannot discharge this.
- Complete the exact-input fresh SciPy reciprocal Windows/Linux matrix with
  matching source/input identities and complete solver/environment records.
- Resolve the upstream numerical cause through controlled interventions; neither
  tiny current/KKT differences nor downstream sensitivity alone proves it.
- Preserve historical FAIL even if a new reference algorithm or software test
  passes. Physical-model validation remains a separate research requirement.

Host commands (no publication or workflow dispatch) use fresh output names:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step44_acceptance.py tests/test_phase2d_step42_replay.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts tests
.\.venv\Scripts\python.exe scripts/phase2d_step44_acceptance.py --root $PWD --output results/phase2d/step44-host-independent-assessment
git diff --check
```

The Python assessment refuses existing/overlapping output. It returns 1 for
completed scientific FAIL/PARTIAL with sufficient mandatory inputs, 2 for missing indispensable input, corrupt input or
execution failure, and produces status records in either case when the output
path is valid. This fixed historical protocol cannot produce exit 0 because its
mandatory historical failures and authentication gaps remain unresolved. It has
no option that converts pytest or fresh QR agreement into scientific PASS.


## STEP 44 host exit-code-2 execution repair (2026-11-01)

This section supersedes the earlier execution description for the repaired Python
entry point. The supplied Windows host reports 42 targeted tests, 710 complete
regression tests and dependency verification passing before the repair. Those
records do not verify this changed source. No hosted execution was dispatched.

The actual failed attempt is
`results/phase2d/step44-permanent-repair-20261101-144005-acca0b03/assessment-1`.
Both adjacent stdout/stderr logs are zero bytes. Its status.json and
numerical-comparisons.json exist and identify two caught errors:
`Comparison scalar differs from original result`, then
`Incomplete comparison identity`. Thus the host did execute Python 3.11.9 and
reach numerical replay; exit 2 was not a Python launch or CLI failure.

The first error comes from strict STEP41 binding of the derived
recomputed-comparisons.json inventory. In run 41256776296, origin
linux-numpy-sensitivity, worker linux-reference, row3, that inventory records
candidate `-0.41468899703150891`; the original SHA-bound result in artifact
13063273167 records `-0.4146889970315089`. Additional cells contain the same
serialization pair. The two literals parse as adjacent binary64 values, so exact
scalar identity correctly rejects the derived transcription. STEP41 used
PowerShell/.NET to generate that inventory. The downstream identity error is a
cascade: the failed assignment leaves historical_comparisons absent, and saved
RMS validation receives an empty list. These are category A evidence-adapter
implementation errors, not evidence that the original result archive is corrupt.

The STEP44 adapter now recognizes only this exact observed row3 scalar pair,
reads the scalar from the original result, and records every correction under
`derived_inventory_serialization_corrections`. It then invokes the unchanged
strict STEP41 binder. Original result/input SHA256, unique complete comparison
identities, retained and reconstructed classifications remain mandatory. Every
other scalar discrepancy remains an error, including discrepancies smaller than
the scientific tolerance. Historical files are untouched. This corrects a
derived transcription; it does not relax numerical acceptance or change any
historical failure to PASS.

Missing indispensable historical inputs or required numerical execution now
remain exit 2, with exact error records. Missing authenticated archive bytes,
reciprocal platform execution and other explicitly unresolved acceptance evidence
remain limitations of a completed PARTIAL assessment (exit 1) when its required
local inputs validate. New output paths work even when results/phase2d does not
yet exist; existing or overlapping evidence paths remain rejected. Diagnostics
and correction records remain beneath the requested new output directory.

Regression additions cover the actual repository failure and its 48-cell binding,
21 preceding and 11 latest failures, arbitrary scalar corruption, wrong result
hashes, missing indispensable inputs, malformed JSON and an invalid root. Existing
PARTIAL/report and output-isolation assertions are preserved. No production
numerical code, field equations, objectives, solver settings, supports, tolerances,
recovery formula or derivative were changed. The 22 earlier failures remain FAIL;
causal attribution remains INCONCLUSIVE; archive authentication INCOMPLETE;
scientific comparison and production acceptance FAIL; scientific status PARTIAL.

Local `.venv/Scripts/python.exe --version` was attempted in this restricted Codex
environment and failed before startup because its configured Python311 base
executable is unavailable here. Repaired tests and full assessments were therefore
NOT EXECUTED here. This does not contradict the functioning external Windows host.
No permanent resolution or verified research checkpoint is claimed. The external
host must run the targeted/full regressions and the command below into a fresh
path, inspect errors/corrections and verify all required README gates before a
checkpoint can be claimed verified.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step44_acceptance.py
.\.venv\Scripts\python.exe -m pytest -q
$out = Join-Path $PWD ('results/phase2d/step44-repaired-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe scripts/phase2d_step44_acceptance.py --root $PWD --output $out
$assessmentExit = $LASTEXITCODE
Get-Content (Join-Path $out 'status.json')
Get-Content (Join-Path $out 'numerical-comparisons.json')
Write-Output "Assessment exit: $assessmentExit"
```

Expected completed verdict is exit 1 only if all indispensable local inputs and
required execution validate. Any remaining such error must still return 2.

## Evidence-binding correction: exact host defect (2026-11-01)

This section supersedes the earlier single-pair diagnosis and repair claim.
The first *decimal token* difference is preceding run 41256776296,
linux-numpy-sensitivity origin, linux-reference worker, row3: inventory
-0.41468899703150891 versus original -0.4146889970315089. Their decimal
values differ by +1e-17 (saved minus inventory), but Python's correctly rounded
binary64 representations agree. This was not the remaining strict-binding failure.

The actual binary64 defect is latest run 41257645149, windows-reference origin,
linux-reference worker, row3, candidate. Original scalar token:
`-0.41468899707880597`; STEP41 inventory / old STEP44 normalized token:
`-0.414688997078806`. The original result is:
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/github-hosted/41257645149/artifact-13064155046/windows-reference/result.json`.
Measured result SHA256 agrees with the comparison seal:
`f3e6b62a40ab48eacae8f8b06ab00502043e8197e0b7ccf711f9d29caf4ba1d4`.
Associated inputs SHA256 agrees with the comparison seal:
`90a86ac4e944f6c0805c375df9dab6beae800d3be1a68d9e28d6b655bd5a544b`.
The comparison inventory measured SHA256 is
`3847225855df15864ef0a4668b15f0684b1b25847e7c0d4bc71fd9e117fac719`.
These authenticate local retained byte identity, not original archive bytes.

Exact reproduction executed in Windows PowerShell:

```powershell
$v = ('{"x":-0.41468899707880597}' | ConvertFrom-Json).x
$v.GetType().FullName # System.Decimal
([double]$v).ToString('G17') # -0.41468899707880602
[double]::Parse('-0.41468899707880597', [cultureinfo]::InvariantCulture).ToString('G17')
# -0.41468899707880597
```

The Decimal-to-Double path changes the value by one binary64 ULP; this is
not merely two textual spellings of the same binary64. The inventory's shorter
token parses to that changed value. Exact decimal-token difference (saved minus
inventory) is `3e-17`; exact binary64 difference is
`0.000000000000000055511151231257827021181583404541015625` = 2^-54.
Bit patterns interpreted as signed Int64 are -4622230044085994866 (derived)
and -4622230044085994867 (saved). The defect is conversion/serialization in a
derived inventory, not an incorrect artifact, cohort, result field or solver
selection. No rounding of an original result is authorized.

Reference inventory token is -0.41468899708091722 (saved token
-0.4146889970809172, the same correctly rounded binary64). The stated PASS is
consistent: the candidate/reference difference is about 2.1112e-12, below
atol + rtol*abs(reference), about 4.2469e-12, for both retained and saved values.
The high-precision comparison also states PASS. This cell was never one of the
11 latest failures. The earlier diagnosis incorrectly described the first
representational pair as adjacent binary64 numbers.

STEP44 now constructs a separate source-bound comparison only for the precise
observed binary64 defect, requiring the pinned original inventory, unchanged
historical row, exact identity and original result/input seals. It records every
historical token representation difference, preserving the retained record,
tokens, exact Decimal differences, binary64 hex, equality flag, conversion method,
source paths and hashes, and reason. The records are reversible: retained_record
contains the complete original comparison. Unequal values are explicitly marked
binary64_equal=false; they are never declared equal. Independent comparison
classification is checked again by unchanged STEP41 against original saved bytes.
Every other binary64 mismatch remains an execution/input failure. This correction
establishes provenance of the adapter defect, not upstream numerical causality.

Regression coverage retains the real historical failing test and requires the
actual one-ULP defect, correct original hashes and unchanged 21/11 failures. Added
adversaries cover candidate/reference identity, swaps, cohort, duplicate/missing
records, nonfinite values, genuine disagreement, false PASS, modified result bytes
and modified inventory bytes. Original decimal-token and binary64 distinctions
are asserted separately.

All three requested commands were attempted again after editing using the existing
.venv: targeted pytest, full pytest and compileall. Each failed before Python
startup: configured Python311 base executable unavailable. No Python regression
pass, reproduced Python traceback, or verified checkpoint is claimed here. The
supplied host failure remains the Python regression evidence; the PowerShell
conversion reproduction and local SHA256 checks above executed successfully.
The host must independently execute the final tests and full scientific gates.

The latest 11 failures, preceding 21 failures and earlier 22 scalar failure paths
remain separate. Scientific comparison FAIL; production acceptance FAIL; overall
PARTIAL; numerical causality INCONCLUSIVE; original archive authentication
INCOMPLETE. Equations, objectives, solver/current settings and all numerical
limits remain unchanged. No historical evidence or STEP41 source was edited.
