# STEP 42 reproducibility closure and hosted solver attribution

2026-11-01. **Implementation prepared; independent numerical experiments executed;
fresh SciPy replay NOT EXECUTED. Scientific comparison FAIL; production acceptance
FAIL; causal root cause INCONCLUSIVE; scientific status PARTIAL.** No verified
research checkpoint or successful hosted execution is claimed.

## Scope and provenance

Repository: `C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization`.
SOURCE_COMMIT: `c37f695c0c772cf14bcb508fb60484d66482f157`.
Feature branch: `codex/phase2d-upstream-attribution`.
O = `results/phase2d/step42-reproducibility-20261101-120046-d90ebceb`.
E = `results/phase2d/step38-independent-verification-20261101-084216-7bda80b7`.
All generated local evidence is below O. AGENTS.md, README, execution/refinement
status, STEP 38–41 reports and their transport, numerical and acceptance
implementations/tests, the captured input schemas, production capture/solver
definitions and existing attribution workflows were inspected.

Only the STEP42 replay, its tests, this report and the authorized upstream
workflow are changed outside O. Production modules, historical numerical files,
earlier reports and other workflows remain untouched. No staging, commit, push,
merge, dispatch, default-branch change or GitHub CLI configuration access occurred.
The existing environment was preserved, and `.venv/` remains ignored.

## Execution-environment diagnosis

The previous reports' statement that Python could not start applies to the
**Codex process**, not to the functioning Windows host reported by the user.
The explicit `.venv/Scripts/python.exe -V` attempt emits
`No Python at '"C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe'`
and exits 103. `.venv/pyvenv.cfg` points to that base interpreter and records
Python 3.11.9. An explicit filesystem probe of that base path returns **Access is
denied** in this restricted execution environment. Therefore the launcher message
does not establish that the host installation is absent or broken. The available
evidence establishes an access boundary; distinguishing every underlying launcher
failure condition would require access unavailable to this process.

| Environment | Evidence and status |
|---|---|
| Actual Windows host | User reports successful regression, compilation and STEP38–41 validation; not newly observed here |
| Codex Windows process | Explicit existing interpreter blocked before startup; base-path access denied; zero Python tests executed |
| GitHub Windows | Historical environment records; new STEP42 execution NOT EXECUTED |
| GitHub Linux | Historical reference and sensitivity records; new STEP42 execution NOT EXECUTED |

No base installation, venv configuration, launcher or package was replaced, and no
alternative Python or execution-policy change was used. Model changes cannot repair
this access boundary. Host validation remains necessary, without implying that the
working host environment itself needs repair.

## Implemented fresh SciPy replay

`scripts/phase2d_step42_replay.py` accepts explicit capture/evidence and fresh output
paths and requires `STEP42_OUTPUT_ROOT`. It refuses overlapping inputs/outputs or
existing outputs. Sorted, finite-only JSON and result SHA256 manifests give each
new experiment an independent identity. Source fingerprints are compared against
local Git blob bytes at the captured commit; full input-file and canonical problem
seals are checked. STEP38's strict JSON/binary64 transport and STEP40's complete
schema/config/support reconstruction validators are explicitly reused. They are
not presented as newly designed independent validators.

The new code additionally requires exact reconstructed M/y equality, then solves
the **captured binary64 M/y**, not regenerated approximate replacements. Missing
matrices, corrupt seals, nonfinite inputs, changed settings, invalid supports,
invalid current scales and non-512-segment quick configurations are rejected.
TRF, exact least-squares solver, bounds [-1,1], tolerance 1e-12 and maximum 1000
iterations are explicit. No x0 is passed. Saved currents never initialize a solve.

Each solve records normalized and physical currents, including binary64 payloads,
support, M/y binary64 byte
SHA256, objective/cost consistency, direct 90-significant-digit Decimal objective,
box feasibility, projected normal-map stationarity, exact active bounds, SciPy
active mask, singular values/condition, status, success, iteration count and
termination message. The existing 1e-12 KKT diagnostic gate is retained. The
normal-map residual accommodates TRF iterates lying just inside an active bound;
it is a diagnostic residual, not an interval optimality certificate.

