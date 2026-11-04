param(
    [string]$Evidence = 'results/ci/phase2d-hosted-investigation-41195815229',
    [string]$Output = 'results/phase2d/hosted-attribution-41195815229'
)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Output) { throw 'Fresh output required' }
$root = (Resolve-Path $Evidence).Path
New-Item -ItemType Directory -Path $Output | Out-Null
function Binary64($v) {
    # Windows PowerShell JSON decimals must be parsed, not cast: decimal-to-double
    # casts can differ by an ulp from Python's correctly rounded lexical parse.
    if ($v -is [decimal]) {
        return [double]::Parse($v.ToString([Globalization.CultureInfo]::InvariantCulture),[Globalization.CultureInfo]::InvariantCulture)
    }
    if ($v -is [array]) {
        for($k=0;$k -lt $v.Count;$k++){$v[$k]=Binary64 $v[$k]}
        return ,$v
    }
    if ($v -is [pscustomobject]) {foreach($p in $v.PSObject.Properties){$p.Value=Binary64 $p.Value}}
    return $v
}
function Load($p) { Binary64 (Get-Content -LiteralPath $p -Raw | ConvertFrom-Json) }
function Save($name,$obj) { $obj | ConvertTo-Json -Depth 80 | Set-Content -Encoding UTF8 "$Output/$name" }
function Inventory {
    @(Get-ChildItem -LiteralPath $root -File -Recurse | Sort-Object FullName | ForEach-Object {
        [ordered]@{path=$_.FullName.Substring($root.Length+1); bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}
    })
}
$before = Inventory
Save 'original-inventory.json' $before
Add-Type -Path (Join-Path $PSScriptRoot 'phase2d_reference.cs') -ReferencedAssemblies System.Numerics
function Currents($q,$i) {
    [double[]]$pre=$q.currents_A.dense
    [double[]]$frozen=$pre.Clone(); $frozen[$q.faults[$i].failed]=0
    return ,([double[][]]@($pre,$frozen,[double[]]$q.faults[$i].recovery_evidence.recovered_currents_A))
}
function Ratio($m,$q,$i,$digits) {
    [Phase2DReference]::Ratio([double[][]]$m.response_T_per_A,[double[]]$m.disturbance_T,[double[]]$m.weights,(Currents $q $i),$digits)
}
function VectorDiff($a,$b) {
    if ($a.Count -ne $b.Count) { throw 'Dimension mismatch' }
    $max=0.; $index=-1; $count=0; $delta=@()
    for($j=0;$j -lt $a.Count;$j++) {
        $d=[double]$b[$j]-[double]$a[$j]; $delta+=,$d
        if($d -ne 0){$count++}; if([math]::Abs($d) -gt $max){$max=[math]::Abs($d);$index=$j}
    }
    [ordered]@{max_absolute=$max; index=$index; changed=$count; delta=$delta}
}
$workers=@('phase2d-windows-reference','phase2d-linux-reference','phase2d-linux-numpy-sensitivity','phase2d-linux-scipy-sensitivity')
$loaded=@{}; $manifests=@(); $audits=@(); $swaps=@(); $diffs=@(); $environments=@()
foreach($worker in $workers) {
    $p=Join-Path $root $worker
    $manifest=Load "$p/manifest.json"; $mismatch=@()
    $expectedNames = @($manifest.PSObject.Properties.Name | Sort-Object)
    $actualNames = @(Get-ChildItem -LiteralPath $p -File -Recurse | ForEach-Object {
        $_.FullName.Substring($p.Length+1).Replace('\','/')
    } | Where-Object { $_ -notin @('manifest.json','committed-reference-comparison.json') } | Sort-Object)
    if ($expectedNames.Count -ne 59 -or (Compare-Object $expectedNames $actualNames)) {
        Save 'status.json' @{status='FAIL';error='Incomplete historical manifest inventory';worker=$worker}
        throw 'Incomplete historical manifest inventory'
    }
    foreach($entry in $manifest.PSObject.Properties) {
        $target=[IO.Path]::GetFullPath((Join-Path $p $entry.Name))
        if(!$target.StartsWith($p+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe manifest path'}
        if((Get-FileHash -LiteralPath $target).Hash -ne $entry.Value){$mismatch+=,$entry.Name}
    }
    $manifests+=,[ordered]@{worker=$worker; entries=@($manifest.PSObject.Properties).Count; mismatches=$mismatch}
    if ($mismatch.Count) {
        Save 'manifest-checks.json' $manifests
        Save 'status.json' @{status='FAIL';error='Historical artifact hash mismatch';worker=$worker}
        throw 'Historical artifact hash mismatch; failed evidence retained'
    }
    $q=Load "$p/quick/results.json"; $m=Load "$p/fault-reference-inputs.json"
    $loaded[$worker]=@{q=$q;m=$m}
    $environments+=,[ordered]@{worker=$worker;execution=(Load "$p/execution.json"); config=$q.metadata.config}
    foreach($i in @(3,4)) {
        $low=Ratio $m $q $i 60; $high=Ratio $m $q $i 90
        $ev=$q.faults[$i].recovery_evidence; $r=$ev.rms_T
        $audits+=,[ordered]@{worker=$worker; row=$i; failed_coil=$q.faults[$i].failed;
            precision60=$low;precision90=$high;saved=$q.faults[$i].fractional_recovery;
            saved_error=[math]::Abs([double]$high-$q.faults[$i].fractional_recovery);
            rms_subtraction_condition=($r[1]+$r[0])/[math]::Abs($r[1]-$r[0]);
            numerator_energy_condition=$ev.numerator_sum_abs_T2/[math]::Abs($ev.numerator_energy_T2);
            denominator_energy_condition=$ev.denominator_sum_abs_T2/[math]::Abs($ev.denominator_energy_T2);
            quick_sha256=(Get-FileHash "$p/quick/results.json").Hash; input_sha256=(Get-FileHash "$p/fault-reference-inputs.json").Hash}
    }
    Write-Host "$worker high precision complete"
}
$win=$loaded[$workers[0]]
foreach($worker in $workers[1..3]) {
    $other=$loaded[$worker]
    $matrixA=@($win.m.response_T_per_A | ForEach-Object {foreach($v in $_){$v}})
    $matrixB=@($other.m.response_T_per_A | ForEach-Object {foreach($v in $_){$v}})
    $diffs+=,[ordered]@{worker=$worker;block='response_T_per_A';difference=(VectorDiff $matrixA $matrixB)}
    foreach($key in @('disturbance_T','weights')) {
        $diffs+=,[ordered]@{worker=$worker;block=$key;difference=(VectorDiff $win.m.$key $other.m.$key)}
    }
    foreach($key in $win.q.currents_A.PSObject.Properties.Name) {
        $diffs+=,[ordered]@{worker=$worker;block="currents_A/$key";difference=(VectorDiff $win.q.currents_A.$key $other.q.currents_A.$key)}
    }
    foreach($i in @(3,4)) {
        $diffs+=,[ordered]@{worker=$worker;block="recovered_currents_A/$i";difference=(VectorDiff $win.q.faults[$i].recovery_evidence.recovered_currents_A $other.q.faults[$i].recovery_evidence.recovered_currents_A)}
        foreach($model in @('windows','other')) {foreach($current in @('windows','other')) {
            $m=if($model -eq 'windows'){$win.m}else{$other.m}
            $q=if($current -eq 'windows'){$win.q}else{$other.q}
            $swaps+=,[ordered]@{worker=$worker;row=$i;model=$model;currents=$current;ratio90=(Ratio $m $q $i 90)}
        }}
    }
}
$failures=[Collections.Generic.List[object]]::new()
function Visit($node,$file,$trail) {
    if($null -eq $node){return}
    if($node -is [System.Management.Automation.PSCustomObject]) {
        if($node.PSObject.Properties['reference'] -and $node.PSObject.Properties['current'] -and
            $node.reference -is [ValueType] -and $node.current -is [ValueType]) {
            $err=[math]::Abs([double]$node.reference-[double]$node.current)
            $bound=1e-13+1e-11*[math]::Abs([double]$node.current)
            if($err -gt $bound) {$failures.Add([ordered]@{file=$file;location=$trail;path=$node.path;reference=$node.reference;current=$node.current;absolute_error=$err;bound=$bound;status='FAIL'})}
        }
        foreach($prop in $node.PSObject.Properties){Visit $prop.Value $file "$trail/$($prop.Name)"}
    } elseif($node -is [array]) {for($k=0;$k -lt $node.Count;$k++){Visit $node[$k] $file "$trail/$k"}}
}
foreach($file in Get-ChildItem -LiteralPath $root -Filter '*.json' -Recurse){Visit (Load $file.FullName) $file.FullName.Substring($root.Length+1) ''}
Save 'failed-comparisons.json' @($failures.ToArray())
Save 'independent-references.json' $audits
Save 'block-swaps.json' $swaps
Save 'vector-differences.json' $diffs
Save 'environments-and-settings.json' $environments
Save 'manifest-checks.json' $manifests
$after=Inventory
if(($before|ConvertTo-Json -Depth 8 -Compress) -ne ($after|ConvertTo-Json -Depth 8 -Compress)){throw 'Original evidence changed'}
Save 'status.json' ([ordered]@{status='INCONCLUSIVE';scientific_status='PARTIAL';head=(git rev-parse HEAD);original_evidence_unchanged=$true;files=$before.Count;
    archive_authentication='INCONCLUSIVE: authenticated run metadata and archive digest evidence required; local manifests alone are insufficient';
    method='Independent BigInteger fixed point direct RMS subtraction at 60 and 90 decimal places, exact binary64 decomposition; not an interval certificate';
    production_correction='None justified';python_execution='BLOCKED: venv base Python executable unavailable'})
Save 'manifest.json' @(Get-ChildItem -LiteralPath $Output -File | ForEach-Object {[ordered]@{path=$_.Name;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}})
