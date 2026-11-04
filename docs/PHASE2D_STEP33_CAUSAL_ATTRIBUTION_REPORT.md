# STEP 33 independent numerical causal attribution

Production acceptance **FAIL**; overall scientific status **PARTIAL**; numerical
root-cause attribution **INCONCLUSIVE**. STEP 33 implementation is prepared,
but software completion and scientific completion have not been demonstrated.
No production correction is proposed.

The checkout remains on `codex/phase2d-upstream-attribution` at
`11c2b1347c7b5359bec0a56e95cc2aa46f03660c`. Existing tracked modifications and
untracked research were inspected and preserved; no staging, commit, push,
dispatch, merge or history rewrite was performed. PR #7 remains draft.

Evidence is under `results/phase2d/step33-20261031-191651-e684d712/`.
Original STEP 32 evidence is
`results/phase2d/step32-host-20261031-183500-a1965e0d/`.
This report supersedes stale execution descriptions only for the particular
successful STEP 32 host record; earlier failed attempts remain unchanged.

| Experiment | Status | Evidence and interpretation |
|---|---|---|
| STEP 32 local file integrity | PASS | 194 manifest entries checked, zero SHA256 mismatches; all five manifests have complete file coverage. This authenticates local consistency, not hosted origin. |
| STEP 32 recorded source fingerprints | PASS | All 96 recorded paths match present bytes. New STEP 33 files are outside that historical inventory. |
| STEP 32 sealed-input transport | PASS | Capture and local worker both record `4faec908829e36e67415e6cf56c7326f6b64149864c5f8cc3ad39404fba05fed`; sealed file hash was independently checked. |
| STEP 32 local execution | PASS | Retained tests.log records 264 passed in 53.56 s; assessment records compilation, analytical, capture, local controls and production verifier exit 0. This is historical local execution evidence. |
| STEP 33 independent input/schema replay | INCONCLUSIVE | Prepared `assess` command could not start Python. Complete numerical schema revalidation was not executed here. |
| A/B/C/D reciprocal experiment | INCONCLUSIVE | Four captures and sixteen replay combinations are required; no STEP 33 hosted workers executed. One Windows capture/local replay cannot populate Linux cells. |
| Current-vector differences | INCONCLUSIVE | Historical STEP 31 evidence supports tiny nonzero differences, but new reciprocal current differences are unavailable. |
| Input-generation and solver effects | INCONCLUSIVE | Prepared paired B-A, D-C, C-A, D-B and interaction (D-C)-(B-A) contrasts require completed exact-input/provenance gates. |
| Discrete support-selection effects | INCONCLUSIVE | Deletion/L1/support and one-ULP D traces exist in STEP 32 capture; hosted reciprocal traces remain unavailable. Effects involving different supports cannot be interpreted as purely continuous solver effects. |
| Fixed-support conditioning | PASS | Saved augmented M ranks 24/23/23, conditions about 1.94679 for dense/row3/row4. These records do not support severe ill-conditioning. |
| Recorded KKT and feasibility | PASS | Saved production KKT maxima 7.79e-19, 1.61e-18, 7.13e-19; zero bound violation, no active bounds. These are recorded binary64 diagnostics, not new independent certificates. |
| STEP 33 residual-based Decimal KKT | INCONCLUSIVE | New 60/90-digit constrained-candidate checks and bounded M/y perturbation probes could not execute. |
| Independent fixed-current fields | PASS | STEP 32 records 60/90-digit agreement and production agreement at two points for each of 25 polygons. New componentwise and vector-norm summaries are unexecuted. |
| Fault-recovery causal pathway | INCONCLUSIVE | Historical current swaps support amplification; new reciprocal block swaps and source-authenticated attribution remain incomplete. |
| STEP 33 local regression/compilation | INCONCLUSIVE | Both attempted; existing .venv launcher exited 103 before Python startup. No STEP 33 test pass is claimed. |
| Hosted STEP 33 comparison | INCONCLUSIVE | No committed STEP 33 implementation or hosted run; publication intentionally not attempted. |
| Historical production comparison | FAIL | Actual run 41231422708 has four successful workers and failed diagnostic and production comparisons in all three Linux contrasts. |

