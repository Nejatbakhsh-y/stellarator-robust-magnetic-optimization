# STEP 34 causal attribution and STEP 35 independent publication review

Date: 2026-11-01. Implementation is prepared locally; required Python 3.11 runtime verification is BLOCKED. Scientific comparison **FAIL**; production acceptance **FAIL**; overall scientific status **PARTIAL**. No research checkpoint is claimed verified.

STEP 35 independently reviewed the implementation and rechecked preserved-byte integrity. Its new corrections have **not** passed runtime regression tests: the existing Python 3.11 environment cannot start. Sections 14–16 distinguish this review from the earlier STEP 34 executions. Publication of a verified implementation remains blocked.

## Research objective, formulation and optimization methodology

The objective is reproducibility and causal investigation of a synthetic planar-coil boundary-field model, including static single-coil recovery. Let A contain normal field per ampere, b the disturbance normal field, W normalized surface weights, Imax=3000 A, Bref=0.001 T, D=A Imax/Bref, d=b/Bref and x=I/Imax. For each selected support S, the bounded ridge problem is

```
minimize 1/2 ||M x_S - y||_2^2,   -1 <= x_S <= 1
M = [sqrt(W) D_S; sqrt(lambda) Identity], y = [-sqrt(W) d; 0]
lambda = 1e-6; unsupported currents = 0
```

SciPy `lsq_linear` uses TRF, the implicit exact least-squares solver, tol=1e-12 and max_iter=1000. Dense support has 24 currents; each investigated fault support has 23. Fault rows 3 and 4 remove coil indices 3 and 6 in the supplied evidence. These are zero-based indices, not a claim that every capture must use those indices independently of its recorded active currents.

The wider implementation also evaluates box-constrained L1 selection with support refitting, iterative deletion, and a finite-scenario minimax objective `min_x max_s ||sqrt(W)(D_s x+d_s)||_2^2 + lambda ||x||_2^2` on the selected support. Eight training and 24 disjoint holdout scenarios are small synthetic samples; this report establishes no general robust outperformance. Fault recovery reoptimizes the original training objective on surviving support and evaluates the fine-grid RMS metric defined in section 6. No optimization objective is replaced by the recovery ratio.

Independent validation separates byte/source provenance from numerical agreement. Four captured origins replay on four workers (16 cells per historical run); the twelve nonreference worker comparisons per origin matrix use the Windows worker as reference. Decimal arithmetic evaluates the saved binary64 inputs without a production solve; spectral, feasibility, KKT, support and field probes test distinct properties. Local SHA256 consistency does not authenticate archive transport. The four recorded environments are described in section 3; they were not recreated by STEP 35.

## 1. Verified source and evidence inventory

Read the checkout AGENTS.md before modification. Work stayed in this research checkout on existing feature branch `codex/phase2d-upstream-attribution`. Existing untracked evidence and tests were preserved. No staging, commit, push, merge, hosted dispatch, GitHub CLI configuration access, environment replacement, or physical-model modification occurred. `.venv/` remains ignored.

Original evidence is `results/phase2d/step34-independent-attribution-20261101-054745-369ad9ef/`. Fresh local analyses and complete attempt logs are in `results/phase2d/step34-local-20261101/`. Each run contains four captures, four replay workers, and sixteen origin/worker result records. Analysis used their actual binary64 hex payloads; no missing scientific values were invented.

Review entrypoints in that fresh directory are `validation-index.json`, `manifest.json`, `numerical-summary.json`, `independent-verified/run-*.json`, `independent-field-and-controls.json`, and `independent-support-and-reference.json`. Each replay analysis records the original result-file SHA256. `runtime-completion/attempts.json` and its logs describe attempts against the final source state. The manifest covers the retained analysis scripts, successful and failed attempts, source fingerprint index and numerical records.

