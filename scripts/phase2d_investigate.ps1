param(
    [string]$Evidence = 'results/ci/phase2d-inputs/run-41061184709',
    [string]$Output = 'results/phase2d/investigation'
)
$ErrorActionPreference = 'Stop'
if (Test-Path $Output) { throw "Refusing to overwrite $Output; choose a fresh output path" }
$root = (Resolve-Path $Evidence).Path
$rows = @(Import-Csv (Join-Path $root 'sha256_inventory.csv'))
if ($rows.Count -ne 247) { throw 'Expected the supplied 247-file inventory' }
foreach ($row in $rows) {
    $path = [IO.Path]::GetFullPath((Join-Path $root $row.Path))
    if (!$path.StartsWith($root+[IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe inventory path' }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $row.SHA256 -or
        (Get-Item -LiteralPath $path).Length -ne [long]$row.Bytes) { throw "Evidence mismatch: $path" }
}
New-Item -ItemType Directory -Path $Output | Out-Null
Add-Type -Path (Join-Path $PSScriptRoot 'phase2d_reference.cs') -ReferencedAssemblies System.Numerics
function Load($path) { Get-Content -LiteralPath $path -Raw | ConvertFrom-Json }
function Currents($quick, $fault) {
    [double[]]$pre = $quick.currents_A.dense
    [double[]]$frozen = $pre.Clone(); $frozen[$fault.failed] = 0
    return ,([double[][]]@($pre, $frozen, [double[]]$fault.recovery_evidence.recovered_currents_A))
}
$workers = @('phase2c-windows-reference','phase2c-linux-reference','phase2c-linux-numpy-sensitivity','phase2c-linux-scipy-sensitivity')
$loaded = @{}; $audit = @(); $hybrids = @(); $failures = @()
foreach ($worker in $workers) {
    $p = Join-Path $root $worker
    $q = Load "$p/quick/results.json"; $input = Load "$p/fault-reference-inputs.json"
    $execution = Load "$p/execution.json"
    $loaded[$worker] = @{quick=$q; input=$input; execution=$execution}
    $comparison = Load "$p/committed-reference-comparison.json"
    foreach ($f in $comparison.failures) {
        $abs = [math]::Abs($f.reference-$f.current)
        $failures += [ordered]@{worker=$worker; path=$f.path; reference=$f.reference; observed=$f.current;
            absolute_error=$abs; relative_error=$abs/[math]::Abs($f.reference);
            threshold=1e-13+1e-11*[math]::Abs($f.current); units='dimensionless'; environment=$execution.environment;
            significance='Outside unchanged scientific gate; repeated evidence paths are retained'}
    }
    for ($i=0; $i -lt $q.faults.Count; $i++) {
        $f=$q.faults[$i]; $currents=Currents $q $f
        $values=@(); foreach ($digits in @(60,90)) {
            $values += [Phase2DReference]::Ratio([double[][]]$input.response_T_per_A,
                [double[]]$input.disturbance_T,[double[]]$input.weights,$currents,$digits)
        }
        $value=[double]::Parse($values[1],[Globalization.CultureInfo]::InvariantCulture)
        $audit += [ordered]@{worker=$worker; row=$i; failed_coil=$f.failed; precision_60=$values[0]; precision_90=$values[1];
            binary64_precision_agreement=([double]$values[0] -eq $value);
            saved=$f.fractional_recovery; absolute_error=[math]::Abs($value-$f.fractional_recovery);
            threshold=1e-13+1e-11*[math]::Abs($value);
            input_sha256=(Get-FileHash "$p/fault-reference-inputs.json").Hash;
            quick_sha256=(Get-FileHash "$p/quick/results.json").Hash}
    }
    Write-Host "$worker independently evaluated $($q.faults.Count) outages"
}
$win=$loaded[$workers[0]]
foreach ($worker in $workers[1..3]) {
    $other=$loaded[$worker]
    foreach ($i in @(3,4)) {
        foreach ($which in @('windows-model-other-currents','other-model-windows-currents')) {
            $model=if ($which -eq 'windows-model-other-currents') {$win} else {$other}
            $cur=if ($which -eq 'windows-model-other-currents') {$other} else {$win}
            $value=[Phase2DReference]::Ratio([double[][]]$model.input.response_T_per_A,
                [double[]]$model.input.disturbance_T,[double[]]$model.input.weights,
                (Currents $cur.quick $cur.quick.faults[$i]),90)
            $hybrids += [ordered]@{worker=$worker; row=$i; experiment=$which; ratio_90=$value}
        }
    }
}
$record=[ordered]@{status='INVESTIGATION_ONLY'; scientific_status='PARTIAL'; inventory_count=$rows.Count;
    inventory_sha256=(Get-FileHash "$root/sha256_inventory.csv").Hash; inventory_verified=$true;
    provenance_scope='User-supplied extracted artifacts; internal hashes verified, no authenticated run API record or original ZIP digest supplied';
    environments=@($workers | ForEach-Object { @{worker=$_; environment=$loaded[$_].execution.environment} });
    reported_failures=$failures; independent_fault_audits=$audit; input_swap_experiments=$hybrids;
    method='BigInteger fixed-point arithmetic, exact binary64 bit decomposition at 60/90 fractional decimal places; direct RMS subtraction, separate from production factored-energy metric; convergence diagnostic, not interval certificate'}
$record | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 "$Output/reference-audit.json"
Write-Host "Wrote $Output/reference-audit.json"