The successful STEP 32 production record binds quick results to SHA256
`36d1955ed6307bea5d41ac48777223f7d2663e4454c93b27f227c15041eff5a1`
and study results to
`9435ee956fa962b6220ab7ab76af8defd95b88651c49755aa9455b34451e54df`.
Its integrity/gate/reproducibility records report local PASS, including a full
repeat. These records and their manifest hashes were inspected. They do not
override cross-platform failures or validate this new implementation.

The saved bounded problems have full column rank and positive ridge. Full column
rank makes each fixed-support quadratic strictly convex, so different approximate
solutions do not demonstrate multiple exact optima. Good condition estimates,
small objective differences and tiny KKT residuals are compatible with different
rounded solver outputs. New checks preserve the physical box and evaluate
residuals and KKT signs directly in Decimal arithmetic, without using normal
equations as a constrained-optimality certificate. The inherited normal-equation
interior reference is a historical auxiliary calculation, not the new certificate.
Neither finite precision nor precision agreement gives an interval proof.

Recorded STEP 32 row3 has B=2.5914425556311055e-5 T,
L-B=5.466485340462775e-11 T and R approximately -0.414688997029067.
Row4 has L-B=5.220686710474351e-10 T and R approximately
0.167266248499725. Saved-minus-90-digit ratio errors are approximately
2.61e-18 and -1.57e-16 respectively. These are saved local measurements,
not new cross-platform comparisons. Negative recovery is retained.

STEP 31E reports row3 denominator subtraction condition about 948121.
Historical reference/SciPy frozen row3 current swaps change R by about
3.2846981893e-11, with zero model-swap effect on those identical frozen inputs.
The historical NumPy row3 differential terms (L,P,B) are approximately
(-1.9406145470e-11, 2.4716938966e-11, 5.7161033600e-12), with nonlinear remainder
about -7.33e-25. Those previously reported values support the immediate
current-to-ratio pathway, not a unique upstream library cause. STEP 33 does not
independently regenerate those historical numbers.

The reciprocal implementation explicitly reuses STEP 32 capture/replay,
bounded coordinate/BVLS checks, solver diagnostics, support traces, Cartesian
field replay, Decimal recovery and block swaps. Exact complete sealed bytes,
M/y, D/d, weights, bounds, supports, regularization and settings remain recorded.
The new implementation verifies cohort OS/Python/NumPy/SciPy records and rejects
missing STEP 33 evidence. Initialization is unchanged: lsq_linear exposes no x0.
One-ULP M and y interventions retain the production bounds/settings and report
active-set changes. They are sensitivity observations, not global error bounds.

Current, dense-current, recovered-current, fine_A, fine_b, fine_weights and joint
swaps retain `R=(L-P)/(L-B)` and the original denominator guard. The differential
is `((1-R)dL-dP+R*dB)/(L-B)` with a nonlinear remainder. fine_A combines field
response and projection; fine_b combines disturbance and normals. Unrecorded
intermediates cannot be separated retrospectively. Support changes and joint
interactions must be reported separately; block effects are not an exhaustive
additive partition.

Read-only GitHub connector evidence confirms draft PR #7's head and the completed
[upstream run 41231422708](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41231422708).
Seal and all four workers succeeded; all three diagnostic comparisons and all
three production comparisons failed. The separate scientific-validation run
41231422707 succeeded. These runs predate STEP 33. Original ZIP bytes were not
downloaded/authenticated in this step; historical worker merge-commit provenance
remains unresolved. GitHub CLI configuration was not accessed.

No evidence identifies a specific NumPy/SciPy/BLAS/LAPACK operation. Version
correlation is insufficient. rtol=1e-11, atol=1e-13, refinement limit 1e-4,
current bounds, production physics and solver settings remain unchanged.
The original 256-segment failure remains; quick geometry remains 512 segments.
Finite-scenario minimax and small synthetic holdouts do not establish robust
outperformance, continuum accuracy, confinement or device validation.