| Run | Recorded source commit | Source paths per capture | Exact artifact manifests | Download file hashes |
|---|---|---:|---:|---:|
| 41256776296 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 | 102 | 18/18 | 240/240 |
| 41257645149 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 | 104 | 18/18 | 240/240 |

All recorded source-path hashes match bytes retrieved from their recorded local Git commit objects, in every cohort. Each replay source map equals its capture map. All replay input seals and copied input bytes match their corresponding captures; all eight complete-problem fingerprints independently recompute correctly. Cross-origin captures are not bitwise identical: A, b, fine_A and fine_b differ; training/fine weights are identical. Fixed-origin replay uses exactly the same bytes across workers. Working files intentionally differ from historical commits after this repair; historical fingerprints are not silently updated.

The eleven-failure assessment from the earlier `step33-hosted-investigation-20261031-204153-ac135ded/comparison/comparison/assessment.json` is byte-identical to the supplied run 41257645149 assessment. Its SHA256 is `069c6636bdb4d8ad4397116365d2bace8273b98d63c9dea05bcad31bf28f2c71`.

Local hashes establish supplied-byte integrity and consistency with local Git objects. They do not independently authenticate transport from GitHub or attest runner hardware. Original ZIP transport digests/signatures are not supplied here; hosted authenticity remains INCONCLUSIVE. The saved run metadata, dependency records, logs, source maps and numerical files are retained, not promoted to authenticated hosted attestations.

## 2. Historical scientific failure inventory

Run 41256776296 contains **21** recovery comparison failures: row3 for all twelve origin/Linux-worker pairs and row4 for the nine pairs with Linux-origin inputs. Run 41257645149 contains the **eleven** failures below. Their current-vector comparisons pass. The failures are retained in full in the original assessments and the independent inventories.

Here “origin / worker” compares that worker against the Windows replay worker on the same origin's captured inputs. Differences below are independently recomputed 90-digit current-to-field-to-R differences, not merely copied comparison maxima.

| Origin | Worker | Recovery row | Decimal signed delta R |
|---|---|---|---:|
| windows-reference | linux-reference | row4 | -2.717251278971e-12 |
| windows-reference | linux-numpy-sensitivity | row3 | 3.161582080683e-11 |
| windows-reference | linux-scipy-sensitivity | row3 | 3.161582080683e-11 |
| linux-reference | linux-numpy-sensitivity | row3 | 3.158395253375e-11 |
| linux-reference | linux-scipy-sensitivity | row3 | 3.158395253375e-11 |
| linux-numpy-sensitivity | linux-reference | row3 | 1.109018376310e-11 |
| linux-numpy-sensitivity | linux-numpy-sensitivity | row3 | 3.555492297367e-11 |
| linux-numpy-sensitivity | linux-scipy-sensitivity | row3 | 3.555492297367e-11 |
| linux-scipy-sensitivity | linux-reference | row3 | 1.109018376310e-11 |
| linux-scipy-sensitivity | linux-numpy-sensitivity | row3 | 3.555492297367e-11 |
| linux-scipy-sensitivity | linux-scipy-sensitivity | row3 | 3.555492297367e-11 |

The original eleven-failure report and the separate 21-failure run are distinct evidence inventories. Independent high-precision reevaluation reproduces the same 11 and 21 fail classifications, respectively, at unchanged rtol=1e-11 and atol=1e-13. No scientific failure is suppressed or relabeled PASS.

## 3. Four-environment numerical comparison

Run 41257645149 records:

| Cohort | Python | NumPy | SciPy | NumPy / SciPy OpenBLAS | Dispatch architecture |
|---|---|---|---|---|---|
| Windows reference | 3.11.9 | 2.4.6 | 1.17.1 | 0.3.31.188.0 / 0.3.30 | Haswell / Haswell |
| Linux reference | 3.11.17 | 2.4.6 | 1.17.1 | 0.3.31.188.0 / 0.3.30 | SkylakeX / SkylakeX |
| Linux NumPy sensitivity | 3.11.17 | 2.3.5 | 1.17.1 | 0.3.30 / 0.3.30 | Haswell / Haswell |
| Linux SciPy sensitivity | 3.11.17 | 2.4.6 | 1.16.3 | 0.3.31.188.0 / 0.3.29.dev | Haswell / Haswell |

