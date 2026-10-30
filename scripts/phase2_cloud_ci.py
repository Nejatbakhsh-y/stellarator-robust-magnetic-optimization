"""Full Phase 2 CI in a disposable worktree; never publish generated evidence."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from stellarator_robust.ci_evidence import compare_study, require_link
from stellarator_robust.evidence import file_hash

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ad1ca5285a20717a03c202c31e5d4a5d2152412c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def references(root):
    manifest = json.loads((root/'results/phase2/manifest.json').read_text())
    if not manifest:
        raise AssertionError('empty manifest')
    required = []
    for folder, pattern in (('src', '*.py'), ('tests', '*.py'), ('scripts', '*.py'), ('configs', '*.json')):
        required.extend((root/folder).rglob(pattern))
    required.append(root/'.gitattributes')
    required.extend(p for p in (root/'results/phase2').rglob('*')
                    if p.is_file() and p.name not in ('manifest.json', 'gate.json'))
    if not all(p.relative_to(root).as_posix() in manifest for p in required):
        raise AssertionError('manifest completeness before regeneration')
    for name, digest in manifest.items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or not (root/path).is_file():
            raise AssertionError('invalid manifest path: '+name)
        if file_hash(root/path) != digest:
            raise AssertionError('manifest mismatch: '+name)
    for name in ('results/quick/results.json', 'results/phase2/study.json'):
        raw = subprocess.check_output(['git', 'cat-file', '--filters', BASE+':'+name], cwd=root) if name.startswith('results/quick/') else subprocess.check_output(['git', 'show', BASE+':'+name], cwd=root)
        if hashlib.sha256(raw).hexdigest() != sha(root/name):
            raise AssertionError('published numerical reference changed: '+name)
    digest = sha(root/'results/phase2/study.json')
    for name in ('training_audit', 'reproducibility', 'failure_sensitivity'):
        require_link(json.loads((root/f'results/phase2/{name}.json').read_text()), digest)
    gate = json.loads((root/'results/phase2/gate.json').read_text())
    if gate['software_status'] != 'PASS' or gate['scientific_status'] != 'PARTIAL' or gate['study_sha256'] != digest:
        raise AssertionError('invalid saved gate')
    return digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--local-overlay', action='store_true', help='Test uncommitted implementation; never remote verification')
    args = parser.parse_args()
    os.chdir(ROOT)
    artifacts = ROOT/'results/ci/phase2-cloud'/('smoke' if args.smoke else 'full')
    artifacts.mkdir(parents=True, exist_ok=True)
    record = dict(status='FAIL', remote_verified=False, local_overlay=args.local_overlay,
                  commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  python=platform.python_version(), platform=platform.platform(),
                  packages={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'matplotlib', 'pytest')},
                  steps=[])
    def run(label, command, cwd):
        start = time.monotonic()
        with (artifacts/(label+'.log')).open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        record['steps'].append(dict(stage=label, command=command, returncode=result.returncode,
                                    seconds=time.monotonic()-start))
        (artifacts/'execution.json').write_text(json.dumps(record, indent=2))
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(label+' failed; see artifact log')
    work = ROOT/'results/reproduction/cloud-work'
    try:
        record['reference_study_sha256'] = references(ROOT)
        if args.smoke:
            run('pytest', [sys.executable, '-m', 'pytest', '-q'], ROOT)
            run('saved-gate', [sys.executable, 'scripts/phase2_gate.py'], ROOT)
        else:
            if work.exists():
                raise RuntimeError('Disposable worktree already exists; preserve and inspect it before retrying')
            run('worktree', ['git', 'worktree', 'add', '--detach', str(work), 'HEAD'], ROOT)
            if args.local_overlay:
                names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], text=True).splitlines()
                for name in names:
                    if name.startswith(('src/', 'scripts/', 'tests/', 'configs/', '.github/')) or name in ('.gitattributes',):
                        target = work/name; target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(ROOT/name, target)
            # Avoid loading editable-install source from the original checkout.
            os.environ['PYTHONPATH'] = str(work/'src')
            reference = json.loads((work/'results/phase2/study.json').read_text())
            # The hash-linked historical input is CRLF. Git's Phase 1 text blob is LF.
            # Validate semantic identity, then use the frozen bytes only in this disposable worktree.
            frozen = work/'results/phase2/phase1_input.json'
            quick = work/'results/quick/results.json'
            if json.loads(frozen.read_text()) != json.loads(quick.read_text()) or sha(frozen) != reference['phase1_sha256']:
                raise AssertionError('frozen Phase 1 input is not the published study input')
            record['phase1_input_bytes'] = dict(checkout_sha256=sha(quick), frozen_sha256=sha(frozen))
            quick.write_bytes(frozen.read_bytes())
            run('fresh-study', [sys.executable, 'scripts/phase2_study.py'], work)
            current = json.loads((work/'results/phase2/study.json').read_text())
            comparison = {}
            previous = Path.cwd(); os.chdir(work)
            try:
                compare_study(reference, current, report=comparison)
            finally:
                os.chdir(previous)
                (artifacts/'checkpoint-comparison.json').write_text(json.dumps(comparison, indent=2))
            for label, script in [('full-repeat', 'phase2_verify'), ('training-audit', 'phase2_training_audit'),
                                  ('negative-gate', 'phase2_failure_check'), ('manifest', 'phase2_refresh_manifest'),
                                  ('final-gate', 'phase2_gate'), ('reports', 'phase2_reports')]:
                run(label, [sys.executable, 'scripts/'+script+'.py'], work)
            record['fresh_study_sha256'] = sha(work/'results/phase2/study.json')
            record['scientific_status'] = 'PARTIAL'
        record['status'] = 'PASS'
    except Exception as exc:
        record['error'] = str(exc)
        raise
    finally:
        if not args.smoke and work.exists():
            for source in (work/'results/phase2', work/'results/reproduction', work/'docs'):
                if source.exists():
                    shutil.copytree(source, artifacts/source.name, dirs_exist_ok=True)
        (artifacts/'execution.json').write_text(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
