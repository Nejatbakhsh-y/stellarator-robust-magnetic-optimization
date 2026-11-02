#requires -Version 5.1
[CmdletBinding()]
param(
    [AllowNull()][AllowEmptyCollection()][object]$RunId,
    [ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')]
    [string]$Repository = 'Nejatbakhsh-y/stellarator-robust-magnetic-optimization',
    [string]$ExpectedCommit,
    [string]$WorkflowName,
    [string]$OutputRoot = 'results/phase2d',
    [ValidateRange(1,86400)][int]$TimeoutSeconds = 1800,
    [ValidateRange(1,60)][int]$PollSeconds = 15,
    [ValidateRange(1,300)][int]$ApiTimeoutSeconds = 60,
    [switch]$LibraryOnly
)
Set-StrictMode -Version Latest

function ConvertTo-Step45RunId {
    param([AllowNull()][AllowEmptyCollection()][object]$Value)
    # Check the original type before any string or numeric conversion.
    $integerTypes = @([byte], [sbyte], [int16], [uint16], [int32], [uint32], [int64], [uint64])
    if ($null -eq $Value -or
        ($Value -isnot [string] -and $Value.GetType() -notin $integerTypes)) {
        throw 'Invalid RunId: expected a canonical positive Int64 decimal integer.'
    }
    $canonical = if ($Value -is [string]) { $Value } else {
        $Value.ToString([Globalization.CultureInfo]::InvariantCulture)
    }
    $parsed = [long]0
    if ($canonical -cnotmatch '\A[1-9][0-9]*\z' -or
        -not [long]::TryParse($canonical, [Globalization.NumberStyles]::None,
            [Globalization.CultureInfo]::InvariantCulture, [ref]$parsed)) {
        throw 'Invalid RunId: expected a canonical positive Int64 decimal integer.'
    }
    return $parsed
}

function Invoke-Step45Gh {
    param([string[]]$Arguments, [int]$LimitSeconds)
    # Only internally constructed, whitespace-free API endpoints are accepted.
    foreach ($argument in $Arguments) {
        if ($argument -notmatch '^[A-Za-z0-9_./-]+$') { throw 'Unsafe CLI argument' }
    }
    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = 'gh'
    $start.Arguments = $Arguments -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $start
    try {
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($LimitSeconds * 1000)) {
            $process.Kill()
            $process.WaitForExit()
            return @{Code=-1; Out=$stdout.Result; Err=$stderr.Result; TimedOut=$true}
        }
        return @{Code=$process.ExitCode; Out=$stdout.Result; Err=$stderr.Result; TimedOut=$false}
    } finally { $process.Dispose() }
}