New independent Decimal code evaluates fine-grid fields, weighted energies, square
roots and recovery at 60/90 significant digits, including cancellation factors,
correct derivatives, final binary64 rounding and separate dense/recovered current
swaps. Fresh solutions and captured saved currents have separate fields. For a
complete historical hosted root, the code additionally recomputes all 48 nonself
saved recovery comparisons across the two reciprocal runs, with original result
SHA256, current/field deltas, KKT, singular values and current-swap controls. These
saved-current evaluations are explicitly labelled as evaluations, not fresh solves.
Supplied historical comparison records are preserved verbatim with file hashes;
false scalar or high-precision acceptance claims and duplicate records are rejected.

Execution/evidence errors are recorded separately from numerical disagreement.
Exit 2 denotes execution/incomplete-input failure; completed diagnostic execution
returns 1 because historical scientific FAIL remains. Missing optional historical
records are explicitly `MISSING_EVIDENCE`, never an authentication pass. New
diagnostic agreement cannot promote production acceptance.

**Runtime limitation:** this Python implementation, its exact semantic seals,
saved-replay analysis and new SciPy solves have not executed in Codex. Static
implementation coverage is not numerical acceptance evidence.

## Fresh independent computations actually executed

To add evidence despite the Python access boundary, a new managed binary64
Householder QR solver was written under O (`qr42.cs`). It solves each exact
captured least-squares problem twice: original row order and reversed row order
of both M and y. This preserves the mathematical least-squares problem while
changing operation order. It is a new independent reference experiment, **not
SciPy TRF**, and is valid only for these full-rank interior solutions. It refuses
out-of-box solutions rather than posing as a bounded optimizer.

All eight input-file byte seals match. All 24 captured dense/row3/row4 systems
were solved in both orders: **48 fresh QR solves**. Existing identified STEP40
.NET helpers supplied binary64 decoding, 90-fractional-place fixed-point direct
KKT/recovery arithmetic and Jacobi singular values. Reuse of these helpers is
explicit; their arithmetic is not a new third high-precision implementation.
O's manifest identifies both new and reused helper source bytes. An analytical
two-column QR check passes with maximum solution error 5.551115123125783e-17.

Executed environment: .NET CLR 4.0.30319.42000, Windows NT 10.0.26300.0, AMD64,
Intel64 Family 6 Model 126 Stepping 5. QR uses sequential managed scalar loops,
with no BLAS, LAPACK, NumPy or SciPy call. This does not recreate any hosted cohort.
`qr-environment.json`, `fresh-independent-qr.json`, `qr-summary.json`,
`objective-and-spectrum-comparisons.json` and `qr-analytical-check.json` record
the fresh measurements and identities.

A subsequent exact-output-transport check found that reloading the scratch
PowerShell numeric JSON changed some current components by up to
5.6843418860808015e-14 A. This is a demonstrated property of that new JSON round
trip, not an identified historical error or an isolated writer-versus-reader
kernel. The original historical input payloads are already binary64 hex.
The initial records and `qr-json-reload-sensitivity.json` remain preserved.
`hex42.cs` and `execute-qr-with-binary-seals.ps1` add exact binary64 current and
normalized-solution payloads to a separate repeat, `fresh-independent-qr-v2.json`.
All **48 recovery texts** (forward, reversed, captured; eight captures, two rows)
match the first experiment exactly. That repeat executes another 48 QR solves:
**96 total executions, 48 distinct problem/order cases**, not 96 independent
experiments. Authoritative exact current payloads are in the v2 file, SHA256
`065acdbd1511183f1dc182288a7927816d98601b222d723dc890749373600e81`.
Using its exact payloads, 32 fresh 60/90-fractional-place evaluations have maximum
ratio discrepancy **1.1589806386267306e-44** (`qr-precision-convergence.json`).
Initial transport-check parsing errors produced no usable convergence record;
the corrected run decodes hex rather than rounded JSON numeric values.
The new Python replay also emits and checks binary64 current payloads.

