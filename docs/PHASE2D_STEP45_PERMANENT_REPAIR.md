# STEP 45 permanent monitoring repair and scientific assessment

## Windows SHA256 harness regression repair (2026-11-02)

This follow-up changes only the monitor test harness and this report. Production
monitoring, workflows, numerical code, tolerances and historical evidence are
unchanged. Nothing was staged, committed, pushed or merged.

### Exact root cause and investigation limits

The supplied hosted failures (41433684553, 41433684343, 41433684626,
41433693674) identify command resolution of `Get-FileHash` in
`test_scalar_binding_and_unique_directories[powershell]`, rather than a solver
failure or a demonstrated incorrect SHA256 calculation. The harness depended on
an available PowerShell command for both snapshot creation and verification.
`Get-FileHash` is supplied by Microsoft.PowerShell.Utility; on this local 5.1 host
it resolves successfully (module version 3.1.0.0). Inspection of the harness and
monitor found no module imports/removals, autoload preference changes or command
shadowing that intentionally excludes it. Each harness uses a fresh `-NoProfile
-NonInteractive -File` subprocess. The exact reason the hosted session could not
resolve the command is **not established** by the available source or supplied
error. No hosted environment diagnosis or exact local reproduction is claimed.
GitHub CLI restrictions were not inspected or bypassed.

### Permanent correction and SHA256 integrity

Both snapshot operations now call the same test-only `Get-TestSha256` helper.
It creates `System.Security.Cryptography.SHA256`, reads exact file bytes with
`System.IO.File.ReadAllBytes`, calls `ComputeHash`, formats all 32 bytes using
`System.BitConverter.ToString` as 64 lowercase hexadecimal characters, and disposes
the hash object in `finally`, including on read/hash failure. It requires no
implicit PowerShell module loading for hashing. Comparison remains an exact,
case-sensitive digest comparison; evidence is never rewritten by the helper.
Python additionally compares all 14 returned snapshots against independent
`hashlib.sha256` digests of the saved bytes. A constant, file-size check or
existence check cannot substitute for the digest.

All 24 invalid objects and both public entry points remain: 48 rejection checks,
zero CLI calls and no directories for invalid IDs, 14 unique valid evidence
directories and 28 mocked CLI calls. Null, empty, arrays, negative, noncanonical,
overflow, floating-point, boolean and misleading object cases are retained.
The offline cases still require scientific comparison NOT_ASSESSED and production
acceptance NOT_ESTABLISHED. Monitoring success establishes no scientific acceptance.

### Local regression results and compatibility

| Check | Result in this follow-up |
|---|---|
| Targeted monitor pytest | Blocked before collection: existing .venv references missing Python311 executable |
| Complete pytest | Same Python startup failure |
| compileall src scripts tests | Same Python startup failure |
| pip check | Same Python startup failure |
| Windows PowerShell 5.1.26100.9711 helper | Executed: standard ASCII `abc` SHA256 vector passed; zero helper parser errors |
| Windows PowerShell 5.1 monitor execution | Blocked: scripts disabled by host execution policy |
| PowerShell 7 | Installed launcher cannot execute: file cannot be accessed by the system |
| git diff --check | Passed after correction |

