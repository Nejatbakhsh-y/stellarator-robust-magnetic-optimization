# Independent numerical investigation

2026-11-03. **Investigation unfinished; scientific acceptance NOT ACCEPTED.**
Source baseline `c7aab608b291238272d64223d9de981687af9a62`, existing branch
`codex/phase2d-upstream-attribution`. No production correction, commit, push,
workflow change or dependency installation was made.

The supplied `PHASE2D_PYTHON` was tested directly. It resolves to
`C:\Users\nejat\AppData\Local\TheaResearch\FinalValidation311\Scripts\python.exe`
and exits 103 before startup because its configured Python311 base executable
cannot be found. Its pyvenv configuration says 3.11.9; that is configuration,
not an executed version measurement. Runtime Python, NumPy, SciPy, BLAS/LAPACK,
threadpool and dependency versions could not be measured. This unexpected host
execution failure must not be interpreted as a negative numerical experiment.

Fresh PowerShell SHA256 calculations verified **71/71 ZIPs**, zero mismatches,
against both supplied STEP49 digests. This verifies bytes against that manifest;
remote run associations are reused historical evidence, not fresh observations.
Logs and hashes are retained in
`results/phase2d/independent-numerical-study-20261103-061511/`.
The original inventory's 53 inputs, four input hashes, 1,379 references,
1,079 direct matches and 300 same-run byte recoveries remain historical evidence.
No fresh semantic/source/capture association certification is claimed.

The actual STEP32 writer assigns `seals[origin]` while copying the input to
`<origin>/inputs.json`. STEP50's generic reader interprets the origin as a
literal member path. The new regression fixture expresses that discrepancy:
the old reader reports MISSING although the expected input exists at the
writer-defined location. The diagnostic explicitly checks that location; it
does not search for convenient matching digests. This is source-supported
evidence of a contract discrepancy, but its regression has **not executed**.
No consumer was changed. Correct local bytes do not establish originating run,
capture/replay pairing, semantic seal or Git identity.

`scripts/phase2d_independent_numerical_study.py` is an unverified numerical
implementation, not another acceptance verifier. It authenticates archive bytes,
requires existing capture byte/semantic seals, and reuses the independent STEP51
polygon integrator and STEP46 Decimal Householder QR/certificates. It adds full
forward products and RMS reductions repeated at 60/90 digits, an empirical
1e-50 precision stabilization diagnostic, both directions of dense/recovered
current ULP probes, and complete generated field/quadrature arrays in NPZ files.
The 1e-50 diagnostic does not replace any acceptance criterion. Original M/y,
solver settings, objectives, support and bounds are preserved. Source identity
checks are retained separately; these diagnostic computations alone cannot
authenticate execution provenance. No calculations from this code executed here.

The implementation does **not** complete original replay-result binding,
elementwise comparison against every original worker Bxyz array, independent
smooth-coil regeneration/refinement, field ULP sweeps or four controlled runtime
experiments. It cannot be used to claim that those requirements passed.
Its reused QR is a bounded reference only when strictly interior; boundary cases
remain uncertified. All these limitations require substantive additional work.

Targeted/full pytest, compileall, pip check, analytical validation, fresh quick
experiment, output checks and the study CLI were attempted with the supplied
interpreter. README recorder, independent audit, full reproduction and report
commands were attempted in a source-only diagnostic copy inside this checkout.
All returned 103 before startup. Zero tests or numerical calculations executed.
The inventory PowerShell script was separately rejected by execution policy;
direct read-only hashing succeeded. An initial inline hashing command had a
PowerShell parse error and was corrected before the successful hash calculation.
Neither failure supplies scientific evidence. Whitespace and original tracked
file checks do not substitute for Python execution.

Historical observations remain separate: 21 failures in run 41256776296,
11 in run 41257645149, and 22 earlier scalar-path failures. The eight unique
saved/fresh pairs (six FAIL, two PASS) are prior measurements, not eight fresh
independent reproductions of all failures. The published original scalar-comparison
JSON records a failed traversal and contains no measurements; it is not a valid
source of new scalar values. No historical values were replaced.

All ten hypotheses are recorded individually in the accompanying JSON. None
has sufficient newly executed numerical evidence for unique attribution.
Cancellation is an algebraically established amplification pathway, not proof
of the operation that generated a difference. Small KKT residuals cannot isolate
OS, library or BLAS effects. Archived wheel comparisons also change bundled BLAS
and have interpreter/dispatch confounders. They are not isolated NumPy causality.

The unchanged limits are rtol=1e-11, atol=1e-13, denominator guard=1e-15 T and
refinement=1e-4. Polygon quadrature convergence and smooth-coil geometric
convergence remain separate requirements. Production quick geometry uses 512
segments; the historical 256-segment failure is preserved. Recovery agreement
remains **FAIL**; independent solver/field reproduction and four-environment
attribution remain **INCOMPLETE**; numerical root cause is **INCONCLUSIVE**;
production acceptance is **FAIL**, scientific acceptance **NOT ACCEPTED**.
Software regression PASS at the published baseline remains a prior observation.
Finite-scenario minimax and small holdouts do not establish general robust
outperformance; no confinement validation follows from field agreement.