| Newly executed measurement | Result |
|---|---:|
| Captures with matching full input SHA256 seals | 8/8 |
| Fresh independent QR solves | 48 distinct problem/order cases; 96 including sealed repeat |
| Fresh SciPy TRF solves | 0 — NOT EXECUTED |
| Maximum direct stationarity, both QR orders | 1.1108140766165024e-18 |
| Maximum primal violation | 0 |
| Maximum condition estimate | 1.9467914804478437 |
| Maximum QR-versus-captured current discrepancy | 2.20001794559721e-12 A |
| Maximum QR-versus-captured objective discrepancy | 2.45775438829281e-33 |
| Maximum row-order current discrepancy | 1.3642420526593924e-12 A |
| Maximum row-order projected fine-field discrepancy | 2.1959279930838234e-19 T |
| Row-order recovery comparisons failing original gate | 0/16 |
| Forward-QR versus captured recovery comparisons failing gate | 6/16, all row3 |
| Maximum forward-QR versus captured recovery discrepancy | 2.87098932036245e-11 |

The QR comparison reference is the corresponding captured vector, not the Windows
worker from a historical reciprocal comparison. The six new failures have separate
identities and do not replace the historical eleven or twenty-one. Duplicate N/S
inputs and repeated runs are not independent physical experiments. Fixed-point
precision above means fractional places; Python's planned Decimal precision means
significant digits. Neither computation is described as a formal error bound.

Initial execution of the retained `.ps1` wrapper was denied by execution policy.
The same numerical commands were run through the tool's inline PowerShell command
interface without changing policy. The first inline execution completed the solves
but failed serializing PowerShell wrappers through JavaScriptSerializer. Repeating
with `ConvertTo-Json -Depth 100` produced the retained numerical records. These
failed attempts are not counted as additional successful experiments.

## Fault rows 3 and 4 and the immediate numerical pathway

Recovery remains R=(L-P)/(L-B), guarded by abs(L-B)>1e-15 T. Its differential is

```
dR = [(P-B)dL -(L-B)dP +(L-P)dB] / (L-B)^2.
```

The new code uses derivatives in B,L,P order:
`[(L-P)/(L-B)^2, (P-B)/(L-B)^2, -1/(L-B)]`.
The old B-P diagnostic sign error is not reintroduced; its historical wrong-sign
file remains unchanged. At (B,L,P)=(1,3,2), the derivative is [1/4,1/4,-1/2].

For the latest Windows capture, independently executed 90-place recovery is:

| Row | Captured saved currents | Fresh forward QR | Fresh reversed-row QR |
|---|---|---|---|
| 3 | -0.414688997080917109499289289655… | -0.414688997065892692181324006934… | -0.414688997066634940237177819202… |
| 4 | 0.167266248497502831671650167492… | 0.167266248497875657541817677264… | 0.167266248498422721439661890085… |

These are full fine-grid high-precision field-to-R evaluations using separate
new and saved currents. Row3 QR-versus-captured FAIL persists before final scalar
binary64 rounding; row4 in this example passes. Full texts are in
`fresh-independent-qr.json` and all 16 classifications in
`qr-vs-captured-recovery.json`. No negative recovery is described as a benefit.

The STEP41 saved Windows example has L-B about 5.46649e-11 T for row3 and
5.22069e-10 T for row4, with dR/dL about 2.58793e10/T and 1.59507e9/T respectively.
Those sensitivity figures are **historical**, not newly measured derivative
experiments. The new QR experiment holds captured fields/weights fixed and
demonstrates another current-to-recovery pathway: solutions with tiny KKT and
objective discrepancies can still fail the recovery criterion. Reversing rows
demonstrably changes this independent algorithm's rounding/current output, but
does not cause a failing comparison in the 16 order-control pairs. It therefore
does not establish operation order as the cause of the historical SciPy failures.

Historical independent field integrations and exact saved fixed-current field
agreement from STEP40/41 remain evidence with their original limitations. STEP42's
new field measurement is projected fine-grid field change from fresh QR currents;
it is not a newly executed full Cartesian Biot–Savart/refinement validation.

## Historical recovery failures remain failures

