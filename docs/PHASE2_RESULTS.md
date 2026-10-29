# Phase 2 results

Scientific status: **PARTIAL**. Study SHA256: `395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258`.

| Method | finest shifted sample [microT] | local estimate [microT] | smooth at candidate [microT] | 512 relative candidate error | successful searches |
|---|---:|---:|---:|---:|---:|
| dense | 298.3499580701 | 299.3326578416 | 299.3378597474 | 1.737804162e-05 | 18/18 |
| matched_nominal | 298.3206634311 | 299.3101488827 | 299.3153502217 | 1.737745484e-05 | 18/18 |
| robust | 298.2983505299 | 299.2656670560 | 299.2708674977 | 1.737703942e-05 | 18/18 |

Each smooth-circle number is evaluated at the polygon-search candidate. It is not a certified smooth-circle global extremum.

| Training seed/count | mean delta [microT] | paired bootstrap 95% [microT] | fraction improved | nominal / robust sum abs current [A] |
|---|---:|---:|---:|---:|
| 20261111/4 | 0.0082193419 | [0.0080124646, 0.0084201096] | 0.000000 | 1966.443954 / 1961.080940 |
| 20261111/8 | 0.0079980561 | [0.0077950886, 0.0081959359] | 0.000000 | 1966.443954 / 1960.701468 |
| 20261112/4 | 0.0070391762 | [0.0068644322, 0.0072019423] | 0.000000 | 1966.443954 / 1974.275003 |
| 20261112/8 | 0.0004417850 | [0.0003894518, 0.0004921714] | 0.000000 | 1966.443954 / 1970.384289 |

Preserved Phase 1 paired mean delta: 0.0062602119 microT (24 samples; positive is worse). Its original output has not been edited.

Peak-location heatmaps, peak_refinement.png and paired_difference.png are computed from this study. Unrounded data and all trials are in results/phase2/study.json. Raw observations use tesla; figures and these tables convert by 1e6.

| Method | finest half-cell sample to local change [microT] | relative change |
|---|---:|---:|
| dense | 0.9826997715 | 0.003293782167 |
| matched_nominal | 0.9894854516 | 0.003316851874 |
| robust | 0.9673165261 | 0.003242782015 |

| Seed/count | nominal / robust q95 [microT] | nominal / robust max [microT] |
|---|---:|---:|
| 20261111/4 | 26.0179235663 / 26.0251022637 | 26.0437229703 / 26.0509004689 |
| 20261111/8 | 26.0179235663 / 26.0249011768 | 26.0437229703 / 26.0506939287 |
| 20261112/4 | 26.0179235663 / 26.0239128380 | 26.0437229703 / 26.0500513957 |
| 20261112/8 | 26.0179235663 / 26.0182567478 | 26.0437229703 / 26.0443170622 |

Tail estimates have only 64 independent scenario draws; these descriptive maxima and quantiles do not establish population-tail superiority.

| Seed/count | nominal training objective | robust training objective | numerical primal-dual gap |
|---|---:|---:|---:|
| 20261111/4 | 0.00066767103106299 | 0.00066763930602381 | 1.574830294e-11 |
| 20261111/8 | 0.00066767103106299 | 0.00066763932866795 | 3.839244038e-11 |
| 20261112/4 | 0.00066608430810436 | 0.00066605538982501 | 8.631138881e-12 |
| 20261112/8 | 0.00066661295947489 | 0.00066660200591304 | 4.653439743e-12 |

Every tested minimax fit reduced its sampled training objective while worsening every paired holdout RMS. This supports objective mismatch and finite training coverage as explanations; it does not identify a unique cause or establish behavior outside the tested synthetic distribution. Training seed/count sensitivity is visible, and shared support did not match total current. No robust mean or tail superiority is established.