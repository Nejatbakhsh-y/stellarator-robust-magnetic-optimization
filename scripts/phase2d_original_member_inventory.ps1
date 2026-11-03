param(
    [string]$ArchiveRoot = 'results/phase2d/step49-original-archives-20261102-120255-a1314650',
    [string]$Output = 'results/phase2d/final-root-cause-local'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Web.Extensions
$json = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$json.MaxJsonLength = [int]::MaxValue
$root = (Resolve-Path $ArchiveRoot).Path
if (Test-Path $Output) { throw 'Fresh output directory required' }
$null = New-Item -ItemType Directory -Path $Output
function Digest([byte[]]$bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
function Save($name, $value) {
    [IO.File]::WriteAllText((Join-Path (Resolve-Path $Output) $name), ($value | ConvertTo-Json -Depth 90), (New-Object Text.UTF8Encoding($false)))
}
$manifestBytes = [IO.File]::ReadAllBytes((Join-Path $root 'manifest.json'))
$manifest = $json.DeserializeObject([Text.Encoding]::UTF8.GetString($manifestBytes))
$archives = @(); $members = @(); $references = @(); $inputs = @(); $environments = @()
foreach ($run in $manifest['runs']) {
    foreach ($artifact in $run['artifacts']) {
        $path = Join-Path $root $artifact['file']
        $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -cne $artifact['verified_sha256'] -or ('sha256:'+$actual) -cne $artifact['github_sha256']) { throw "Archive mismatch: $path" }
        $archives += [ordered]@{run_id=$run['run_id']; artifact_id=$artifact['id']; source_sha=$run['source_sha']; file=$artifact['file']; sha256=$actual; status='MATCH_SUPPLIED_MANIFEST'}
        $zip = [IO.Compression.ZipFile]::OpenRead($path)
        $local = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        try {
            foreach ($entry in $zip.Entries) {
                if ($entry.FullName.EndsWith('/')) { continue }
                if ($entry.Length -gt 134217728) { throw 'Member size bound exceeded' }
                $stream = $entry.Open(); $buffer = New-Object IO.MemoryStream
                try { $stream.CopyTo($buffer); $bytes = $buffer.ToArray() } finally { $stream.Dispose(); $buffer.Dispose() }
                $name = $entry.FullName
                if ($local.ContainsKey($name)) { throw 'Duplicate member' }
                $record = [ordered]@{run_id=$run['run_id']; artifact_id=$artifact['id']; member=$name; sha256=(Digest $bytes); length=$bytes.Length}
                $members += $record
                $local.Add($name, @{record=$record; bytes=$bytes})
            }
            foreach ($name in $local.Keys) {
                $leaf = ($name -split '/')[-1]
                if ($leaf -in @('inputs.json','sealed-inputs.json')) {
                    $data = $json.DeserializeObject([Text.Encoding]::UTF8.GetString($local[$name].bytes))
                    $inputs += [ordered]@{run_id=$run['run_id']; artifact_id=$artifact['id']; member=$name; sha256=$local[$name].record.sha256; schema=$data['schema']; authentication='ZIP_MEMBER_BYTES_ONLY'; semantic_seal='NOT_EXECUTED'}
                }
                if ($leaf -eq 'environment.json') {
                    $environments += @{identity=$local[$name].record; original=$json.DeserializeObject([Text.Encoding]::UTF8.GetString($local[$name].bytes))}
                }
                if ($leaf -notin @('manifest.json','input-sha256.json','input-manifest.json','output-manifest.json')) { continue }
                $data = $json.DeserializeObject([Text.Encoding]::UTF8.GetString($local[$name].bytes))
                if ($data -isnot [Collections.IDictionary]) { continue }
                $mapping = $data
                if ($data.ContainsKey('outputs')) { $mapping = $data['outputs'] }
                $base = if ($name.Contains('/')) { $name.Substring(0,$name.LastIndexOf('/')+1) } else { '' }
                foreach ($target in $mapping.Keys) {
                    $pairs = @()
                    if ($mapping[$target] -is [Collections.IDictionary] -and $leaf -eq 'input-manifest.json') {
                        foreach ($relative in $mapping[$target].Keys) { $pairs += @{path=($target+'/'+$relative); expected=$mapping[$target][$relative]; external=$true} }
                    } else { $pairs += @{path=($base+$target); expected=$mapping[$target]; external=$false} }
                    foreach ($pair in $pairs) {
                        if ($pair.expected -isnot [string] -or $pair.expected -cnotmatch '^[0-9a-f]{64}$') { continue }
                        $status = 'MISSING_EVIDENCE'
                        if ($local.ContainsKey($pair.path)) { $status = if ($local[$pair.path].record.sha256 -ceq $pair.expected) {'MATCH'} else {'MISMATCH'} }
                        $references += [ordered]@{run_id=$run['run_id']; artifact_id=$artifact['id']; seal_member=$name; requested_member=$pair.path; expected_sha256=$pair.expected; external=$pair.external; direct_status=$status}
                    }
                }
            }
        } finally { $zip.Dispose() }
    }
}
foreach ($reference in $references) {
    if ($reference.direct_status -eq 'MATCH') { continue }
    $matches = @($members | Where-Object { $_.run_id -eq $reference.run_id -and $_.sha256 -ceq $reference.expected_sha256 })
    $reference['same_run_exact_bytes'] = $matches
    $reference['classification'] = if ($reference.direct_status -eq 'MISMATCH') {'CONTENT_MISMATCH'} elseif ($matches.Count) {'BYTES_RECOVERED_PATH_ASSOCIATION_UNPROVEN'} else {'MISSING_EVIDENCE'}
}
Save 'archive-inventory.json' $archives
Save 'member-inventory.json' $members
Save 'seal-reference-investigation.json' $references
Save 'numerical-input-inventory.json' $inputs
Save 'historical-environments.json' $environments
Save 'inventory-summary.json' ([ordered]@{manifest_sha256=(Digest $manifestBytes); archives=$archives.Count; members=$members.Count; numerical_input_members=$inputs.Count; unique_input_hashes=@($inputs.sha256 | Sort-Object -Unique).Count; seal_references=$references.Count; reference_counts=@($references | Group-Object { $_['direct_status'] } | Select-Object Name,Count); unresolved_counts=@($references | Where-Object direct_status -ne MATCH | Group-Object { $_['classification'] } | Select-Object Name,Count); trust_scope='Original bytes match supplied STEP49 manifest; no fresh external attestation; no semantic or numerical validation'; implementation_sha256=(Get-FileHash $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()})