`historical-preservation.json` binds the original STEP41 comparison file SHA256;
`preserved-eleven-latest.json` retains every latest failed record including both
result hashes and input hash. These are preserved historical calculations,
not newly executed STEP42 SciPy results. The eleven original high-precision deltas:

| Origin | Worker | Row | Historical delta R |
|---|---|---:|---:|
| Windows | Linux reference | 4 | -2.717251278971e-12 |
| Windows | Linux NumPy sensitivity | 3 | 3.161582080683e-11 |
| Windows | Linux SciPy sensitivity | 3 | 3.161582080683e-11 |
| Linux reference | Linux NumPy sensitivity | 3 | 3.158395253375e-11 |
| Linux reference | Linux SciPy sensitivity | 3 | 3.158395253375e-11 |
| Linux NumPy sensitivity | Linux reference | 3 | 1.109018376310e-11 |
| Linux NumPy sensitivity | Linux NumPy sensitivity | 3 | 3.555492297367e-11 |
| Linux NumPy sensitivity | Linux SciPy sensitivity | 3 | 3.555492297367e-11 |
| Linux SciPy sensitivity | Linux reference | 3 | 1.109018376310e-11 |
| Linux SciPy sensitivity | Linux NumPy sensitivity | 3 | 3.555492297367e-11 |
| Linux SciPy sensitivity | Linux SciPy sensitivity | 3 | 3.555492297367e-11 |

The preceding run's 21 failures and earlier 22 extracted failed scalar paths are
preserved separately, including the earlier-record source hash in
`preserved-earlier-failures.json`. Original 256-segment refinement failure remains.
No previous result, manifest omission or failed comparison is relabelled.

## Four-way hosted coverage

| Exact input origin → execution OS | Historical captured coverage | Fresh STEP42 SciPy execution |
|---|---|---|
| Windows → Windows | Present in both reciprocal runs | NOT EXECUTED |
| Windows → Linux | Present in both reciprocal runs | NOT EXECUTED |
| Linux → Windows | Present in both reciprocal runs | NOT EXECUTED |
| Linux → Linux | Present in both reciprocal runs | NOT EXECUTED |

The existing `.github/workflows/phase2d-upstream-attribution.yml` is extended,
not duplicated. Its pull_request `synchronize` trigger is retained. Existing
workers now upload complete captured solver inputs; four added replay workers
consume all four sealed origins and require four captures. A comparison job runs
even after scientific failures, requires all four worker/origin sets, checks
input/source identities and worker environments, and compares fresh currents,
objectives, KKT and high-precision recovery. Numerical evidence upload uses
`if: always()` and missing artifacts are errors. Completed replay remains an
explicit scientific FAIL; neither `continue-on-error` nor tolerance relaxation
hides it. No workflow was dispatched or hosted result inferred from this edit.

The original numerical cohorts remain NumPy/SciPy 2.4.6/1.17.1 on Windows and
Linux, 2.3.5/1.17.1 on Linux, and 2.4.6/1.16.3 on Linux. Actual Python patch,
OS/architecture, executable/prefix, CPU report, complete numerical build config,
loaded BLAS/LAPACK threadpools and thread variables are recorded. Python patch,
bundled BLAS and CPU dispatch can still differ; this four-cohort design does not
isolate operating-system or individual library effects. Hardware self-report is
not attestation.

## Original archive authentication

Fresh connected GitHub artifact listings were acquired for all four requested
runs. All **46** ID/name/digest/size/source-head associations match the supplied
local artifact inventory, with zero mismatches. All are advertised unexpired.
This independently corroborates metadata, not original archive bytes.

| Run | Artifacts | Source commit | Fresh run-list observation |
|---|---:|---|---|
| 41195815229 | 5 | ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 | Requested run found; workflow 402677493; failure |
| 41231422708 | 7 | 11c2b1347c7b5359bec0a56e95cc2aa46f03660c | Requested run found; workflow 402952506; failure |
| 41256776296 | 17 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 | Commit-filtered first-page listing omits requested run; gap remains |
| 41257645149 | 17 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 | Requested run found; workflow 403150023; failure |

