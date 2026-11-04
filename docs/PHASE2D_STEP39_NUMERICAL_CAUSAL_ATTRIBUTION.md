# STEP 39 independent numerical causal attribution

2026-11-01. **Implementation prepared; Python verification BLOCKED.** Fresh
PowerShell/.NET numerical checks completed. Scientific comparison **FAIL**;
production acceptance **FAIL**; scientific status **PARTIAL**; causal root cause
**INCONCLUSIVE**. This is not a verified research checkpoint.

## Research question and scope

Why do frozen optimization inputs yield slightly different coil-current vectors
in nominally equivalent environments, while fixed-current field evaluations
agree? Does recovery-ratio sensitivity explain the downstream discrepancies,
and can a particular operating system, library, BLAS implementation, support
transition or termination choice be identified as the cause?

AGENTS.md, README, execution status, refinement diagnosis, Phase 2D source and
STEP 31/31E/32/33/34–35/36/38 reports were inspected. Historical assertions are
distinguished below from fresh calculations. No STEP 37 numerical experiment
was discovered or inferred from numbering. The feature branch remains
`codex/phase2d-upstream-attribution`, starting HEAD
`8476e5208b60d23ef10d36db026339996218785f`. Only the three STEP 39 deliverables
were added outside the supplied evidence output root. No production module,
existing test, workflow, historical result or scientific threshold was edited.
Nothing was staged, committed, pushed, merged or dispatched. GitHub CLI
configuration was not accessed. The existing environment was not replaced.

