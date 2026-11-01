# Invoke under the host's ordinary script policy; no execution-policy changes.
$ErrorActionPreference = 'Stop'
if ((Get-Location).Path -ne (Split-Path $PSScriptRoot -Parent)) { throw 'Run from research checkout root' }
if ((git branch --show-current) -ne 'codex/phase2d-upstream-attribution') { throw 'Wrong branch' }
if ((git remote get-url origin) -ne 'https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git') { throw 'Wrong repository' }
$py = '.\.venv\Scripts\python.exe'
$run = 'results/phase2d/upstream-host-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,8)
if (Test-Path -LiteralPath $run) { throw 'Fresh output required' }
New-Item -ItemType Directory -Path $run | Out-Null
$steps = [System.Collections.Generic.List[object]]::new()
$before = @{}
# Include ignored supplied historical evidence as well as all tracked/untracked work.
$names = @(git ls-files --cached --others --exclude-standard)
$historical = 'results/ci/phase2d-hosted-investigation-41195815229'
if (!(Test-Path -LiteralPath $historical)) { throw 'Historical evidence missing' }
$historicalFiles = @(Get-ChildItem -LiteralPath $historical -File -Recurse)
if ($historicalFiles.Count -ne 247) { throw 'Expected 247 historical files' }
$names += @($historicalFiles | ForEach-Object { $_.FullName.Substring((Get-Location).Path.Length+1) })
foreach ($name in $names) {
    if (Test-Path -LiteralPath $name -PathType Leaf) { $before[$name] = (Get-FileHash -LiteralPath $name -Algorithm SHA256).Hash }
}
$before | ConvertTo-Json -Depth 4 | Set-Content "$run/preexisting-sha256.json"
$status = 'INCONCLUSIVE'
function Check([string]$label, [string[]]$arguments) {
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $py @arguments 2>&1 | Tee-Object -FilePath "$run/$label.log"
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
    $steps.Add(@{label=$label;arguments=$arguments;exit_code=$code})
    if ($code -ne 0) {
        if ($label -ne 'python311') { $script:status = 'FAIL' }
        throw "$label failed ($code); logs retained"
    }
}
try {
    git rev-parse HEAD | Set-Content "$run/head.txt"
    git status --porcelain=v1 --untracked-files=all | Set-Content "$run/status-before.txt"
    Check 'python311' @('-c','import sys; assert sys.version_info[:2] == (3,11); print(sys.version)')
    Check 'tests' @('-m','pytest','-q')
    Check 'compile' @('-m','compileall','-q','src','scripts','tests')
    Check 'analytical' @('-m','stellarator_robust.cli','validate')
    Check 'prepare' @('scripts/phase2d_upstream.py','prepare','--output',"$run/sealed")
    $inputFile = "$run/sealed/inputs.json"
    $digest = (Get-FileHash -LiteralPath $inputFile -Algorithm SHA256).Hash.ToLowerInvariant()
    Check 'worker' @('scripts/phase2d_upstream.py','run','--input',$inputFile,'--input-sha256',$digest,'--output',"$run/worker")
    Check 'repeat' @('scripts/phase2d_upstream.py','run','--input',$inputFile,'--input-sha256',$digest,'--output',"$run/repeat")
    Check 'repeat-compare' @('scripts/phase2d_upstream.py','compare','--input-sha256',$digest,'--reference',"$run/worker",'--current',"$run/repeat",'--output',"$run/comparison")
    # Fresh quick, output, independent audit, study, complete repeat, and hash-bound gates.
    Check 'production' @('scripts/phase2c_verify.py','--output',"$run/production")
    Check 'fault-audit' @('scripts/phase2c_fault_audit.py','--root',"$run/production")
    Check 'legacy-scientific-comparison' @('scripts/phase2c_legacy_compare.py','--root',"$run/production")
    Check 'geometry-investigation' @('scripts/phase2b_investigate.py','--output',"$run/production/investigation",'--corrected',"$run/production")
    Check 'finalize' @('scripts/phase2c_finalize.py','--output',"$run/production")
    $status = 'PASS'
}
catch { $steps.Add(@{error=$_.Exception.Message}); throw }
finally {
    $changed = @()
    foreach ($name in $before.Keys) {
        if (!(Test-Path -LiteralPath $name -PathType Leaf)) { $changed += $name }
        elseif ((Get-FileHash -LiteralPath $name -Algorithm SHA256).Hash -ne $before[$name]) { $changed += $name }
    }
    if ($changed.Count) { $status = 'FAIL' }
    @{local_required_gates=$status;scientific_status='PARTIAL';causal_status='INCONCLUSIVE';
      production_cross_platform='FAIL (historical; fresh hosted run pending)';steps=@($steps.ToArray());
      changed_preexisting=$changed;historical_count=$historicalFiles.Count} |
        ConvertTo-Json -Depth 12 | Set-Content "$run/report.json"
    $hashes = @{}
    foreach ($f in @(Get-ChildItem -LiteralPath $run -File -Recurse)) {
        $hashes[$f.FullName.Substring((Resolve-Path $run).Path.Length+1)] = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
    }
    $hashes | ConvertTo-Json -Depth 4 | Set-Content "$run/manifest.json"
    Write-Output "Evidence retained: $run"
    if ($changed.Count) { throw 'Preexisting evidence changed; preservation gate FAIL' }
}
