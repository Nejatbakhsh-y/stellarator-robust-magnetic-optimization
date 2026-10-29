"""Preserve refinement evidence before applying any acceptance criteria."""
import json
from pathlib import Path
import numpy as np
from stellarator_robust.model import benchmark, response

data = json.loads(Path('results/quick/results.json').read_text())
c = data['metadata']['config']; I = np.array(data['currents_A']['dense'])
rows = []; previous = None
for count in [32, 64, 128, 256, 512, 1024]:
    p, n, w, coils, _, b = benchmark(c['nt'], c['np'], count, c['nphi'], c['ntheta'])
    r = b+response(p, n, coils)@I
    rms = float(np.sqrt(w@(r*r)))
    row = {'segments': count, 'rms_T': rms,
           'relative_rms_change': None if previous is None else abs(rms/previous-1)}
    rows.append(row); print(json.dumps(row), flush=True); previous = rms
Path('results/quick/refinement_diagnosis.json').write_text(json.dumps(
    {'input_config': c, 'fixed_currents_A': I.tolist(), 'rows': rows}, indent=2))
