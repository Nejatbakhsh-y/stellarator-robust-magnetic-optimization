# Research report

## Abstract and motivation

Independent synthetic planar-coil boundary-field correction was executed with bounded dense, sparse and sampled-minimax fits. The experiment evaluates normal magnetic-field error only; no confinement or device validation is claimed.

## Formulation and configuration

See SCIENTIFIC_METHODS.md for SI geometry, quadrature, dimensionless objectives, uncertainty assumptions and solver tolerances. This run used 24 shaping coils, 240 training points, a shifted 960-point validation grid, 512 segments, a 3000 A command bound and Bref=0.001 T. Training/holdout seeds are 20261029/20261030 with 8/24 scenarios. All holdout comparisons use paired disturbances.

## Executed comparisons

| Method | Active (>1 A) | Training RMS [microT] | Fine RMS [microT] | Holdout mean [microT] | Holdout q95 [microT] | Sum abs current [A] |
|---|---:|---:|---:|---:|---:|---:|
| zero | 0 | 30.48271525 | 30.95589774 | 30.95556475 | 30.97388508 | 0.000000 |
| dense | 21 | 25.75951507 | 25.91442556 | 25.90215549 | 25.98194891 | 2069.970450 |
| unregularized | 21 | 25.75951457 | 25.91415816 | 25.90188738 | 25.98168705 | 2070.683218 |
| l1_1e-06 | 21 | 25.75952042 | 25.91440860 | 25.90214200 | 25.98196102 | 2067.966367 |
| l1_1e-05 | 19 | 25.75966411 | 25.91451474 | 25.90223572 | 25.98203978 | 2061.611041 |
| l1_0.0001 | 4 | 26.00128626 | 26.14463797 | 26.13191336 | 26.20933493 | 1368.523353 |
| l1_0.001 | 0 | 30.48271525 | 30.95589774 | 30.95556475 | 30.97388508 | 0.000000 |
| l1_0.01 | 0 | 30.48271525 | 30.95589774 | 30.95556475 | 30.97388508 | 0.000000 |
| matched_nominal | 12 | 25.77040435 | 25.92337147 | 25.91100497 | 25.99049756 | 1966.443954 |
| robust | 12 | 25.77134351 | 25.92944605 | 25.91726518 | 25.99735802 | 1970.744293 |

## Interpretation and uncertainty

Robust minus matched-nominal paired mean RMS difference: 0.006260212 microT; observed range [0.004224770, 0.008019145] microT. Positive means worse robust performance. Robust holdout improvement is not established. The permitted support is identical (12 coils), with no constraint matching total current. Twenty-four samples are descriptive only; no confidence interval or population-tail guarantee is claimed.

Weighted dimensionless response condition number: 1.94734884; rank 24. Minimum sampled coil clearance (including background): 0.392039827 m. Maximum commanded bound violation: 0 A; maximum observed actual holdout violation: 0 A.

## Single-coil failures

| Failed index | Pre RMS [microT] | Frozen RMS [microT] | Recovered RMS [microT] | Fractional recovery |
|---|---:|---:|---:|---:|
| 0 | 25.9144256 | 28.5706666 | 28.1681606 | 0.1515322 |
| 1 | 25.9144256 | 26.0969359 | 26.0483910 | 0.2659842 |
| 2 | 25.9144256 | 25.9235306 | 25.9222412 | 0.1416082 |
| 3 | 25.9144256 | 25.9144802 | 25.9145029 | -0.4146890 |
| 6 | 25.9144256 | 25.9149476 | 25.9148603 | 0.1672662 |
| 7 | 25.9144256 | 25.9469961 | 25.9349567 | 0.3696402 |
| 8 | 25.9144256 | 26.1606579 | 26.0350815 | 0.5099915 |
| 9 | 25.9144256 | 26.0553356 | 26.0291040 | 0.1861587 |
| 10 | 25.9144256 | 25.9158009 | 25.9148594 | 0.6845641 |
| 11 | 25.9144256 | 25.9163649 | 25.9156826 | 0.3518408 |
| 12 | 25.9144256 | 25.9157598 | 25.9153533 | 0.3046569 |
| 13 | 25.9144256 | 25.9159189 | 25.9154235 | 0.3317652 |
| 14 | 25.9144256 | 25.9164223 | 25.9155775 | 0.4231068 |
| 15 | 25.9144256 | 25.9145404 | 25.9144219 | 1.0317964 |
| 16 | 25.9144256 | 26.8896773 | 26.5467396 | 0.3516402 |
| 17 | 25.9144256 | 26.1601634 | 26.1141887 | 0.1870884 |
| 18 | 25.9144256 | 25.9181514 | 25.9163128 | 0.4934657 |
| 19 | 25.9144256 | 25.9176344 | 25.9166574 | 0.3044842 |
| 20 | 25.9144256 | 25.9171479 | 25.9164351 | 0.2618622 |
| 21 | 25.9144256 | 25.9173400 | 25.9165175 | 0.2822227 |
| 22 | 25.9144256 | 25.9172534 | 25.9161948 | 0.3743356 |

Negative or greater-than-one recovery fractions are retained. Tiny failure effects make these ratios sensitive. Recovery is static bounded refitting. Per-scenario disturbed frozen/recovered results are retained in results.json, with failed actual current enforced at zero.

## Verification, figures and reproducibility

Analytical and benchmark sensitivity evidence is in VALIDATION_REPORT.md and results/quick/audit.json. Second full-run reproducibility: PASS. Generated data source commit: `d711580800820b3b38bcd7006994c58b4665226c`, dirty flag `True`. Artifact commits may follow source commits; no claim that development artifacts were generated from a clean revision is made.

Figures in results/quick: geometry.png, normal_field.png, convergence.png, pareto.png, current_tradeoff.png, currents.png, holdout.png, outages.png. Each is computed from the recorded config and numerical arrays. Heatmaps share a symmetric field scale. Pareto samples are not certified global optima.

Execute README commands, followed by `python scripts/audit_quick.py`, `python scripts/reproduce_check.py`, and `python scripts/write_reports.py` using the existing virtual environment. Full precision values, solver convergence/feasibility, package versions and scenario draws are stored in JSON; selected sparse tradeoffs are also CSV.

## Limitations and future extensions

Quick grid peak fields are less resolved than RMS; use the measured sensitivity below rather than interpreting quick peak values as continuum maxima. Research preset and larger paired uncertainty studies are PLANNED, as are current-bound/ridge parameter sweeps, independent SIMSOPT checks, confidence analysis and plasma equilibrium/field-line validation. See LIMITATIONS.md. No fourteen-day execution or remote CI success is implied.

## References

Verified public bibliography and access dates: SOURCE_VERIFICATION.md. Published background is distinct from own assumptions and numerical results as categorized in SCIENTIFIC_METHODS.md.