## Authenticated four-way continuation, 4 November 2026

This section adds new observations without replacing the historical findings
above. Baseline branch head is `60b2e5b2daacb783e9994c90929197306ccb1d53`.
Run [41870669468](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41870669468)
executed GitHub's synthetic PR checkout `c6cd21793c71bbf0d9dc7dd934f3642fa991b52c`;
the API identifies its two parents and tree `14d7587d3f2dd3375de792579b5badf319679274`,
which equals the baseline tree. This is source-tree equality, not a merged PR.
The four capture and four reciprocal replay ZIPs plus comparison ZIP were
downloaded, SHA256-checked against fresh GitHub metadata and internally checked.
All 144 recorded source fingerprints match baseline Git blobs. Binary64 arrays
were independently decoded with `struct`, preserving every serialized bit.

All four workers completed four captures with no recorded execution errors.
The current run has **48/48 passing current comparison records and 23/32 failing
recovery-ratio records**. The prior 24/32 observation at `f1c3309` is preserved as
a different run, not corrected or pooled. Reference/self comparisons and shared
inputs are dependent records, not independent experiment counts.

Independent direct Decimal evaluation of the full weighted residual, square
root and `R=(L-P)/(L-B)` reproduced all 32 stored ratios to better than `1e-75`.
For a Windows origin and Linux-reference origin, define A=Windows inputs/Windows
execution, B=Windows inputs/Linux execution, C=Linux inputs/Windows execution and
D=Linux inputs/Linux execution. Effects below are signed differences in R:

| Case | Input effect C-A | Execution effect B-A | Interaction D-C-B+A | Total D-A |
|---|---:|---:|---:|---:|
| row3 | -7.11818382135e-11 | -5.26401105714e-11 | +8.63417865080e-11 | -3.74801622768e-11 |
| row4 | -5.50578159359e-12 | -4.57978093721e-12 | +7.88603707461e-12 | -2.19952545618e-12 |

The fixed-Windows-input execution discrepancies are relatively 1.26938768448e-10
and 2.73801856519e-11 for row3/row4. Large interaction terms prohibit a unique
additive attribution. Analogous four-way cells exist for both Linux sensitivity
cohorts. The NumPy 2.3.5 versus 2.4.6 execution contrast changes these ratios on
identical input bytes; it also changes the bundled numerical implementation.
SciPy 1.16.3 versus 1.17.1 yields identical recorded ratios to Linux reference in
these selected controls. Neither observation isolates a general library cause.
Windows Python is 3.11.9; Linux is 3.11.18, with recorded one-thread OpenBLAS and
CPU-dispatch differences. OS, interpreter, wheel build and kernel remain coupled.

The augmented matrix condition numbers are 1.9467914804478406 to
1.9467914804478432. All 48 captured solves terminate successfully with status 3
and zero iterations: the unconstrained solution is already feasible. Thus these
records do not demonstrate an ill-conditioned matrix or failed optimization
convergence. Twice-orthogonalized independent Decimal QR at 60/90 digits differs
by at most 1.45e-59 in normalized current. On fixed inputs, diagnostic changes
among LAPACK `gelsd`, `gelss` and `gelsy` shift R by up to 3.64e-11 relative to
the high-precision QR reference. These are controlled local interventions,
not a replacement production solver or proof of a unique historical kernel bug.

Recorded denominators range from about 5.46648534046e-11 to 5.22068671047e-10 T.
Windows/Linux input differences include maximum fine-response changes of
4.49986253229e-22 T/A and disturbance changes of 1.89735380185e-19 T; fine weights
are identical. The captured problem is deterministic nominal geometry/static
outage fitting, not a random actuation draw. No seed/order/serialization defect
was found; separate perturbation and seeded-scenario regressions remain required.

The quotient differential predicts the observed fixed-input current effects
with residual at most 4.68e-24 in R. Selected single-current one-ULP interventions
move R by up to 2.41e-12. Repeating metric evaluation at 60/90 digits differs by
at most 1.47e-53; ordinary binary64 RMS subtraction differs from the independent
reference by 3.77e-12 to 8.20e-11 in the selected cases. High-precision metric
evaluation therefore removes an evaluation-arithmetic uncertainty but does not
remove the recorded current-generation sensitivity.

The demonstrated mechanism is amplification of small input/execution/current
differences by a sensitive derived ratio. A specific defective input generator,
serializer, ordering rule or production solver operation has **not** been
established. No production numerical implementation, tolerance, denominator
guard or historical reference was changed. Unique upstream root cause remains
INCONCLUSIVE; full independent scientific acceptance remains NOT ESTABLISHED and
production acceptance FAIL. This bounded investigation does not establish
smooth-geometry/full-field, confinement or engineering acceptance. Availability,
commands and regression outcomes are tracked in [release readiness](FINAL_RELEASE_READINESS.md).
