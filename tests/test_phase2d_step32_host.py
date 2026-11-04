"""Exercise the actual host native-failure wrapper without numerical runs."""
import json
from pathlib import Path
import shutil
import subprocess
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'scripts/phase2d_step32_host.ps1'


def test_dependency_declared_and_checked_before_collection():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8-sig'))
    assert any(d.startswith('threadpoolctl') for d in project['project']['optional-dependencies']['dev'])
    source = HOST.read_text(encoding='utf-8-sig')
    assert source.index("Run-Python 'dependency-preflight'") < source.index("Run-Python 'tests'")
    assert 'if ($Publish -and (Get-Command gh' in source


def test_native_exit_two_retained_and_visible(tmp_path):
    exe = shutil.which('pwsh')
    if not exe:
        pytest.skip('PowerShell 7 unavailable')
    source = HOST.read_text(encoding='utf-8-sig')
    function = source[source.index('function Run-Python('):source.index('function Inventory(')]
    script = tmp_path / 'failure.ps1'
    script.write_text(
        "$ErrorActionPreference='Stop'\n$out=$PSScriptRoot\n"
        "$py=(Get-Process -Id $PID).Path\n"
        "$report=@{steps=@();local_validation='INCONCLUSIVE'}\n"
        "function Save-Json($Path,$Value) { $Value | ConvertTo-Json -Depth 20 | Set-Content $Path }\n"
        + function +
        "\ntry { Run-Python 'dependency-preflight' @('-NoProfile','-Command',"
        "'[Console]::Error.WriteLine(\"ModuleNotFoundError: threadpoolctl\"); exit 2') }\n"
        "catch { [Console]::Error.WriteLine(\"stage=$stage; $_\"); exit 2 }\n",
        encoding='utf-8')
    try:
        result = subprocess.run([exe, '-NoProfile', '-File', str(script)], capture_output=True, text=True)
    except OSError as exc:
        pytest.skip(f'PowerShell cannot start: {exc}')
    assert result.returncode == 2
    assert 'stage=dependency-preflight' in result.stderr
    assert 'exit 2' in result.stderr
    record = json.loads((tmp_path / 'execution.json').read_text(encoding='utf-8-sig'))
    assert record['steps'][0]['exit_code'] == 2
    assert record['local_validation'] != 'PASS'
    assert 'threadpoolctl' in (tmp_path / 'dependency-preflight.log').read_text(encoding='utf-8-sig')
