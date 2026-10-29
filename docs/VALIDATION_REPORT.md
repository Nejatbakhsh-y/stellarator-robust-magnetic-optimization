# Validation report

Evidence tier: VERIFIED for the executed reduced-order checks; continuum/device validation remains PARTIAL/PLANNED.

Automated suite output (recorded from execution):

```text
...........                                                              [100%]
11 passed in 1.89s
```

An initial premature run failed collection (package not installed yet); it was rerun after installation. The original numerical audit also failed its 128-to-256 segment refinement gate. That failure was investigated, not suppressed: see REFINEMENT_DIAGNOSIS.md. The unchanged relative 1e-4 gate is now applied to the configured 512-segment resolution and the final refinement. An independent smooth-circle reference and observed-order gates were added.

| Check | Evidence |
|---|---|
| Center/axis analytical field and sign | test_analytic_convergence; test_linearity_orientation_rotation_and_singularity |
| Surface area, normals and weights; planarity; nonzero disturbance | test_surface_and_planarity |
| Independent direct-vector midpoint vs matrix | test_independent_vector_response and audit below |
| Zero current, current reversal, rotational covariance and wire rejection | test_linearity_orientation_rotation_and_singularity |
| Bounded ridge vs independent normal equations; support/failure exclusion | test_baseline_bounds_ridge_and_failed_support |
| Sparse KKT, refit support and every deletion step | test_sparse_kkt_refit_and_delete |
| Finite-difference objective gradient; minimax feasibility | test_objective_finite_difference_and_robust |
| Fixed-seed scenarios, independent seeds and rigid planarity | test_scenarios_reproducibility_and_rigid_geometry |
| Failed actual current including additive offset | test_outage_removes_gain_and_offset |
| Independent adaptive circle reference; off-axis second-order convergence | test_independent_smooth_circle_reference; test_off_axis_polygon_convergence_to_smooth_reference |

Analytical circle convergence (relative error; polygon approximation, exact segment integration):

| Segments | Maximum center/axis relative error |
|---:|---:|
| 16 | 0.0130523683387 |
| 32 | 0.00322519656642 |
| 64 | 0.000803965355987 |
| 128 | 0.000200846011002 |
| 256 | 5.02024280522e-05 |

Error decreases by approximately four on doubling segments, consistent with second-order polygon geometry. The 256-segment threshold is 6e-5, based on second-order circle approximation rather than floating-point equality.

Independent 100-subdivision midpoint-integral comparison maximum absolute normal-field discrepancy: 1.87806855571e-15 T (threshold 1e-10 T).

Fixed dense currents, shifted grids (different grids from training):

| theta x phi | RMS [microT] | Maximum [microT] |
|---|---:|---:|
| 10 x 24 | 26.1098740284 | 226.7285170313 |
| 20 x 48 | 25.9144255563 | 287.9772607004 |
| 40 x 96 | 25.9151229513 | 298.3499580701 |

Fixed dense currents, training grid, varied segment geometry (background refined too), compared to an independent adaptive smooth-circle integral:

| Segments | RMS [microT] | Relative residual error | Observed order | Relative RMS change |
|---:|---:|---:|---:|---:|
| 32 | 25.6246448203 | 0.0052916921211 | — | — |
| 64 | 25.7261835950 | 0.00132340510774 | 1.99947437 | 0.00396254369273 |
| 128 | 25.7515783810 | 0.000330881212786 | 1.99986947 | 0.000987118278881 |
| 256 | 25.7579277031 | 8.27221711583e-05 | 1.99996742 | 0.000246560500488 |
| 512 | 25.7595150726 | 2.0680659495e-05 | 1.99999186 | 6.16264454907e-05 |
| 1024 | 25.7599119174 | 5.17017217185e-06 | 1.99999796 | 1.54057565864e-05 |

Adaptive circle-integral absolute error estimate (sum of vector norm estimates): 2.30847773356e-16 T. Finest grid relative RMS change: 2.69114579645e-05.

Audit gates:

```json
{
  "independent_midpoint_agreement_1e-10_T": true,
  "smooth_reference_error_estimate_relative_1e-8": true,
  "analytic_256_segments_relative_6e-5": true,
  "last_refinement_relative_rms_change_1e-4": true,
  "configured_refinement_relative_rms_change_1e-4": true,
  "configured_residual_vs_smooth_reference_relative_1e-4": true,
  "last_three_orders_between_1p95_and_2p05": true,
  "fine_grid_relative_rms_change_1e-4": true,
  "all_solvers_successful": true
}
```

Two full quick executions reproduce numerical results at rtol=1e-11, atol=1e-13; maximum current difference 0 A and maximum holdout RMS difference 0 T; scenario records identical. Faults, summaries, Pareto data, analytical convergence and solver statuses also compared. Runtime/commit metadata excluded. Results SHA256: `83162de245bfa5f64fad773f0c8212ccb04d2ae8af8287c03589fd8ee8374889`.

Recorded solver statuses:

```json
{
  "dense": {
    "success": true,
    "seconds": 0.0009622999932616949
  },
  "unregularized": {
    "success": true,
    "seconds": 0.0005150999641045928
  },
  "l1_1e-06": {
    "iterations": 55,
    "gradient_map_step": 9.13945288720519e-09,
    "success": true
  },
  "l1_1e-05": {
    "iterations": 53,
    "gradient_map_step": 8.57922077129869e-09,
    "success": true
  },
  "l1_0.0001": {
    "iterations": 39,
    "gradient_map_step": 5.503553446306597e-10,
    "success": true
  },
  "l1_0.001": {
    "iterations": 1,
    "gradient_map_step": 0.0,
    "success": true
  },
  "l1_0.01": {
    "iterations": 1,
    "gradient_map_step": 0.0,
    "success": true
  },
  "robust": {
    "success": true,
    "message": "Optimization terminated successfully",
    "violation": 8.385219602002891e-16,
    "iterations": 32,
    "epigraph": 0.0006663976957018363,
    "seconds": 0.005400699912570417
  }
}
```

All returned solver statuses succeeded and command bounds were enforced. Output generation checks validate required images and finite holdout arrays. Remote GitHub Actions has not been observed and is not claimed to pass. Research-scale continuum convergence, external solver agreement, and manufacturing-distribution validation remain PLANNED.
