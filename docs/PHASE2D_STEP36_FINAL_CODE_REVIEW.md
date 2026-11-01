# STEP 36 final scientific code review

Corrected three-file review, 2026-11-01. Branch: codex/phase2d-upstream-attribution.
HEAD: a6eaf7cb9681f7dd5a966baf5b34384542ed5b9a.

Implementation review and focused corrections are complete locally. Runtime verification is BLOCKED. Scientific comparison = FAIL; production acceptance = FAIL; scientific status = PARTIAL; causal root cause = INCONCLUSIVE. This is not a verified research checkpoint or a publication-ready verified release.

## Original three-file change inventory

The initial tracked modifications were exactly the three authorized files below. The previous STEP 36 report incorrectly said there were two; that report is preserved as prior-step36-report.md in the fresh evidence directory. The preexisting STEP 33 tests were independently examined and retained. No original modification was discarded or reverted. Uncommitted file contents establish purpose, not editor identity or edit time.

| File | Original changes against HEAD and scientific justification |
| --- | --- |
| scripts/phase2d_step32.py | Replaces discarded validate_solve verdict with require_solve; preserves failed solve evidence when possible; validates finite scalar KKT and constraint violation, nonnegative KKT, five literal-success sensitivity records, and finite available 60/90-digit ratios above the existing denominator guard; adds validate_replay to recompute saved production optimality and Decimal metrics from sealed inputs and currents; comparisons enforces that validator. These close acceptance paths for incomplete, invalid, stale or nonfinite certificates. |
| scripts/phase2d_step33.py | Assessment now invokes STEP 32 validate_replay; local gate requires exact 60/90 precision and M/y perturbation inventories, correct precision labels, finite nonnegative Decimal objective/KKT/violation, zero violation, KKT <= 1e-12, PASS diagnostics and literal Boolean successes. This prevents vacuous success and forged PASS labels accompanying invalid diagnostics. |
| tests/test_phase2d_step33.py | Nine parameterized mutations cover empty Decimal records, missing precision, empty probes, NaN, Infinity, negative objective, excessive KKT, positive constraint violation and truthy false-success strings. A valid control precedes mutation. The inherited STEP 32 gate is deliberately isolated; existing STEP 34 tests cover the shared solve and integration gates. These are scientific failure regressions, not grounds to reject this preexisting test file. |

All three modifications are justified validation repairs. Existing objectives, ridge assembly, current bounds, physical constraints, field and recovery calculations remain intact. rtol=1e-11, atol=1e-13, refinement limit=1e-4, quick geometry=512 segments, denominator guard=1e-15 T and KKT limit=1e-12 are unchanged.

## Mathematical and caller review

For f(x)=||Mx-y||^2/2, gradient=M.T@(Mx-y). Interior stationarity requires gradient zero; at lower bound -1 it requires gradient >= 0 and at upper bound +1 gradient <= 0. The existing projected KKT signs implement these conditions correctly. Box feasibility is separately required. STEP 33 Decimal residual-based evaluation uses exact binary64 conversions at 60/90 decimal digits; it is a candidate check, not an interval certificate. Full-rank augmented fixed-support matrices imply strict convexity, without proving cross-platform equality of rounded solutions.

require_solve enforces the complete case gate inventory and incompleteness verdict returned by validate_solve, and requires available finite recovery values. STEP 32 replay calls it before diagnostics; STEP 32 saved comparisons invoke validate_replay; STEP 33 inherits those paths and assessment explicitly invokes validate_replay. STEP 33 main installs its extended gate for its own replay/comparison, while assess intentionally reads the STEP 32 schema. Missing required fields raise rather than pass. Comparison failures remain accumulated and classified FAIL; incomplete or malformed evidence cannot establish acceptance.

STEP 33 comparison independently recomputes saved Decimal KKT records. STEP 32 validate_replay rebinds production optimality and complete high-precision recovery objects to saved currents and sealed arrays. Exact equality of deterministic Decimal metric objects is stricter than a tolerance relaxation. Binary64 production diagnostics use the existing agreement rules.

## Additional focused corrections

