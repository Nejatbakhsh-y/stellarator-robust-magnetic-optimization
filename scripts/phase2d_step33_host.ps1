#requires -Version 7.0
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$EvidenceRoot,
  [Parameter(Mandatory=$true)][string]$OutputRoot,
  [switch]$PublishDiagnostic
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
  $failureRoot = Join-Path $PSScriptRoot ("../results/phase2d/step33-preflight-failure-" + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $failureRoot | Out-Null
  $failure = @{ stage=$stage; error=$_.Exception.Message; exception=$_.ToString(); overall_scientific_status='PARTIAL'; local_validation='FAIL'; preflight='FAIL'; exit_code=2 }
  $failure | ConvertTo-Json | Set-Content (Join-Path $failureRoot 'execution.json') -Encoding utf8
  [Console]::Error.WriteLine("STEP33 stage=$stage failed: $_; record=$failureRoot/execution.json")
  exit 2
}
$report = [ordered]@{ implementation='UNVERIFIED'; local_validation='INCONCLUSIVE'; hosted_execution='NOT_EXECUTED'; hosted_workflow_discovery='NOT_EXECUTED'; hosted_scientific_comparison='INCONCLUSIVE'; evidence_authenticity='INCONCLUSIVE'; numerical_causal_attribution='INCONCLUSIVE'; production_acceptance='FAIL'; overall_scientific_status='PARTIAL'; steps=@(); historical_preservation='INCONCLUSIVE' }
function Save-Json($Path, $Value) { $Value | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding utf8 }
function Git-Read([string[]]$Arguments) {
  $value = & git @Arguments
  if ($LASTEXITCODE) { throw "Git failed with exit ${LASTEXITCODE}: $Arguments" }
  return $value
}
function Wait-Step33Run([string]$Commit, [int]$MaxPolls=420, [int]$PollSeconds=30) {
  $script:stage = 'hosted-workflow-discovery'
  $report.hosted_execution = 'INCONCLUSIVE'
  if ($Commit -cnotmatch '^[0-9a-f]{40}$' -or $MaxPolls -lt 1 -or $MaxPolls -gt 420 -or $PollSeconds -lt 0 -or $PollSeconds -gt 60) { throw 'Invalid bounded discovery arguments' }
  $expectedBase = 'codex/phase2d-cross-platform-reproducibility'
  $workflowPath = '.github/workflows/phase2d-step33-causal.yml'
  for ($poll=0; $poll -lt $MaxPolls; $poll++) {
    # Repository REST listing does not depend on default-branch workflow registration.
    # Do not filter by head_sha: PR runs can identify a synthetic merge commit.
    $json = & gh api "repos/$repository/actions/runs?branch=$branch&per_page=100"
    if ($LASTEXITCODE) { throw 'Authenticated workflow listing failed' }
    $listing = ConvertFrom-Json -InputObject ($json -join "`n") -ErrorAction Stop
    if ($null -eq $listing.total_count -or $null -eq $listing.workflow_runs -or $listing.workflow_runs -isnot [array]) { throw 'Malformed workflow listing' }
    # Refuse truncated inventories rather than silently choosing an older candidate.
    if ($listing.total_count -gt 100) { throw 'Workflow listing exceeds bounded inventory; narrow observation required' }
    $runs = @(); $seen = @{}
    foreach ($candidate in $listing.workflow_runs) {
      if ($candidate.path -cne $workflowPath -or $candidate.event -cnotin @('push','pull_request')) { continue }
      if ($candidate.repository.full_name -cne $repository -or $candidate.head_repository.full_name -cne $repository) { throw 'Malformed workflow repository identity' }
      $source = $candidate.head_sha
      if ($candidate.event -ceq 'push') {
        if ($candidate.head_branch -cne $branch -or $source -cne $Commit) { continue }
      } else {
        if ($candidate.pull_requests -isnot [array]) { throw 'Malformed PR association' }
        $prs = @($candidate.pull_requests)
        if ($prs.Count -ne 1) { throw 'Missing or ambiguous PR association' }
        $pr = $prs[0]
        if ($pr.number -ne 7 -or $pr.head.ref -cne $branch -or $pr.base.ref -cne $expectedBase -or $pr.head.sha -cne $Commit) { continue }
        # Run association binds the historical source; current authenticated PR metadata
        # independently confirms repository and branch identity, never substitutes its SHA.
        $prJson = & gh api "repos/$repository/pulls/7"
        if ($LASTEXITCODE) { throw 'Authenticated PR metadata unavailable' }
        $identity = ConvertFrom-Json -InputObject ($prJson -join "`n") -ErrorAction Stop
        if ($identity.number -ne 7 -or $identity.head.ref -cne $branch -or $identity.base.ref -cne $expectedBase -or $identity.head.repo.full_name -cne $repository -or $identity.base.repo.full_name -cne $repository -or $identity.head.sha -cne $Commit) { throw 'PR #7 identity or source commit mismatch' }
        if ($source -cne $Commit) {
          $mergeJson = & gh api "repos/$repository/commits/$source"
          if ($LASTEXITCODE) { throw 'Synthetic merge metadata unavailable' }
          $merge = ConvertFrom-Json -InputObject ($mergeJson -join "`n") -ErrorAction Stop
          if ($source -cnotmatch '^[0-9a-f]{40}$' -or $merge.sha -cne $source -or @($merge.parents).Count -ne 2 -or $merge.parents[0].sha -cne $pr.base.sha -or $merge.parents[1].sha -cne $Commit) { throw 'Synthetic merge is not bound to PR source and base' }
        }
      }
      [long]$id = 0
      $created = [DateTimeOffset]::MinValue
      if (-not [long]::TryParse([string]$candidate.id, [ref]$id) -or $id -le 0 -or $seen.ContainsKey($id)) { throw 'Malformed or ambiguous eligible workflow run ID' }
      if ([string]$candidate.run_attempt -notmatch '^[1-9][0-9]*$') { throw 'Malformed run attempt' }
      $seen[$id] = $true
      if ([string]$candidate.created_at -notmatch '^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$' -or -not [DateTimeOffset]::TryParse([string]$candidate.created_at, [ref]$created)) { throw 'Malformed eligible workflow creation timestamp' }
      if ($candidate.status -cnotin @('queued','in_progress','completed','waiting','pending','requested') -or ($candidate.status -ceq 'completed' -and $candidate.conclusion -cnotin @('success','failure','cancelled','skipped','timed_out','action_required','neutral','startup_failure','stale'))) { throw 'Malformed workflow status' }
      $run = [pscustomobject]@{databaseId=$id; status=$candidate.status; conclusion=$candidate.conclusion; event=$candidate.event; headSha=$source; sourceSha=$Commit; runAttempt=$candidate.run_attempt}
      $runs += [pscustomobject]@{Run=$run; Created=$created; Id=$id}
    }
    $selected = $runs | Sort-Object -Property @{Expression='Created';Descending=$true}, @{Expression='Id';Descending=$true} | Select-Object -First 1
    $run = if ($selected) { $selected.Run } else { $null }
    $report.hosted_workflow_discovery = if ($run) { 'PASS' } else { 'NOT_YET_VISIBLE' }
    $report.hosted_execution = if ($run) { 'RUNNING' } else { 'NOT_EXECUTED' }
    Save-Json (Join-Path $out 'hosted-discovery.json') @{poll=$poll+1; matches=$runs; status=$report.hosted_workflow_discovery}
    Save-Json (Join-Path $out 'execution.json') $report
    if ($run -and $run.status -eq 'completed') { return $run }
    if ($poll+1 -lt $MaxPolls) { Start-Sleep -Seconds $PollSeconds }
  }
  $report.hosted_workflow_discovery = if ($run) { 'PASS' } else { 'NOT_FOUND_WITHIN_BOUND' }
  throw 'Bounded polling ended: run absent or still running; comparison not executed'
}
function Set-HostedComparison([int]$ExitCode) {
  $report.hosted_scientific_comparison = if ($ExitCode -eq 0) { 'PASS' } elseif ($ExitCode -eq 1) { 'FAIL' } else { 'INCONCLUSIVE' }
  if ($ExitCode -eq 0 -and $report.hosted_run_conclusion -ne 'success') { $report.hosted_scientific_comparison='INCONCLUSIVE' }
  $report.numerical_causal_attribution = $report.hosted_scientific_comparison
  if ($ExitCode -eq 1) { $report.hosted_execution='NUMERICAL_COMPARISON_FAILURE' }
  elseif ($ExitCode -eq 0 -and $report.hosted_run_conclusion -eq 'success') { $report.hosted_execution='PASS' }
  elseif ($ExitCode -eq 0) { $report.hosted_execution='HOSTED_INFRASTRUCTURE_OR_SOFTWARE_FAILURE' }
  else { $report.hosted_execution='INCONCLUSIVE' }
}
function Set-HostedRun($Run) {
  $report.hosted_run_conclusion=$Run.conclusion; $report.run_id=$Run.databaseId
  $report.hosted_execution = if ($Run.conclusion -eq 'success') { 'INCONCLUSIVE' }
    elseif ($Run.conclusion -in @('startup_failure','timed_out')) { 'HOSTED_INFRASTRUCTURE_FAILURE' }
    else { 'HOSTED_FAILURE_UNCLASSIFIED' }
  # Preserve the run-level observation even if artifacts are also missing.
  $report.hosted_run_outcome=$report.hosted_execution
}
function Set-HostFailure {
  # Only actual local gates may change an established local PASS.
  if ($stage -eq 'hosted-workflow-discovery' -and $report.hosted_workflow_discovery -notin @('PASS','NOT_FOUND_WITHIN_BOUND')) {
    $report.hosted_workflow_discovery='FAIL'; $report.hosted_execution='INCONCLUSIVE'
  }
}
function Require-Step33Artifacts($Artifacts, $RunId, $Attempt) {
  $report.hosted_artifacts='INCONCLUSIVE'
  foreach ($kind in @('capture','replay')) {
    foreach ($cohort in @('windows-reference','linux-reference','linux-numpy-sensitivity','linux-scipy-sensitivity')) {
      $required = @($Artifacts | Where-Object { $_.name -cmatch ("^step33-$kind-$cohort-$RunId-" + $(if ($Attempt) { [regex]::Escape([string]$Attempt) } else { '[1-9][0-9]*' }) + '$') -and -not $_.expired })
      if ($required.Count -ne 1) {
        $report.hosted_artifacts='FAIL'; $report.hosted_execution='MISSING_REQUIRED_ARTIFACTS'
        throw 'Missing or ambiguous required artifact; numerical comparison not executed'
      }
    }
  }
  $report.hosted_artifacts='PASS'
}
function Run-Python([string]$Name, [string[]]$Arguments) {
  $script:stage = $Name
  Write-Host "STEP33 stage=$Name"
  & $py @Arguments *> (Join-Path $out "$Name.log")
  $rc = $LASTEXITCODE
  if ($Name -eq 'hosted-comparison') { Set-HostedComparison $rc }
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
  if ($PublishDiagnostic -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    & gh auth status *> (Join-Path $out 'github-auth.log')
    $githubAvailable = $LASTEXITCODE -eq 0
  }
  $report.github_authentication = if ($githubAvailable) { 'PASS' } else { 'NOT_CHECKED_LOCAL_OR_UNAVAILABLE' }
  if (-not $githubAvailable -and $PublishDiagnostic) { throw 'GitHub authentication unavailable; no publication' }
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
    if ($PublishDiagnostic) { throw }
  }
  } else {
    $report.original_hosted_artifact_authenticity = 'INCONCLUSIVE'
  }
  Run-Python 'workflow-validation' @('scripts/verify_phase2d_step33_workflow.py','.github/workflows/phase2d-step33-causal.yml','--host-preflight')
  $report.preflight = 'PASS'
  Run-Python 'tests' @('-m','pytest','-q')
  Run-Python 'compilation' @('-m','compileall','-q','src','scripts','tests')
  Run-Python 'analytical' @('-m','stellarator_robust.cli','validate')
  Run-Python 'step32-evidence-integrity' @('scripts/phase2d_step33.py','assess','--inputs',$evidence,'--output',"$out/step32-assessment")
  Run-Python 'historical-review' @('scripts/phase2d_step33.py','historical','--inputs','results/phase2d/step31-20261031-165725-a14c217c/raw','--output',"$out/historical-review")
  Run-Python 'capture' @('scripts/phase2d_step33.py','capture','--output',"$out/capture")
  Run-Python 'local-controlled' @('scripts/phase2d_step33.py','local','--inputs',"$out/capture",'--output',"$out/local")
  # Fresh quick, independent audit, output checks, study and complete repeats;
  # all reports bind exact result hashes. Historical default paths are preserved.
  Run-Python 'full-production-verification' @('scripts/phase2c_verify.py','--output',"$out/production")
  Run-Python 'fault-audit' @('scripts/phase2c_fault_audit.py','--root',"$out/production")
  Run-Python 'legacy-comparison' @('scripts/phase2c_legacy_compare.py','--root',"$out/production")
  Run-Python 'investigation' @('scripts/phase2b_investigate.py','--output',"$out/production/investigation",'--corrected',"$out/production")
  Run-Python 'finalization' @('scripts/phase2c_finalize.py','--output',"$out/production")
  & git fsck --no-reflogs *> (Join-Path $out 'git-fsck.log')
  if ($LASTEXITCODE) { throw 'Git object integrity failed' }
  $report.local_validation = 'PASS'
  $report.implementation = 'LOCAL_GATES_PASSED'
  if ($PublishDiagnostic) {
    $pr = & gh pr view 7 --repo $repository --json isDraft,headRefName,headRefOid,baseRefName,state
    if ($LASTEXITCODE) { throw 'Existing PR metadata unavailable' }
    $prRecord = $pr | ConvertFrom-Json
    if (-not $prRecord.isDraft -or $prRecord.state -ne 'OPEN' -or $prRecord.baseRefName -ne 'codex/phase2d-cross-platform-reproducibility' -or $prRecord.headRefName -ne $branch -or $prRecord.headRefOid -ne $report.starting_head) { throw 'Draft PR #7 identity or remote head mismatch' }
    Save-Json (Join-Path $out 'publication-pr-preflight.json') $prRecord
    $allowed = @('pyproject.toml','scripts/phase2d_step31_diagnose.py','scripts/phase2d_step31e_review.py','scripts/phase2d_step32.py','scripts/phase2d_step32_host.ps1','scripts/phase2d_step32_repair_validate.ps1','tests/test_phase2d_step31.py','tests/test_phase2d_step31e.py','tests/test_phase2d_step32.py','tests/test_phase2d_step32_host.py','docs/PHASE2D_STEP31E_ROOT_CAUSE_ASSESSMENT.md','docs/PHASE2D_STEP31_REPRODUCIBILITY.md','docs/PHASE2D_STEP31_ROOT_CAUSE_REPORT.md','docs/PHASE2D_STEP32_CAUSAL_ATTRIBUTION_REPORT.md','docs/PHASE2D_STEP32_EXPERIMENT_PROTOCOL.md','docs/PHASE2D_STEP32_HOST_REPAIR.md','.github/workflows/phase2d-step32-causal.yml','docs/PHASE2D_STEP33_VALIDATION_REPORT.md','scripts/phase2d_step33.py','scripts/phase2d_step33_host.ps1','tests/test_phase2d_step33.py','tests/test_phase2d_step33_host.py','scripts/verify_phase2d_step33_workflow.py','tests/test_phase2d_step33_workflow.py','docs/PHASE2D_STEP33_CAUSAL_ATTRIBUTION_REPORT.md','docs/PHASE2D_STEP33_EXPERIMENT_PROTOCOL.md','.github/workflows/phase2d-step33-causal.yml')
    $staged = @(Git-Read @('diff','--cached','--name-only'))
    if (@($staged | Where-Object { $_ -and $_ -notin $allowed }).Count) { throw 'Unrelated staged changes; publication refused' }
    foreach ($path in $preexisting.Keys) {
      if ((Get-FileHash -LiteralPath (Join-Path $repo $path) -Algorithm SHA256).Hash -ne $preexisting[$path]) { throw "Preexisting file changed: $path" }
    }
    if ((ConvertTo-Json (Inventory $evidence) -Compress) -ne (ConvertTo-Json $before -Compress)) { throw 'Historical evidence changed' }
    Save-Json (Join-Path $out 'publication-inventory.json') @($allowed | ForEach-Object { @{path=$_; sha256=(Get-FileHash -LiteralPath (Join-Path $repo $_) -Algorithm SHA256).Hash.ToLowerInvariant()} })
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
    $run = Wait-Step33Run $commit
    $stage = 'hosted-artifacts'
    Set-HostedRun $run
    & gh api "repos/$repository/actions/runs/$($run.databaseId)/jobs?per_page=100" | Set-Content (Join-Path $out 'hosted-jobs.json')
    if ($LASTEXITCODE) { throw 'Job metadata unavailable' }
    $metadata = & gh api "repos/$repository/actions/runs/$($run.databaseId)/artifacts?per_page=100"
    if ($LASTEXITCODE) { throw 'Artifact metadata unavailable' }
    $metadata | Set-Content (Join-Path $out 'hosted-artifacts.json')
    $artifacts = ($metadata | ConvertFrom-Json).artifacts
    Require-Step33Artifacts $artifacts $run.databaseId $run.runAttempt
    $hosted = Join-Path $out 'hosted'; New-Item -ItemType Directory $hosted | Out-Null
    foreach ($artifact in $artifacts) {
      if ($artifact.name -notmatch '^step33-' -or $artifact.expired) { throw 'Unexpected or expired hosted artifact' }
      Download-VerifiedArtifact $artifact $hosted
    }
    $report.evidence_authenticity='PASS'
    $normalized = Join-Path $out 'hosted-evidence'; New-Item -ItemType Directory $normalized | Out-Null
    foreach ($stage in @('capture','replay')) {
      foreach ($cohort in @('windows-reference','linux-reference','linux-numpy-sensitivity','linux-scipy-sensitivity')) {
        $matches = @($artifacts | Where-Object { $_.name -ceq "step33-$stage-$cohort-$($run.databaseId)-$($run.runAttempt)" })
        if ($matches.Count -ne 1) { throw 'Missing or ambiguous required artifact' }
        Copy-Item -LiteralPath (Join-Path $hosted $matches[0].name) -Destination (Join-Path $normalized "$stage-$cohort") -Recurse
      }
    }
    Run-Python 'hosted-comparison' @('scripts/phase2d_step33.py','compare','--inputs',$normalized,'--expected-head',$commit,'--output',"$out/hosted-comparison")
    if ($report.hosted_run_conclusion -ne 'success' -and $report.hosted_scientific_comparison -ne 'FAIL') {
      $report.hosted_execution='HOSTED_INFRASTRUCTURE_OR_SOFTWARE_FAILURE'
      throw 'Hosted workflow failed; downloaded comparison cannot establish hosted success; inspect hosted-jobs.json'
    }
    if ($report.hosted_scientific_comparison -eq 'FAIL') { throw 'Completed hosted numerical comparison failed; evidence retained' }
  }
} catch {
  $report.error = $_.Exception.Message
  $report.failed_stage = $stage
  $report.exception = $_.ToString()
  $report.script_stack_trace = $_.ScriptStackTrace
  if (-not $report.preflight) { $report.preflight = 'FAIL' }
  Set-HostFailure
  [Console]::Error.WriteLine("STEP33 stage=$stage failed: $_; execution record=$out/execution.json")
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
  if (-not $PublishDiagnostic -and $null -ne $initialIndex) {
    $report.index_preserved = ((Git-Read @('diff','--cached','--binary') | Out-String) -ceq ($initialIndex | Out-String))
  }
  & git diff --check *> (Join-Path $out 'git-diff-check.log')
  $report.diff_check_exit = $LASTEXITCODE
  $report.exit_code = if ($report.error -or $report.historical_preservation -ne 'PASS' -or $report.preexisting_changed.Count -or $report.diff_check_exit -or $report.index_preserved -eq $false) { 2 } else { 0 }
  if ($report.exit_code -and -not $report.error) {
    $report.failed_stage = 'preservation-and-git-integrity'
    $report.error = 'Final preservation or Git integrity checks failed; see execution.json'
    [Console]::Error.WriteLine("STEP33 stage=$($report.failed_stage) failed; exit=2; record=$out/execution.json")
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