The observed 5.1 digest was
`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
The helper uses APIs available in Windows PowerShell 5.1 and PowerShell 7, but a
full runtime pass on either shell is not claimed. The existing .venv was preserved;
no execution-policy override was used. The temporary known-vector file was removed.
Final controlling-host regression and hosted scientific-validation/Windows capture
job passes remain required; this session cannot claim CI passed or the historical
785 passed / 4 skipped count was reproduced.

### Historical evidence and remaining scientific failures

Only the two authorized files differ in the working tree. No historical evidence
was written by this repair; historical manifests were not newly reauthenticated.
The earlier integrity results below remain historical records, not fresh checks.
The harness continues hashing each monitor.json immediately after creation and
checking every earlier snapshot after all later invocations, now also against
Python's SHA256 implementation when the test can execute.

STEP 32 and STEP 33 retain their recorded scientific comparison failures. STEP 45
retains historical FAIL and incomplete fresh artifact-level closure. No scientific
FAIL or artifact-upload failure is suppressed, and no verified research checkpoint
or production acceptance is claimed. All original scientific limitations below
remain in force.

2026-11-02. Automation implementation prepared; runtime verification BLOCKED.
Scientific comparison FAIL; production acceptance FAIL; overall scientific status
PARTIAL. This is not a verified research checkpoint.

Work remained on `codex/phase2d-upstream-attribution` in this checkout. Supplied
hosted source: `b780b5dd399645868275a56a1f10c997a561286a`. Only the new monitor,
its portable regression tests and this report are proposed. No production code,
historical evidence, numerical criterion or workflow was changed. Nothing was
staged, committed, pushed, dispatched or merged. GitHub CLI configuration was
neither inspected nor bypassed. PR #7 was not modified.

## Automation repair

`scripts/phase2d_step45_monitor.ps1` accepts only primitive integer values or
canonical ASCII positive decimal strings representable as Int64. Both public
RunId parameters preserve the original object; explicit validation rejects arrays,
null, booleans, floating-point/Decimal values and other objects before conversion,
directory creation or CLI calls. Only after type and full-string representation
checks does invariant-culture, NumberStyles.None Int64.TryParse run. It never
discovers a run by casting a list of search results. Each poll is
exactly `gh api repos/OWNER/REPO/actions/runs/RUN_ID`, parsed with
`ConvertFrom-Json`. Run ID, repository full name and API URL, expected full source
commit and exact workflow name must match before accepting status. Arrays and
missing fields fail closed. Command construction uses separate internally
validated tokens and no shell evaluation or positional run collections.

The reported `accepts at most 1 arg(s), received 50` establishes a CLI argument
cardinality failure, not a scientific failure. The supplied evidence does not
retain the exact failing invocation or its variables, so an array-expansion versus
multiline-JSON explanation cannot be uniquely established. The new implementation
removes both routes by using an explicitly supplied scalar and a single run API
endpoint. No live GitHub call was attempted here under the local restriction.

Queued and in-progress runs poll until completion or deadline; unknown states
fail closed. Completed success, failure, cancelled, timed_out, action_required,
skipped (also neutral, stale, startup_failure) preserve their exact conclusions.
Polling stops on completion. Each native process has a timeout and concurrently
drained stdout/stderr; a hung API process is terminated. Polling is bounded by
`TimeoutSeconds` plus at most one second of rounding/process shutdown overhead;
terminal log retrieval has its own `ApiTimeoutSeconds` bound.

Every invocation uses a GUID directory and preserves raw poll JSON, stderr,
available full job logs and `monitor.json`. Log retrieval uses one scalar
`gh run view RUN_ID --repo OWNER/REPO --log`; it retrieves successful and failed
job logs without limiting collection to the last failed step. Unavailable logs
remain MISSING_EVIDENCE and do not overwrite the observed conclusion. There is
no claim that unavailable remote logs were preserved. Input binding errors occur
before directory creation and must be retained by the caller's invocation log.

Monitor exit 0 means completed GitHub success with logs preserved, **never
scientific acceptance**. Exit 1 means a completed non-success GitHub conclusion;
exit 2 means monitoring/log evidence incomplete. JSON always distinguishes
`monitor_status`, `github_status`, `github_conclusion`, `log_status`,
`scientific_comparison=NOT_ASSESSED` and
`production_acceptance=NOT_ESTABLISHED`. It does not infer scientific status from
GitHub's conclusion or rewrite a scientific exit code.

Controlling-host example (each call creates new outputs):

```powershell
.\scripts\phase2d_step45_monitor.ps1 -RunId 41426274201 `
  -ExpectedCommit b780b5dd399645868275a56a1f10c997a561286a `
  -WorkflowName 'Phase 2D STEP 45 independent causal validation'
