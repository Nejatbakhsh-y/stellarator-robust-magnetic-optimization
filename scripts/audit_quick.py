"""Independent audit; save errors and gate outcomes before raising on failure."""
import json
import hashlib
import sys
from pathlib import Path
import numpy as np
from stellarator_robust.model import benchmark, response, surface, field, MU0, circle
from stellarator_robust.validation import independent_midpoint, independent_circle

out = Path(sys.argv[1] if len(sys.argv)>1 else 'results/quick')
data = json.loads((out/'results.json').read_text())
c = data['metadata']['config']; I = np.array(data['currents_A']['dense'])
p, n, w, coils, error, b = benchmark(c['nt'], c['np'], c['segments'], c['nphi'], c['ntheta'], c.get('geometry_version', 'legacy-v1'))
A = response(p, n, coils)
idx = np.array([1, 17, 63, 123])
direct = sum(independent_midpoint(p[idx], coil, amp, 100) for coil, amp in zip(coils, I))
diff = (A@I)[idx]-np.sum(direct*n[idx], axis=1)
reference_vector, reference_error = independent_circle(p, error, 1500.)
for coil, amp in zip(coils, I):
    vector, estimate = independent_circle(p, coil, amp)
    reference_vector += vector
    reference_error += estimate
reference = np.sum(reference_vector*n, axis=1)
reference_rms = float(np.sqrt(w@(reference*reference)))
grid = []
for multiplier in [1, 2, 4]:
    pv, nv, av = surface(1., .25, c['nt']*multiplier, c['np']*multiplier, .5)
    r = np.sum(field(pv, error, 1500.)*nv, axis=1)+response(pv, nv, coils)@I
    grid.append({'theta_count': c['nt']*multiplier, 'phi_count': c['np']*multiplier,
                 'rms_T': float(np.sqrt((av/av.sum())@(r*r))), 'max_T': float(max(abs(r)))})
segment = []; previous_rms = None; previous_error = None
for count in [32, 64, 128, 256, 512, 1024]:
    pp, nn, ww, cc, ee, bb = benchmark(c['nt'], c['np'], count, c['nphi'], c['ntheta'], c.get('geometry_version', 'legacy-v1'))
    r = bb+response(pp, nn, cc)@I
    rms = float(np.sqrt(ww@(r*r)))
    vector_error = float(np.sqrt(ww@((r-reference)**2)))
    segment.append({'segments': count, 'rms_T': rms,
                    'relative_rms_change': None if previous_rms is None else abs(rms/previous_rms-1),
                    'weighted_residual_error_T': vector_error,
                    'relative_residual_error': vector_error/reference_rms,
                    'observed_order': None if previous_error is None else float(np.log2(previous_error/vector_error))})
    previous_rms, previous_error = rms, vector_error
axis = np.array([[0., 0., 0.], [0., 0., .3], [0., 0., 1.]])
B = field(axis, circle([0, 0, 0], [0, 0, 1], 1., 256))[:, 2]
axis_reference = MU0/(2*(1+axis[:, 2]**2)**1.5)
configured = next(row for row in segment if row['segments']==c['segments'])
grid_change = abs(grid[-1]['rms_T']/grid[-2]['rms_T']-1)
gates = {
    'independent_midpoint_agreement_1e-10_T': bool(max(abs(diff))<1e-10),
    'smooth_reference_error_estimate_relative_1e-8': bool(reference_error/reference_rms<1e-8),
    'analytic_256_segments_relative_6e-5': bool(max(abs(B/axis_reference-1))<6e-5),
    'last_refinement_relative_rms_change_1e-4': bool(segment[-1]['relative_rms_change']<1e-4),
    'configured_refinement_relative_rms_change_1e-4': bool(configured['relative_rms_change']<1e-4),
    'configured_residual_vs_smooth_reference_relative_1e-4': bool(configured['relative_residual_error']<1e-4),
    'last_three_orders_between_1p95_and_2p05': all(1.95<row['observed_order']<2.05 for row in segment[-3:]),
    'fine_grid_relative_rms_change_1e-4': bool(grid_change<1e-4),
    'all_solvers_successful': all(row['success'] for row in data['solver_status'].values()),
}
audit = {'status': 'PASS' if all(gates.values()) else 'FAIL', 'gates': gates,
         'results_sha256': hashlib.sha256((out/'results.json').read_bytes()).hexdigest(),
         'configured_segments': c['segments'], 'matrix_vs_independent_midpoint_max_abs_T': float(max(abs(diff))),
         'smooth_circle_reference_rms_T': reference_rms, 'smooth_reference_error_estimate_T': reference_error,
         'analytic_axis_z_m': axis[:, 2].tolist(), 'analytic_reference_T': axis_reference.tolist(),
         'analytic_computed_T': B.tolist(), 'axis_relative_error': (abs(B/axis_reference-1)).tolist(),
         'fine_grid_relative_rms_change': grid_change,
         'fixed_dense_grid_sensitivity': grid, 'fixed_dense_segment_sensitivity': segment}
(out/'audit.json').write_text(json.dumps(audit, indent=2, allow_nan=False))
print(json.dumps(audit, indent=2), flush=True)
if audit['status'] != 'PASS':
    raise AssertionError(f"Independent audit failed: {[key for key, value in gates.items() if not value]}")
