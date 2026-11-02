# STEP 46 independent scientific causal assessment

2026-11-02. **Scientific comparisons FAIL; production acceptance FAIL; numerical
root cause INCONCLUSIVE; original artifact-byte authentication MISSING_EVIDENCE;
overall scientific status PARTIAL.** Independent Python calculations and new
tests are prepared but runtime-unverified. This is not a verified checkpoint.

Source commit: `3eabd1a98dad81493e664929890ba0effdd97a05`.
Branch: `codex/phase2d-upstream-attribution`. Evidence directory:
`results/phase2d/step46-independent-science-20261102-092351-51df8b20/` (O).
Only this report, the STEP46 script/test and ignored evidence are added. No
production equation, threshold, workflow, historical reference or environment
was changed. No commit, push, dispatch or merge occurred. AGENTS.md prohibits
inspecting or bypassing GitHub CLI configuration restrictions; connected GitHub
read tools were used instead. No monitoring repair was repeated.

## Evidence and authentication

The preexisting O/run-* archives contain run metadata, artifact inventories and
failed-step logs. New independent connector responses are retained separately in
`connected-github-records.json` and `connected-failed-job-logs.json`.
`run-identities.json` transcribes the archived run identities; it does not claim
the connector's latest-attempt API is an attempt-specific metadata attestation.
All listed archived runs have attempt **1** and the supplied source SHA.

| Study | Workflow ID | Run ID | Observed result |
|---|---:|---:|---|
| STEP32 | 403150022 | 41437268360 | Four captures and four replays succeed; compare exits 1 |
| STEP33 | 403150023 | 41437268262 | Four captures and four replays succeed; compare exits 1 |
| STEP45 | 404372820 | 41437268393 | Four captures succeed; four replays and compare fail |
| Upstream | 402952506 | 41437276646 | Scientific differences and failed STEP42 workers/comparison |
| Scientific validation | 401108055 | 41437268342 | Validation job succeeds |

The connector supplies only first-page artifact/job lists and latest-attempt
jobs. These scope limits are retained; no completeness or mixed-attempt claim is
made. Capture/replay job names identify Windows reference (NumPy 2.4.6/SciPy
1.17.1), Linux reference (2.4.6/1.17.1), Linux NumPy sensitivity
(2.3.5/1.17.1), Linux SciPy sensitivity (2.4.6/1.16.3). These names indicate
configured versions, not a new local loaded-library measurement.

Comparison archive identities from retained metadata and upload logs include:

| Artifact | ID | GitHub ZIP SHA256 |
|---|---:|---|
| STEP32 comparison, run 41437268360 attempt 1 | 13136414538 | `9a122a738e6bc082fd093459ea01f724759b2b27a481c66a99d0b0a2b8aeac1a` |
| STEP33 comparison, run 41437268262 attempt 1 | 13137621043 | `ce998801f91f0c2a32342d5750c742a28ee7fcaccf9dbeb7adae7f7efb0adb4b` |

GitHub returned a reusable download reference for artifact 13137621043. The
local byte transfer failed with `System.Net.WebException: Unable to connect to
the remote server`. No archive bytes or local ZIP digest were obtained. Metadata
has `expired=false`; local unavailability does not establish expiration. Input
and result SHA256 for these current numerical comparisons remain
**MISSING_EVIDENCE**, rather than being filled with older-run identifiers.
Old STEP38 extracted bytes are independently checked against retained inventories
in `historical-integrity.json`; local integrity does not authenticate GitHub
origin. Older STEP40 numerical records remain older evidence.

## Hypotheses, mathematics and independent method

The hypotheses are: (1) artifact/serialization errors explain apparent failures;
(2) solver current differences are amplified by recovery conditioning;
(3) fixed-current field evaluation contributes; (4) a unique solver/library
mechanism explains the upstream discrepancy. These require separate controls.

For `R=(L-P)/(L-B)`, differentiation gives

```
dR = ((P-B)dL - (L-B)dP + (L-P)dB)/(L-B)^2.
```

The gradient in B,L,P order is `[(L-P)/(L-B)^2, (P-B)/(L-B)^2,
-1/(L-B)]`. At (1,3,2), it is exactly (1/4,1/4,-1/2).
STEP39's superseded wrong-sign diagnostic is documented in STEP40; it is not a
demonstrated production-equation defect. No sign change to production is made.