Full platform, loaded-library paths, numerical build configurations and threadpool records are preserved in the independent JSON inventories. These are recorded environments, not four environments recreated locally. OS, Python patch version, hardware dispatch and binary library builds are confounded. Changing a NumPy/SciPy wheel can also change the bundled BLAS. The experiments do not isolate OS alone, one Python patch, one NumPy function or a particular BLAS/LAPACK kernel as the unique cause.

## 4. Current-vector discrepancy analysis

The largest same-input worker current differences are 2.0463630789890885e-12 A (first run) and 2.8279600883251987e-12 A (eleven-failure run). Every current element passes the existing current comparison. This does not imply that a derived cancellation-sensitive recovery ratio passes its own tolerance.

The same-origin tests hold M, y, the fine-grid response, disturbance, weights, failed-coil identity and selected support fixed. Therefore worker-dependent current differences are sufficient to transmit the observed same-origin ratio discrepancies. Direct Decimal evaluations of those saved current vectors reproduce the failed ratios. This establishes an immediate numerical pathway, not the original machine instruction responsible for the differing currents.

Independent finite-segment Decimal evaluation covers all 24 shaping coils plus the disturbance coil, every Cartesian component, at the two recorded production probes. Across both runs, all 800 coil/worker/origin reference comparisons round to identical binary64 reference components; the largest 90-digit textual difference is 5e-93 T. Against saved production components the maximum difference is 2.0328790734103208e-19 T. Summing the independently checked fields with captured fixed currents gives a maximum fixed-current component difference of 5.149960319306146e-19 T; all checked components pass unchanged tolerances. These are two-probe checks, not an independent full-grid or continuum certificate.

## 5. KKT and conditioning diagnostics

An independent standard-library Jacobi diagonalization of M-transpose-M reproduces the stored singular values within the existing comparison tolerance. For the Windows capture, the largest and smallest singular values are approximately 0.0698262079285197 and 0.0358673276669861. All three fixed-support augmented systems have condition number about 1.94679148044784 and full column rank: dense 24; fault rows 23. This does not support severe least-squares ill-conditioning or nonuniqueness as an explanation. Gram-based spectral diagnostics square conditioning and are diagnostic, not a replacement production solver.

Independent 90-digit residual-based KKT maxima are at most 1.452678614988151e-18 in the first run and 2.177393437897335e-18 in the eleven-failure run; every bound violation is zero. Active lower/upper bound sets are empty. Recorded production termination is success=True, status=3, nit=0: the unconstrained solution is already optimal. “Maximum iterations” and active-bound switching are not supported explanations for these saved candidates.

Independent 60/90-digit Gaussian elimination on the fixed-support normal systems reproduces saved Decimal reference vectors at binary64 precision for every worker and capture. Both precisions round identically. This is an independent arithmetic implementation for the supplied, well-conditioned interior problems; it is not an interval optimality certificate. Recomputed KKT residuals provide a separate residual-based check.

All saved worker support decisions agree for a fixed origin, including deletion support/removal decisions, sparse-path support and failed-coil supports. The saved one-ULP D interventions retain those decisions. This establishes observed support stability for these probes only.

## 6. Recovery-ratio sensitivity analysis

Define B as pre-failure RMS, L as frozen post-failure RMS, and P as recovered RMS. For R=(L-P)/(L-B),

```
N = L-P;  D = L-B
kappa_N = (|L|+|P|)/|N|
kappa_D = (|L|+|B|)/|D|
dR = [R*dB + (1-R)*dL - dP] / D  + higher-order terms
```

