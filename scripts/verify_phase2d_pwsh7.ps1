#requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateNotNullOrEmpty()][string]$TargetPath
)

$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) {
    [Console]::Error.WriteLine('PowerShell 7 or later is required.')
    exit 2
}
try {
    $target = (Resolve-Path -LiteralPath $TargetPath -ErrorAction Stop).ProviderPath
    if (-not (Test-Path -LiteralPath $target -PathType Leaf) -or
        (Get-Item -LiteralPath $target).PSProvider.Name -ne 'FileSystem') {
        throw 'TargetPath must identify an existing filesystem file.'
    }
    $tokens = $null
    $parseErrors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile(
        $target, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) {
        foreach ($parseError in $parseErrors) {
            [Console]::Error.WriteLine(('{0}:{1}:{2}: {3}: {4}' -f
                $target, $parseError.Extent.StartLineNumber,
                $parseError.Extent.StartColumnNumber, $parseError.ErrorId,
                $parseError.Message))
        }
        exit 1
    }
    Write-Output "PowerShell 7 syntax OK: $target"
    exit 0
} catch {
    [Console]::Error.WriteLine("PowerShell syntax verification failed: $($_.Exception.Message)")
    exit 2
}
