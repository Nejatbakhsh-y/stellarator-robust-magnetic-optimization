# Phase 2 limitations

Scientific status: **PARTIAL**. Study SHA256: `395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258`.

Continuum peak convergence remains UNRESOLVED: local extrema and shifted-grid samples are observed lower bounds. No interval arithmetic or global certificate is implemented. The smooth-field reference is checked at candidate locations only; it is not independently globally optimized. Polygon error and manufacturing-scenario sampling uncertainty are separate. Holdout differences are conditional on the 512-segment numerical model; their bootstrap intervals exclude discretization error. Small paired differences need their own paired segment/grid-refinement study before interpreting their sign as a smooth-field result. The Phase 1 residual error gate is not a bound on each paired difference.

Only two training seeds, two training counts and 64 IID holdout draws were executed. Magnitude, ridge, support, common-mode/correlated and shifted-envelope sensitivities remain unfinished. Current-budget matching is unavailable. No tuning was done; a separate validation cohort must be introduced before any later tuning. The larger research preset was not executed. The full-dimensional numerical dual audit and independent scalar convex reference are additional checks; neither is an interval-arithmetic proof of optimality. External SIMSOPT comparison was not executed.

This is independent synthetic reduced-order vacuum-filament research, with no Thea Energy affiliation or proprietary geometry. No confinement, equilibrium, energy-output, force, thermal, mechanical or reactor performance claim is supported. Phase 1's negative robustness finding is preserved. New results are reported across every predeclared trial without selecting favorable seeds.