Thus a well-conditioned current solve can feed a highly cancellation-sensitive metric. Neither numerator nor denominator is a field residual norm by itself; both are differences of close RMS values.

For the eleven-failure Windows capture / Windows replay, independently recomputed references are:

| Quantity | Row3: failed coil 3 | Row4: failed coil 6 |
|---|---:|---:|
| L-P (T) | -2.266891323393847e-11 | 8.732446806418296e-11 |
| L-B (T) | 5.466485340462301e-11 | 5.220686710474448e-10 |
| R | -0.4146889970809171 | 0.1672662484975028 |
| Numerator conditioning | 2286346.177091853 | 593531.3329066207 |
| Denominator conditioning | 948121.1884690125 | 99276.92668726138 |

Full 60/90-digit B, L, P, N, D, R and derivative values are in the JSON records. Exact binary64-to-Decimal conversion is used for currents, responses, disturbances and weights. Across all results, 60-versus-90-digit ratio differences are below 1.47e-53. The largest saved stable-recovery versus independent Decimal ratio error is 6.32e-16. These errors are far below the failed inter-worker differences (up to about 3.56e-11 in the eleven-failure run). Merely using higher precision for the final ratio cannot reconcile genuinely different saved optimized currents.

Both denominators exceed the retained 1e-15 T denominator guard; these historical ratios are defined. Row3 has negative numerator/recovery: its recovered fine-grid RMS exceeds the frozen RMS. This is not evidence of recovery benefit. Row4's positive recovery is specific to this metric, case and finite evaluation.

Independent block substitutions on Windows baseline currents change row3 R by about -1.4465e-14 when only fine_A is replaced by Linux values, at most 2.695e-15 when only fine_b is replaced, and zero for identical weights. Row4 field/disturbance substitutions are at most about 2.342e-15. For the same-origin worker comparisons these blocks are byte-identical, so they cannot be the changing input. Fine_A combines coil response and normal projection; fine_b combines disturbance and normals. Their unrecorded intermediate operation errors cannot be separately reconstructed.

## 7. Controlled causal experiments

1. **Same-origin reciprocal replay:** four origins by four workers, identical sealed solver and evaluation inputs per origin. Independent Decimal ratios reproduce all failed classifications. This isolates the current-to-metric pathway from changing geometry, disturbance and weights for these comparisons.
2. **Field, disturbance and weight substitutions:** freshly recomputed one-block interventions quantify their effects above. They are small for the supplied cross-origin samples and zero as varying causes within a sealed origin; this is not a global error bound.
3. **Independent solver reference:** newly recomputed 60/90-digit interior solutions agree with saved Decimal references, while tiny production-current differences remain. Full rank, small KKT residuals and stable support exclude neither ordinary rounding nor library sensitivity.
4. **Thread counts, equivalent orderings and BVLS:** supplied one-/two-thread current vectors are identical in the eleven-failure run. All recorded sensitivity solvers succeed. The largest recorded row/column reordering change is 7.216449660063518e-16 in normalized current; one-ULP input probes change normalized current by at most 1.3381772344771502e-15 in L2. Active sets remain equal. Newly recomputed KKT residuals of saved sensitivity candidates are below 2.18e-18. These saved interventions were independently evaluated, not freshly rerun through SciPy in this session.
5. **Environment interventions:** recorded reference and wheel sensitivity cohorts demonstrate numerical environment dependence. Architecture and bundled BLAS changes prevent assigning unique causality to NumPy, SciPy, BLAS/LAPACK or OS separately. No CPU-dispatch pinning or kernel-isolation experiment was executed locally.

## 8. Demonstrated implementation defects

**Ignored validation verdicts:** validate_solve() validates structure and recomputed evidence, then returns `(gates, incomplete)`. STEP 32 replay and comparison, and STEP 33 assessment, discarded those returns. A structurally valid failed-termination/repeat record or unavailable independent reference could therefore continue without its solve verdict being enforced. This is a caller defect, not proof of an incorrect optimizer solution.

