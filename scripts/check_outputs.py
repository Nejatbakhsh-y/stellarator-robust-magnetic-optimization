"""Fail CI on absent outputs, unconverged solvers, or inconsistent fault enforcement."""
import json
import sys
from pathlib import Path
import numpy as np

root = Path(sys.argv[1])
data = json.loads((root/'results.json').read_text())
for name in ['geometry', 'normal_field', 'convergence', 'pareto', 'currents', 'holdout', 'outages', 'current_tradeoff']:
    assert (root/f'{name}.png').stat().st_size > 1000
assert all(s['success'] for s in data['solver_status'].values())
assert all(f['recovered_current_A']==0 for f in data['faults'])
assert data['summary']['zero']['nominal']['rms_T']>0
assert all(r['command_bound_violation_A']<1e-8 for r in data['summary'].values())
assert all(np.all(np.isfinite(x)) for x in data['holdout_rms_T'].values())
print('Output checks passed')