Source review found sensitivity solvers could report success while returning infeasible or nonstationary candidates. STEP 32 now evaluates all five freshly generated sensitivity current vectors for finite values, feasibility and KKT at the existing limits. The reused replay leaves extended record validation to its callers, because STEP 33 adds its diagnostics after the base replay returns. STEP 33 now checks both its unperturbed and one-ULP perturbed solver candidates independently of success flags, including finite computed objective/KKT/violation. NumPy Boolean solver successes remain supported; truthy strings do not pass.

Six new STEP 33 regression mutations test NaN current, infinite current, out-of-box current, interior nonstationarity despite success, unsuccessful termination and string success, each with a valid zero-current control. No optimizer objective or historical calculation was changed. These corrections and tests remain runtime-unverified.

Limitations: saved sensitivity/perturbation diagnostics are not all independently rebound by every historical consumer; generated probe checks do not authenticate archived probe payloads. Missing keys may surface as KeyError rather than a normalized ValueError, but do not pass. Strict JSON cannot preserve a nonfinite value as a JSON number; failed-candidate serialization is best effort and may itself fail. No universal malformed-evidence or archival-authenticity certificate is claimed.

## Executed validation

Fresh evidence directory: results/phase2d/step36-corrected-review-20261101-073524/.

| Check | Actual result |
| --- | --- |
| Complete pytest regression suite | BLOCKED before Python startup, exit 103; zero tests executed |
| Focused STEP 32/33/34 and upstream tests | BLOCKED before Python startup, exit 103 |
| compileall src scripts tests | BLOCKED before Python startup, exit 103 |
| Analytical validation | BLOCKED before Python startup, exit 103 |
| Fresh README quick experiment, output checks, independent audit | Each attempted; BLOCKED before Python startup, exit 103 |
| Phase 2C verifier, including full production repeat | Attempted in fresh output scope; BLOCKED before Python startup, exit 103 |
| STEP 34 independent Decimal forensic rerun | Attempted with required environment; BLOCKED before Python startup, exit 103 |
| Prior analysis/STEP 35 integrity checks | 128 recorded file digests freshly checked; zero mismatches |
| Independent saved recovery scalar comparison | 21/24 failures in run 41256776296; 11/24 in run 41257645149 |
| Independent binary64 current decoding/comparison | All 72 current-vector comparisons pass; maximum differences 2.04636307898909e-12 A and 2.8279600883252e-12 A respectively |
| Git whitespace / index / environment ignore | diff --check passes; staged diff empty; .venv ignored |

The .venv launcher cannot find its configured base interpreter C:/Users/nejat/AppData/Local/Programs/Python/Python311/python.exe. No alternate interpreter, installation or environment replacement was used. attempts.json preserves command argument arrays and individual logs. Final-state attempts are recorded separately after the last edits. No Python test, compilation, new solve, analytical validation or full reproducibility pass is claimed.

PowerShell independently decoded little-endian binary64 current vectors and compared saved scalars using abs(candidate-reference) <= 1e-13 + 1e-11*abs(reference). Records include result-file SHA256, origin and worker. These checks use the Windows worker as reference for each sealed origin, excluding self comparisons. They validate saved numerical differences, not a new solve. Historical-before.json snapshots 4,555 preexisting result files; historical-after-check.json records the final preservation check. Source hashes bind the three final files; they do not authenticate hosted execution.

## STEP 34 attribution and unresolved scientific failures

The existing docs/PHASE2D_STEP34_FINAL_CAUSAL_ATTRIBUTION.md, including STEP 35 additions, was inspected and preserved. All eleven failures in the later historical run remain unresolved. Software gate repairs do not explain away or remove them.

Fresh current decoding confirms the reported same-origin current discrepancies. All current comparisons pass the original tolerance, while the derived recovery ratios fail. For R=(L-P)/(L-B), the first-order differential is

    dR = ((1-R)*dL - dP + R*dB)/(L-B).

Subtracting close RMS values can amplify small changes. The historical denominators, approximately 5.4665e-11 T (row3) and 5.2207e-10 T (row4), exceed the original guard but still permit cancellation sensitivity. Negative row3 recovery is not a recovery benefit.

