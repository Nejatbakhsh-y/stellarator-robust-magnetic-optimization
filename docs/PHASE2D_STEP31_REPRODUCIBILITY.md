# Phase 2D Step 31 reproducibility

Status: **PARTIAL / Python execution blocked**. Tests executed: **0**.
The required `.venv/Scripts/python.exe` returns 103 because its configured base
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe` is unavailable.
No replacement interpreter, environment recreation or security bypass was used.

Actual attempts are recorded in
`results/phase2d/step31-local-review-20261031/python-attempts.json`:
full pytest, compileall, new diagnostic, analytical validation, fresh quick run,
independent audit, output check and full Phase 2C verification. Each exited 103
before Python startup. There is no new passing result SHA256 or verified checkpoint.

PowerShell read-only inspection did execute: all 361 source inventory hashes,
all entries in 18 manifests, worker/production statuses, direct seal byte
equality, source fingerprint comparison, solver summaries, and all failed scalar
tolerance comparisons. The resulting analysis is explicitly labeled as an
inspection, with BLOCKED_PYTHON execution status. A manifest hashes that analysis,
status, source inventory and attempt logs. Supplied absolute paths are retained
in the original source-hashes.json; the new Python diagnostic relocates entries
under raw/ and rejects path escape, missing, extra and modified evidence.

Prepared regression tests cover inventory integrity, missing/extra evidence,
seal fingerprints, signed zero versus numerical equality, malformed/nonfinite
arrays and scalars, missing solver results, input contracts, denominator guard
and differential amplification, row 3, row 4, incorrect PASS classification,
and independent Decimal/compensated calculations. The downloaded-input test
skips explicitly if the latest Phase 2D bundle is unavailable. None has passed here.

After the existing environment is restored on the ordinary host, run from this
checkout in PowerShell. These commands use fresh directories and perform no
publication. Expected diagnostic exit 1 means investigation completion with
retained scientific failure; exit 2 means incomplete/invalid evidence or an
execution error. Read status.json in either case. A completion record remains
PARTIAL and must not be presented as production acceptance.

```powershell
$python = '.\.venv\Scripts\python.exe'
$evidence = 'results/phase2d/step31-20261031-165725-a14c217c'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$diagnostic = "results/phase2d/step31-diagnostic-$stamp"
$validation = "results/phase2d/step31-validation-$stamp"
if ((Test-Path $diagnostic) -or (Test-Path $validation)) { throw 'Choose fresh output paths' }
& $python --version
if ($LASTEXITCODE -ne 0) { throw 'Existing Python 3.11 environment unavailable' }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& $python -m compileall -q src scripts tests
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
& $python scripts/phase2d_step31_diagnose.py --evidence-root $evidence --output $diagnostic
$diagnosticExit = $LASTEXITCODE
Get-Content "$diagnostic/status.json"
if ($diagnosticExit -ne 1) { throw 'Diagnostic incomplete; inspect evidence error' }
# Existing verifier includes analytical validation, quick experiment, independent
# audit, output checks, full quick/study repeats and result SHA256-linked gates.
& $python scripts/phase2c_verify.py --output $validation
if ($LASTEXITCODE -ne 0) { throw 'Full verification failed; retain all logs' }
& $python scripts/phase2c_fault_audit.py --root $validation
if ($LASTEXITCODE -ne 0) { throw 'Independent fault audit failed' }
Get-Content "$validation/gate.json"
Get-Content "$validation/reproducibility.json"
Get-FileHash "$validation/quick/results.json" -Algorithm SHA256
Get-FileHash "$validation/study/study.json" -Algorithm SHA256
```

Verify diagnostic manifests independently:

```powershell
$manifest = Get-Content "$diagnostic/manifest.json" -Raw | ConvertFrom-Json
foreach ($entry in $manifest.PSObject.Properties) {
    $actual = (Get-FileHash -LiteralPath (Join-Path $diagnostic $entry.Name) -Algorithm SHA256).Hash
    if ($actual -ne $entry.Value) { throw "Manifest mismatch: $($entry.Name)" }
}
```

`analysis.json` contains every original production/frozen comparison, exact
array comparisons using the existing binary64 unpacker, solver metrics, field
checks, 60/90-digit ratios, reciprocal model/current swaps and their interaction.
`source-sha256.json` binds all source evidence; `manifest.json` binds the output
files. Worker source fingerprints are compared to the supplied commit with
differences reported, rather than silently relabeling the observed source commit.
Authentication of the run and resolution of that mismatch remain separate work.