The new script independently implements Decimal forward products, weighted RMS,
quotient and gradient, central finite differences, current-only interventions,
linear prediction and nonlinear residual, componentwise relative condition,
direct least-squares residuals, exact-bound KKT signs, box feasibility and
projected-gradient residual. It adds scalar Householder QR at 60/90 digits,
distinct from STEP40's modified Gram-Schmidt implementation. It certifies no
bounded solution when the unconstrained reference is outside the box or rank
deficient. Decimal precision convergence is empirical, not interval arithmetic.

The script explicitly reuses STEP42's strict transport/source/problem validation
and exact M/y reconstruction. New arithmetic calls no production numerical
helper. A fresh TRF solve uses saved M/y, and compares saved/fresh normalized
vectors and physical currents through independent residuals and fine-grid
fields. It records both fault identities (row3 coil 3, row4 coil 6), one-ULP
current probes, independent reference recovery, binary64 recovery and aggregate
binary64 evaluation error. The latter combines field products, reductions,
roots and quotient; it is not an isolated serialization or reduction-order test.
Original saved-result ratios must be bound separately; the script explicitly
marks their absence. Saved matrix fields are not a fresh geometry integral.

Run on the controlling host with an isolated new output directory:

```powershell
.\.venv\Scripts\python.exe scripts/phase2d_step46_independent.py --capture <sealed-capture-directory> --input-sha256 <original-input-sha256> --output results/phase2d/step46-host-new
```

Exit 2 without inputs preserves missing evidence. Exit 1 after diagnostic
execution preserves historical scientific FAIL. A passing local saved/fresh
ratio is limited to that input/environment; it cannot close hosted comparisons.
No alternate production solver is introduced.

All original limits remain: rtol=1e-11, atol=1e-13, refinement=1e-4,
denominator guard=1e-15 T, physical bounds +/-3000 A; `lsq_linear`, method=trf,
lsq_solver=exact, tol=1e-12, max_iter=1000. Quick geometry remains 512 segments.

## Numerical findings and causal classification

Retained STEP40/41 measurements report 21 preceding and 11 latest **older-run**
ratio failures that persist in high-precision field/RMS arithmetic. They report
all 72 nonself current comparisons passing, maximum difference
2.8279600883251987e-12 A. These are cited prior findings, not newly executed
STEP46 measurements and not counts for the November 2 runs.

Representative older saved-current independent ratios were row3
`-0.4146889970809171094992892896548706787...` and row4
`0.1672662484975028316716501674920593179...`. Rounded reported gaps L-B were
approximately 5.466485340356966e-11 T and 5.220686710494032e-10 T respectively;
dR/dL approximately 2.587931566676031e10/T and 1.595065549179688e9/T.
Both gaps exceed the guard. The guard prevents division by an extremely small
absolute denominator; it does not guarantee a well-conditioned ratio.
Negative row3 recovery is not a benefit. A small absolute field/current change
can therefore matter to the unchanged ratio gate even when current gates pass.

| Class | Independent assessment |
|---|---|
| A Artifact authentication | MISSING_EVIDENCE: original ZIP bytes/current numerical seals unavailable locally |
| B Missing historical evidence | Original archive authentication remains incomplete; preserve local inventories |
| C Genuine numerical discrepancies | Supported by older independently recomputed ratios; current comparison exits confirmed, exact current failing cells unavailable |
| D Solver non-reproducibility | Older same-input output differences supported; fresh current-run mechanism INCONCLUSIVE |
| E Current-vector sensitivity | Older current-to-field-to-ratio pathway supported; new controlled calculation unexecuted |
| F Recovery-ratio sensitivity | Analytically established cancellation amplification; numerical magnitude cited from older records |
| G Floating-point serialization | Known one-ULP STEP44 derived-record defect was repaired; it cannot explain eleven older failures that persist at high precision |
| H Genuine software defects | No new production defect established; workflow exit 1 alone is not proof of a solver defect |
| I Missing experimental controls | Need authenticated identical M/y, current swaps, fixed-current independent fields and four-cohort driver controls for these exact run attempts |