STEP 34's retained independent 60/90-digit recalculation preserves the failed classifications; its precision differences below 1.47e-53 and saved-ratio errors below 6.32e-16 are much smaller than worker discrepancies reaching about 3.56e-11. Retained residual KKT maxima below 2.18e-18, zero violation, full rank, condition around 1.947 and stable supports do not establish severe ill-conditioning, nonuniqueness or active-bound switching. These Decimal/KKT/conditioning figures were reviewed, not freshly rerun in STEP 36.

The immediate current-to-sensitive-ratio pathway is supported. Unique originating OS, NumPy, SciPy, BLAS/LAPACK, CPU-dispatch or kernel causality is INCONCLUSIVE: wheel/build, hardware and environment interventions remain confounded. Gate defects are separate demonstrated software issues, not established causes of historical discrepancies. Higher precision applied only to the final ratio cannot reconcile differing current vectors.

## Exact reproducibility commands

Run from this research checkout after the existing Python 3.11 base installation is available. Use a new output path each time and inspect each exit code before dependent commands.

```powershell
$py = '.\.venv\Scripts\python.exe'
$out = 'results/phase2d/step36-repeat-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
& $py --version
& $py -m pytest -q
& $py -m pytest -q tests/test_phase2d_step32.py tests/test_phase2d_step33.py tests/test_phase2d_step34.py tests/test_upstream_attribution.py
& $py -m compileall -q src scripts tests
& $py -m stellarator_robust.cli validate
& $py -m stellarator_robust.cli run --config configs/quick.json --output "$out/quick"
& $py scripts/check_outputs.py "$out/quick"
& $py scripts/audit_quick.py "$out/quick"
& $py scripts/phase2c_verify.py --output "$out/production"
& $py scripts/phase2c_fault_audit.py --root "$out/production"
& $py scripts/phase2c_legacy_compare.py --root "$out/production"
& $py scripts/phase2b_investigate.py --output "$out/production/investigation" --corrected "$out/production"
& $py scripts/phase2c_finalize.py --output "$out/production"
& $py scripts/phase2d_step34_independent.py --evidence results/phase2d/step34-independent-attribution-20261101-054745-369ad9ef --output "$out/forensic"
git diff --check
```

README test_and_record.py and reproduce_check.py use fixed historical paths. For exact baseline README reproduction, use a fresh isolated copy of this same research checkout, with only its source/configuration/test/package files and scripts, and run those commands there using the existing .venv interpreter. Do not run them over existing historical outputs. The Phase 2C verifier supplies an additional fresh full repeat, not a substitute claim that baseline reproducibility passed. Finalization requires its legacy inputs. Historical forensic reproduction requires the separately supplied local evidence. No remote workflow dispatch is needed for these local commands.

## Final acceptance and publication readiness

STEP 36 implementation status: reviewed and corrected locally; mandatory runtime validation incomplete. Three-file code review: all original changes retained and scientifically justified. Complete regression results: BLOCKED, zero executed tests. Independent scientific validation: saved scalar/current checks and byte-integrity checks completed; fresh numerical solver/Decimal validation BLOCKED.

scientific_comparison = FAIL
production_acceptance = FAIL
causal_root_cause = INCONCLUSIVE
scientific_status = PARTIAL

Remaining blockers: functioning existing Python 3.11 runtime; passing final-source focused and complete regressions, compilation, analytical/quick/audit/output/full reproducibility gates with result-SHA-bound records; unresolved eleven historical comparisons; incomplete causal isolation and hosted authenticity. Publication as verified code is blocked. Nothing was staged, committed, pushed, merged or dispatched; no historical evidence was deleted. Work remained in this feature branch and research checkout. GitHub CLI restrictions were not inspected or bypassed.

The 256-segment failed refinement evidence remains applicable and preserved. Finite-scenario minimax and small holdout samples do not establish general robust outperformance, continuum peak convergence, plasma confinement or device validation. Incomplete research milestones remain incomplete.
