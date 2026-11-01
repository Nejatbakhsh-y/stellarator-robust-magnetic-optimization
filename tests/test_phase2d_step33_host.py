"""Execute host helpers with a fake gh; never publish or call GitHub."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'scripts/phase2d_step33_host.ps1'
SOURCE = HOST.read_text(encoding='utf-8-sig')
SHA = 'a' * 40
BASE_SHA = 'b' * 40
NAME = 'Phase 2D STEP 33 controlled causal attribution'


def invoke(tmp_path, records, command):
    exe = shutil.which('powershell') or shutil.which('pwsh')
    if not exe:
        pytest.skip('PowerShell unavailable')
    helpers = SOURCE[SOURCE.index('function Wait-Step33Run('):SOURCE.index('function Run-Python(')]
    fixture = tmp_path / 'runs.json'
    fixture.write_text(json.dumps(dict(total_count=len(records), workflow_runs=records) if isinstance(records, list) else records), encoding='utf-8')
    script = tmp_path / 'fixture.ps1'
    script.write_text(
        "$ErrorActionPreference='Stop'\n$out=$PSScriptRoot\n"
        "$repository='owner/repo'; $branch='research'\n"
        "$report=@{local_validation='PASS';implementation='LOCAL_GATES_PASSED';"
        "numerical_causal_attribution='INCONCLUSIVE';hosted_run_conclusion='success'}\n"
        "function Save-Json($Path,$Value) {}\n"
                "function gh { $script:cli=@($args); $global:LASTEXITCODE=0; "
        "if ($args[1] -like '*/pulls/7') { '{\"number\":7,\"head\":{\"ref\":\"research\",\"sha\":\"" + SHA + "\",\"repo\":{\"full_name\":\"owner/repo\"}},\"base\":{\"ref\":\"codex/phase2d-cross-platform-reproducibility\",\"repo\":{\"full_name\":\"owner/repo\"}}}' } "
        "elseif ($args[1] -like '*/commits/*') { '{\"sha\":\"" + 'c' * 40 + "\",\"parents\":[{\"sha\":\"" + BASE_SHA + "\"},{\"sha\":\"" + SHA + "\"}]}' } "
        "else { Get-Content (Join-Path $out 'runs.json') -Raw } }\n"
        + helpers + '\ntry { ' + command +
        " } catch { Set-HostFailure; $report.error=$_.Exception.Message }\n"
        "@{report=$report;cli=$script:cli} | ConvertTo-Json -Depth 20\n",
        encoding='utf-8')
    result = subprocess.run([exe, '-NoProfile', '-File', str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def record(**changes):
    result = dict(id=9, path='.github/workflows/phase2d-step33-causal.yml', head_sha=SHA,
                  event='push', head_branch='research', status='completed', conclusion='success',
                  created_at='2026-10-31T12:00:00Z', run_attempt=1,
                  repository=dict(full_name='owner/repo'), head_repository=dict(full_name='owner/repo'))
    result.update(changes)
    return result


def test_branch_only_commit_discovery(tmp_path):
    result = invoke(tmp_path, [record()], "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0")
    assert result['report']['hosted_workflow_discovery'] == 'PASS'
    assert '--workflow' not in result['cli']
    assert result['cli'][0] == 'api'
    assert 'actions/runs?branch=research&per_page=100' in result['cli'][1]


def test_latest_matching_run(tmp_path):
    result = invoke(tmp_path, [record(id=8), record()],
                    "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0; $report.selected=$r.databaseId")
    assert result['report']['selected'] == 9


def test_creation_time_precedes_run_id(tmp_path):
    result = invoke(tmp_path, [record(id=20, created_at='2026-10-30T12:00:00Z'),
                               record(created_at='2026-10-31T12:00:00Z')],
                    "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0; $report.selected=$r.databaseId")
    assert result['report']['selected'] == 9


def test_creation_time_tie_uses_numeric_run_id(tmp_path):
    result = invoke(tmp_path, [record(created_at='2026-10-31T12:00:00Z'),
                               record(id=10, created_at='2026-10-31T12:00:00Z')],
                    "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0; $report.selected=$r.databaseId")
    assert result['report']['selected'] == 10


@pytest.mark.parametrize('records', [
    [record(id='invalid')], [record(created_at='invalid')],
    [record(), record()], record(),
])
def test_malformed_or_ambiguous_discovery_fails(tmp_path, records):
    result = invoke(tmp_path, records, "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0")['report']
    assert result['hosted_workflow_discovery'] == 'FAIL'
    assert result['local_validation'] == 'PASS'
    assert result['numerical_causal_attribution'] == 'INCONCLUSIVE'


def test_cli_failure_preserves_local_pass(tmp_path):
    result = invoke(tmp_path, [], "function gh { $global:LASTEXITCODE=1 }; $r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 2 0")['report']
    assert result['hosted_workflow_discovery'] == 'FAIL'
    assert result['hosted_execution'] == 'INCONCLUSIVE'
    assert result['local_validation'] == 'PASS'


def test_delayed_visibility(tmp_path):
    command = (
        "$script:polls=0; function Start-Sleep {}\n"
        "function gh { $script:polls++; $global:LASTEXITCODE=0; "
        "if ($script:polls -eq 1) { '{\"total_count\":0,\"workflow_runs\":[]}' } else { Get-Content (Join-Path $out 'runs.json') -Raw } }; "
        "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 2 0; $report.polls=$script:polls"
    )
    result = invoke(tmp_path, [record()], command)['report']
    assert result['polls'] == 2
    assert result['hosted_workflow_discovery'] == 'PASS'


@pytest.mark.parametrize('changes', [dict(path='other.yml'), dict(head_sha='wrong'),
                                    dict(event='workflow_dispatch'), dict(head_branch='main'), dict(head_branch=None)])
def test_exact_identity_rejection(tmp_path, changes):
    r = record(); r.update(changes)
    result = invoke(tmp_path, [r], "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0")['report']
    assert result['hosted_execution'] == 'NOT_EXECUTED'
    assert result['local_validation'] == 'PASS'


def test_missing_run_is_not_comparison(tmp_path):
    result = invoke(tmp_path, [], "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0")['report']
    assert result['hosted_workflow_discovery'] == 'NOT_FOUND_WITHIN_BOUND'
    assert result['numerical_causal_attribution'] == 'INCONCLUSIVE'


def test_pending_run(tmp_path):
    r = record(); r['status'] = 'in_progress'
    result = invoke(tmp_path, [r], "$r=Wait-Step33Run 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 1 0")['report']
    assert result['hosted_execution'] == 'RUNNING'
    assert result['local_validation'] == 'PASS'


@pytest.mark.parametrize('conclusion', ['startup_failure', 'timed_out'])
def test_hosted_infrastructure_failure(tmp_path, conclusion):
    result = invoke(tmp_path, [], "Set-HostedRun ([pscustomobject]@{databaseId=9;conclusion='" + conclusion + "'}); Set-HostFailure")['report']
    assert result['hosted_execution'] == 'HOSTED_INFRASTRUCTURE_FAILURE'
    assert result['numerical_causal_attribution'] == 'INCONCLUSIVE'
    assert result['local_validation'] == 'PASS'


@pytest.mark.parametrize('code,conclusion,scientific,execution', [
    (0, 'success', 'PASS', 'PASS'),
    (1, 'failure', 'FAIL', 'NUMERICAL_COMPARISON_FAILURE'),
    (2, 'failure', 'INCONCLUSIVE', 'INCONCLUSIVE'),
    (0, 'failure', 'INCONCLUSIVE', 'HOSTED_INFRASTRUCTURE_OR_SOFTWARE_FAILURE'),
])
def test_comparison_status(tmp_path, code, conclusion, scientific, execution):
    result = invoke(tmp_path, [], f"$report.hosted_run_conclusion='{conclusion}'; Set-HostedComparison {code}; Set-HostFailure")['report']
    assert result['numerical_causal_attribution'] == scientific
    assert result['hosted_execution'] == execution
    assert result['local_validation'] == 'PASS'


def test_missing_artifacts_gate_precedes_comparison(tmp_path):
    result = invoke(tmp_path, [], 'Require-Step33Artifacts @() 9')['report']
    assert result['hosted_execution'] == 'MISSING_REQUIRED_ARTIFACTS'
    assert result['numerical_causal_attribution'] == 'INCONCLUSIVE'
    assert result['local_validation'] == 'PASS'
    assert SOURCE.index('    Require-Step33Artifacts $artifacts') < SOURCE.index("Run-Python 'hosted-comparison'")


def test_no_unintended_publication():
    publication = SOURCE.index('    $pr = & gh pr view')
    assert SOURCE.rfind('if ($PublishDiagnostic) {', 0, publication) > SOURCE.index("$report.local_validation = 'PASS'")
    assert 'gh workflow run' not in SOURCE
    assert 'gh pr merge' not in SOURCE
    assert 'git merge' not in SOURCE
    assert '--force' not in SOURCE
    assert '--workflow' not in SOURCE
    assert 'branches: [codex/phase2d-upstream-attribution]' in (ROOT / '.github/workflows/phase2d-step33-causal.yml').read_text()


def pr_record(**changes):
    item = record(event='pull_request', pull_requests=[dict(
        number=7, head=dict(ref='research', sha=SHA),
        base=dict(ref='codex/phase2d-cross-platform-reproducibility', sha=BASE_SHA))])
    item.update(changes)
    return item


@pytest.mark.parametrize('merge', [False, True])
def test_pr_source_and_synthetic_merge(tmp_path, merge):
    item = pr_record(head_sha='c' * 40 if merge else SHA)
    result = invoke(tmp_path, [item], f"$r=Wait-Step33Run '{SHA}' 1 0; $report.source=$r.sourceSha")['report']
    assert result['hosted_workflow_discovery'] == 'PASS'
    assert result['source'] == SHA


@pytest.mark.parametrize('field,value', [('number', 8), ('head.ref', 'wrong'),
                                         ('base.ref', 'main'), ('head.sha', 'd' * 40)])
def test_pr_identity_rejected(tmp_path, field, value):
    item = pr_record()
    target = item['pull_requests'][0]
    if '.' in field:
        parent, field = field.split('.')
        target = target[parent]
    target[field] = value
    result = invoke(tmp_path, [item], f"$r=Wait-Step33Run '{SHA}' 1 0")['report']
    assert result['hosted_execution'] == 'NOT_EXECUTED'
    assert result['local_validation'] == 'PASS'


def test_invalid_merge_parents(tmp_path):
    result = invoke(tmp_path, [pr_record(head_sha='d' * 40)],
                    f"$r=Wait-Step33Run '{SHA}' 1 0")['report']
    assert result['hosted_workflow_discovery'] == 'FAIL'


def test_successful_and_failed_run(tmp_path):
    for conclusion in ('success', 'failure'):
        result = invoke(tmp_path, [record(conclusion=conclusion)],
                        f"$r=Wait-Step33Run '{SHA}' 1 0; Set-HostedRun $r")['report']
        assert result['hosted_run_conclusion'] == conclusion
        assert result['local_validation'] == 'PASS'
        assert result['numerical_causal_attribution'] == 'INCONCLUSIVE'


def test_workflow_stage_guards():
    text = (ROOT / '.github/workflows/phase2d-step33-causal.yml').read_text()
    assert 'types: [opened, synchronize, reopened]' in text
    assert 'branches: [codex/phase2d-cross-platform-reproducibility]' in text
    assert 'pull_request_target' not in text
    assert 'permissions:\n  contents: read' in text
    assert "if: always() && needs.capture.result == 'success' && needs.replay.result == 'success'" in text
    comparison = text.split('      - run: python scripts/phase2d_step33.py compare', 1)[1].split('      - uses:', 1)[0]
    assert 'if: always()' not in comparison
    assert text.count('ref: "${{ github.event.pull_request.head.sha || github.sha }}"') == 3
    assert text.count('if-no-files-found: error') == 5


def test_incomplete_and_ambiguous_artifacts(tmp_path):
    for artifacts in ([], [dict(name='step33-capture-windows-reference-9-1', expired=False)]):
        literal = json.dumps(artifacts).replace("'", "''")
        result = invoke(tmp_path, [], "$a=ConvertFrom-Json '" + literal + "'; Require-Step33Artifacts $a 9 1")['report']
        assert result['hosted_artifacts'] == 'FAIL'
        assert result['local_validation'] == 'PASS'


def test_complete_artifact_inventory(tmp_path):
    artifacts = [dict(name=f'step33-{kind}-{cohort}-9-1', expired=False)
                 for kind in ('capture', 'replay')
                 for cohort in ('windows-reference', 'linux-reference',
                                'linux-numpy-sensitivity', 'linux-scipy-sensitivity')]
    literal = json.dumps(artifacts)
    result = invoke(tmp_path, [], "$a=ConvertFrom-Json '" + literal + "'; Require-Step33Artifacts $a 9 1")['report']
    assert result['hosted_artifacts'] == 'PASS'
