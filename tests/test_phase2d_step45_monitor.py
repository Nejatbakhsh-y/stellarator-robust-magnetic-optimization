"""Offline PowerShell contract tests. Never invokes GitHub or authenticates history."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/phase2d_step45_monitor.ps1'
SHELLS = [s for s in ('powershell', 'pwsh') if shutil.which(s)]


def run_ps(shell, tmp_path, body):
    harness = tmp_path / 'harness.ps1'
    harness.write_text("$ErrorActionPreference='Stop'\n. '" + str(SCRIPT).replace("'", "''") +
                       "' -LibraryOnly\n" + body, encoding='utf-8-sig')
    return subprocess.run([shell, '-NoProfile', '-NonInteractive', '-File', str(harness)],
                          capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize('shell', SHELLS or [None])
@pytest.mark.parametrize('case', [
    'success', 'failure', 'cancelled', 'timed_out', 'action_required', 'skipped',
    'malformed', 'missing', 'wrong_id', 'repo', 'commit', 'workflow', 'api',
    'timeout', 'api_timeout', 'array_json', 'log_failure', 'queued', 'in_progress',
    'unknown', 'null_conclusion', 'id_array', 'url',
])
def test_monitor_offline(shell, tmp_path, case):
    if shell is None:
        pytest.skip('PowerShell unavailable')
    body = r'''
$global:calls = @()
$global:case = '__CASE__'
function Invoke-Step45Gh {
    param([string[]]$Arguments,[int]$LimitSeconds)
    $global:calls += ,$Arguments
    if ($Arguments[0] -eq 'run') {
        $code = if ($global:case -eq 'log_failure') {1} else {0}
        return @{Code=$code;Out='scientific FAIL retained';Err='';TimedOut=$false}
    }
    $run = @{id=41426274201; repository=@{full_name='owner/repo'};
        url='https://api.github.com/repos/owner/repo/actions/runs/41426274201';
        head_sha=('b'*40); name='Expected workflow'; status='completed'; conclusion='failure'}
    $code=0; $timed=$false
    switch ($global:case) {
        'success' {$run.conclusion='success'}
        'cancelled' {$run.conclusion='cancelled'}
        'timed_out' {$run.conclusion='timed_out'}
        'action_required' {$run.conclusion='action_required'}
        'skipped' {$run.conclusion='skipped'}
        'missing' {$run.Remove('id')}
        'wrong_id' {$run.id=1}
        'id_array' {$run.id=@(41426274201,41426273939)}
        'url' {$run.url='https://api.github.com/repos/other/repo/actions/runs/41426274201'}
        'repo' {$run.repository.full_name='other/repo'}
        'commit' {$run.head_sha='a'*40}
        'workflow' {$run.name='wrong'}
        'api' {$code=1}
        'api_timeout' {$timed=$true}
        'unknown' {$run.status='waiting'}
        'null_conclusion' {$run.conclusion=$null}
        'timeout' {$run.status='queued';$run.conclusion=$null}
        'queued' {if ($global:calls.Count -eq 1) {$run.status='queued';$run.conclusion=$null}}
        'in_progress' {if ($global:calls.Count -eq 1) {$run.status='in_progress';$run.conclusion=$null}}
    }
    $raw=$run | ConvertTo-Json
    if ($global:case -eq 'malformed') {$raw='{ broken'}
    if ($global:case -eq 'array_json') {$raw='['+$raw+','+$raw+']'}
    return @{Code=$code;Out=$raw;Err='retained stderr';TimedOut=$timed}
}
$json=Invoke-Step45Monitor -RunId 41426274201 -Repository owner/repo -ExpectedCommit ('b'*40) -WorkflowName 'Expected workflow' -OutputRoot '__OUT__' -TimeoutSeconds 2 -PollSeconds 1
@{record=($json|ConvertFrom-Json);calls=$global:calls} | ConvertTo-Json -Depth 12
'''.replace('__CASE__', case).replace('__OUT__', str(tmp_path).replace("'", "''"))
    proc = run_ps(shell, tmp_path, body)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.lstrip('\ufeff'))
    record = result['record']
    calls = result['calls']
    for args in calls:
        if args[0] == 'api':
            assert args == ['api', 'repos/owner/repo/actions/runs/41426274201']
        else:
            assert args == ['run', 'view', '41426274201', '--repo', 'owner/repo', '--log']
    terminal = {'success', 'failure', 'cancelled', 'timed_out', 'action_required',
                'skipped', 'log_failure', 'queued', 'in_progress'}
    expected = 'COMPLETED' if case in terminal else 'TIMEOUT' if case in {'timeout', 'api_timeout'} else 'ERROR'
    assert record['monitor_status'] == expected
    assert record['scientific_comparison'] == 'NOT_ASSESSED'
    assert record['production_acceptance'] == 'NOT_ESTABLISHED'
    if case in terminal:
        assert record['github_conclusion'] == (case if case in terminal - {'log_failure', 'queued', 'in_progress'} else 'failure')
        assert record['log_status'] == ('MISSING_EVIDENCE' if case == 'log_failure' else 'PRESERVED')
        assert calls[-1][0] == 'run'
    directory = Path(record['output_directory'])
    assert json.loads((directory / 'monitor.json').read_text(encoding='utf-8-sig')) == record
    assert (directory / 'poll-1.json').exists()
    assert (directory / 'poll-1.stderr.log').exists()


@pytest.mark.parametrize('shell', SHELLS or [None])
def test_scalar_binding_and_unique_directories(shell, tmp_path):
    if shell is None:
        pytest.skip('PowerShell unavailable')
    body = r'''
function Get-TestSha256 {
    param([string]$LiteralPath)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.IO.File]::ReadAllBytes($LiteralPath)
        return [System.BitConverter]::ToString($sha256.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}
$global:calls=0
function Invoke-Step45Gh {
    param([string[]]$Arguments,[int]$LimitSeconds)
    $global:calls++
    if ($Arguments[0] -eq 'run') {return @{Code=0;Out='scientific FAIL retained';Err='';TimedOut=$false}}
    $id=[long]($Arguments[1].Split('/')[-1])
    return @{Code=0;Err='';TimedOut=$false;Out=(@{id=$id;repository=@{full_name='owner/repo'};
        url=('https://api.github.com/'+$Arguments[1]);head_sha=('b'*40);name='expected';
        status='completed';conclusion='success'} | ConvertTo-Json)}
}
$invalid = New-Object 'System.Collections.Generic.List[object]'
$invalid.Add($null)
$invalid.Add('')
$invalid.Add(@())
$invalid.Add(@(1))
$invalid.Add(@(1,2))
foreach ($value in @(0,-1,'1 2','1,2','01','+1','1.0','1e2',$true,$false,
    '9223372036854775808',' ',"1`n",[double]1,[single]1,[decimal]1,
    [uint64]::MaxValue,[pscustomobject]@{id=1})) { $invalid.Add($value) }
$misleading=New-Object PSObject
$misleading | Add-Member -MemberType ScriptMethod -Name ToString -Value {'1'} -Force
$invalid.Add($misleading)
if ($invalid.Count -ne 24 -or $invalid[2] -isnot [array] -or $invalid[2].Count -ne 0 -or
    $invalid[3] -isnot [array] -or $invalid[3].Count -ne 1 -or
    $invalid[4] -isnot [array] -or $invalid[4].Count -ne 2) {throw 'fixture lost invalid values'}
$rejected=0
foreach ($bad in $invalid) {
    # Exercise both public entry points, preserving arrays as parameter objects.
    foreach ($entry in @('function','script')) {
        try {
            if ($entry -eq 'function') {
                Invoke-Step45Monitor -RunId $bad -Repository owner/repo -ExpectedCommit ('b'*40) -WorkflowName expected -OutputRoot '__OUT__'
            } else {
                & '__SCRIPT__' -RunId $bad -Repository owner/repo -ExpectedCommit ('b'*40) -WorkflowName expected -OutputRoot '__OUT__'
            }
            throw 'accepted invalid ID'
        } catch {
            if ($_.Exception.Message -notlike 'Invalid RunId:*') {throw}
            $rejected++
        }
        if ($global:calls -ne 0) {throw 'invalid ID invoked CLI'}
        if (@(Get-ChildItem -LiteralPath '__OUT__' -Directory).Count -ne 0) {throw 'invalid ID created evidence'}
    }
}
$directories=New-Object 'System.Collections.Generic.List[string]'
$snapshots=New-Object 'System.Collections.Generic.List[object]'
foreach ($valid in @(1,123,41371734831,'1','123','41371734831',[long]::MaxValue)) {
    foreach ($repeat in 1..2) {
        $record=Invoke-Step45Monitor -RunId $valid -Repository owner/repo -ExpectedCommit ('b'*40) -WorkflowName expected -OutputRoot '__OUT__' | ConvertFrom-Json
        if ($record.monitor_status -ne 'COMPLETED' -or $record.github_conclusion -ne 'success') {throw 'valid ID failed'}
        if ($directories.Contains($record.output_directory)) {throw 'overwritten'}
        $directories.Add($record.output_directory)
        $snapshots.Add(@{Path=(Join-Path $record.output_directory 'monitor.json');Hash=(Get-TestSha256 -LiteralPath (Join-Path $record.output_directory 'monitor.json'))})
    }
}
foreach ($snapshot in $snapshots) {
    if ((Get-TestSha256 -LiteralPath $snapshot.Path) -cne $snapshot.Hash) {throw 'previous evidence changed'}
}
@{rejected=$rejected;directories=$directories;calls=$global:calls;snapshots=@($snapshots.ToArray())}|ConvertTo-Json -Depth 4
'''.replace('__OUT__', str(tmp_path).replace("'", "''")).replace('__SCRIPT__', str(SCRIPT).replace("'", "''"))
    proc = run_ps(shell, tmp_path, body)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.lstrip('\ufeff'))
    assert result['rejected'] == 48
    assert len(set(result['directories'])) == 14
    assert result['calls'] == 28
    assert len(result['snapshots']) == 14
    for snapshot in result['snapshots']:
        assert snapshot['Hash'] == hashlib.sha256(Path(snapshot['Path']).read_bytes()).hexdigest()