function Invoke-Step45Monitor {
    [CmdletBinding()]
    param(
        [AllowNull()][AllowEmptyCollection()][object]$RunId,
        [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')][string]$Repository,
        [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{40}$')][string]$ExpectedCommit,
        [Parameter(Mandatory=$true)][ValidateNotNullOrEmpty()][string]$WorkflowName,
        [Parameter(Mandatory=$true)][string]$OutputRoot,
        [ValidateRange(1,86400)][int]$TimeoutSeconds=1800,
        [ValidateRange(1,60)][int]$PollSeconds=15,
        [ValidateRange(1,300)][int]$ApiTimeoutSeconds=60
    )
    $ErrorActionPreference = 'Stop'
    $RunId = ConvertTo-Step45RunId -Value $RunId
    $directory = Join-Path $OutputRoot ('step45-monitor-' + $RunId + '-' + [guid]::NewGuid().ToString('N'))
    [void](New-Item -ItemType Directory -Path $directory -ErrorAction Stop)
    $record = [ordered]@{schema='step45-monitor-v1'; run_id=$RunId; repository=$Repository;
        expected_commit=$ExpectedCommit; workflow=$WorkflowName; monitor_status='INCOMPLETE';
        github_status=$null; github_conclusion=$null; identity_verified=$false;
        scientific_comparison='NOT_ASSESSED'; production_acceptance='NOT_ESTABLISHED';
        log_status='NOT_ATTEMPTED'; output_directory=[IO.Path]::GetFullPath($directory); error=$null}
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $endpoint = 'repos/{0}/actions/runs/{1}' -f $Repository,$RunId
    $poll = 0
    try {
        while ($true) {
            $remaining = $TimeoutSeconds - $clock.Elapsed.TotalSeconds
            if ($remaining -le 0) { $record.monitor_status='TIMEOUT'; break }
            $limit = [Math]::Max(1,[Math]::Min($ApiTimeoutSeconds,[Math]::Ceiling($remaining)))
            $reply = Invoke-Step45Gh -Arguments @('api',$endpoint) -LimitSeconds $limit
            $poll++
            $reply.Out | Set-Content -LiteralPath (Join-Path $directory "poll-$poll.json") -Encoding UTF8
            $reply.Err | Set-Content -LiteralPath (Join-Path $directory "poll-$poll.stderr.log") -Encoding UTF8
            if ($reply.TimedOut) { $record.monitor_status='TIMEOUT'; break }
            if ($reply.Code -ne 0) { throw "GitHub API exit $($reply.Code)" }
            $run = $reply.Out | ConvertFrom-Json -ErrorAction Stop
            if ($null -eq $run -or $run -is [array]) { throw 'Expected one run JSON object' }
            if ($run.id -is [array] -or [string]$run.id -cne [string]$RunId) { throw 'Run ID mismatch' }
            if ($run.repository.full_name -ine $Repository -or
                $run.url -ine ('https://api.github.com/' + $endpoint)) { throw 'Repository identity mismatch' }
            if ($run.head_sha -ine $ExpectedCommit) { throw 'Source commit mismatch' }
            if ($run.name -cne $WorkflowName) { throw 'Workflow name mismatch' }
            $record.identity_verified=$true
            $record.github_status=$run.status
            $record.github_conclusion=$run.conclusion
            if ($run.status -eq 'completed') {
                if ($run.conclusion -notin @('success','failure','cancelled','timed_out','action_required','skipped','neutral','stale','startup_failure')) {
                    throw 'Unknown completed conclusion'
                }
                $record.monitor_status='COMPLETED'
                # Preserve all available job logs, including successful jobs in failed runs.
                # CLI failure here never replaces the actual GitHub conclusion.
                try {
                    $logs = Invoke-Step45Gh -Arguments @('run','view',[string]$RunId,'--repo',$Repository,'--log') -LimitSeconds $ApiTimeoutSeconds
                    $logs.Out | Set-Content -LiteralPath (Join-Path $directory 'run.log') -Encoding UTF8
                    $logs.Err | Set-Content -LiteralPath (Join-Path $directory 'run-log.stderr.log') -Encoding UTF8
                    $record.log_status = if ($logs.Code -eq 0 -and -not $logs.TimedOut) {'PRESERVED'} else {'MISSING_EVIDENCE'}
                } catch { $record.log_status='MISSING_EVIDENCE'; $record.error=$_.Exception.Message }
                break
            }
            if ($run.status -notin @('queued','in_progress')) { throw 'Unknown nonterminal status' }
            if ($null -ne $run.conclusion) { throw 'Nonterminal run has conclusion' }
            $remaining = $TimeoutSeconds - $clock.Elapsed.TotalSeconds
            if ($remaining -le 0) { $record.monitor_status='TIMEOUT'; break }
            Start-Sleep -Milliseconds ([int](1000 * [Math]::Min($PollSeconds,$remaining)))
        }
    } catch { $record.monitor_status='ERROR'; $record.error=$_.Exception.Message }
    $record['polls']=$poll
    $record['elapsed_seconds']=$clock.Elapsed.TotalSeconds
    $json = $record | ConvertTo-Json -Depth 8
    $json | Set-Content -LiteralPath (Join-Path $directory 'monitor.json') -Encoding UTF8
    $json
}

if (-not $LibraryOnly) {
    # Preserve the original input until explicit validation in the monitor.
    $json = Invoke-Step45Monitor -RunId $RunId -Repository $Repository -ExpectedCommit $ExpectedCommit -WorkflowName $WorkflowName -OutputRoot $OutputRoot -TimeoutSeconds $TimeoutSeconds -PollSeconds $PollSeconds -ApiTimeoutSeconds $ApiTimeoutSeconds
    $json
    $result = $json | ConvertFrom-Json
    if ($result.monitor_status -ne 'COMPLETED' -or $result.log_status -ne 'PRESERVED') { exit 2 }
    if ($result.github_conclusion -ne 'success') { exit 1 }
    exit 0
}
