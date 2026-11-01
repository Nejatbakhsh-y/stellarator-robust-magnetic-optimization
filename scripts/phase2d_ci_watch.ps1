[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Repository,
    [Parameter(Mandatory=$true)][string]$Branch,
    [Parameter(Mandatory=$true)][string]$Commit,
    [string]$Workflow = 'ci.yml',
    [ValidateRange(1,420)][int]$MaxPolls = 120,
    [ValidateRange(0,60)][int]$PollSeconds = 15
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$result = [ordered]@{status='ERROR'; run_id=$null; commit=$Commit; workflow=$Workflow; conclusion=$null; error=$null}
$code = 2
function Invoke-Gh([string[]]$Arguments) {
    $lines = @(& gh @Arguments)
    if ($LASTEXITCODE -ne 0) { throw "GitHub CLI failed: $($Arguments[0])" }
    return ($lines -join "`n").Trim()
}
function Read-Run([string]$Id) {
    $json = Invoke-Gh @('api',"repos/$Repository/actions/runs/$Id")
    $run = ConvertFrom-Json -InputObject $json
    if ($run -isnot [pscustomobject]) { throw 'Run metadata must be an object' }
    foreach ($key in @('id','head_sha','head_branch','path','status','conclusion','event')) {
        if ($null -eq $run.PSObject.Properties[$key]) { throw "Missing run property: $key" }
    }
    if ([string]$run.id -cne $Id -or $run.head_sha -cne $Commit -or
        $run.head_branch -cne $Branch -or $run.path -cne ".github/workflows/$Workflow" -or
        $run.event -cnotin @('push','pull_request')) { throw 'Selected run identity mismatch' }
    return $run
}
try {
    if ($Repository -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' -or
        [string]::IsNullOrWhiteSpace($Branch) -or $Commit -cnotmatch '^[0-9a-f]{40}$' -or
        $Workflow -notmatch '^[A-Za-z0-9_.-]+\.ya?ml$') { throw 'Invalid repository, branch, commit or workflow' }
    # REST fields are filtered by gh itself. No array/object coercion for IDs.
    # Query all statuses; a previous success must never hide a later failure.
    $query = '.workflow_runs | sort_by([if .event == "pull_request" then 1 else 0 end, .created_at, .id]) | last | .id // empty'
    $query = '[.[] | .workflow_runs[]] | {workflow_runs: .} | ' + $query
    $endpoint = "repos/$Repository/actions/workflows/$Workflow/runs?branch=$([uri]::EscapeDataString($Branch))&head_sha=$Commit&per_page=100"
    for ($poll=0; $poll -lt $MaxPolls; $poll++) {
        if ($null -eq $result.run_id) {
            $id = Invoke-Gh @('api','--paginate','--slurp',$endpoint,'--jq',$query)
            if ($id -eq '') { $result.status='MISSING' }
            elseif ($id -cnotmatch '^[1-9][0-9]*$') { throw 'Malformed scalar run ID' }
            else { $result.run_id=$id }
        }
        if ($null -ne $result.run_id) {
            $run = Read-Run $result.run_id
            $result.conclusion=$run.conclusion
            if ($run.status -ceq 'completed') {
                if ($run.conclusion -ceq 'success') { $result.status='PASS'; $code=0 }
                else {
                    $result.status='FAIL'; $code=1
                    # Keep logs off stdout so the final stdout record remains JSON.
                    $logs = & gh run view $result.run_id --repo $Repository --log-failed 2>&1
                    $logCode = $LASTEXITCODE
                    foreach ($line in $logs) { [Console]::Error.WriteLine([string]$line) }
                    if ($logCode -ne 0) { $result.error='Failing log retrieval failed' }
                }
                break
            }
            elseif ($run.status -cin @('queued','waiting','pending','requested')) { $result.status='QUEUED' }
            elseif ($run.status -ceq 'in_progress') { $result.status='RUNNING' }
            else { throw 'Malformed run status' }
        }
        if ($poll+1 -lt $MaxPolls) { Start-Sleep -Seconds $PollSeconds }
    }
} catch { $result.status='ERROR'; $result.error=$_.Exception.Message; $code=2 }
$result | ConvertTo-Json -Compress
exit $code
