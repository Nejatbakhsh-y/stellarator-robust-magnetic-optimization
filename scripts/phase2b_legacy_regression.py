"""Execute README-equivalent legacy checks in separate, ignored output paths."""
import copy
import json
from pathlib import Path
import subprocess
import sys
from stellarator_robust.phase2b import preserve_legacy, load, sha
from stellarator_robust.ci_evidence import compare, clearance_paths

out = Path('results/ci/phase2b-legacy'); out.mkdir(parents=True, exist_ok=True)
records = []
def run(name, args):
    with (out/(name+'.log')).open('w') as log:
        result = subprocess.run([sys.executable, *args], stdout=log, stderr=subprocess.STDOUT)
    records.append(dict(stage=name, command=['python', *args], returncode=result.returncode))
    (out/'commands.json').write_text(json.dumps(records, indent=2)+'\n')
    print(name, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(name+' failed')

preserve_legacy()
run('tests', ['-m', 'pytest', '-q'])
run('analytical', ['-m', 'stellarator_robust.cli', 'validate'])
for label in ('first', 'repeat'):
    run(label, ['-m', 'stellarator_robust.cli', 'run', '--config', 'configs/quick.json', '--output', str(out/label)])
    run(label+'-outputs', ['scripts/check_outputs.py', str(out/label)])
run('independent-audit', ['scripts/audit_quick.py', str(out/'first')])
first = load(out/'first/results.json'); repeat = load(out/'repeat/results.json')
old = load('results/quick/results.json')
groups = ['summary', 'currents_A', 'holdout_rms_T', 'pareto', 'faults', 'convergence', 'solver_status']
for label, reference, current in [('repeat', first, repeat), ('historical', old, first)]:
    a, b = copy.deepcopy(reference), copy.deepcopy(current)
    for data in (a, b):
        for status in data['solver_status'].values():
            if 'seconds' in status:
                assert status['seconds'] >= 0
                status.pop('seconds')
    for group in groups:
        compare(a[group], b[group], label+'/'+group)
    sa = dict(holdout=a['scenarios']['holdout'], training={'quick':a['scenarios']['train']})
    sb = dict(holdout=b['scenarios']['holdout'], training={'quick':b['scenarios']['train']})
    paths = clearance_paths(sa)
    assert paths == clearance_paths(sb)
    compare(sa, sb, '/scenarios', exact=True, approximate_paths=paths)
audit = load(out/'first/audit.json')
assert audit['status'] == 'PASS' and audit['results_sha256'] == sha(out/'first/results.json')
result = dict(status='PASS', rtol=1e-11, atol=1e-13, commands=records,
              results_sha256=sha(out/'first/results.json'), legacy_evidence=preserve_legacy())
(out/'reproducibility.json').write_text(json.dumps(result, indent=2)+'\n')
print('Actual legacy quick repeat, historical comparison and independent audit PASS')
