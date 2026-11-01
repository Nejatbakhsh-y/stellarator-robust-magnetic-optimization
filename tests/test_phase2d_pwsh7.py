"""PowerShell 7 parser checks use -File and never execute their target."""
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / 'scripts/verify_phase2d_pwsh7.ps1'
HOST = ROOT / 'scripts/phase2d_step33_host.ps1'


def verifier_args(executable, target):
    return [executable, '-NoLogo', '-NoProfile', '-NonInteractive',
            '-File', str(VERIFIER), '-TargetPath', str(target)]


@pytest.fixture
def pwsh():
    executable = shutil.which('pwsh')
    if executable is None:
        pytest.skip('pwsh is unavailable')
    # A discovered but broken launcher must fail, not silently skip.
    return executable


def verify(pwsh, target):
    return subprocess.run(verifier_args(pwsh, target), capture_output=True,
                          text=True, cwd=ROOT, timeout=30)


def test_invocation_arguments():
    assert verifier_args('pwsh', HOST) == [
        'pwsh', '-NoLogo', '-NoProfile', '-NonInteractive', '-File',
        str(VERIFIER), '-TargetPath', str(HOST)]


def test_valid_syntax(pwsh, tmp_path):
    target = tmp_path / 'valid.ps1'
    target.write_text('param($x)\nWrite-Output $x\n', encoding='utf-8')
    result = verify(pwsh, target)
    assert result.returncode == 0, result.stderr
    assert str(target.resolve()) in result.stdout


def test_invalid_syntax(pwsh, tmp_path):
    target = tmp_path / 'invalid.ps1'
    target.write_text('function Broken {\n', encoding='utf-8')
    result = verify(pwsh, target)
    assert result.returncode != 0
    assert str(target.resolve()) in result.stderr
    assert 'MissingEndCurlyBrace' in result.stderr


def test_missing_target(pwsh, tmp_path):
    result = verify(pwsh, tmp_path / 'missing.ps1')
    assert result.returncode != 0
    assert result.stderr.strip()


def test_parse_without_execution_and_spaces(pwsh, tmp_path):
    target = tmp_path / 'target with spaces.ps1'
    marker = tmp_path / 'executed.txt'
    escaped = str(marker).replace("'", "''")
    target.write_text(f"Set-Content -LiteralPath '{escaped}' -Value executed\n"
                      "throw 'Target must never execute'\n", encoding='utf-8')
    original = target.read_bytes()
    result = verify(pwsh, target)
    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    assert target.read_bytes() == original


@pytest.mark.parametrize('target', [VERIFIER, HOST])
def test_repository_scripts_parse(pwsh, target):
    result = verify(pwsh, target)
    assert result.returncode == 0, result.stderr