$monitorExit = $LASTEXITCODE
```

The script uses Windows PowerShell 5.1-compatible syntax and APIs. Execution on
both 5.1 and 7 remains required; compatibility is not claimed runtime verified.

### Run-ID regression correction (2026-11-02)

The supplied pytest failures name both `test_scalar_binding_and_unique_directories`
shell variants. A direct Windows PowerShell 5.1.26100.9711 binding probe reproduced
the underlying acceptance: the original `[long]` parameter converts the string
`'1,2'` into **12** before ValidateRange runs. Implicit numeric conversion therefore
loses the original invalid representation. The original test catches this even
though its mocked CLI throws: the monitor catches that exception and returns an
ERROR record, so the test's subsequent `accepted invalid ID` assertion fires.

The same probe showed that the original fixture
`@(@(1,2),@(),0,-1,'1 2','1,2')` preserves both arrays on this 5.1 host;
both fail scalar binding, as do zero, negative one and `'1 2'`. Array flattening
was investigated and was **not observed for this exact construction**. PowerShell
pipeline/function output enumeration can flatten or omit arrays, so the replacement
fixture explicitly uses `List[object].Add` and verifies the retained array types
and lengths. A separate executed fixture probe confirmed 24 entries, with array
lengths 0, 1 and 2 at indices 2, 3 and 4. No evidence supports attributing the
reported failure to fixture flattening. The demonstrated defect is monitor
parameter coercion; the harness needed broader coverage and preservation assertions.
The original 7 runtime failure could not independently be reproduced here.

The expanded regression checks 24 invalid objects through both public entry points
(48 rejections), requiring explicit `Invalid RunId:` errors, zero mocked CLI calls
and no evidence directories or success records. Cases include the requested invalid
IDs plus floating-point, Decimal, unsigned overflow, trailing newline and an object
whose ToString returns `'1'`. Valid numeric and string IDs 1, 123 and 41371734831,
plus Int64.MaxValue, each run twice against synthetic successful responses. The
test requires 14 distinct directories and unchanged SHA256 digests for all earlier
monitor.json records. These are test assertions, not claims of completed execution.

Verification attempted after this correction using the existing `.venv`:

| Check | Observed result |
|---|---|
| Targeted monitor pytest | Cannot start: configured Python311 executable missing |
| Full pytest | Same Python startup failure |
| compileall src scripts tests | Same Python startup failure |
| pip check | Same Python startup failure |
| Windows PowerShell 5.1 monitor parsing | Executed, zero parser errors |
| Windows PowerShell monitor runtime | Blocked: running scripts disabled by execution policy |
| PowerShell 7 parsing/runtime | Launcher cannot execute: file cannot be accessed by the system |
| Git diff --check | Executed successfully; authorized files remain untracked |
| Git fsck --full | Exit 0; dangling blobs reported, no corruption reported |
| .venv ignore | git check-ignore confirms .venv is ignored |

Neither previously failing pytest variant nor any full-suite pass is claimed.
The native binding and fixture probes executed as inline PowerShell commands;
they do not constitute monitor runtime tests. No execution-policy or GitHub CLI
restriction was bypassed. No staging, commit, push, merge or numerical change was
performed. All original scientific and evidence limitations below remain in force.

## STEP 32 scientific comparison

Read the actual retained failure log and run JSON in
`results/phase2d/step45-permanent-repair-20261102-052548-daf98800/`.
Run 41426273939 names the expected repository, STEP 32 workflow and supplied
commit, completed with GitHub conclusion failure. The supplied capture/replay
success observation is consistent with a later comparison failure. The retained
comparison log contains the command and exit **1**, with no traceback or printed
failed quantities. In `phase2d_step32.py`, `main(compare)` sets exit 1 only after
`comparisons` returns a nonempty scientific failure list and writes the assessment;
exceptions use exit 2. Thus the log and source support completed scientific
comparison failure, not a setup/CLI error.

The comparator first verifies all captures and workers, source identity, exact
replay-input bytes and seals, replay structure, independent fields and constrained
optimality. It then compares currents, objectives, recovery ratios, supports,
fields and regenerated arrays under original criteria. No demonstrated software
defect justifies changing it. However, the **new run's assessment artifact and
original ZIP bytes are not present in the supplied directory**. Its exact failed
quantities and bindings cannot be independently rechecked from this log alone.
Do not substitute earlier runs' eleven failures for this run's failure list.
Categories A/B/C/D are not demonstrated for this new run; E is supported by the
retained earlier controlled numerical evidence, but exact attribution of the new
comparison remains incomplete pending its assessment and artifact verification.
The observed FAIL remains FAIL. STEP 33 run 41426281909 separately records its
comparison exit 1; it is not STEP 32 evidence.

## STEP 45 scientific comparison and failed steps

Run 41426274201 metadata matches repository, source commit, workflow name and
completed/failure. The supplied logs explicitly show:

| Job cohort | Step | Exit |
|---|---|---|
| windows-reference | STEP 42 reciprocal sealed-input replay | 1 |
| linux-reference | STEP 42 reciprocal sealed-input replay | 1 |
| linux-scipy-sensitivity | STEP 42 reciprocal sealed-input replay | 1 |
| windows-reference | STEP 45 QR/LAPACK diagnostics | 1 |
| linux-reference | STEP 45 QR/LAPACK diagnostics | 1 |
| linux-numpy-sensitivity | STEP 45 QR/LAPACK diagnostics | 1 |
| linux-scipy-sensitivity | STEP 45 QR/LAPACK diagnostics | 1 |
| compare | Require every cohort; retain historical FAIL | 1 |

This table describes observed steps, not an invented complete job inventory.
The NumPy-sensitivity replay exit is not in the supplied excerpt. Full job metadata
and original worker diagnostic artifacts are needed to close that gap.

STEP 45 explicitly returns 2 when execution/evidence errors are collected and 1
otherwise, even with completed diagnostics, because historical scientific FAIL
and acceptance blockers remain. STEP 42 uses the same incomplete-versus-retained-
FAIL distinction. These observed exits therefore do **not** independently show an
artifact authentication exception, infrastructure error or solver execution crash.
They also do not establish that fresh numerical comparisons all failed: completed
diagnostics can still exit 1 to retain historical failure. Worker status.json,
solver-comparisons.json and recovery-comparisons.json must distinguish these.
The workflow already uploads with `always()` and executes diagnostics/comparison
after earlier scientific failure without changing their exits. No correction to
that behavior is justified. Fresh four-cohort scientific closure remains incomplete.

## Numerical root cause

Reviewed STEP 31/32/33/34/36/38/39/40/41/42/44/45 reports and the STEP 32 comparison,
STEP 45 coordinator, tests and causal workflow. Prior evidence is evidence of
prior execution, not a fresh computation in this repair.

The quotient and differential remain

```
R = (L-P)/(L-B)
dR = [(P-B)dL-(L-B)dP+(L-P)dB]/(L-B)^2
```

The gradient in B,L,P order is `[1/4,1/4,-1/2]` at B=1,L=3,P=2.
Historical row3 (failed coil 3) has L-B about 5.46648534e-11 T,
R about -0.4146889970809171 and dR/dL about 2.58793e10/T.
Row4 (failed coil 6) independently has L-B about 5.22068671e-10 T,
R about 0.1672662484975028 and dR/dL about 1.59507e9/T. Both denominators exceed
the 1e-15 T guard. Cancellation amplifies tiny RMS/current differences; passing
current-vector tolerances or KKT checks cannot imply passing recovery ratios.

STEP 40/41 retain ten row3 and one row4 failures in the latest old replay, twelve
row3 and nine row4 in its predecessor; 22 earlier extracted scalar paths are a
separate inventory. High-precision saved-current field/RMS calculations preserve
failures, so final quotient serialization alone does not explain them. The known
STEP 44 one-ULP derived Decimal-to-Double adapter error was already repaired; that
cell passed tolerance and does not explain the failed inventory. Original inputs,
source seals and currents must be retained for further controls.

Prior independent fixed-current field and finite-wire checks support the limited
coordinates tested. Exact-input current swaps support a current-to-recovery
pathway. They do not isolate BLAS/LAPACK, NumPy, SciPy, CPU dispatch, FMA or
reduction order as a unique cause. Version cohorts also change bundled libraries.
STEP 42's row-order QR controls did not themselves produce a failed recovery
contrast; that does not exclude reduction effects in other operations. STEP 45
provides independent Decimal QR, LAPACK-driver and current-sensitivity controls,
but this session cannot newly execute them. No production correction is justified.

Unchanged: rtol=1e-11, atol=1e-13, refinement=1e-4, guard=1e-15 T;
`lsq_linear(method='trf', lsq_solver='exact', tol=1e-12, max_iter=1000)`,
physical bounds +/-3000 A and quick geometry 512 segments. The original
256-segment failed audit remains intact. No reference, model or historical value
was changed to obtain PASS.

## Evidence authentication

Four historical runs retain distinct identities:

| Run | Retained source commit |
|---|---|
| 41195815229 | ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 |
| 41231422708 | 11c2b1347c7b5359bec0a56e95cc2aa46f03660c |
| 41256776296 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 |
| 41257645149 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 |

STEP 45's earlier metadata retrieval reports workflow IDs 402677493, 402952506,
403150023 and 403150023 respectively. This session read retained local metadata;
it did not newly authenticate GitHub responses. Metadata identity is distinct from
archive-byte authentication. The original ZIP bytes remain MISSING_EVIDENCE;
no approximation or newly generated archive replaces them. Extracted-file SHA256
checks establish local byte consistency only, not origin or numerical reproduction.
The new `historical-integrity.json` records each observed digest separately from
its expected digest: **3,599 entries checked, zero mismatches**, across
`downloaded-files.sha256` and `historical-before.sha256`. This executed check
does not fill manifest omissions or authenticate original ZIPs. Independent
numerical reproduction remains blocked here.

## Regression and execution records

New portable pytest cases use synthetic GitHub responses, mock only the CLI
boundary, and execute the real PowerShell monitor. They cover scalar/array IDs,
missing IDs, malformed and array JSON, API errors/timeouts, queued/in-progress
polling, terminal conclusions, all identity checks, unavailable logs, unique output
directories and prevention of false scientific acceptance. No ignored research
result is required. Existing STEP 32 and STEP 45 tests cover comparison integrity,
original numerical gates/derivative, SHA256 checks, missing evidence and false PASS.
Those scientific implementations were left unchanged because no new defect was
demonstrated. A real clean-checkout execution is still required.

Validation attempts are retained under
`results/phase2d/step45-repair-validation-f617f05611af418f8a498ceea7e7ba30/`:

- `python -m pytest -q`: attempted using existing `.venv`; exit 103 before startup.
- `python -m compileall -q src scripts tests`: same startup failure, exit 103.
- `python -m pip check`: same startup failure, exit 103.
- Windows PowerShell parser: no monitor syntax errors observed.
- Offline PowerShell harness: script execution denied by execution policy; no
  cases executed successfully. `powershell-cases.json` retains every blocked attempt.
- `git diff --check`: executed successfully; it does not check untracked file content.

No Python tests passed, no new solver was executed, and no PS5.1/PS7 runtime pass
is claimed. The existing environment was not replaced; host restrictions were not
bypassed. README analytical validation, quick experiment, output checks, independent
audit and full reproducibility are not passed for this change. They must execute
on the controlling host in isolated outputs and produce passing records tied to
result-file SHA256 before any checkpoint is called verified.

## Separate final verdicts

| Required verdict | Result |
|---|---|
| AUTOMATION REPAIR | Implemented; runtime verification blocked |
| STEP 32 SCIENTIFIC COMPARISON | Observed FAIL; new assessment/artifact inspection incomplete |
| STEP 45 SCIENTIFIC COMPARISON | Retained FAIL; fresh artifact-level outcome details incomplete |
| NUMERICAL ROOT CAUSE | Current-to-recovery amplification supported; unique upstream cause INCONCLUSIVE |
| ORIGINAL EVIDENCE AUTHENTICATION | Metadata retained; original archive bytes MISSING_EVIDENCE |
| REGRESSION TESTS | Added; Python startup and PowerShell policy block execution |
| PRODUCTION ACCEPTANCE | FAIL |
| OVERALL SCIENTIFIC STATUS | PARTIAL |
| REMAINING BLOCKERS | Host runtime tests, new run assessments/diagnostic archives, original archive authentication, controlled kernel attribution, final-source README and clean-checkout gates |

Finite-scenario minimax and small holdout samples do not establish robust
outperformance, continuum maxima, engineering feasibility or confinement validation.
