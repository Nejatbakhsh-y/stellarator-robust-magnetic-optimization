# Phase 2D final root-cause and acceptance disposition

2026-11-03. **NOT ACCEPTED — REQUIRES ADDITIONAL EXPERIMENTAL EVIDENCE OR MATHEMATICAL REDESIGN.** Scientific numerical root cause remains **INCONCLUSIVE**. The evidence-location problem is partially attributed, but the requested numerical investigation could not be completed in this process. This document is an adverse disposition, not a verified research checkpoint or a new numbered stage.

Baseline: `b9df6e64093ce16d8d20f164ad97bc66f77e93b6`, branch `codex/phase2d-upstream-attribution`. Production code, numerical algorithms, tests, frozen results, workflows and thresholds were not changed. No commit, push, merge or workflow dispatch was performed. GitHub CLI configuration was not inspected. The supplied 956 regression/36 STEP52 PASS observations remain prior controller observations; they are not fresh results here.

## Executed evidence recovery

The independent PowerShell/.NET reader in `scripts/phase2d_original_member_inventory.ps1` opened all 71 original STEP49 ZIPs without extracting or executing archived code. All archive SHA256 values match both manifest digests. The manifest SHA256 is `4ca1db2a783f2d62295e5ec2ef623b434a03c1b5a2a485f728c0f67df3d4a26e`. Fresh connected GitHub artifact responses for runs 41465448215, 41465448226, 41465448239 and 41465460206 corroborate all 71 artifact IDs, names, SHA256 digests and run/source associations. Responses and every association check are retained in [the evidence directory](phase2d-final-evidence/remote-association-checks.json). These attest the downloaded artifact associations; they do not independently attest runner hardware or every executed source file.

The scan authenticated 1,155 member byte strings to these archives and located 53 numerical input members with four distinct hashes. [The input inventory](phase2d-final-evidence/numerical-input-inventory.json) lists every run/artifact/member/schema/hash. Repeated identical input bytes are not independent experiments. Byte authentication does not replace semantic seal validation.

Of 1,379 parsed SHA256 references, 1,079 match their interpreted local member directly. **All 300 remaining references have exact SHA256-matching original member bytes within the same run.** There are zero content mismatches and zero unmatched digests in this parsed reference set. This does not prove that every scientifically required artifact was captured. Arbitrary omitted evidence cannot be detected by a list of existing seals.

| Missing-path family | Count | Finding |
|---|---:|---|
| `comparison/input-sha256.json` | 16 | Referenced manifests occur in separate capture/replay archives; consumer-relative interpretation is insufficient |
| `input-sha256.json` cohort keys | 32 | Keys identify origins; actual replay input members are `<origin>/inputs.json` |
| `step45/input-manifest.json` | 176 | Nested protected-root snapshot references; exact content exists within the run |
| `step45-comparison/input-manifest.json` | 76 | Nested snapshot references; exact content exists within the run |

The exact evidence for every reference, including every alternative matching member, is in [seal-reference-investigation.json](phase2d-final-evidence/seal-reference-investigation.json). Original path/run associations remain explicit `BYTES_RECOVERED_PATH_ASSOCIATION_UNPROVEN`; no file was relabelled or substituted. In terms of the requested A–F classes, the observed mechanisms concern A/C/D (path interpretation, nesting and normalization). B (wrong source/run association) is not demonstrated. E/F (missing source or numerical evidence) are not established merely by these 300 path misses. Other uncaptured evidence remains MISSING_EVIDENCE.

A precise reader/writer contract discrepancy is visible in the existing source. `phase2d_step32.py` writes `seals[origin] = sha(cap/'inputs.json')` and copies bytes to `out/origin/inputs.json`. STEP33 delegates to that writer. `phase2d_step50_reproduction.seals`, reused by STEP51/52, interprets each key as a member path. For example, run 41465448215, replay artifact 13153300612 seals `windows-reference` to `90a86ac4e944f6c0805c375df9dab6beae800d3be1a68d9e28d6b655bd5a544b`; the exact bytes occur at `windows-reference/inputs.json` in that archive and at `inputs.json` in capture artifact 13153060601. This demonstrates why an absent interpreted path is not absent input bytes. Source inspection alone does not authenticate every writer's executed source. No existing verifier was corrected: the mandatory reproducible Python failure test, independent corrected execution and full regression requirements cannot be satisfied here.

Two complete .NET inventory runs produced identical SHA256 values for all five substantive inventory/environment/reference outputs. The summary was corrected to group PowerShell dictionaries by their actual keys; the original and repeated local outputs are preserved under ignored `results/phase2d/final-root-cause-*`. This is inventory reproducibility, not numerical reproducibility. The reader does not claim the strict Python ZIP safety/CRC/semantic/source acceptance contract has passed.

## Recovery-ratio and causal attribution report

