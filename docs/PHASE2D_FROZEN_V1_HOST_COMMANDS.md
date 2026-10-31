# Phase 2D frozen v1: exact regular-host execution

Use the already verified Windows Python 3.11.9 environment from ordinary
PowerShell. No interpreter installation, permission change, alternate runtime,
PowerShell execution-policy change or sandbox workaround is required.
All output directories below are fresh. Do not rerun against existing outputs.
The new code has been developed/reviewed but not executed inside Codex.

## Tests, independent controls and full scientific replay

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
$ErrorActionPreference = 'Stop'
if ((git branch --show-current) -ne 'codex/phase2d-cross-platform-reproducibility') { throw 'Wrong branch' }
$py = '.\.venv\Scripts\python.exe'
$run = 'results/ci/phase2d-frozen-host-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
New-Item -ItemType Directory -Path $run | Out-Null
Start-Transcript -Path "$run/host-transcript.txt"

& $py -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'New regression suite failed; inspect before continuing' }
& $py -m compileall -q src scripts tests
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
& $py -m stellarator_robust.cli validate
if ($LASTEXITCODE -ne 0) { throw 'Analytical validation failed' }

& $py scripts/phase2d_frozen.py seal --source benchmarks/phase2d-frozen-v1 --output "$run/shared-inputs"
if ($LASTEXITCODE -ne 0) { throw 'Frozen-input sealing failed' }
& $py scripts/phase2d_frozen.py run --fixture "$run/shared-inputs" --output "$run/windows" --cohort windows-reference
if ($LASTEXITCODE -ne 0) { throw 'Frozen diagnostic failed; retain record.json and inspect all component/reference failures' }

# Original independent all-file inventory, 84 reference audits and 24 swaps.
# Its documented exit code 1 means scientific disagreement remains unresolved.
& $py scripts/phase2d_investigate.py --evidence results/ci/phase2d-inputs/run-41061184709 --output "$run/archive-investigation"
$investigationExit = $LASTEXITCODE
$investigation = Get-Content -LiteralPath "$run/archive-investigation/reference-audit.json" -Raw | ConvertFrom-Json
if ($investigationExit -ne 1 -or $investigation.status -ne 'INVESTIGATION_COMPLETE') { throw 'Archive investigation did not complete' }

# Unchanged production benchmark: full quick/study, independent audits,
# actual second quick/study, strict numerical repeat and training audit.
& $py scripts/phase2c_verify.py --output "$run/science"
if ($LASTEXITCODE -ne 0) { throw 'Full numerical pipeline failed' }
& $py scripts/phase2c_fault_audit.py --root "$run/science"
if ($LASTEXITCODE -ne 0) { throw 'Independent production metric audit failed' }
& $py scripts/phase2c_legacy_compare.py --root "$run/science"
if ($LASTEXITCODE -ne 0) { throw 'Unchanged-science regression failed' }
& $py scripts/phase2b_investigate.py --output "$run/science/investigation" --corrected "$run/science"
if ($LASTEXITCODE -ne 0) { throw 'Geometry/peak investigation failed' }
& $py scripts/phase2c_finalize.py --output "$run/science"
if ($LASTEXITCODE -ne 0) { throw 'Manifest/source integrity verification failed' }

Stop-Transcript
Write-Output "Inspect all records under $run; scientific status remains PARTIAL"
```

If a command fails, preserve its output directory and transcript, report its
actual exit code, and fix the specific defect/discrepancy. Do not delete output,
change thresholds, treat a missing record as PASS, or continue toward a verified
publication without reviewing the failure. `record.json` retains a FAIL record
and partial outputs when calculation raises an exception. The frozen diagnostic
can fail a reference gate even when two workers agree with one another.

The full replay commands do not write `results/quick`, `results/phase2`,
`results/phase2b`, or `results/phase2c`. The original 247-file evidence directory
is read-only input. Existing earlier Phase 2D investigation records are retained.
The Windows `record.json` is local evidence, not a Linux/hosted result.

## Hosted interpretation and later publication

After host tests and code review, preserve the execution records and all 247
original files durably. `.github/workflows/phase2d-frozen-inputs.yml` prepares
one sealed Windows artifact and supplies it unchanged to all four requested
cohorts. It compares all three Linux workers against Windows, retaining complete
record differences even when completed workers fail a local reference check.
The separate existing full-science workflow remains unchanged and can still
fail its known production ratio comparisons; a diagnostic PASS does not exempt
those fields or override that failure.

Review the existing uncommitted work and its snapshot before choosing files for
a commit. Do not blindly discard or overwrite earlier Phase 2D work. Once the
investigation has an executed, reviewed checkpoint, ordinary authenticated
PowerShell publication commands are:

```powershell
git status --short
git diff --check
# Stage the reviewed implementation, frozen fixture, reports and durable evidence.
git commit -m 'Add frozen-input Phase 2D field and optimizer attribution diagnostics'
git push -u origin codex/phase2d-cross-platform-reproducibility
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/phase2c-stable-fault-metrics --head codex/phase2d-cross-platform-reproducibility --draft --title 'Phase 2D frozen-input reproducibility investigation (PARTIAL)' --body-file docs/PHASE2D_FROZEN_V1_REPORT.md
gh run list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --branch codex/phase2d-cross-platform-reproducibility
```

Use `gh pr create` only if a Phase 2D PR does not already exist; otherwise update
its branch normally. Never merge PRs #1-#5 or any new draft, force-push, inspect
prohibited GitHub CLI configuration inside Codex, or infer cross-platform
success before completed actual comparisons. No publication was attempted by
this continuation while the new tests and references remain unexecuted.