**Undefined recovery omitted from incompleteness:** validate_solve() previously marked incompleteness from unavailable solver references only. A recovery record correctly returning None at the existing denominator guard could leave all solve gates true and incomplete false. It now also marks unavailable fractional recovery incomplete. A synthetic zero-response evaluation regression isolates this edge case without modifying training inputs or the production model.

**Insufficient Decimal diagnostic gate:** STEP 32 require_replay() checked the presence of precision keys but did not reject a present None, NaN or Infinity ratio. It now requires finite, nonnegative RMS values, finite denominator above the existing guard, and a finite available ratio. Missing keys continue to fail closed. Saved 60/90-digit metric objects are also recomputed from sealed arrays and saved current vectors before comparison/assessment; arbitrary finite but inconsistent ratios are rejected.

These defects follow from the inspected control flow. Supplemental execution exercises the actual require_solve() function body against failed/incomplete verdicts. Real producer mutation regressions are added but remain unexecuted because Python 3.11 is unavailable. No defect above is demonstrated to have caused the eleven historical differences: their denominators are defined, reference diagnostics pass, and high-precision recomputation preserves their scientific FAIL. No additional mathematical error inside validate_solve() is established here.

## 9. Justified corrective changes

Added require_solve(), which checks the full returned case inventory, every solve gate, incompleteness and finite available recovery values. STEP 32 replay/comparison and STEP 33 assessment enforce it; STEP 33 replay/comparison inherit enforcement through the reused STEP 32 engine. Valid failed evidence remains readable through validate_solve(), preserving its diagnostic API. Executed failed replay candidates are saved under content-derived filenames before the gate raises when a CLI output directory is available.

Added an independent standard-library forensic script and focused regression cases for failed solver/repeat records, incomplete verdicts, undefined recovery, nonfinite/missing ratios and early replay rejection. All production objectives, ridge weight, bounds, constraints and scientific acceptance tolerances remain unchanged: rtol=1e-11, atol=1e-13, refinement 1e-4, quick geometry 512 segments. No historical numerical result was overwritten.

## 10. Independent regression evidence

| Check | Actual outcome |
|---|---|
| Standard-library arithmetic and extracted actual gate tests | 6 passed on maintenance Python 3.13.9; supplemental only |
| Independent sealed-evidence, Decimal field/ratio/KKT and spectral calculations | Completed on maintenance Python 3.13.9; numerical records hash-bound to original result files |
| New real-producer and targeted scientific pytest tests | BLOCKED before Python startup, launcher exit 103 |
| Complete pytest suite | BLOCKED before Python startup, exit 103; zero suite tests executed |
| Required Python 3.11 compilation | BLOCKED before Python startup, exit 103 |
| Supplemental Python 3.11 grammar parse and maintenance-interpreter compile | 79 source/script/test files PASS; not a Python 3.11 runtime check |
| Analytical validation, quick run, output checks, independent quick audit, reproducibility check | Each attempted with existing .venv; all BLOCKED before startup, exit 103 |
| Full Phase 2C production verifier and fault audit | Both attempted in fresh output scope; BLOCKED before startup, exit 103 |
| Git diff integrity / git fsck | Both exit 0; line-ending warnings and any dangling objects preserved in logs |

The configured .venv is Python 3.11.9 but its base executable `C:/Users/nejat/AppData/Local/Programs/Python/Python311/python.exe` is absent. The available `C:/Users/nejat/AN/python.exe` is 3.13.9. It was used only for clearly labeled, dependency-free forensic calculations and supplemental syntax/tests, not as a substitute scientific environment. No package installation or environment replacement was attempted. PowerShell may wrap unittest's stderr progress as NativeCommandError text; the saved supplemental test process exit is zero and unittest reports six tests OK.

