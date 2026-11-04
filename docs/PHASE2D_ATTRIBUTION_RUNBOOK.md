# Phase 2D attribution runbook

Run from this research checkout on an ordinary Windows host where the existing
Python 3.11 `.venv` and normal script policy work. Do not bypass policy or replace
the environment to hide a startup failure. No publication is authorized.

```powershell
Set-Location C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization
.\.venv\Scripts\python.exe --version
.\scripts\phase2d_upstream_host.ps1
```

The script verifies checkout identity and branch, requires the 247 historical
files, inventories existing work, creates a timestamp/GUID output directory,
and stops at a failed required gate. Its finally block preserves logs, hashes,
preexisting-file verification and a machine-readable report. Launcher failure
is INCONCLUSIVE. An executed validation violation is FAIL. Local PASS never
means production cross-platform agreement or causal identification.

The required sequence is full tests, compilation, analytical validation, exact
input capture, sealed solve/regenerated solve/field/reference experiments, full
second diagnostic run, comparison, then `phase2c_verify.py` with a fresh output
root, fault audit, legacy scientific comparison, geometry investigation and finalization. The production verifier includes fresh quick
execution, output checks, independent audit, study, complete quick/study repeat,
training audit and result-SHA256 checks. Original README evidence paths are
preserved. The historical comparison failures remain authoritative until actual
new production comparisons establish otherwise.

For individual experiments, choose a new output name every time:

```powershell
$py = '.\.venv\Scripts\python.exe'
$run = 'results/phase2d/upstream-manual-' + [guid]::NewGuid().ToString('N')
& $py scripts/phase2d_upstream.py prepare --output "$run/sealed"
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed; retain evidence' }
$inputFile = "$run/sealed/inputs.json"
$digest = (Get-FileHash -LiteralPath $inputFile -Algorithm SHA256).Hash.ToLowerInvariant()
& $py scripts/phase2d_upstream.py run --input $inputFile --input-sha256 $digest --output "$run/worker"
if ($LASTEXITCODE -ne 0) { throw 'Attribution gate incomplete or failed; retain evidence' }
& $py scripts/phase2d_upstream.py run --input $inputFile --input-sha256 $digest --output "$run/repeat"
if ($LASTEXITCODE -ne 0) { throw 'Repeated attribution failed; retain evidence' }
& $py scripts/phase2d_upstream.py compare --input-sha256 $digest --reference "$run/worker" --current "$run/repeat" --output "$run/comparison"
if ($LASTEXITCODE -ne 0) { throw 'Comparison failed; retain evidence' }
```

Inspect `status.json`, `manifest.json`, `environment.json`, source fingerprints,
`input-comparisons.json`, `frozen-solve.json`, `regenerated-solve.json`,
`frozen-fields.json` and `independent-fields.json`. Inputs and currents are hex
binary64 arrays; decode using `upstream_attribution.unpack`, never a lossy JSON
decimal conversion. Scientific reports must bind the actual result SHA256 and
retain failed records. Never substitute fine-grid audit matrices for coarse M/y.

The restricted PR/manual workflow `.github/workflows/phase2d-upstream-attribution.yml`
prepares a Windows seal and four independent workers: Windows reference, Linux
reference, Linux NumPy sensitivity and Linux SciPy sensitivity. It retains each
worker's diagnostics and independent full production run on failure. Comparison
steps retain all three Windows/Linux diagnostic and production comparisons.
Existing frozen and production workflows remain unchanged. This workflow has
not been dispatched or validated here. Dispatch requires a separately authorized
publication of these files; no push or PR is part of this continuation.

Interpret the stages separately. Identical M/y with differing currents localizes
the effect to the numerical solve path. Differing regenerated M/y requires
following geometry, field projection and scaling/assembly records, then testing
swaps rather than naming a library from a version correlation. Identical currents
with differing fixed field components localizes an evaluation contribution.
Use the actual row-3 and row-4 ratios, denominator sensitivity and reference
errors to determine whether an observed difference explains the failed bounds.
Driver/rounding sensitivity is supporting evidence, not a production correction.

Keep `rtol=1e-11`, `atol=1e-13`, refinement 1e-4, current bounds and solver settings.
An active-bound reference marked INCONCLUSIVE requires independent constrained
optimization before acceptance. A diagnostic PASS cannot override a production
FAIL. Overall scientific scope remains PARTIAL even after numerical agreement.

Review remediation is documented in `PHASE2D_REVIEW_REMEDIATION.md`. The host
script now requires branch `codex/phase2d-upstream-attribution`. Comparisons
require `--input-sha256` from the original seal, complete manifests and exact
serialized inputs. Hosted dependency setup also requires the new
`scripts/phase2d_dependencies.py`; include it in any later selective staging.
It uses exact package pins and records resolver download hashes. Availability
of these wheels on all four cohorts remains unverified; there is no fallback.

For historical source provenance, use a fresh output path:

```powershell
& $py scripts/phase2d_upstream.py historical --reference results/ci/phase2d-hosted-investigation-41195815229/phase2d-windows-reference --output "$run/historical-source-review"
```

That command verifies the historical manifest and original Git source objects.
It deliberately returns INCONCLUSIVE/nonzero while authenticated archive/run
evidence is unavailable. Hash agreement alone cannot authenticate a download.