The unchanged definition is `R=(L-P)/(L-B)` with denominator guard `1e-15 T`. Its first-order differential is

```
dR = ((L-P)dB + (P-B)dL - (L-B)dP)/(L-B)^2.
```

Thus a denominator above the guard can still amplify tiny current/field/reduction errors enough to violate the ratio tolerance. This is a mathematical sensitivity mechanism; it does not uniquely identify which upstream operation generated a perturbation.

Historical STEP51/52 reports give row3/row4 denominators approximately `5.46648534046e-11 T` and `5.22068671047e-10 T`, saved/fresh current differences up to `2.04636307898909e-12 A`, condition approximately 1.94679 and saved/fresh KKT maxima below `1.7e-18`. Those are **historical measurements**, not independently rerun certificates here. A moderately conditioned least-squares matrix and small KKT residual do not certify stability of a cancellation-dominated derived ratio. Row3 is failed coil 3; row4 is failed coil 6 in the captured ordering.

The historical 21 failures in run 41256776296, 11 in run 41257645149 and earlier 22 scalar-path failures remain separate observations. They were not replaced by the four newer archive runs. Original archives and tracked historical results were left intact. An attempted extra PowerShell scalar traversal failed on a dictionary method overload; its failure is recorded, and it supplies no numerical measurements. No fresh high-precision quotient, solver-current, field, ULP, perturbation, residual or condition measurement is claimed.

| Potential origin | Current causal conclusion | Missing discriminating measurement |
|---|---|---|
| Input generation | INCOMPLETE | Exact arrays and geometry compared across authenticated origins |
| Geometry | INCOMPLETE | Independent smooth reconstruction and oriented vertex comparisons |
| Magnetic field evaluation | INCOMPLETE | Complete independent Bxyz arrays for each original worker current |
| Linear algebra | INCOMPLETE | Identical M/y solves with recorded LAPACK/BLAS/dispatch controls |
| Constrained optimization | INCOMPLETE | Full original support, bounds, termination and independent KKT/objectives |
| Floating-point arithmetic | INCOMPLETE | Both-direction ULP interventions and high-precision forward products |
| Serialization | Historical derived serialization defect retained; scope unresolved | Original binary64 versus emitted scalars for every failure |
| Quotient calculation | Sensitivity mechanism established algebraically; numerical attribution INCOMPLETE | Original B/L/P, numerator and denominator recomputed at converged precision |

## Magnetic-field validation report

**INCOMPLETE.** No independent field evaluation executed in this session. The preserved original Biot–Savart expression is `1e-7 integral(dl cross (p-r)/|p-r|^3)` in metres, amperes and tesla. STEP51's independent Gauss–Legendre saved-segment integrator is available, but did not start here. A saved-polygon quadrature check is not a smooth-coil segment-refinement check. Hash equality or aggregate component maxima do not substitute for complete elementwise Bx/By/Bz comparisons.

The original 256-segment refinement failure remains in `REFINEMENT_DIAGNOSIS.md`. Quick production uses 512 segments; the refinement limit remains `1e-4`. No new PASS is inferred from that historical correction. Independent geometry, orientation/reversed-current checks, training/fine grids, disturbance scaling, saved/fresh currents, smooth-circle convergence and complete residual arrays remain required.

## Four-environment report and unavailable controls

Fresh artifact metadata authenticates the supplied four-cohort archived experiments. It does not constitute re-execution. All retained archived environment JSON, including versions, build/thread metadata where present, is available in [historical-environments.json](phase2d-final-evidence/historical-environments.json), bound to member SHA256 identities. Historical libraries/BLAS/CPU dispatch and Python patch differences remain confounded. No unique OS, NumPy, SciPy, BLAS or dispatch cause is established.

All four fresh controlled configurations remain INCOMPLETE: Windows reference, Linux reference, Linux NumPy sensitivity and Linux SciPy sensitivity. The existing STEP33 workflow captures separately and reciprocally replays inputs; it uses different bundled numerical libraries and runner configurations. It does not isolate every requested upstream factor or provide a full independent smooth-field/precision intervention. No workflow was modified or dispatched. A successful hosted status would not close these scientific requirements.

## Actual execution and acceptance

The existing `.venv` records Python 3.11.9 with base `C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`. Its launcher exits **103** before Python startup because that base cannot be found from this process. `py -3.11 --version` also reports no installed Python. This establishes a process-local execution blocker, not the state of an external controlling host. No alternate environment was substituted and no installation outside this checkout was attempted.

Actual outputs and exit codes are in [execution/commands.json](phase2d-final-evidence/execution/commands.json). Targeted STEP51/52 tests, complete pytest, compileall, pip check, analytical CLI validation, fresh quick run, output checks, independent audit, README recorder, full reproduction and STEP51 numerical reproduction were each attempted. All eleven exited 103. None executed Python. Fixed-path README helpers therefore made no historical writes; a working interpreter must use the source-only diagnostic copy below before running them.

