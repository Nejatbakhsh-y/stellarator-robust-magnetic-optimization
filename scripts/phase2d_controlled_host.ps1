# Run from ordinary Windows PowerShell in this research checkout.
$ErrorActionPreference = 'Stop'
if ((git branch --show-current) -ne 'codex/phase2d-cross-platform-reproducibility') { throw 'Wrong branch' }
if ((git remote get-url origin) -ne 'https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git') { throw 'Wrong repository' }
$py = '.\.venv\Scripts\python.exe'
$run = 'results/ci/phase2d-controlled-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
if (Test-Path -LiteralPath $run) { throw 'Fresh output required' }
New-Item -ItemType Directory -Path $run | Out-Null
$steps = [System.Collections.Generic.List[object]]::new()
function Invoke-Check([string]$Label, [string[]]$Arguments) {
    & $py @Arguments 2>&1 | Tee-Object -FilePath "$run/$Label.log"
    $code = $LASTEXITCODE
    $steps.Add([ordered]@{label=$Label; arguments=$Arguments; exit_code=$code})
    if ($code -ne 0) { throw "$Label failed with exit code $code; preserve logs" }
}
Start-Transcript -Path "$run/transcript.txt"
try {
    git rev-parse HEAD | Set-Content "$run/head.txt"
    git status --short --untracked-files=all | Set-Content "$run/git-status.txt"
    Invoke-Check 'frozen-tests' @('-m','pytest','-q','tests/test_phase2d_frozen.py')
    Invoke-Check 'full-tests' @('-m','pytest','-q')
    Invoke-Check 'compile' @('-m','compileall','-q','src','scripts','tests')
    Invoke-Check 'analytical' @('-m','stellarator_robust.cli','validate')
    Invoke-Check 'original-windows-manifest' @('scripts/phase2d_frozen.py','verify-evidence','--root','results/ci/phase2d-frozen-host-20261030-205117-4a683b/windows')
    Invoke-Check 'prepare' @('scripts/phase2d_frozen.py','prepare','--output',"$run/shared")
    $contractHash = (Get-FileHash "$run/shared/contract.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    Invoke-Check 'windows' @('scripts/phase2d_frozen.py','run','--fixture',"$run/shared/fixture",'--contract',"$run/shared/contract.json",'--contract-sha256',$contractHash,'--output',"$run/windows",'--cohort','windows-reference')
    Invoke-Check 'new-windows-manifest' @('scripts/phase2d_frozen.py','verify-evidence','--root',"$run/windows")
    # Includes fresh quick experiment, output checks, independent audit,
    # study, full second quick/study, strict repeat and training checks.
    Invoke-Check 'production-replay' @('scripts/phase2c_verify.py','--output',"$run/science")
    Invoke-Check 'production-fault-audit' @('scripts/phase2c_fault_audit.py','--root',"$run/science")
    Invoke-Check 'production-legacy' @('scripts/phase2c_legacy_compare.py','--root',"$run/science")
    Invoke-Check 'production-investigation' @('scripts/phase2b_investigate.py','--output',"$run/science/investigation",'--corrected',"$run/science")
    Invoke-Check 'production-manifest' @('scripts/phase2c_finalize.py','--output',"$run/science")
}
finally {
    [ordered]@{scientific_status='PARTIAL'; steps=@($steps.ToArray()); head=(git rev-parse HEAD)} | ConvertTo-Json -Depth 8 | Set-Content "$run/execution.json"
    Stop-Transcript
    $files = @(Get-ChildItem -LiteralPath $run -File -Recurse)
    $hashes = [ordered]@{}
    foreach ($file in $files) {
        $name = $file.FullName.Substring((Resolve-Path $run).Path.Length+1).Replace('\','/')
        $hashes[$name] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $hashes | ConvertTo-Json -Depth 5 | Set-Content "$run/manifest.json"
    Write-Output "Evidence retained at $run; hosted comparisons still required."
}