## 11. Remaining scientific uncertainty

The immediate pathway is supported: small environment-dependent optimized-current differences enter a strongly cancellation-sensitive ratio. A unique root cause at an individual NumPy/SciPy/BLAS/LAPACK operation or OS behavior is **INCONCLUSIVE**. Architecture/build confounding, absent authenticated archive transport, and inability to rerun the required Python 3.11 scientific stack limit attribution. Neither ordinary floating-point rounding nor a library defect is uniquely established as the upstream cause.

Two field probes per polygon do not validate the full grid, continuum extrema, plasma equilibrium, field-line confinement, finite conductors or engineering feasibility. Finite-scenario minimax and small holdout samples do not demonstrate general robust outperformance. Earlier failed refinement evidence, production discrepancies and incomplete research milestones remain applicable.

## 12. Reproducibility instructions

Restore the ordinary existing Python 3.11 base installation before executing the scientific gates; keep .venv and its dependency contract. No hosted workflow dispatch or publication is required for the local repair. Use a new output path for every run. For dependency-free forensic reproduction:

```powershell
& C:/Users/nejat/AN/python.exe scripts/phase2d_step34_independent.py `
  --evidence results/phase2d/step34-independent-attribution-20261101-054745-369ad9ef `
  --output results/phase2d/step34-independent-repeat-NEW
& C:/Users/nejat/AN/python.exe tests/test_phase2d_step34_stdlib.py
```

A repeated independent forensic run produced identical numerical and historical records; changed working-file hashes are explicitly enumerated in repeat-differences.json. All 486 original supplied files remained unchanged. The first command deliberately labels the maintenance interpreter. The evidence-local `summarize.py`, `field-and-controls.py` and `support-and-reference.py` preserve the additional recomputation procedures and exact original paths. Their outputs and logs are retained locally; no temporary evidence is published.

After Python 3.11 is functioning, run `.venv/Scripts/python.exe -m pytest -q`, targeted STEP 32/33/34 and upstream tests, `-m compileall -q src scripts tests`, analytical validation, and the README quick/output/independent-audit/reproduction gates. The project's `scripts/phase2c_verify.py --output results/phase2d/step34-production-NEW` supplies fresh production/repeat scope; follow with its fault audit and required finalization checks. See `runtime-final/attempts.json` for exact attempted commands and arguments. Do not reuse a historical directory or claim a result-SHA-bound production pass until its required records actually pass.

## 13. Final scientific acceptance verdict

**STEP 34 IMPLEMENTATION STATUS:** validation repair and independent forensic analysis implemented; Python 3.11 scientific runtime verification incomplete.

**REGRESSION TEST RESULTS:** six supplemental dependency-free tests pass; targeted and full required Python 3.11 suites BLOCKED, not passed.

**INDEPENDENT NUMERICAL RESULTS:** local supplied evidence integrity passes; all 32 replay inputs are sealed; Decimal ratios independently preserve 21/11 scientific failures; bounded interior candidates and sampled fixed-current fields pass the evaluated checks.

**ROOT-CAUSE ATTRIBUTION:** current-vector differences amplified by recovery-ratio cancellation are demonstrated as the immediate pathway. Unique upstream numerical-library/OS/kernel cause remains INCONCLUSIVE. Validation-control defects are repaired separately and are not established causes of the historical values.

**SCIENTIFIC COMPARISON STATUS:** FAIL.

**PRODUCTION ACCEPTANCE:** FAIL.

**OVERALL SCIENTIFIC STATUS:** PARTIAL.

**REMAINING BLOCKERS:** functioning existing Python 3.11 environment; execution of new/complete regression and all required production gates; independent hosted archive authentication; controlled environment/kernel isolation; unresolved full scientific comparison. No acceptance threshold is weakened.

## 14. STEP 35 implementation audit and corrections