Let E denote
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/`
and O denote
`results/phase2d/step39-independent-attribution-20261101-095118-07af8f3a/`.
All fresh numerical evidence is in O. Its records bind comparisons to original
result-file SHA256 values; `manifest.json` binds generated files. These seals
establish local identities, not hosted archive authentication.

## Mathematical formulation

For physical currents I, x=I/3000 A, D=A·3000/Bref, d=b/Bref,
Bref=0.001 T, W=diag(w), and a fixed support S:

```
minimize 0.5 ||M x_S - y||²,  -1 <= x_S <= 1
M = [sqrt(W) D_S; sqrt(1e-6) Identity]
y = [-sqrt(W) d; 0]
```

Physical bounds remain ±3000 A. Unsupported currents are zero. The frozen
solver is `lsq_linear`, TRF, implicit exact least-squares solver, tol=1e-12,
max_iter=1000. No tolerance or termination criterion was changed. Comparison
uses the unchanged asymmetric bound `1e-13 + 1e-11*abs(reference)`; refinement
remains 1e-4 and quick geometry 512 segments.

The full production study also includes L1 support selection, deletion, and
finite-scenario minimax on eight training scenarios with 24 holdout scenarios.
Those small finite samples do not establish robust outperformance. The frozen
ridge replay is not an independently reconstructed SLSQP/minimax experiment.
Complete SLSQP initial states/constraints are outside this captured subset;
no SLSQP numerical reproduction is claimed. No confinement validation follows.

## Evidence inventory and source provenance

| Fresh STEP 39 check | Result | Qualification |
|---|---:|---|
| Download inventory and historical baseline | 3,599 entries; zero mismatches | 1,096 download + 2,503 historical entries; supplied hash inventories |
| STEP 33 capture source maps against local Git blobs | 824 entries; zero mismatches | 102 paths × four origins and 104 paths × four origins |
| Captures / saved reciprocal replay cells | 8 / 32 | Four origins × four workers, in each of two runs |
| Frozen input transport mismatches | 0 / 32 | File SHA256 equality to the corresponding capture |
| Saved field comparisons | 192 / 192 bitwise equal | Eight components × 24 nonself worker contrasts |
| Support inventories | 32 | Dense, deletion sequence and sparse selection supports |
| Environment files inventoried | 36 | Saved self-reports with original-file SHA256 |

Fresh results are `integrity.json`, `source-git-checks.json`, `replays.json`,
`fixed-field-comparisons.json`, `support-inventory.json`,
`support-comparisons.json` and `environment-inventory.json` in O.

Recorded commits are ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 (41195815229),
11c2b1347c7b5359bec0a56e95cc2aa46f03660c (41231422708),
cf77cf5466beadec7bd273e5c72ce9732cf253a7 (41256776296), and
1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 (41257645149).
The 824 fresh Git checks concern the last two runs only. Earlier worker/head
discrepancies described in STEP 31 remain unresolved; they are not overwritten
by checks on later artifacts.

STEP 38 records 46 extracted artifacts, no locally authenticated original ZIP
bytes, four incomplete early manifests, and a workflow-identity gap for
41256776296. STEP 39 did not acquire archives or perform a remote provenance
query. Extracted-file hashes cannot authenticate unavailable original archives.
The Python implementation reuses STEP 38's strict inventory/source validators
as transport checks and computes its own numerical diagnostics. That Python
inventory validation did not execute here; the fresh .NET checks above are
separate executed checks, not a claim that every inherited validator passed.

## Solver-input reconstruction and four-way attribution

Fresh .NET reconstruction from each original saved A,b,w reproduced D,d and
all dense/row3/row4 M,y arrays with **maximum numerical difference zero**.
Summing saved normalized weights sequentially gives 1.0000000000000018,
consistent with the existing comparison tolerance; weights were not renormalized.
Input dimensions are dense 264×24 and faults 263×23 on 240 training points.
`input-reconstruction.json` retains supports, solver arguments, initialization
descriptions and input-file digests. `conditioning.json` retains the spectra.
The Python implementation additionally fingerprints serialized individual arrays
and per-case numerical input inventories; those computations remain unexecuted.

Saved initialization arrays are retained. `lsq_linear` has no user x0 argument;
its recorded initialization is an internally computed unconstrained solution,
not a controllable supplied x0. Arbitrarily changing the solver to add x0 would
not reproduce the original experiment. Initialization and driver probes in the
historical diagnostics remain observations unless independently rerun.

| Required cell | Historical execution evidence | Fresh STEP 39 optimizer execution |
|---|---|---|
| A: Windows inputs / Windows worker | Available in both runs | BLOCKED |
| B: Windows inputs / Linux worker | Available in both runs | BLOCKED |
| C: Linux inputs / Windows worker | Available in both runs | BLOCKED |
| D: Linux inputs / Linux worker | Available in both runs | BLOCKED |

All four captured origins are replayed on four workers in each run. Within a
fixed origin, all inputs are byte-identical. Different origins are not presumed
identical: prior saved records show small field/geometry input-generation
differences and identical weights. Thus there is evidence of differences both
before the solver (regeneration) and after identical M/y reach the solver
(frozen solves). Regeneration is not a necessary cause of frozen-solve differences.

All **72** nonself current-vector comparisons pass the unchanged tolerance;
their maximum differences are 2.04636307898909e-12 A (41256776296) and
2.82796008832520e-12 A (41257645149). They are not bitwise-identical solutions.
All 96 saved solver termination records report success, status 3, nit=0,
“The unconstrained solution is optimal.” See `termination-inventory.json`.
That localizes the recorded termination path to the unconstrained least-squares
initialization, without proving which low-level operation produced rounding
differences. No iterative TRF active-bound transition is observed in these cases.

## Conditioning, feasibility and KKT analysis

For g=Mᵀ(Mx−y), lower-bound multipliers are nonnegative g at x=−1;
upper-bound multipliers are nonnegative −g at x=1. Stationarity is
g−lambda_lower+lambda_upper=0. Primal feasibility, dual feasibility and
complementarity are evaluated separately. The fresh check decodes physical
currents and divides by 3000 to obtain x, so rounding during this conversion is
included in its candidate residual. It is not an interval certificate.

| Case | Independent condition estimate | Normal-equation condition | Maximum stationarity | Primal violation / active bounds |
|---|---:|---:|---:|---|
| Dense | 1.94679148044784 | about 3.7900 | 1.16713199197762e-18 | 0 / 0 |
| Row 3 | 1.94679148044784 | about 3.7900 | 1.86768779636103e-18 | 0 / 0 |
| Row 4 | 1.94679148044784 | about 3.7900 | 2.17300016045435e-18 | 0 / 0 |

Fresh spectra use an independent binary64 Jacobi eigensolve of MᵀM followed by
square roots, **not an SVD**. Positive separated eigenvalues support ranks
24/23/23 here; Gram formation would be unreliable for diagnosing very small
singular values in an ill-conditioned matrix. The prepared Python code uses SVD
and the standard dimension-scaled epsilon cutoff, plus 90-digit residual KKT.
Neither that SVD nor that Decimal KKT was newly executed. Saved SVD records
agree qualitatively with the fresh estimates. In these interior candidates the
inferred multipliers are zero, so dual violation and complementarity are zero.
Severe matrix ill-conditioning is not supported as the mechanism in this subset.

## Recovery-ratio differential: requested sign is incorrect

For the unchanged definition R=(L−P)/(L−B), quotient differentiation gives:

```
dR = [(P-B)dL - (L-B)dP + (L-P)dB] / (L-B)^2
```

The requested `(B-P)dL` has the opposite sign. It cannot be confirmed
mathematically. For B=1,L=3,P=2, the correct dR/dL=+0.25; the requested
expression gives −0.25. An independently executed .NET Decimal central
difference at h=1e-7 gives **0.250000000000000625**.
`derivative-counterexample.json` preserves this calculation. The dedicated
Python tests include the quotient-rule identity and this sign counterexample.
The initial diagnostic following the requested sign is preserved as
`initial-wrong-requested-dL-sign.json`, explicitly superseded by corrected
`recovery-sensitivity.json`. No production equation was edited.

## Fault rows 3 and 4: sensitivity and cancellation

Representative latest-run Windows-origin/Windows-worker saved RMS values:

| Quantity | Row 3, failed coil 3 | Row 4, failed coil 6 |
|---|---:|---:|
| B [T] | 2.5914425556311052e-5 | 2.5914425556311052e-5 |
| L [T] | 2.5914480221164456e-5 | 2.5914947624982100e-5 |
| P [T] | 2.5914502890077691e-5 | 2.5914860300514034e-5 |
| L−P [T] | −2.2668913234990661e-11 | 8.7324468067418977e-11 |
| L−B [T] | 5.4664853403569658e-11 | 5.2206867104940321e-10 |
| (abs(L)+abs(P))/abs(L−P) | 2,286,346.177 | 593,531.333 |
| (abs(L)+abs(B))/abs(L−B) | 948,121.188 | 99,276.927 |
| dR/dB [1/T] | −7.586025962e9 | 3.203912776e8 |
| dR/dL [1/T] | 2.587931567e10 | 1.595065549e9 |
| dR/dP [1/T] | −1.829328971e10 | −1.915456827e9 |

Both denominators exceed the original **1e-15 T** guard; no guard was removed,
regularized or silently bypassed. Numerator cancellation and small denominators
amplify absolute RMS changes. An isolated 1e-21 T change in L predicts a
row3 ratio change about 2.59e-11 and row4 about 1.60e-12. This is a local
derivative calculation, not evidence that such an L intervention occurred.

Fresh binary64 central differences on all 64 row records, at h=0.001·abs(L−B),
confirm derivative signs and scales; this step deliberately avoids pretending
that arbitrarily tiny finite differences are accurate in binary64. For the
representative row3 dR/dL, the result is 2.587934160e10 versus analytical
2.587931567e10 (about 1e-6 relative error, consistent with finite-step error).
The Decimal counterexample provides an independent precision check.

Fresh .NET code also independently evaluates fine-grid RMS and R from each saved
dense/fault current vector, fine_A, fine_b and fine_weights. These binary64
evaluations are in `recovery-sensitivity.json`; differing summation order can
change final ratio digits. They do not replace production saved-ratio failures.
Fresh exact-binary64-to-Decimal 60/90-digit full-matrix recomputation is BLOCKED.
The prepared Python implementation includes it, fixed-current block swaps,
current-gradient chain rules, field-matrix/disturbance/weight sensitivities,
and fixed-support limitations. None of those unexecuted Python diagnostics is
presented here as a measured result. A high-precision evaluation at fixed saved
currents would not establish reproducibility of the optimization outputs.

## All eleven latest failures and earlier failed evidence

W=windows-reference, L=linux-reference, N=linux-numpy-sensitivity,
S=linux-scipy-sensitivity. Reference is the Windows worker on the same origin.
Every row below remains **FAIL** under the original tolerance.

| Origin | Worker | Fault row | Candidate minus reference R |
|---|---|---:|---:|
| W | L | 4 | −2.71740963064815e-12 |
| W | N | 3 | 3.16158210722506e-11 |
| W | S | 3 | 3.16158210722506e-11 |
| L | N | 3 | 3.15842907383512e-11 |
| L | S | 3 | 3.15842907383512e-11 |
| N | L | 3 | 1.10901288152832e-11 |
| N | N | 3 | 3.55555584974354e-11 |
| N | S | 3 | 3.55555584974354e-11 |
| S | L | 3 | 1.10901288152832e-11 |
| S | N | 3 | 3.55555584974354e-11 |
| S | S | 3 | 3.55555584974354e-11 |

The latest run has 10 row3 failures and one row4 failure. The preceding run
41256776296 retains 12 row3 and nine row4 failures, **21** total. All 32 failed
comparisons, including original scalar values and both result-file SHA256
references, are in O/comparisons.json. Duplicate N/S origins are separate saved
comparisons, not independent physical experiments.

Additionally, `early-failure-recheck.json` rechecks 22 previously extracted scalar
failure paths: 16 from 41195815229 and six from 41231422708. Every original
comparison-file SHA256 matches the extraction record and all 22 scalar
classifications still fail. This rechecks the extracted scalar inventory and
original-file identity; it is not a new independent traversal/extraction of every
early source JSON. Nested duplicated metrics are not counted as new experiments.

## Independent magnetic-field validation

Fixed-current forward evaluation, optimized-current reproducibility and ratio
reproducibility are three separate requirements. Fresh comparison of the eight
saved field arrays gives **192/192 bitwise-equal** nonself records. Those arrays
use captured currents, not each worker's slightly different optimized currents.

A separately coded eight-point Gauss–Legendre integration evaluates
`dl cross r / |r|^3` on every polygon segment, all 240 saved training points and
all 25 coils. This is independent **binary64 quadrature**, not the historical
high-precision reference and not a smooth-circle/refinement certificate.
It evaluates Bx,By,Bz for all 96 saved dense/row3/row4 optimized current vectors;
the full vectors are in `saved-current-field-vectors.json` (flattened xyz triples).
It also compares captured-current fields to saved field arrays:

| Field | Maximum absolute component error [T] |
|---|---:|
| Disturbance | 7.86046575051991e-19 |
| Dense | 8.40256683676266e-19 |
| Row 3 | 8.80914265144472e-19 |
| Row 4 | 9.08019319456610e-19 |

`independent-field-checks.json` binds these comparisons to input, fields and
result-file hashes. Historical 60/90-digit field checks remain saved observations.
Fresh Decimal reference checks at two deterministic points, all polygons and
all saved current vectors are implemented but **not executed**. Consequently
the requested fresh high-precision field validation remains incomplete.

## Support, repeated execution and controlled experiments

For all 32 saved cells, dense active-support indices, complete deletion removal
ordering and sparse selected supports match the Windows worker on that origin.
Fault supports consistently remove zero-based coils 3 and 6. No support change
is observed in these contrasts; this does not prove that support transitions
can never matter. The fresh support comparison concerns saved paths, not new
deletion or sparse solves. The prepared Python validator additionally checks
ordered deletion transitions and records refit supports.

Saved environments report Windows Python 3.11.9 versus Linux 3.11.17; reference
NumPy 2.4.6/SciPy 1.17.1, NumPy sensitivity 2.3.5, and SciPy sensitivity 1.16.3.
NumPy/SciPy OpenBLAS builds differ (0.3.31.188.0/0.3.30, sensitivity builds
including 0.3.29.dev). All recorded pools have one thread. Haswell/SkylakeX
dispatch differs across workers and runs. Library cohorts also change bundled
BLAS, interpreter patches and runner environments. These are confounded factors,
not isolated interventions establishing OS, NumPy, SciPy or BLAS causality.

Executed controlled arithmetic: exact frozen-input transport checks; independent
matrix assembly; fresh residual/KKT calculations; direct quadrature on identical
polygons/currents; derivative finite differences; corrected-sign counterexample.
Fresh repeated optimizer/thread (one versus two threads) controls are implemented
but not executed. No new numerical-library version cohort, changed-termination
experiment or reciprocal OS solve completed. Historical probe labels alone are
not causal demonstrations.

## Validation and execution limitations

`attempts.json` and individual logs record actual invocations of targeted pytest,
complete pytest, compilation, analytical CLI validation, quick experiment,
output checks, independent audit, README test-and-record, full reproducibility,
physics/refinement tests and the STEP 39 CLI. **Every invocation exited 103
before Python startup. Zero Python tests executed.** The existing .venv launcher
cannot find `C:/Users/nejat/AppData/Local/Programs/Python/Python311/python.exe`.
An isolated validation copy under O keeps fixed-path README writers away from
historical results. Final-source targeted/compile attempts are recorded separately.

The dedicated tests cover all 18 requested categories, with additional sign
counterexample, weighted-RMS and exact square-loop reference tests. They have
not passed runtime validation. Prepared code is not certified by static review.
No dependency installation or alternative interpreter was used.

Running the generated .ps1 file was blocked by the machine's script-execution
policy. No execution-policy setting was changed. Subsequent inline PowerShell
and .NET compiler invocations completed the explicitly reported fresh checks.
Windows PowerShell's case-insensitive JSON conversion rejects D/d together;
the numerical input reader uses a case-sensitive .NET dictionary. An initial
compiler-reference attempt failed and was corrected by compiling the helper
classes together. These attempts are not counted as successful scientific checks.
The generated helper script is retained for review; its initial blocked invocation
does not itself constitute execution evidence. Exact successful inline commands
are retained in the tool transcript; output records identify executed methods.

Git whitespace checking passed, the index remains empty and .venv remains
ignored. Historical preservation is checked again at closure in O. No passing
checkpoint report is produced without the mandatory Python/repeat gates.

## Reproducibility commands

After the existing Python 3.11 base interpreter is restored by the environment
owner, run from this checkout, retaining O and choosing a new output subdirectory:

```powershell
$O = Join-Path $PWD 'results/phase2d/step39-independent-attribution-20261101-095118-07af8f3a'
$E = Join-Path $PWD 'results/phase2d/step38-independent-verification-20261101-084216-7bda80b7'
$env:PYTHONPYCACHEPREFIX = Join-Path $O 'pycache'
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step39_attribution.py -p no:cacheprovider --basetemp "$O/targeted-fresh"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp "$O/full-fresh"
.\.venv\Scripts\python.exe -m compileall -q scripts/phase2d_step39_attribution.py tests/test_phase2d_step39_attribution.py
.\.venv\Scripts\python.exe scripts/phase2d_step39_attribution.py --input $E --output-root $O --output "$O/python-attribution-fresh"
```

The CLI returns 2 for incomplete evidence, including unavailable original archive
authentication, and retains historical scientific FAIL even after successful
calculations. `--saved-only` explicitly skips fresh optimizer controls. Runtime
results and compilation caches must stay within O. Run the remaining README
gates in a fresh source/config/test copy under O, as in attempts.json; do not
execute fixed-path recording scripts against historical results/quick.

## Scientific verdict and STEP 40 requirements

**OBSERVED / REPRODUCED:** saved frozen-input identity, tiny current differences,
32 recovery failures across the two later runs, 22 early scalar-path failures,
well-conditioned fixed-support problems, feasible interior currents, small
independent KKT residuals, unchanged support paths, fixed-current field agreement,
large ratio cancellation/sensitivity, and the requested differential's sign error.

**CAUSALLY ATTRIBUTED:** the mathematical dL sign discrepancy is conclusively
an algebraic error in the requested expression. It is not an optimization defect
or the historical numerical root cause. Small denominators causally amplify
scalar perturbations as demonstrated by the quotient and finite differences;
this alone does not identify the upstream source of observed differences.

**INCONCLUSIVE:** unique OS/library/BLAS/dispatch mechanism, fresh cross-platform
solver reproducibility, full high-precision field-to-ratio evaluation, and a
verified final-source implementation. No evidence supports relaxing any gate.

STEP 40 requires restoration of the existing runtime and executed final-source
tests; full README hash-linked gates; authenticated original archives and the
remaining provenance gaps; fresh 60/90-digit calculations; and controlled
reciprocal solves holding exact input bytes, interpreter, BLAS and dispatch fixed
while varying one factor at a time. Preserve currents, objectives, KKT, support,
iteration/termination records, fields and recovery values for every intervention.
Broader minimax, holdout and confinement questions remain separate.

Final: `scientific_comparison=FAIL`, `production_acceptance=FAIL`,
`scientific_status=PARTIAL`, `causal_root_cause=INCONCLUSIVE`.