| Requirement | Verdict |
|---|---|
| 71 original ZIP bytes and fresh artifact/run digest association | PASS |
| Complete original evidence/source/semantic authentication | INCOMPLETE |
| Independent numerical reproduction | INCOMPLETE |
| Magnetic-field validation | INCOMPLETE |
| Recovery-ratio validation | FAIL; historical disagreements unresolved |
| Four-environment causal validation | INCOMPLETE |
| Targeted and complete regression, compilation, dependencies | INCOMPLETE; launcher exit 103 |
| README checkpoint and full repeat | INCOMPLETE; launcher exit 103 |
| Historical tracked result/source/test/workflow integrity against baseline | PASS for unchanged tracked paths; archive digests PASS |
| Inventory repeated execution | PASS within stated inventory scope |
| Production acceptance | FAIL |
| Final scientific acceptance | FAIL |

Fresh connected PR metadata confirms [PR #7](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/pull/7) **open, draft and unmerged**, head `b9df6e64093ce16d8d20f164ad97bc66f77e93b6`. Publication is blocked by failed validation preconditions. No new commit exists, no push occurred and the working tree contains these unpublished deliverables. A clean-tree or remote-publication success is not claimed.

## Reproducible protocol for remaining measurements

1. Restore access to the recorded existing Python 3.11 base on the authorized execution host; preserve `.venv` and package versions. Record actual `sys.version`, executable, NumPy/SciPy versions, `show_config`, `show_runtime`, loaded threadpools, BLAS/LAPACK versions, thread variables and CPU dispatch. A launcher failure is not a scientific measurement.
2. Re-run the original archive/member authentication and strict existing Python source/seal checks. Use `scripts/phase2d_step51_numerical.py --archive-root <STEP49-root> --manifest <STEP49-root>/manifest.json --output <fresh-output>`. Recover each of the 300 associations from exact same-run member bytes and the original writer/source contract. Retain all alternative matches. Authenticate the actual source Git objects and complete manifests; do not normalize originals in place. Add a regression that reproduces the origin-key contract before correcting a consumer, then independently check the corrected mapping. Until those tests execute, keep associations incomplete.
3. For every original failure bind run, artifact, member, input SHA256, result SHA256, support/fault and saved binary64 current vector. Re-solve original M/y using TRF/exact, tol=1e-12, max_iter=1000 and original bounds/scales/ridge. Independently calculate 60/90+ digit QR references, feasibility, residual/objective, projected KKT and singular values. Preserve both saved and fresh vectors; do not replace them by similar inputs.
4. Independently integrate every unit-coil and disturbance Bxyz array on training and fine grids. Test orientation and reversed currents, dimensions/units and smooth circular geometry separately. Retain complete arrays and pointwise residuals against saved worker arrays, then repeat for saved/fresh/faulted currents. Execute the original 1e-4 refinement gate. Polygon quadrature and smooth-coil convergence require separate records.
5. Form all B/L/P RMS operands from original binary64 fields at high precision; retain L-P, L-B and R. Vary precision until results stabilize; label this empirical convergence. Apply both-direction one-ULP interventions to dense and recovered currents, current/response/field swaps, exact-input forward products and scalar serialization comparisons. Record delta-I, delta-B, delta-M, predicted derivative terms, nonlinear remainder and all original ratio failures at rtol=1e-11, atol=1e-13, guard=1e-15 T.
6. Execute the four worker environments on the **same authenticated input bytes**, with recorded vectors, objectives, KKT, ratios and fields. Separate origin-input swaps from fixed-input solver swaps. Hold interpreter, BLAS, dispatch and threads fixed in additional one-factor interventions to isolate a library effect; a wheel replacement that changes BLAS remains confounded. Preserve an experiment matrix stating exactly which controls were held fixed and unavailable.
7. In a fresh source-only diagnostic directory **inside this checkout**, excluding historical results and `.venv`, use the existing `.venv` absolute interpreter with the diagnostic source installed/resolved there. Run the entire README test/analytical/quick/output/record/audit/reproduce/report sequence and full regression/compile/dependency checks. Fixed-path helpers must resolve to the diagnostic copy; verify that before execution. Seal actual logs, exit codes and every result SHA256. Rehash historical evidence before/after. Only after all software/evidence/publication checks pass may ordinary branch commit/push commands be used; do not merge PR #7.

No finite-scenario minimax or small holdout result establishes general robust outperformance. These synthetic planar coils do not establish confinement, equilibrium, external experimental/device validation or continuum-peak convergence. Missing controls prevent permanent scientific resolution. The defensible present disposition is **NOT ACCEPTED — REQUIRES ADDITIONAL EXPERIMENTAL EVIDENCE OR MATHEMATICAL REDESIGN**.
