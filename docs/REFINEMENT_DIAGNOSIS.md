# Segment-refinement failure investigation

The original independent audit **failed**, and no research commit was created before this investigation. The assertion required the relative dense-residual RMS change from 128 to 256 segments below 1e-4; that requirement was not met. The audit raised before writing evidence; it now records measurements and gate outcomes before raising on failure.

## Original fixed-current diagnostic

The original 64-segment dense currents were held fixed while all shaping and disturbance circles were rebuilt at each resolution. Inputs and full precision measurements are in `results/quick/refinement_diagnosis.json`.

| Segments | RMS [T] | Relative change from preceding level |
|---:|---:|---:|
| 32 | 2.562464384642033e-5 | — |
| 64 | 2.5726183940324714e-5 | 3.962595324756846e-3 |
| 128 | 2.5751579058501403e-5 | 9.871311748215206e-4 |
| 256 | 2.57579284637258e-5 | 2.465637237225593e-4 |
| 512 | 2.575951585405498e-5 | 6.162725125258284e-5 |
| 1024 | 2.575991270407495e-5 | 1.5405958024183874e-5 |

Differences decrease approximately fourfold per doubling, as expected for polygon approximation to a circle. The original comparison stopped too early. The failure is attributable to insufficient geometry refinement for the stated tolerance, rather than evidence that the tolerance should be relaxed. No segment-integral implementation defect has been detected by the analytical, independent polygon integration, rotation and smooth-circle tests.

## Correction and stronger gates

The quick configuration now uses **512 segments**, and the unexecuted larger preset uses 1024. The solver formula and original 1e-4 relative refinement tolerance are unchanged. The audit measures six levels (32–1024), additionally requiring:

- configured-resolution RMS change from the preceding level below 1e-4;
- full weighted residual-array error against an independent smooth-circle integral below 1e-4 relative to reference RMS;
- last three observed convergence orders between 1.95 and 2.05;
- final refinement RMS change below the original 1e-4 limit;
- accurate adaptive quadrature, center/axis and polygon midpoint checks, fine-grid RMS agreement and successful solver statuses.

The smooth reference integrates circular position and tangent with adaptive quadrature, without using the segment formula. It is checked against analytical axial fields and then used off axis. Production-resolution results are regenerated and audited. The old diagnostic and new optimized-current refinement tables have different fixed-current inputs and must not be conflated.

Final gate outcomes, errors and orders are in `results/quick/audit.json` and generated `VALIDATION_REPORT.md`. Report rendering requires passing audit, tests and full reproducibility records linked to the exact result-file hash.

## Remaining limits

Sampled RMS and polygon refinement do not establish continuum peak-field convergence, equilibrium, confinement or hardware robustness. Adaptive quadrature estimates are not formal interval bounds. Holdout tails use a small synthetic sample. Robust minimax optimization is not assumed to improve nominal or holdout error.
