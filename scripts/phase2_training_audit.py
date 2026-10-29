"""Replay training draws and bound the convex primal using a simplex dual."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from stellarator_robust.model import benchmark
from stellarator_robust.uncertainty import scenarios
from stellarator_robust.optimize import baseline

out = Path('results/phase2'); source = out/'study.json'
d = json.loads(source.read_text())
c = json.loads(Path('results/quick/results.json').read_text())['metadata']['config']
p, n, w, coils, _, b = benchmark(c['nt'], c['np'], d['config']['segments'], c['nphi'], c['ntheta'])
rows = []
for trial in d['trials']:
    count, seed = trial['count'], trial['train_seed']
    A, off, records = scenarios(p, n, coils, count, seed)
    assert records == d['scenarios']['training'][f'{seed}/{count}']
    As, bs = A*c['imax_A']/c['bref_T'], (b+off)/c['bref_T']
    ridge, support = trial['ridge'], trial['support']
    def losses(x):
        residual = np.einsum('smj,j->sm', As, x)+bs
        return np.sum(w*residual*residual, axis=1)
    nominal = np.array(trial['nominal_current_A'])/c['imax_A']
    robust = np.array(trial['robust_current_A'])/c['imax_A']
    primal = float(max(losses(robust))+ridge*(robust@robust))
    nominal_objective = float(max(losses(nominal))+ridge*(nominal@nominal))
    # For any probability vector lambda, min_x sum lambda_s L_s(x)+ridge||x||²
    # lower-bounds min_x max_s L_s(x)+ridge||x||². Each inner solve is bounded LS.
    def dual(lam, with_gradient=False):
        weights = (lam[:, None]*w).ravel()
        x, _ = baseline(As.reshape(-1, As.shape[-1]), bs.ravel(), weights, ridge, support)
        ls = losses(x)
        value = float(lam@ls+ridge*(x@x))
        return (-value/1e-3, -ls/1e-3) if with_gradient else value
    fit = minimize(lambda v: dual(v, True), np.ones(count)/count, jac=True,
                   method='SLSQP', bounds=[(0, 1)]*count,
                   constraints={'type': 'eq', 'fun': lambda v: v.sum()-1,
                                'jac': lambda v: np.ones(count)},
                   options={'ftol': 1e-12, 'maxiter': 500})
    lam = np.maximum(fit.x, 0); lam /= lam.sum()
    lower = dual(lam); gap = primal-lower
    row = {'seed': seed, 'count': count, 'nominal_training_objective': nominal_objective,
           'robust_training_objective': primal, 'dual_lower_estimate': lower,
           'primal_dual_gap': gap, 'dual_weights': lam.tolist(),
           'dual_solver_success': bool(fit.success), 'dual_message': str(fit.message),
           'primal_saved_objective_difference': abs(primal-trial['objective']),
           'epigraph_residual': float(max(losses(robust))-trial['solver']['epigraph'])}
    rows.append(row); print(json.dumps(row), flush=True)
checks = {'scenario_records_identical': True,
          'saved_objectives_match_1e-12': all(r['primal_saved_objective_difference'] < 1e-12 for r in rows),
          'robust_training_no_worse_1e-8': all(r['robust_training_objective'] <= r['nominal_training_objective']+1e-8 for r in rows),
          'numerical_dual_gap_1e-8': all(-1e-10 <= r['primal_dual_gap'] < 1e-8 for r in rows),
          'epigraph_residual_1e-8': all(r['epigraph_residual'] < 1e-8 for r in rows)}
result = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks, 'trials': rows,
          'study_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'interpretation': 'Numerical convex-dual check with bounded least-squares inner solves; no interval-arithmetic certificate or external cross-code validation'}
(out/'training_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