The connector returned an original ZIP file reference for artifact **13063239980**,
`step33-capture-windows-reference-41257645149-1`. Its advertised digest is
`15ee0f5083d98f3445f3a96ba4400bbf5bd5dac7795664d1bd62effe2e18dfe1`.
The local transfer failed: **Unable to connect to the remote server**. No original
archive bytes were hashed, extracted or compared in STEP42. Other archive
transfers are NOT EXECUTED following the demonstrated common transport failure.
All 46 original byte archives remain **UNAVAILABLE locally**, not proven expired.
`archive-authentication.json` distinguishes advertised digests from null measured
archive SHA256 and identifies the single attempted download. Signed URLs are not
retained in the report. No generated ZIP substitutes for an original archive.
The four incomplete early manifests and prior source/workflow gaps remain intact.

## Tests, acceptance and remaining blockers

New regressions cover actual solver objective/KKT on an analytical system,
bounded solutions, feasibility/stationarity rejection, nonfinite and invalid
scalar rejection, derivative signs/finite differences, denominator guard,
60/90-place comparisons, analytical field-to-recovery evaluation, failure
preservation, false high-precision PASS rejection, missing/duplicate evidence,
exact captured reconstruction, corrupt fingerprints/payloads, source identity,
solver settings and environment provenance. Historical-capture parametrizations
require the local ignored evidence; hosted fresh captures are separately validated
by the replay jobs. No test pass count is claimed for unexecuted Python tests.

Focused pytest, full pytest, compilation, fresh replay, analytical validation,
quick experiment, output checks and independent audit were attempted using the
explicit existing venv interpreter. Every attempt exits **103 before startup**.
README test recording and full reproduce_check were also attempted in a source
copy below O and exit 103. Final-source focused/compilation attempts are hash-bound
in `final-source-python-attempts.json`. `python-attempts.json` and individual logs
record arguments and results. The new .NET QR analytical check and 48 numerical
solves executed successfully; Git whitespace checks pass. Passing those checks is
not a substitute for the required Python/production result-SHA-bound gates.

The reproducible host invocation, using the existing working host environment and
a fresh child directory, is:

```powershell
$env:STEP42_OUTPUT_ROOT = Join-Path $PWD 'results/phase2d/step42-reproducibility-20261101-120046-d90ebceb'
$env:PYTHONPYCACHEPREFIX = Join-Path $env:STEP42_OUTPUT_ROOT 'host-pycache'
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step42_replay.py -p no:cacheprovider
.\.venv\Scripts\python.exe scripts/phase2d_step42_replay.py --input results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/github-hosted --expected-captures 8 --history results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/recomputed-comparisons.json --history results/phase2d/step41-final-acceptance-20261101-110323-7fe7248c/early-failures.json --output "$env:STEP42_OUTPUT_ROOT/host-scipy-replay"
```

Exit 1 is expected for a completed replay retaining scientific FAIL; exit 2 means
execution/input failure and must not be reinterpreted as a scientific result.
Full README gates must run independently with new result-file SHA256 records.
No successful hosted or production result is supplied by this command listing.

**Remaining blockers are observed gaps, not a speculative roadmap:** Codex cannot
access the existing Python base; final Python regressions and production gates
are unexecuted here; no fresh four-cohort SciPy artifacts exist; original archive
bytes cannot reach the checkout; the run/workflow and incomplete-manifest gaps
remain; the eleven/latest, twenty-one/preceding and earlier scientific failures
remain. The unique upstream floating-point kernel is unresolved. No attribution
to NumPy, SciPy, BLAS, LAPACK, hardware or OS is justified by the new QR evidence.

`scientific_comparison=FAIL`, `production_acceptance=FAIL`,
`causal_root_cause=INCONCLUSIVE`, `scientific_status=PARTIAL`.
rtol=1e-11, atol=1e-13, refinement limit=1e-4, 512-segment geometry, equations,
objectives, original solver settings and physical constraints are unchanged.
Finite-scenario minimax and small holdouts do not establish general robust
outperformance; no confinement or device validation is claimed.