Small KKT residuals measure approximate optimization quality, not bitwise output
identity or a bound on recovery error. Full rank implies uniqueness in exact
arithmetic for a fixed support, not identical binary64 solver output across
machines. OS/library cohorts also change bundled kernels and dependencies; they
do not identify CPU dispatch, BLAS, SVD, FMA or SciPy as a unique cause. No new
controlled experiment isolates one such mechanism. Root cause stays
**INCONCLUSIVE**. The STEP45 coordinator deliberately retains historical FAIL
with exit 1 even after completed diagnostics; its red job alone does not identify
which fresh numerical gate failed. Obtain its sealed status and worker results.

## Regression and final verdict

### Missing-evidence handling repair (2026-11-02)

The reported source-fingerprint failure is repaired at the source-read boundary.
STEP46 verifies that the diagnostic source is a file before reading it, hashes
its actual bytes when available, and records JSON `null` in the existing
`diagnostic_source_sha256` manifest field when unavailable. A disappearance
between the check and read is handled specifically as `FileNotFoundError`.
No alternate source path or fabricated digest is used. A digest identifies
local bytes only; it does not authenticate historical evidence.

Missing source identity keeps independent calculation and ratio validation
INCOMPLETE and forces exit 2. Missing authenticated capture files are translated
at the STEP42 transport-loading boundary into an incomplete assessment with
exit 2. Both assessment and manifest are written in the new isolated output
directory before that return. Invalid source seals and other validation errors
remain explicit errors; unrelated filesystem failures are not broadly caught.
The assessment and manifest keys are preserved. Historical scientific comparisons
remain FAIL, production acceptance FAIL, and overall scientific status PARTIAL.
No scientific equations, solver settings, tolerances or historical hashes changed.

Regression coverage now includes existing/missing source files, an independently
known SHA256, exact newline bytes, source disappearance during reading, unrelated
read errors, unavailable source identity despite a synthetic local calculation,
missing authenticated inputs, incorrect authenticated source identity, missing
output parents, historical-file byte preservation and no false historical PASS.
Synthetic calculations in tests do not establish scientific acceptance.

The initial reproduction attempt and post-repair validation used the existing
`.venv/Scripts/python.exe`; all Python commands stopped before collection or
execution with exit 103 and the missing configured base executable message:
`No Python at '"C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe'`.
The following required checks were attempted after the repair:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step46_independent.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts tests
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

`git diff --check` succeeds. The three deliverables are preexisting untracked
files; separate `git diff --no-index --check -- /dev/null <file>` checks report
no whitespace defects (exit 1 denotes differing files; Git also warns of future
LF-to-CRLF conversion). No test pass or verified research checkpoint is claimed for this repair.
The controlling host still needs to execute the regression and full validation.

The required existing `.venv/Scripts/python.exe` exits **103** before Python
startup, reporting its configured Python311 base executable unavailable. Targeted
pytest, full pytest, compileall, pip check and analytical validation were each
attempted; exact commands/output are in `validation-attempts.json`. No tests were
collected and no new Python numerical calculation passed. The environment was
not replaced. New tests are runtime-unverified; the requirement that they pass
remains outstanding. `git diff --check` succeeds, but this does not compile or
validate the new untracked Python files. README quick/audit/output/full-repeat
gates cannot execute until the same interpreter blocker is resolved; no verified
research checkpoint is claimed. Scientific-validation CI is successful for the
published source, not these new uncommitted deliverables.

1. Independent calculation: implementation prepared; execution INCOMPLETE.
2. Artifact authentication: metadata corroborated; byte authentication MISSING_EVIDENCE.
3. STEP32 scientific comparison: FAIL.
4. STEP33 scientific comparison: FAIL.
5. STEP45 scientific comparison: FAIL; individual gate attribution incomplete.
6. Recovery-ratio validation: historical FAIL preserved; current-run independent calculation INCOMPLETE.
7. Numerical root-cause attribution: INCONCLUSIVE; conditioning pathway supported by prior evidence.
8. Production acceptance: FAIL.
9. Overall scientific status: PARTIAL.
10. Blockers: working required Python runtime, passing new/full tests and README
    gates, original current-run archive bytes authenticated to metadata/digests,
    input/result seals, attempt-specific complete four-cohort evidence and
    controlled numerical attribution. No missing result is replaced by a fresh
    or older result. Finite-scenario minimax/small holdouts do not establish
    general robust outperformance, confinement or physical-model validation.
