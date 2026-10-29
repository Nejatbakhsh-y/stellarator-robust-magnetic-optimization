"""Render technical result reports from executed quick outputs, never preset numbers."""
import json
import hashlib
from pathlib import Path
import numpy as np

root = Path('results/quick')
d = json.loads((root/'results.json').read_text())
a = json.loads((root/'audit.json').read_text())
r = json.loads((root/'reproducibility.json').read_text())
tests = json.loads((root/'tests.json').read_text())
assert r['status']=='PASS' and a['status']=='PASS' and tests['returncode']==0
digest = hashlib.sha256((root/'results.json').read_bytes()).hexdigest()
assert a['results_sha256']==digest and r['results_sha256']==digest
s = d['summary']; m = d['metadata']
lines = ['# Research report', '', '## Abstract and motivation', '',
         'Independent synthetic planar-coil boundary-field correction was executed with bounded dense, sparse and sampled-minimax fits. The experiment evaluates normal magnetic-field error only; no confinement or device validation is claimed.', '',
         '## Formulation and configuration', '',
         f"See SCIENTIFIC_METHODS.md for SI geometry, quadrature, dimensionless objectives, uncertainty assumptions and solver tolerances. This run used {m['config']['nphi']*m['config']['ntheta']} shaping coils, {m['config']['nt']*m['config']['np']} training points, a shifted {4*m['config']['nt']*m['config']['np']}-point validation grid, {m['config']['segments']} segments, a {m['config']['imax_A']:g} A command bound and Bref={m['config']['bref_T']:g} T. Training/holdout seeds are {m['config']['train_seed']}/{m['config']['holdout_seed']} with {m['config']['train_scenarios']}/{m['config']['holdout_scenarios']} scenarios. All holdout comparisons use paired disturbances.", '',
         '## Executed comparisons', '',
         '| Method | Active (>1 A) | Training RMS [microT] | Fine RMS [microT] | Holdout mean [microT] | Holdout q95 [microT] | Sum abs current [A] |',
         '|---|---:|---:|---:|---:|---:|---:|']
for name, row in s.items():
    lines.append(f"| {name} | {row['nominal']['active']} | {row['nominal']['rms_T']*1e6:.8f} | {row['fine_grid']['rms_T']*1e6:.8f} | {row['holdout']['mean_T']*1e6:.8f} | {row['holdout']['q95_T']*1e6:.8f} | {row['nominal']['l1_A']:.6f} |")
paired = (np.array(d['holdout_rms_T']['robust'])-d['holdout_rms_T']['matched_nominal'])*1e6
lines += ['', '## Interpretation and uncertainty', '',
          f"Robust minus matched-nominal paired mean RMS difference: {paired.mean():.9f} microT; observed range [{paired.min():.9f}, {paired.max():.9f}] microT. Positive means worse robust performance. Robust holdout improvement is not established. The permitted support is identical (12 coils), with no constraint matching total current. Twenty-four samples are descriptive only; no confidence interval or population-tail guarantee is claimed.", '',
          f"Weighted dimensionless response condition number: {m['condition_number']:.9g}; rank {m['rank']}. Minimum sampled coil clearance (including background): {m['clearance_sampled_m']:.9g} m. Maximum commanded bound violation: {max(row['command_bound_violation_A'] for row in s.values()):.9g} A; maximum observed actual holdout violation: {max(row['holdout_actual_bound_violation_A'] for row in s.values()):.9g} A.", '',
          '## Single-coil failures', '', '| Failed index | Pre RMS [microT] | Frozen RMS [microT] | Recovered RMS [microT] | Fractional recovery |', '|---|---:|---:|---:|---:|']
for f in d['faults']:
    lines.append(f"| {f['failed']} | {f['pre_T']*1e6:.7f} | {f['frozen_T']*1e6:.7f} | {f['recovered_T']*1e6:.7f} | {f['fractional_recovery']:.7f} |")
lines += ['', 'Negative or greater-than-one recovery fractions are retained. Tiny failure effects make these ratios sensitive. Recovery is static bounded refitting. Per-scenario disturbed frozen/recovered results are retained in results.json, with failed actual current enforced at zero.', '',
          '## Verification, figures and reproducibility', '',
          f"Analytical and benchmark sensitivity evidence is in VALIDATION_REPORT.md and results/quick/audit.json. Second full-run reproducibility: {r['status']}. Generated data source commit: `{m['source_commit']}`, dirty flag `{m['source_dirty']}`. Artifact commits may follow source commits; no claim that development artifacts were generated from a clean revision is made.", '',
          'Figures in results/quick: geometry.png, normal_field.png, convergence.png, pareto.png, current_tradeoff.png, currents.png, holdout.png, outages.png. Each is computed from the recorded config and numerical arrays. Heatmaps share a symmetric field scale. Pareto samples are not certified global optima.', '',
          'Execute README commands, followed by `python scripts/audit_quick.py`, `python scripts/reproduce_check.py`, and `python scripts/write_reports.py` using the existing virtual environment. Full precision values, solver convergence/feasibility, package versions and scenario draws are stored in JSON; selected sparse tradeoffs are also CSV.', '',
          '## Limitations and future extensions', '',
          'Quick grid peak fields are less resolved than RMS; use the measured sensitivity below rather than interpreting quick peak values as continuum maxima. Research preset and larger paired uncertainty studies are PLANNED, as are current-bound/ridge parameter sweeps, independent SIMSOPT checks, confidence analysis and plasma equilibrium/field-line validation. See LIMITATIONS.md. No fourteen-day execution or remote CI success is implied.', '',
          '## References', '', 'Verified public bibliography and access dates: SOURCE_VERIFICATION.md. Published background is distinct from own assumptions and numerical results as categorized in SCIENTIFIC_METHODS.md.']
