# Final Research Portfolio Summary

## Project title

**Robust Optimization and Independent Validation of Planar-Coil Magnetic-Field Models**

Repository: [Nejatbakhsh-y/stellarator-robust-magnetic-optimization](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization).

Independent computational research demonstration. No employment, collaboration, endorsement or scientific validation by Thea Energy is implied. The synthetic geometry does not reproduce proprietary Eos or Helios designs.

## Concise project description

Developed a synthetic planar-coil magnetic-field correction benchmark combining Biot–Savart modeling, bounded and sparse current optimization, finite-scenario minimax training, paired uncertainty evaluation and static coil-failure recovery. Preserved negative robustness findings and unresolved numerical validation failures. Demonstration complete with documented limitations; not accepted for production use.

## Professional research summary

This independent applied-mathematics project investigates normal-field correction on a prescribed synthetic toroidal boundary using 24 planar shaping coils and a separate disturbance coil. The original quick benchmark uses 512 polygon segments, a 240-point training grid, a shifted 960-point evaluation grid and ±3000 A command bounds. A magnetic response matrix converts fixed-geometry fitting into constrained linear algebra.

The methodology combines bounded ridge least squares, box-constrained L1/FISTA support selection and refitting, iterative coil deletion, finite-scenario minimax optimization and paired holdout comparisons. Uncertainty includes rigid coil translations and rotations plus current gain and offset errors. Static recovery refits surviving currents after each nominally active dense coil fails.

Mathematical work includes nondimensionalizing the response and objective, expressing minimax fitting as a convex epigraph, evaluating area-weighted surface residuals, and analyzing an algebraically factored recovery ratio and its perturbation sensitivity. These are applied formulations and numerical analyses; no claim of novel general optimization theory is made.

The implementation uses Scientific Python: Python 3.11, NumPy, SciPy, Matplotlib and pytest, with JSON configurations, saved scenario draws, result-file hashes and manifests. Numerical validation methods include analytical center/axis loop formulas, independent midpoint and smooth-circle integration, segment/grid refinement, derivative and support checks, repeated runs, numerical dual checks in later studies, and high-precision recorded-input recovery probes.

Historical dense fine-grid RMS was 25.91442556 microtesla compared with 30.95589774 microtesla for zero shaping current. A four-active-coil sparse example reached 26.14463797 microtesla. The robust fit worsened matched-nominal mean RMS by 0.006260212 microtesla on 24 paired holdouts. Four later 64-scenario comparisons also worsened every paired holdout RMS; sampled minimax training success did not establish generalized robustness.

The project concludes as a research demonstration, with full independent scientific validation incomplete, recovery-ratio comparison failures preserved, numerical root cause inconclusive and production acceptance failed. Original coil 3 recovery was negative and coil 15 exceeded one; neither was clipped. Local historical checks do not supersede later adverse comparisons. No confinement, equilibrium, global continuum-peak or hardware-readiness claim is supported.

## LinkedIn-ready project description

**Independent Research Project — Planar-Coil Magnetic-Field Modeling and Optimization**

Built a Scientific Python research demonstration applying numerical analysis, linear algebra and constrained optimization to a synthetic 24-coil magnetic-field correction problem. Implemented bounded ridge fitting, sparse support selection, finite-scenario minimax optimization, uncertainty quantification and static single-coil recovery, with analytical and independent integration checks and reproducibility records.

Reported the evidence transparently: nominal field correction and sparse tradeoffs were demonstrated, while robust holdout performance worsened and sensitive recovery-ratio comparisons remained unresolved. Completed the demonstration with documented limitations; full scientific acceptance is not established and production acceptance failed. Independent work with no Thea Energy affiliation, endorsement or device-validation claim.

## Technical skills summary

| Area | Demonstrated work |
|---|---|
| Applied mathematics | Surface geometry, normal-field objectives, nondimensionalization, perturbation analysis |
| Numerical analysis | Polygon approximation, quadrature, observed convergence, cancellation and conditioning |
| Linear algebra | Magnetic response matrices, rank/conditioning diagnostics, augmented ridge least squares |
| Constrained optimization | Box bounds, support restrictions, sparse proximal methods and bounded refitting |
| Robust optimization | Finite-scenario convex minimax epigraph, matched-support comparisons, numerical training audits |
| Uncertainty quantification | Synthetic rigid/actuation errors, disjoint seeds, paired holdouts, conditional bootstrap interpretation |
| Independent model validation | Analytical references, separate integration paths, high-precision probes and explicit incomplete gates |
| Scientific Python | NumPy, SciPy, Matplotlib, pytest and configuration-driven experiments |
| Reproducible computational research | Saved raw arrays/scenarios, SHA256 records, versioned contracts and preserved failures |

## Evidence, limitations and final status

All quoted measurements are historical, not freshly rerun for portfolio preparation. The existing environment launcher failed before Python startup; no numerical dependencies were installed or modified. Byte hashes were checked during documentation preparation, which is distinct from executing numerical validation.

Sources: [final report](FINAL_RESEARCH_DEMONSTRATION_REPORT.md), [original results](RESEARCH_REPORT.md), [historical validation](VALIDATION_REPORT.md), [Phase 2 results](PHASE2_RESULTS.md), [Phase 2C results](PHASE2C_RESULTS.md), [final adverse disposition](PHASE2D_FINAL_ROOT_CAUSE_AND_ACCEPTANCE.md), [machine-readable verdict](phase2d-final-evidence/scientific-verdict.json).

**Scientific comparison: FAIL. Full independent scientific validation: INCOMPLETE. Numerical root cause: INCONCLUSIVE. Full scientific acceptance: NOT ESTABLISHED. Production acceptance: FAIL. Historical evidence: PRESERVED. PR #7: OPEN AND UNMERGED under the established record. Research demonstration: COMPLETE WITH DOCUMENTED LIMITATIONS.**
