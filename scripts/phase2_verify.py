"""Run real regression commands and full repeated experiments; preserve Phase 1 files."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from stellarator_robust.evidence import file_hash

out = Path('results/phase2')
out.mkdir(parents=True, exist_ok=True)
records = []


def execute(args):
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    records.append({'command': [sys.executable, *args], 'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    (out/'commands.json').write_text(json.dumps(records, indent=2))
    print('completed', args, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(result.stderr+result.stdout)


def compare(a, b, trail=''):
    if isinstance(a, dict):
        assert a.keys() == b.keys(), trail
        for key in a:
            if key not in ['seconds', 'elapsed_seconds', 'source_dirty']:
                compare(a[key], b[key], trail+'/'+key)
    elif isinstance(a, list):
        assert len(a) == len(b), trail
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, trail+f'/{i}')
    elif isinstance(a, (int, float)) and not isinstance(a, bool):
        np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13, err_msg=trail)
    else:
        assert a == b, trail


execute(['-m', 'pytest', '-q'])
execute(['-m', 'stellarator_robust.cli', 'validate'])
reg = out/'regression'
execute(['-m', 'stellarator_robust.cli', 'run', '--config', 'configs/quick.json', '--output', str(reg)])
execute(['scripts/check_outputs.py', str(reg)])
execute(['scripts/audit_quick.py', str(reg)])
repeat = Path('results/reproduction/phase2-regression')
execute(['-m', 'stellarator_robust.cli', 'run', '--config', 'configs/quick.json', '--output', str(repeat)])
first = json.loads((reg/'results.json').read_text())
second = json.loads((repeat/'results.json').read_text())
for key in first:
    if key != 'metadata':
        compare(first[key], second[key], key)
historical = json.loads(Path('results/quick/results.json').read_text())
for key in ['summary', 'currents_A', 'holdout_rms_T', 'pareto', 'faults', 'scenarios', 'solver_status', 'convergence']:
    compare(historical[key], first[key], 'historical/'+key)
execute(['scripts/phase2_study.py', '--output', 'results/reproduction/phase2-study'])
study = out/'study.json'
compare(json.loads(study.read_text()), json.loads(Path('results/reproduction/phase2-study/study.json').read_text()))
(out/'reproducibility.json').write_text(json.dumps({
    'status': 'PASS', 'rtol': 1e-11, 'atol': 1e-13,
    'phase1_historical_match': True, 'full_phase1_repeat': True, 'full_phase2_repeat': True,
    'study_sha256': hashlib.sha256(study.read_bytes()).hexdigest(),
    'regression_sha256': hashlib.sha256((reg/'results.json').read_bytes()).hexdigest()}, indent=2))
# Bind all executed evidence and source files; gate/report files are deliberately excluded.
paths = list(Path('src').rglob('*.py'))+list(Path('tests').rglob('*.py'))
paths += list(Path('scripts').glob('*.py'))+list(Path('configs').glob('*.json'))
paths += [p for p in out.rglob('*') if p.is_file() and p.name not in ['manifest.json', 'gate.json']]
paths += [Path('.gitattributes')]
manifest = {p.as_posix(): file_hash(p) for p in sorted(paths)}
(out/'manifest.json').write_text(json.dumps(manifest, indent=2))
print('Full repeat and historical comparisons PASS', flush=True)
