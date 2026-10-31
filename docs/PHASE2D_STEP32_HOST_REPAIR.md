# STEP 32 host failure investigation and repair

Overall scientific status: **PARTIAL**. Source repair is prepared; repaired-host
runtime validation is **BLOCKED**, not PASS. No production optimization code,
solver settings, bounds, objectives or numerical tolerances were changed.

## Verified failure

The existing record under
`results/phase2d/step32-host-20261031-181424-abb419e6/assessment.json`
records Python-version exit 0, then pytest exit 2 and
`tests failed with exit 2; evidence retained`. Its `tests.log` identifies
`ModuleNotFoundError: No module named 'threadpoolctl'` while collecting
`tests/test_phase2d_step32.py`, imported by `scripts/phase2d_step32.py:18`.
The original host redirects Python output to a log, catches the exception without
printing it, and executes its final explicit `exit 2`. Thus the recorded failure
is pytest collection, propagated through the host's explicit exit; it is not
parameter binding, output freshness, Python startup or authentication failure.
This conclusion identifies the retained invocation. No claim is made about any
unrecorded launcher invocation. The original host bytes are preserved as
`results/phase2d/step32-repair-20261031-181855-e9d0f395/host-before.ps1`.

## Source inspection and correction

The complete script was reviewed, including publication and finalization paths.

| Area | Finding / repair |
|---|---|
| Requires / version | `#requires -Version 7.0` retained. No replacement with Windows PowerShell 5.1. |
| Parameters | Mandatory string `EvidenceRoot`, mandatory string `OutputRoot`, optional switch `Publish` retained. No aliases or binding changes needed. |
| Initialization | Previously outside the handler. Now caught, with console exception and a unique fallback execution record inside this checkout. Existing/rejected output is never used for that record. |
| Evidence / output | Resolve existing evidence, require directory, require fresh output inside checkout and disjoint paths; no original files overwritten. |
| Repository / branch | Existing exact origin, checkout and feature-branch checks retained. Stage identified as repository-preflight. |
| Python | Existing `.venv/Scripts/python.exe` and exact Python 3.11 requirement retained. |
| Dependencies | Import preflight added before pytest. `threadpoolctl>=3,<4` added to the development extra in `pyproject.toml`, because STEP 32 tests import it but it was undeclared. No automatic installation or alternate interpreter. |
| Native exits | Python arguments, native exit code and logs retained; stage printed before each invocation. Git failure message now includes native exit code. |
| Catch / exits | Console diagnostic includes stage, exception and record path. Reports include failing stage, exception, script stack and final exit code. Failed preflight records FAIL. Final integrity failure also prints an explicit diagnostic. |
| GitHub | Local execution does not probe `gh` authentication or fetch hosted artifacts. `Publish` still requires authentication and all existing publication prerequisites. No GitHub configuration was read. |
| Publication | Selective staging, source preservation, commit/push checks, bounded polling, artifact digest checks and scientific comparison remain in the existing optional interface; none was executed. |
| Scientific stages | Regression, compilation, analytical validation, historical review, capture, controlled diagnostics, complete production/repeat verification, audits, investigation and finalization retained. |

Ordinary PowerShell parameter-binding and `#requires` failures occur before
script execution and cannot be recorded by its own handler. Runtime or filesystem
failure preventing the handler from writing likewise requires launcher logs.
The repair does not claim to intercept those external failures.

## Executed checks and limitations

Evidence root:
`results/phase2d/step32-repair-20261031-181855-e9d0f395`.
New attempts are retained in `attempts-7859bb3df2344b588ae90d99f7220ec9`.

* Supplied PowerShell executable: launch failed with “The file cannot be accessed
  by the system.” Both syntax/version and host invocation were attempted, the
  latter with the supplied STEP 31E EvidenceRoot, fresh OutputRoot and no Publish.
  Consequently actual parameter acceptance and PS7 execution remain unverified.
* Available Windows PowerShell 5.1 parser: zero syntax errors, retained in
  `syntax-check.json` (and final parser record). This is only a static check.
* Existing `.venv` Python: every attempted command exited **103**, reporting no
  Python at the configured Python311 base path. Python 3.11, complete pytest,
  compileall, analytical validation, historical diagnostics, capture, controlled
  local replay and complete production verification were attempted. None started
  Python. Downstream audit/investigation/finalization attempts also failed at
  startup; no numerical result or passing hash-bound checkpoint was produced.
* Added regression tests exercise the real Run-Python wrapper with a child native
  exit 2, verify visible stage/exit diagnostics and retained log/JSON, and check
  dependency declaration/preflight ordering. These tests remain **UNEXECUTED**.
* Independently checked all **362** recorded analysis/raw hashes in supplied
  STEP 31E evidence-sha256.json: zero mismatches. This verifies local byte identity,
  not hosted ZIP authenticity. Before/after assessment hashes are retained.
* Git fsck passed. HEAD remains `11c2b1347c7b5359bec0a56e95cc2aa46f03660c`,
  branch `codex/phase2d-upstream-attribution`, index empty, `.venv` ignored.
  An intermediate diff check found an extra final blank line introduced during
  editing; that was removed and the final check is recorded separately.
* Launching the optional repair-validation script was denied by the local script
  execution policy. No policy was changed. Native verification attempts were
  recorded through ordinary inline shell commands instead.

## Scientific status and remaining work

All historical failures remain. STEP 31E records reference/SciPy frozen and
regenerated row-3 failures, NumPy frozen row-3/row-4 and regenerated row-3 failures.
Production acceptance remains FAIL; numerical causal attribution and hosted
artifact byte authentication remain INCONCLUSIVE. Successful software execution
would not identify a unique numerical mechanism. The original 256-segment
refinement failure remains preserved. Quick geometry remains 512 segments;
rtol=1e-11, atol=1e-13 and refinement limit 1e-4 are unchanged.
Finite-scenario minimax and small synthetic holdouts do not establish robust
outperformance, continuum peak certification or confinement validation.

After ordinary host maintenance restores the supplied PS7 and existing Python
3.11 environment, install the declared development dependencies using that
environment and rerun the host without Publish into another fresh output.
Require complete pytest and compilation, analytical validation, quick experiment,
independent audit, output checks and complete repeat with passing records tied to
result-file SHA256 before declaring a checkpoint verified. The optional
`scripts/phase2d_step32_repair_validate.ps1` records separate verification attempts
on an ordinary host where scripts are permitted.

Remaining hosted requirements include authenticating original archive digests
against extracted bytes, resolving worker/source provenance, and executing and
reviewing all four capture/replay cohorts and reciprocal comparisons at unchanged
gates. Local source inspection cannot establish hosted agreement. No commit,
push, publication, PR merge or workflow dispatch occurred during this repair.
