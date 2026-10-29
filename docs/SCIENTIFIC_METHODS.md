# Scientific methods

## A. Published background

The normal-field residual and sparse shaping-current viewpoint are motivated by Wu, Kruger and Swanson (2025). Public sources are verified in SOURCE_VERIFICATION.md. No published device geometry or performance gain is reproduced here. The boundary residual is a proxy, not a confinement demonstration.

## B. Own assumptions

All lengths are metres, currents amperes, fields tesla. The conventional mu0 approximation is 4*pi*1e-7 H/m (not an exact modern SI constant). The circular torus has R=1 and a=.25. Its coordinates are ((R+a cos theta) cos phi, (R+a cos theta) sin phi, a sin theta); outward unit normal is (cos theta cos phi, cos theta sin phi, sin theta). Periodic rectangle weights use a(R+a cos theta) dtheta dphi, normalized to one for objectives. Total physical area is 4*pi^2*R*a.

Coils have radius .16 m, centers on a winding torus with minor radius .65 m and tangent planes defined by its outward normals. The quick array has 8 toroidal by 3 poloidal locations. Coil index orders poloidal angle then toroidal angle. Positive currents follow the right-hand normal. A fixed 1500 A, .22 m radius disturbance coil is centered at (1.6,.25,.35) with normal proportional to (1,.2,.4). It is synthetic. No analytic toroidal guide field is needed for this normal-field correction problem. Bref=.001 T is a fixed reporting/objective scale, not the total magnetic field strength.

## C. Numerical calculations

Each circle is an inscribed closed polygon. The forward solver evaluates the exact finite straight-segment Biot–Savart expression, summing (r1 cross r2)(|r1|+|r2|)/[|r1||r2|(|r1||r2|+r1 dot r2)] times mu0*I/(4*pi). Points within 1e-4 m of any segment are rejected before evaluation. Collinear exterior points contribute zero. Batches of 128 points bound memory. Circle approximation converges quadratically away from wires; it is tested against analytic center and axis formulas. Independent composite midpoint integration over segments checks the response matrix without reusing its segment formula.

A is the unit-current normal response in T/A; b is the fixed disturbance normal field. I=Imax*x with |x|<=1; D=A*Imax/Bref, d=b/Bref. Baseline minimizes sum w*(d+D*x)^2 + ridge*||x||^2. Ridge therefore has a documented dimensionless meaning, rather than a raw SI current penalty. SciPy bounded least squares uses augmented sqrt(ridge) identity rows. All sparse refits use the same bounds and ridge.

FISTA minimizes one half of that quadratic plus penalty*||x||1. Its proximal step soft-thresholds then clips to [-1,1]. A fixed-point proximal residual <1e-8 stops iteration, with a hard 30000-iteration failure. A physical 1 A threshold selects support, followed by bounded refitting. Refit active counts may fall below support sizes. Optimize-then-delete removes the lowest absolute current on the allowed support and reoptimizes, recording every removal. These are sampled tradeoffs, not proven globally optimal Pareto fronts.

Robust optimization minimizes a finite-scenario maximum weighted squared dimensionless loss plus ridge*||x||^2. A convex epigraph is solved by SciPy SLSQP with analytic objective/constraint derivatives, ftol=1e-12 and maximum 2000 iterations. Solver failure or epigraph violation >1e-8 raises. This is minimax over sampled scenarios, not CVaR or distribution-free robustness. The allowed support is the half-array deletion-path support, shared by matched nominal and robust fits; they have identical bounds but can differ in realized active counts and total current.

Scenario translations are independent uniform components in [-.003,.003] m; rotation-vector components in [-.01,.01] rad, about each coil center. Current gains are uniform in [-.02,.02] and additive offsets in [-2,2] A. Realized currents are (1+gain)*command+offset, applied once. Background is fixed. Rigid transforms preserve planarity. An entire polygon stays outside the evaluation surface if the torus signed distance at vertices minus half the maximum edge length exceeds .05 m, using the 1-Lipschitz distance bound. Invalid scenarios abort with diagnostics rather than silently resampling.

Training and holdout seeds are distinct; fine-grid evaluation doubles both angular resolutions and shifts each angle by a half cell. Holdout geometry scenarios are evaluated directly on that independent grid. All methods share paired holdout draws. The JSON records exact scenario parameters. Uncertainty summaries are finite-sample mean, median, 90th/95th quantiles and maximum; no confidence or population guarantees are asserted. Commands obey bounds; actual current can exceed them under the stated actuation errors and must be reported separately.

Every nominally active dense coil is failed separately. Frozen setpoints set its command to zero; recovery restricts the bounded solve to surviving coils. In disturbed outage evaluation its additive offset is also removed, enforcing exactly zero actual current. Fractional RMS recovery is (fault RMS-recovered RMS)/(fault RMS-pre RMS), undefined for negligible denominators; values outside [0,1] are retained. Static recovery has no dynamic or hardware guarantee.

## D. Interpretation

Lower area-weighted boundary RMS measures only this synthetic boundary correction task. High-resolution discrepancy, conditioning, finite sample uncertainty and negative robustness results must constrain interpretation. Research-scale studies and physical equilibrium validation remain separate milestones.
