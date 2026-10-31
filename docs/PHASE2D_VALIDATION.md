# Phase 2D validation record

Status: **PARTIAL / blocked**, not a verified research checkpoint.

Executed in this session:

| Command/check | Actual result |
|---|---|
| `git branch --show-current`, `git rev-parse HEAD` | requested branch and baseline confirmed |
| `.venv\Scripts\python.exe --version` | failed: configured Python 3.11 executable missing |
| `py -0p` | no installed Python registrations found |
| `python --version` | Python 3.13.9; not substituted for required environment |
| PowerShell SHA256/length verification of supplied CSV | 247 entries, zero mismatches |
| Read supplied cross-platform comparison records | Windows/Linux FAIL, NumPy sensitivity FAIL, SciPy sensitivity PASS |
| `git cat-file -t 23279366436b37a6c6715556ff266f1384d183ce` | return code 1; object unavailable |
| `scripts/phase2d_investigate.ps1` | return code 1, PowerShell execution policy rejection |
| `Add-Type -Path scripts/phase2d_reference.cs -ReferencedAssemblies System.Numerics` plus scalar evaluation | return code 0; compiled; exact R=0.5 smoke example |
| PowerShell parser AST inspection of the prepared runner | return code 0; zero static parse errors; does not execute the runner |
| Final SHA256/length recheck after additions | return code 0; all 247 supplied entries unchanged |
| `git diff --exit-code 5a415c457e9f60c983a52d309a242583d73b40b6 -- results` before new records | return code 0; historical tracked results unchanged |

New pytest count: **0 executed**. Full regression, analytical validation,
geometry validation, quick experiment, independent audit, output checks,
full repeat, Phase 2D studies, source fingerprints, Python compilation and
scientific report consistency gates have NOT passed in this session.
The independent reference runner has not executed any archived outage.
One combined shell verification command initially failed to parse because
it piped directly from a `foreach` statement. The corrected verification
command returned 0. This command-construction error did not execute or
modify the investigation runner or evidence.

Required remediation: restore the existing `.venv` Python 3.11 installation.
The prepared PowerShell investigation runner also needs an administrator-
approved script execution mechanism; no execution-policy bypass was attempted.
GitHub access remains subject to AGENTS.md and was not attempted through gh.

The new workflow prepares the four requested cohorts using the unchanged
Phase 2C scientific calculation and fail-closed comparison pipeline, writing
fresh Phase 2D artifact paths. It is an investigation workflow, not a separately
corrected numerical benchmark. Missing/incomplete workers fail existing contracts;
manifests and scientific tolerances are retained. Artifact upload uses `always()`.
It has not run or undergone a hosted workflow validation. Failures are expected
to remain until a justified upstream correction is established.

## Resumed Python investigation

The Python implementation replaces the runner dependency on PowerShell script
execution. No policy change is required or attempted. The old runner is retained.
New tests cover independent scalar reference values, negative recovery and the
denominator guard, inventory completeness/tampering, path escape rejection,
nonfinite JSON rejection and retention of missing/extra differing fields.
These tests are prepared, **not passed**.

All following actual `.venv/Scripts/python.exe` attempts returned **103**:

* `--version`
* `-m pytest -q`
* `-m stellarator_robust.cli validate`
* `-m compileall -q src scripts tests`
* `scripts/phase2d_investigate.py --output results/phase2d/python-investigation`

The launcher reports that it cannot find its configured Python at
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`.
A separate `Test-Path` for that exact configured path produced Access is
denied; this does not establish that the installed interpreter is absent.
The required remedy for this session is read/execute access to the configured
Python 3.11 installation and its runtime files through the sandbox, or an
authorized accessible project environment using that installed interpreter.
Do not substitute Python 3.13 or change script execution policy.

Exact argument lists, return codes and launcher errors are retained in
`results/phase2d/resume-access-checks.json`. No tests were collected and no
scientific calculation started. Remaining expensive studies were not launched
repeatedly through a launcher already known to fail. All earlier unexecuted
validation requirements remain outstanding. Full verification, verified
commits and publication remain pending; no hosted results are asserted.

## 2026-10-30 remediation continuation

Latest execution status: **PARTIAL / local execution blocked**. See
[the versioned remediation record](../results/phase2d/remediation-20261030-193501/STATUS.md)
for exact commands, historical hashes, I/O changes and outstanding phases. The
current attempt executed zero tests: the required .venv launcher exited 103 before
Python startup. All 247 preserved inputs match their hashes. Existing investigation
records contain 84 agreed/converged audits and 24 swaps, with zero manifest hash
mismatches; they were inspected, not recalculated here. Earlier statements that
swaps were merely prepared describe the earlier attempt and are superseded by
this inspection of the preserved investigation. No physical or numerical correction,
new hosted pass, verified checkpoint, commit or publication is claimed.
