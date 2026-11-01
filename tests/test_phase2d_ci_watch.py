"""Run the monitor against a fake CLI, without network or credentials."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/phase2d_ci_watch.ps1'
SHA = 'a' * 40


@pytest.fixture(params=['powershell', 'pwsh'])
def shell(request):
    exe = shutil.which(request.param)
    if not exe:
        pytest.skip(f'{request.param} unavailable')
    # An installed executable which fails to start is a failure, not a skip.
    return exe


def invoke(tmp_path, shell, scalar='9', conclusion='success', status='completed', **changes):
    run = dict(id=9, head_sha=SHA, head_branch='research',
               path='.github/workflows/ci.yml', status=status,
               conclusion=conclusion, event='pull_request')
    run.update(changes)
    (tmp_path / 'run.json').write_text(json.dumps(run), encoding='utf-8')
    wrapper = tmp_path / 'fake.ps1'
    wrapper.write_text(
        "$ErrorActionPreference='Stop'\n"
        "function global:gh { $global:LASTEXITCODE=0; "
        "if ($args -contains '--jq') { '" + scalar.replace("'", "''") + "' } "
        "elseif ($args[0] -eq 'api') { Get-Content '" + str(tmp_path / 'run.json') + "' -Raw } "
        "else { 'failing logs'; } }\n"
        "& '" + str(SCRIPT) + "' -Repository owner/repo -Branch research -Commit "
        + SHA + ' -MaxPolls 1 -PollSeconds 0\nexit $LASTEXITCODE\n', encoding='utf-8')
    proc = subprocess.run([shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(wrapper)],
                          capture_output=True, text=True)
    return proc, json.loads(proc.stdout)


@pytest.mark.parametrize('scalar,expected', [('', 'MISSING'), ('null', 'ERROR'),
                         ('{}', 'ERROR'), ('[9,10]', 'ERROR'), ('0', 'ERROR'),
                         ('9\n10', 'ERROR'), ('garbage', 'ERROR')])
def test_invalid_ids(tmp_path, shell, scalar, expected):
    proc, report = invoke(tmp_path, shell, scalar=scalar)
    assert proc.returncode != 0
    assert report['status'] == expected


@pytest.mark.parametrize('conclusion', ['failure', 'cancelled', 'timed_out', 'neutral', 'skipped', None])
def test_unsuccessful(tmp_path, shell, conclusion):
    proc, report = invoke(tmp_path, shell, conclusion=conclusion)
    assert proc.returncode == 1
    assert report['status'] == 'FAIL'
    assert 'failing logs' in proc.stderr


def test_success(tmp_path, shell):
    proc, report = invoke(tmp_path, shell)
    assert proc.returncode == 0
    assert report['status'] == 'PASS'
    assert report['run_id'] == '9'


@pytest.mark.parametrize('status,expected', [('queued', 'QUEUED'), ('in_progress', 'RUNNING')])
def test_pending(tmp_path, shell, status, expected):
    proc, report = invoke(tmp_path, shell, status=status)
    assert proc.returncode != 0
    assert report['status'] == expected


@pytest.mark.parametrize('changes', [dict(head_sha='b'*40), dict(id=8), dict(path='wrong'),
                                      dict(head_branch='main')])
def test_identity(tmp_path, shell, changes):
    proc, report = invoke(tmp_path, shell, **changes)
    assert proc.returncode != 0
    assert report['status'] == 'ERROR'


def test_multiple_run_selection_contract():
    source = SCRIPT.read_text()
    assert '--jq' in source and '--paginate' in source and '--slurp' in source
    assert 'sort_by([if .event == "pull_request" then 1 else 0 end, .created_at, .id]) | last' in source
    assert 'head_sha=$Commit' in source
    assert '.databaseId' not in source