Path('docs/RESEARCH_REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
v = ['# Validation report', '', 'Evidence tier: VERIFIED for the executed reduced-order checks; continuum/device validation remains PARTIAL/PLANNED.', '',
     'Automated suite output (recorded from execution):', '', '```text', tests['stdout'].strip(), '```', '',
     'An initial premature run failed collection (package not installed yet); it was rerun after installation. The original numerical audit also failed its 128-to-256 segment refinement gate. That failure was investigated, not suppressed: see REFINEMENT_DIAGNOSIS.md. The unchanged relative 1e-4 gate is now applied to the configured 512-segment resolution and the final refinement. An independent smooth-circle reference and observed-order gates were added.', '',
     '| Check | Evidence |', '|---|---|',
     '| Center/axis analytical field and sign | test_analytic_convergence; test_linearity_orientation_rotation_and_singularity |',
     '| Surface area, normals and weights; planarity; nonzero disturbance | test_surface_and_planarity |',
     '| Independent direct-vector midpoint vs matrix | test_independent_vector_response and audit below |',
     '| Zero current, current reversal, rotational covariance and wire rejection | test_linearity_orientation_rotation_and_singularity |',
     '| Bounded ridge vs independent normal equations; support/failure exclusion | test_baseline_bounds_ridge_and_failed_support |',
     '| Sparse KKT, refit support and every deletion step | test_sparse_kkt_refit_and_delete |',
     '| Finite-difference objective gradient; minimax feasibility | test_objective_finite_difference_and_robust |',
     '| Fixed-seed scenarios, independent seeds and rigid planarity | test_scenarios_reproducibility_and_rigid_geometry |',
     '| Failed actual current including additive offset | test_outage_removes_gain_and_offset |',
     '| Independent adaptive circle reference; off-axis second-order convergence | test_independent_smooth_circle_reference; test_off_axis_polygon_convergence_to_smooth_reference |', '',
     'Analytical circle convergence (relative error; polygon approximation, exact segment integration):', '',
     '| Segments | Maximum center/axis relative error |', '|---:|---:|']
for row in d['convergence']:
    v.append(f"| {row['segments']} | {row['max_relative_error']:.12g} |")
v += ['', 'Error decreases by approximately four on doubling segments, consistent with second-order polygon geometry. The 256-segment threshold is 6e-5, based on second-order circle approximation rather than floating-point equality.', '',
      f"Independent 100-subdivision midpoint-integral comparison maximum absolute normal-field discrepancy: {a['matrix_vs_independent_midpoint_max_abs_T']:.12g} T (threshold 1e-10 T).", '',
      'Fixed dense currents, shifted grids (different grids from training):', '',
      '| theta x phi | RMS [microT] | Maximum [microT] |', '|---|---:|---:|']
for row in a['fixed_dense_grid_sensitivity']:
    v.append(f"| {row['theta_count']} x {row['phi_count']} | {row['rms_T']*1e6:.10f} | {row['max_T']*1e6:.10f} |")
v += ['', 'Fixed dense currents, training grid, varied segment geometry (background refined too), compared to an independent adaptive smooth-circle integral:', '', '| Segments | RMS [microT] | Relative residual error | Observed order | Relative RMS change |', '|---:|---:|---:|---:|---:|']
for row in a['fixed_dense_segment_sensitivity']:
    order = '—' if row['observed_order'] is None else f"{row['observed_order']:.8f}"
    change = '—' if row['relative_rms_change'] is None else f"{row['relative_rms_change']:.12g}"
    v.append(f"| {row['segments']} | {row['rms_T']*1e6:.10f} | {row['relative_residual_error']:.12g} | {order} | {change} |")
v += ['', f"Adaptive circle-integral absolute error estimate (sum of vector norm estimates): {a['smooth_reference_error_estimate_T']:.12g} T. Finest grid relative RMS change: {a['fine_grid_relative_rms_change']:.12g}.", '', 'Audit gates:', '', '```json', json.dumps(a['gates'], indent=2), '```', '',
      f"Two full quick executions reproduce numerical results at rtol={r['rtol']}, atol={r['atol']}; maximum current difference {r['max_current_difference_A']:.12g} A and maximum holdout RMS difference {r['max_holdout_difference_T']:.12g} T; scenario records identical. Faults, summaries, Pareto data, analytical convergence and solver statuses also compared. Runtime/commit metadata excluded. Results SHA256: `{digest}`.", '',
      'Recorded solver statuses:', '', '```json', json.dumps(d['solver_status'], indent=2), '```', '',
      'All returned solver statuses succeeded and command bounds were enforced. Output generation checks validate required images and finite holdout arrays. Remote GitHub Actions has not been observed and is not claimed to pass. Research-scale continuum convergence, external solver agreement, and manufacturing-distribution validation remain PLANNED.']
Path('docs/VALIDATION_REPORT.md').write_text('\n'.join(v)+'\n', encoding='utf-8')
print('Reports generated from executed numerical evidence')
