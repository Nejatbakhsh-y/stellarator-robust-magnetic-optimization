# Record repair verification attempts even when the required runtimes cannot start.
$ErrorActionPreference = 'Stop'
$root = Join-Path $PSScriptRoot '../results/phase2d/step32-repair-20261031-181855-e9d0f395'
$run = Join-Path $root ('validation-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run | Out-Null
$py = Join-Path $PSScriptRoot '../.venv/Scripts/python.exe'
$pwsh = 'C:/Users/nejat/AppData/Local/Microsoft/WindowsApps/pwsh.exe'
$evidence = Join-Path $PSScriptRoot '../results/phase2d/step31e-20261031-173238-bf04cf36/assessment'
function Inventory($Path) {
  $hashes = [ordered]@{}
  Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName | ForEach-Object {
    $hashes[$_.FullName] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
  }
  return $hashes
}
$before = Inventory $evidence
$head = git rev-parse HEAD
$index = git diff --cached --binary | Out-String
$records = @()
function Attempt($Name, $Exe, [string[]]$Arguments) {
  $row = [ordered]@{stage=$Name; executable=$Exe; arguments=$Arguments; exit_code=$null; status='FAIL'}
  try {
    & $Exe @Arguments *> (Join-Path $run "$Name.log")
    $row.exit_code = $LASTEXITCODE
    if ($LASTEXITCODE -eq 0) { $row.status='PASS' }
  } catch {
    $row.exception = $_.ToString()
    $_ | Out-String | Set-Content (Join-Path $run "$Name-launch-error.log")
  }
  $script:records += $row
  $script:records | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $run 'attempts.json')
}
Attempt 'ps7-syntax' $pwsh @('-NoLogo','-NoProfile','-NonInteractive','-Command', '$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path scripts/phase2d_step32_host.ps1),[ref]$t,[ref]$e)|Out-Null;$e;if($e.Count){exit 1};$PSVersionTable.PSVersion.ToString()')
Attempt 'python-version' $py @('-c','import sys; assert sys.version_info[:2]==(3,11); print(sys.version)')
Attempt 'dependencies' $py @('-c','import numpy, scipy, matplotlib, pytest, threadpoolctl; print(threadpoolctl.__version__)')
Attempt 'regression' $py @('-m','pytest','-q')
Attempt 'compilation' $py @('-m','compileall','-q','src','scripts','tests')
Attempt 'host-local' $pwsh @('-NoLogo','-NoProfile','-NonInteractive','-File',"$PSScriptRoot/phase2d_step32_host.ps1",'-EvidenceRoot',$evidence,'-OutputRoot',"$run/host-output")
Attempt 'analytical' $py @('-m','stellarator_robust.cli','validate')
Attempt 'historical-review' $py @('scripts/phase2d_step32.py','historical','--inputs','results/phase2d/step31-20261031-165725-a14c217c/raw','--output',"$run/historical-review")
Attempt 'capture' $py @('scripts/phase2d_step32.py','capture','--output',"$run/capture")
Attempt 'local-controlled' $py @('scripts/phase2d_step32.py','local','--inputs',"$run/capture",'--output',"$run/local")
Attempt 'full-production-verification' $py @('scripts/phase2c_verify.py','--output',"$run/production")
Attempt 'fault-audit' $py @('scripts/phase2c_fault_audit.py','--root',"$run/production")
Attempt 'legacy-comparison' $py @('scripts/phase2c_legacy_compare.py','--root',"$run/production")
Attempt 'investigation' $py @('scripts/phase2b_investigate.py','--output',"$run/production/investigation",'--corrected',"$run/production")
Attempt 'finalization' $py @('scripts/phase2c_finalize.py','--output',"$run/production")
$after = Inventory $evidence
$before | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $run 'historical-before.json')
$after | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $run 'historical-after.json')
git diff --check *> (Join-Path $run 'git-diff-check.log'); $diffExit=$LASTEXITCODE
git fsck --full *> (Join-Path $run 'git-fsck.log'); $fsckExit=$LASTEXITCODE
@{historical_preserved=(($before|ConvertTo-Json -Compress) -ceq ($after|ConvertTo-Json -Compress)); head_preserved=($head -eq (git rev-parse HEAD)); index_preserved=($index -ceq (git diff --cached --binary | Out-String)); diff_check_exit=$diffExit; fsck_exit=$fsckExit; scientific_status='PARTIAL'} | ConvertTo-Json | Set-Content (Join-Path $run 'integrity.json')
Write-Output $run
