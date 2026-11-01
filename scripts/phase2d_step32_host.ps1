#requires -Version 7.0
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$EvidenceRoot,
  [Parameter(Mandatory=$true)][string]$OutputRoot,
  [switch]$Publish
)
$ErrorActionPreference = 'Stop'
$stage = 'initialization'
try {
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $repo
$branch = 'codex/phase2d-upstream-attribution'
$repository = 'Nejatbakhsh-y/stellarator-robust-magnetic-optimization'
$py = Join-Path $repo '.venv/Scripts/python.exe'
$out = [IO.Path]::GetFullPath($OutputRoot, $repo)
$evidence = (Resolve-Path -LiteralPath $EvidenceRoot).Path
if (-not (Test-Path -LiteralPath $evidence -PathType Container)) { throw 'EvidenceRoot must be a directory' }
if (Test-Path -LiteralPath $out) { throw 'OutputRoot must be fresh' }
if (-not $out.StartsWith($repo + [IO.Path]::DirectorySeparatorChar)) { throw 'Output must be inside research checkout' }
if ($out.StartsWith($evidence + [IO.Path]::DirectorySeparatorChar) -or $evidence.StartsWith($out + [IO.Path]::DirectorySeparatorChar)) { throw 'Evidence and output must be disjoint' }
New-Item -ItemType Directory -Path $out | Out-Null
} catch {
  # Never write into a rejected/existing output or evidence directory.
  $failureRoot = Join-Path $PSScriptRoot ("../results/phase2d/step32-preflight-failure-" + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $failureRoot | Out-Null
  $failure = @{ stage=$stage; error=$_.Exception.Message; exception=$_.ToString(); overall_scientific_status='PARTIAL'; local_validation='FAIL'; preflight='FAIL'; exit_code=2 }
  $failure | ConvertTo-Json | Set-Content (Join-Path $failureRoot 'execution.json') -Encoding utf8
  [Console]::Error.WriteLine("STEP32 stage=$stage failed: $_; record=$failureRoot/execution.json")
  exit 2
}
$report = [ordered]@{ implementation='UNVERIFIED'; local_validation='INCONCLUSIVE'; hosted_execution='NOT_EXECUTED'; evidence_authenticity='INCONCLUSIVE'; numerical_causal_attribution='INCONCLUSIVE'; production_acceptance='FAIL'; overall_scientific_status='PARTIAL'; steps=@(); historical_preservation='INCONCLUSIVE' }
function Save-Json($Path, $Value) { $Value | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding utf8 }
function Git-Read([string[]]$Arguments) {
  $value = & git @Arguments
  if ($LASTEXITCODE) { throw "Git failed with exit ${LASTEXITCODE}: $Arguments" }
  return $value
}
function Run-Python([string]$Name, [string[]]$Arguments) {
  $script:stage = $Name
  Write-Host "STEP32 stage=$Name"
  & $py @Arguments *> (Join-Path $out "$Name.log")
  $rc = $LASTEXITCODE
  $report.steps += @{ name=$Name; arguments=$Arguments; exit_code=$rc }
  Save-Json (Join-Path $out 'execution.json') $report
  if ($rc) {
    if ($Name -eq 'hosted-comparison') {
      $report.hosted_scientific_comparison = if ($rc -eq 1) { 'FAIL' } else { 'INCONCLUSIVE' }
      if ($rc -eq 1) { return }
      throw 'Hosted comparison evidence/validation failed; local validation status retained'
    }
    $report.local_validation = if ($rc -eq 103) { 'INCONCLUSIVE' } else { 'FAIL' }
    throw "$Name failed with exit $rc; evidence retained"
  }
}
function Inventory([string]$Root) {
  $record = [ordered]@{}
  Get-ChildItem -LiteralPath $Root -Recurse -File | ForEach-Object {
    $record[$_.FullName.Substring($Root.Length+1).Replace('\','/')] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  return $record
}
function Download-VerifiedArtifact($Artifact, [string]$Destination) {
  if ($Artifact.expired -or $Artifact.digest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Expired artifact or missing authenticated digest' }
  $zip = Join-Path $Destination ($Artifact.name + '.zip')
  $psi = [Diagnostics.ProcessStartInfo]::new('gh')
  $psi.UseShellExecute=$false; $psi.RedirectStandardOutput=$true; $psi.RedirectStandardError=$true; $psi.CreateNoWindow=$true
  foreach ($arg in @('api',"repos/$repository/actions/artifacts/$($Artifact.id)/zip")) { $psi.ArgumentList.Add($arg) }
  $proc = [Diagnostics.Process]::Start($psi)
  $stream = [IO.File]::Create($zip)
  try { $proc.StandardOutput.BaseStream.CopyTo($stream) } finally { $stream.Dispose() }
  $err = $proc.StandardError.ReadToEnd(); $proc.WaitForExit()
  if ($proc.ExitCode) { throw "Artifact download failed: $err" }
  $digest = 'sha256:' + (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($digest -cne $Artifact.digest) { throw 'Hosted ZIP digest mismatch' }
  Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $Destination $Artifact.name)
}
$before = $null; $preexisting = [ordered]@{}; $initialIndex = $null
$stage = 'repository-preflight'
try {
  if ((Git-Read @('rev-parse','--show-toplevel')).Replace('/','\') -ne $repo.Replace('/','\')) { throw 'Repository root mismatch' }
  if ((Git-Read @('remote','get-url','origin')) -notmatch '^https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization(?:\.git)?$') { throw 'Repository identity mismatch' }
  if ((Git-Read @('branch','--show-current')) -ne $branch) { throw 'Research branch required' }
  $report.starting_head = Git-Read @('rev-parse','HEAD')
  $initialIndex = Git-Read @('diff','--cached','--binary')
  Git-Read @('status','--porcelain=v1','--untracked-files=all') | Set-Content (Join-Path $out 'preexisting-status.txt')
  $paths = Git-Read @('ls-files','--cached','--others','--exclude-standard')
  foreach ($path in $paths) {
    $full = Join-Path $repo $path
    if ((Test-Path -LiteralPath $full -PathType Leaf) -and -not $full.StartsWith($out + [IO.Path]::DirectorySeparatorChar)) {
      $preexisting[$path] = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
    }
  }
  Save-Json (Join-Path $out 'preexisting-sha256.json') $preexisting
  $stage = 'evidence-preflight'
  $before = Inventory $evidence
  if ($before.Count -eq 0) { throw 'Missing historical evidence' }
  Save-Json (Join-Path $out 'historical-before.json') $before
  $stage = 'publication-preflight'
  # Local runs do not access GitHub; publication still requires authentication.
  $githubAvailable = $false
  if ($Publish -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    & gh auth status *> (Join-Path $out 'github-auth.log')
    $githubAvailable = $LASTEXITCODE -eq 0
  }
  $report.github_authentication = if ($githubAvailable) { 'PASS' } else { 'NOT_CHECKED_LOCAL_OR_UNAVAILABLE' }
  if (-not $githubAvailable -and $Publish) { throw 'GitHub authentication unavailable; no publication' }
  if ($githubAvailable) {
  try {
  $originalMetadata = & gh api "repos/$repository/actions/runs/41231422708/artifacts?per_page=100"
  if ($LASTEXITCODE) { throw 'Original artifact metadata unavailable' }
  $originalMetadata | Set-Content (Join-Path $out 'original-hosted-artifacts.json')
  & gh api "repos/$repository/actions/runs/41231422708/jobs?per_page=100" | Set-Content (Join-Path $out 'original-hosted-jobs.json')
  if ($LASTEXITCODE) { throw 'Original jobs unavailable' }
  $originalArtifacts = ($originalMetadata | ConvertFrom-Json).artifacts
  if ($originalArtifacts.Count -ne 7) { throw 'Original artifact inventory incomplete' }
  $originalArchives = Join-Path $out 'original-hosted-archives'
  New-Item -ItemType Directory $originalArchives | Out-Null
  foreach ($artifact in $originalArtifacts) {
    Download-VerifiedArtifact $artifact $originalArchives
    $localRoot = Join-Path $repo "results/phase2d/step31-20261031-165725-a14c217c/raw/$($artifact.name)"
    $actual = Inventory (Join-Path $originalArchives $artifact.name)
    $local = Inventory $localRoot
    if ($actual.Count -ne $local.Count) { throw 'Original extracted artifact file inventory differs' }
    foreach ($name in $actual.Keys) { if ($actual[$name] -cne $local[$name]) { throw "Original hosted/local byte mismatch: $name" } }
  }
  $report.original_hosted_artifact_authenticity = 'PASS'
  } catch {
    $report.original_hosted_artifact_authenticity = 'INCONCLUSIVE'
    $report.original_hosted_artifact_error = $_.Exception.Message
    if ($Publish) { throw }
  }
  } else {
    $report.original_hosted_artifact_authenticity = 'INCONCLUSIVE'
  }
  Run-Python 'python-version' @('-c', 'import sys; assert sys.version_info[:2] == (3,11); print(sys.version)')
  Run-Python 'dependency-preflight' @('-c', 'import numpy, scipy, matplotlib, pytest, threadpoolctl; print(threadpoolctl.__version__)')
  $report.preflight = 'PASS'
  Run-Python 'tests' @('-m','pytest','-q')
  Run-Python 'compilation' @('-m','compileall','-q','src','scripts','tests')
  Run-Python 'analytical' @('-m','stellarator_robust.cli','validate')
  Run-Python 'historical-review' @('scripts/phase2d_step32.py','historical','--inputs','results/phase2d/step31-20261031-165725-a14c217c/raw','--output',"$out/historical-review")
  Run-Python 'capture' @('scripts/phase2d_step32.py','capture','--output',"$out/capture")
  Run-Python 'local-controlled' @('scripts/phase2d_step32.py','local','--inputs',"$out/capture",'--output',"$out/local")
  # Fresh quick, independent audit, output checks, study and complete repeats;
  # all reports bind exact result hashes. Historical default paths are preserved.
  Run-Python 'full-production-verification' @('scripts/phase2c_verify.py','--output',"$out/production")
  Run-Python 'fault-audit' @('scripts/phase2c_fault_audit.py','--root',"$out/production")
  Run-Python 'legacy-comparison' @('scripts/phase2c_legacy_compare.py','--root',"$out/production")
  Run-Python 'investigation' @('scripts/phase2b_investigate.py','--output',"$out/production/investigation",'--corrected',"$out/production")
  Run-Python 'finalization' @('scripts/phase2c_finalize.py','--output',"$out/production")
  $report.local_validation = 'PASS'
  $report.implementation = 'LOCAL_GATES_PASSED'
  if ($Publish) {
    $allowed = @('scripts/phase2d_step32.py','scripts/phase2d_step32_host.ps1','tests/test_phase2d_step32.py','docs/PHASE2D_STEP32_CAUSAL_ATTRIBUTION_REPORT.md','docs/PHASE2D_STEP32_EXPERIMENT_PROTOCOL.md','.github/workflows/phase2d-step32-causal.yml')
    $staged = @(Git-Read @('diff','--cached','--name-only'))
    if (@($staged | Where-Object { $_ -and $_ -notin $allowed }).Count) { throw 'Unrelated staged changes; publication refused' }
    foreach ($path in $preexisting.Keys) {
      if ((Get-FileHash -LiteralPath (Join-Path $repo $path) -Algorithm SHA256).Hash -ne $preexisting[$path]) { throw "Preexisting file changed: $path" }
    }
    if ((ConvertTo-Json (Inventory $evidence) -Compress) -ne (ConvertTo-Json $before -Compress)) { throw 'Historical evidence changed' }
    Git-Read @('diff','--check') | Out-Null
    & git add -- @allowed
    if ($LASTEXITCODE) { throw 'Selective staging failed' }
    & git diff --cached --check
    if ($LASTEXITCODE) { throw 'Staged diff invalid' }
    & git commit -m 'Add STEP 32 controlled reciprocal causal diagnostics'
    if ($LASTEXITCODE) { throw 'Commit failed' }
    $commit = Git-Read @('rev-parse','HEAD'); $report.published_commit = $commit
    & git push origin "HEAD:refs/heads/$branch"
    if ($LASTEXITCODE) { throw 'Push failed' }
    # Push trigger, never dispatch; no PR creation or merging.
    $deadline = [DateTime]::UtcNow.AddMinutes(210)
    $run = $null
    do {
      $runs = & gh run list --repo $repository --workflow phase2d-step32-causal.yml --commit $commit --json databaseId,headSha,status,conclusion --limit 20
      if ($LASTEXITCODE) { throw 'Workflow listing failed' }
      $run = @($runs | ConvertFrom-Json | Where-Object { $_.headSha -eq $commit }) | Select-Object -First 1
      if ($run -and $run.status -eq 'completed') { break }
      Start-Sleep -Seconds 30
    } while ([DateTime]::UtcNow -lt $deadline)
    if (-not $run -or $run.status -ne 'completed') { $report.hosted_execution='TIMEOUT'; throw 'Bounded workflow polling timed out' }
    $report.hosted_execution = $run.conclusion; $report.run_id = $run.databaseId
    & gh api "repos/$repository/actions/runs/$($run.databaseId)/jobs?per_page=100" | Set-Content (Join-Path $out 'hosted-jobs.json')
    if ($LASTEXITCODE) { throw 'Job metadata unavailable' }
    $metadata = & gh api "repos/$repository/actions/runs/$($run.databaseId)/artifacts?per_page=100"
    if ($LASTEXITCODE) { throw 'Artifact metadata unavailable' }
    $metadata | Set-Content (Join-Path $out 'hosted-artifacts.json')
    $artifacts = ($metadata | ConvertFrom-Json).artifacts
    $hosted = Join-Path $out 'hosted'; New-Item -ItemType Directory $hosted | Out-Null
    foreach ($artifact in $artifacts) {
      if ($artifact.name -notmatch '^step32-' -or $artifact.expired) { throw 'Unexpected or expired hosted artifact' }
      Download-VerifiedArtifact $artifact $hosted
    }
    $report.evidence_authenticity='PASS'
    $normalized = Join-Path $out 'hosted-evidence'; New-Item -ItemType Directory $normalized | Out-Null
    foreach ($stage in @('capture','replay')) {
      foreach ($cohort in @('windows-reference','linux-reference','linux-numpy-sensitivity','linux-scipy-sensitivity')) {
        $matches = @($artifacts | Where-Object { $_.name -like "step32-$stage-$cohort-$($run.databaseId)-*" })
        if ($matches.Count -ne 1) { throw 'Missing or ambiguous required artifact' }
        Copy-Item -LiteralPath (Join-Path $hosted $matches[0].name) -Destination (Join-Path $normalized "$stage-$cohort") -Recurse
      }
    }
    Run-Python 'hosted-comparison' @('scripts/phase2d_step32.py','compare','--inputs',$normalized,'--expected-head',$commit,'--output',"$out/hosted-comparison")
  }
} catch {
  $report.error = $_.Exception.Message
  $report.failed_stage = $stage
  $report.exception = $_.ToString()
  $report.script_stack_trace = $_.ScriptStackTrace
  if (-not $report.preflight) { $report.preflight = 'FAIL' }
  if ($report.local_validation -ne 'FAIL') { $report.local_validation = 'FAIL' }
  [Console]::Error.WriteLine("STEP32 stage=$stage failed: $_; execution record=$out/execution.json")
} finally {
  if ($before) {
    $after = Inventory $evidence
    Save-Json (Join-Path $out 'historical-after.json') $after
    $report.historical_preservation = if ((ConvertTo-Json $after -Compress) -ceq (ConvertTo-Json $before -Compress)) { 'PASS' } else { 'FAIL' }
  }
  $changed = @()
  foreach ($path in $preexisting.Keys) {
    $full = Join-Path $repo $path
    if (-not (Test-Path -LiteralPath $full) -or (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash -ne $preexisting[$path]) { $changed += $path }
  }
  $report.preexisting_changed = $changed
  if (-not $Publish -and $null -ne $initialIndex) {
    $report.index_preserved = ((Git-Read @('diff','--cached','--binary') | Out-String) -ceq ($initialIndex | Out-String))
  }
  & git diff --check *> (Join-Path $out 'git-diff-check.log')
  $report.diff_check_exit = $LASTEXITCODE
  $report.exit_code = if ($report.error -or $report.historical_preservation -ne 'PASS' -or $report.preexisting_changed.Count -or $report.diff_check_exit -or $report.index_preserved -eq $false) { 2 } else { 0 }
  if ($report.exit_code -and -not $report.error) {
    $report.failed_stage = 'preservation-and-git-integrity'
    $report.error = 'Final preservation or Git integrity checks failed; see execution.json'
    [Console]::Error.WriteLine("STEP32 stage=$($report.failed_stage) failed; exit=2; record=$out/execution.json")
  }
  Save-Json (Join-Path $out 'assessment.json') $report
  Save-Json (Join-Path $out 'status.json') $report
  Save-Json (Join-Path $out 'execution.json') $report
  foreach ($name in @('environment.json','source-sha256.json','input-sha256.json')) {
    $nested = Join-Path $out "capture/$name"
    if (Test-Path -LiteralPath $nested) { Copy-Item -LiteralPath $nested -Destination (Join-Path $out $name) }
    else { Save-Json (Join-Path $out $name) @{status='NOT_EXECUTED';reason='Capture unavailable; see execution report'} }
  }
  Save-Json (Join-Path $out 'manifest.json') (Inventory $out)
}
if ($report.error -or $report.historical_preservation -ne 'PASS' -or $report.preexisting_changed.Count -or $report.diff_check_exit -or $report.index_preserved -eq $false) { exit 2 }
