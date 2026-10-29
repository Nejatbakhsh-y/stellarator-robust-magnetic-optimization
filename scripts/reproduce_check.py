"""Repeat the complete quick experiment; compare numerical results and statuses."""
import hashlib
import json
from pathlib import Path
import numpy as np
from stellarator_robust.experiments import run

path = Path('results/quick/results.json')
first = json.loads(path.read_text())
second = run('configs/quick.json', 'results/reproduction')
rtol, atol = 1e-11, 1e-13
def compare(left, right, trail=''):
    if isinstance(left, dict):
        assert left.keys()==right.keys(), trail
        for key in left:
            if key != 'seconds':
                compare(left[key], right[key], trail+'/'+key)
    elif isinstance(left, list):
        assert len(left)==len(right), trail
        for idx, (a, b) in enumerate(zip(left, right)):
            compare(a, b, trail+f'/{idx}')
    elif isinstance(left, (int, float)) and not isinstance(left, bool):
        np.testing.assert_allclose(left, right, rtol=rtol, atol=atol, err_msg=trail)
    else:
        assert left==right, trail

record = {'status': 'FAIL', 'rtol': rtol, 'atol': atol,
          'results_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
try:
    groups = ['summary', 'currents_A', 'holdout_rms_T', 'pareto', 'faults', 'convergence', 'scenarios', 'solver_status']
    for group in groups:
        compare(first[group], second[group], group)
    assert first['scenarios']==second['scenarios']
    record.update(status='PASS', groups_compared=groups, scenario_records_identical=True,
                  max_current_difference_A=max(float(np.max(abs(np.array(v)-second['currents_A'][k]))) for k, v in first['currents_A'].items()),
                  max_holdout_difference_T=max(float(np.max(abs(np.array(v)-second['holdout_rms_T'][k]))) for k, v in first['holdout_rms_T'].items()))
except Exception as exc:
    record['error'] = str(exc)
    raise
finally:
    Path('results/quick/reproducibility.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2), flush=True)