The review covered `upstream_attribution.py`, STEP 32/33 replay and assessment, STEP 34 forensic calculations, the requested upstream/STEP 34/host tests, and the preserved STEP 33/34 numerical records. Production model, solver, uncertainty, configuration and historical result files were not modified. Existing STEP 34 changes were preserved.

Additional demonstrated control-flow defects were found:

- `require_replay()` used `kkt_max > 1e-12` without checking finite numeric type or nonnegativity. IEEE NaN makes this comparison false. It now validates finite scalar constraint/KKT diagnostics before applying the unchanged gate. It also rejects negative KKT magnitudes.
- The same gate checked BVLS and thread successes but omitted the two equivalent row/column reordering solve successes. All five now require an actual Boolean `True`.
- Saved production optimality diagnostics were trusted after their threshold check. `validate_replay()` now recomputes all production optimality fields from the sealed M/y and saved currents, checking inventory, active sets, rank and numerical agreement. This closes a stale or fabricated certificate pathway.
- The dependency-free forensic script accepted a missing/empty evidence root and produced an empty summary. It now rejects this before creating output. Canonical binary64 shape/hex validation, equal-length dot products and recovery/KKT dimension checks prevent malformed payload coercion and silent zip truncation. A singular finite-segment reference now raises instead of substituting a zero contribution. Evidence and output trees must be disjoint in either direction.

Regressions cover these changes, including a nominal diagnostic record followed by each invalid mutation, an inconsistent saved KKT certificate, malformed payloads and absent evidence. These are source-reviewed corrections, **not runtime-verified corrections**. They are not established causes of the historical discrepancies. The existing STEP 34 failed/incomplete-solve gates remain in place.

## 15. STEP 35 verification record and reproduction

Fresh scope: `results/phase2d/step35-validation-20261101-063445/`. Its `attempts.json` contains 17 exact command/argument records with individual logs. Every existing `.venv/Scripts/python.exe` invocation returned **103 before Python startup**. This includes targeted tests, complete pytest, compilation, analytical validation, quick experiment, output checks, test recording, independent audit, full repeat, Phase 2C verification/fault/legacy/finalization, investigation, and the forensic script/tests. Zero current-revision Python tests executed. The earlier six supplemental passing tests in section 10 apply to STEP 34 only.

PowerShell checks freshly verified all **486** original files against the preserved forensic inventories and the earlier forensic manifest against its referenced files. All **32** replay input hashes and seals equal their origin capture hashes. `evidence-integrity.json` records each replay result-file SHA256; `source-integrity.json` records **1,854** source-hash checks against **206** distinct local Git source blobs. Those checks pass. The supplied inventories still record 21 and 11 failures. STEP 35 did not independently rerun Decimal arithmetic or four numerical environments; numerical values in sections 2–7 are retained STEP 34 observations whose bytes were rechecked here. Neither a fresh reproducibility pass nor authenticated hosted execution is claimed.

The initial attempt to execute a saved PowerShell review script was denied by system execution policy; no policy setting was changed. Ordinary inline PowerShell hash checks completed instead. Windows PowerShell's case-insensitive JSON conversion rejected an assessment containing distinct `D`/`d` keys; failure counts were then read from the hash-verified forensic inventories. This parser limitation is not a scientific failure or a reason to change scientific key names. The unused saved review script and initial attempt details remain local.

`git diff --check` and `git fsck --no-reflogs` returned 0. `.venv/` remains ignored. No staging, commit, push, merge, GitHub CLI invocation or configuration inspection occurred.

After the existing Python 3.11 installation is restored externally, reproduce with new paths from this checkout:

```powershell
$py = '.\.venv\Scripts\python.exe'
$out = 'results/ci/step35-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
& $py --version
& $py -m pytest -q tests/test_upstream_attribution.py tests/test_phase2d_step32.py tests/test_phase2d_step33.py tests/test_phase2d_step34.py tests/test_phase2d_step34_stdlib.py tests/test_phase2d_step33_host.py
& $py -m pytest -q
& $py -m compileall -q src scripts tests
& $py -m stellarator_robust.cli validate
& $py scripts/phase2c_verify.py --output "$out/production"
& $py scripts/phase2c_fault_audit.py --root "$out/production"
& $py scripts/phase2c_legacy_compare.py --root "$out/production"
& $py scripts/phase2b_investigate.py --output "$out/production/investigation" --corrected "$out/production"
& $py scripts/phase2c_finalize.py --output "$out/production"
& $py scripts/phase2d_step34_independent.py --evidence results/phase2d/step34-independent-attribution-20261101-054745-369ad9ef --output "$out/forensic"
git diff --check
git fsck --no-reflogs
```

Check each exit code and stop the dependent pipeline on failure. `phase2c_verify.py` runs the complete pytest, analytical, quick, output, independent smooth-field audit and separate quick/study repeat in its requested output scope, and binds gates to result SHA256. Existing finalization also reads immutable legacy evidence; its presence remains a prerequisite. The README's original baseline quick workflow remains required for a verified research checkpoint. Its standalone `test_and_record.py` and `reproduce_check.py` write fixed historical-default paths, so perform that workflow in a fresh isolated copy of this research checkout, preserving existing evidence. The fresh Phase 2C verifier is an additional versioned benchmark, not a claim that an unexecuted baseline gate passed. Original downloaded evidence is a separately supplied local input, excluded from publication; the forensic replay command is unavailable without it.

## 16. Publication handoff and final STEP 35 verdict

The reviewable publication allowlist is:

```
src/stellarator_robust/upstream_attribution.py
scripts/phase2d_step32.py
scripts/phase2d_step33.py
scripts/phase2d_step34_independent.py
tests/test_upstream_attribution.py
tests/test_phase2d_step34.py
tests/test_phase2d_step34_stdlib.py
tests/test_phase2d_step33_host.py
docs/PHASE2D_STEP34_FINAL_CAUSAL_ATTRIBUTION.md
```

This list includes existing STEP 34 work and new STEP 35 changes; it is a review boundary, not a passing validation claim. Do not publish `results/phase2d/` downloads, forensic outputs, attempt logs, backups, environments or machine configuration. No evidence-local helper is required to import the public package or run unit tests. Extended historical forensic conclusions require separately supplied evidence; their absence from the proposed publication is an explicit reproducibility limitation. No license has been selected in the project, and no open-source licensing claim is made.

| Requested outcome | Final verdict |
|---|---|
| STEP 35 implementation status | Audit/corrections/report prepared locally; runtime verification BLOCKED |
| SOFTWARE VALIDATION / regression tests | BLOCKED; no current-revision Python tests executed |
| NUMERICAL REPRODUCIBILITY | Historical byte/source consistency PASS; fresh numerical rerun BLOCKED; cross-environment comparisons FAIL |
| Scientific comparison | **FAIL** |
| Causal root cause | **INCONCLUSIVE**; immediate current-to-sensitive-ratio pathway supported by retained experiments |
| SCIENTIFIC ACCEPTANCE / production acceptance | **FAIL** |
| Overall scientific status | **PARTIAL** |
| ENGINEERING VALIDATION | Not established; no confinement or device validation |
| Publication readiness | Reviewable local source/report only; verified-release readiness BLOCKED |

Remaining blockers are the missing Python 3.11 base executable, unexecuted regression/production gates for these corrections, unresolved inter-environment scientific comparisons, incomplete transport authentication, confounded numerical-library/hardware interventions, and incomplete full-grid/continuum/device validation. Software tests passing later would not by themselves resolve scientific acceptance. The final machine-readable classifications remain `scientific_comparison=FAIL`, `production_acceptance=FAIL`, `scientific_status=PARTIAL`, `causal_root_cause=INCONCLUSIVE`.
