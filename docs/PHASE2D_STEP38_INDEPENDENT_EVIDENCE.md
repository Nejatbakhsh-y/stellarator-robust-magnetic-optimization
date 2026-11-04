# STEP 38 independent hosted evidence authentication and numerical reproducibility

Date: 2026-11-01. Execution status: **PARTIAL; mandatory Python validation BLOCKED**.
Scientific comparison **FAIL**; production acceptance **FAIL**; scientific status
**PARTIAL**; causal root cause **INCONCLUSIVE**; evidence authentication **INCOMPLETE**.
No verified research checkpoint is claimed.

## STEP 38C independent review (2026-11-01)

Review completed with justified verifier/test corrections; executable validation
remains BLOCKED. This review supersedes the implementation-coverage description
below, while preserving all historical observations and failed evidence. Only
this report, the STEP 38 verifier and its dedicated test file were edited.

Fresh read-only PowerShell checks in this review rehashed **3,599/3,599** supplied
download/historical inventory entries with zero mismatches, enumerated **46/46**
indexed extracted directories and found **zero ZIP files** in E. Therefore original
archives for **46 artifacts remain unavailable locally**. These checks establish
local file consistency with supplied hash lists, not the authenticity of the hash
lists or of original GitHub archive bytes. The retained live connector responses
were reviewed as historical provenance observations; no new remote query was
performed during STEP 38C. The workflow-identity gap for 41256776296 remains.

The actual retained comparison/replay records were inspected again: **32 replay
cells**, **72 passing current-vector comparisons**, and **192 nonself field
component records with zero reported numerical difference**. This is inspection
of saved measurements, not newly executed optimizer or field evaluations. Fresh
PowerShell arithmetic on every saved reference/candidate recovery scalar under
the unchanged asymmetric tolerance found zero classification mismatches:
**21 failures for 41256776296 and 11 for 41257645149 (32 total)**. The required
"11 remaining" describes the latest run; it must not erase the preceding 21.
The four incomplete historical manifests and earlier scientific failures remain.

Code review identified and corrected premature replay-completeness accounting,
empty/missing field payload acceptance, insufficient solver-diagnostic validation,
unchecked source-digest format, noncanonical evidence paths, duplicate artifact
IDs, incomplete frozen seals, and missing fault-support/current-vector checks.
The verifier now checks all eight required field components, solver settings,
finite numeric diagnostics, status/success consistency, active masks, objective
consistency with the independently evaluated frozen problem, and complete seal
maps. Successful current/recovery/field comparison records include result-file
SHA256 references; field comparisons also include both fields-file SHA256 values.
Malformed numerical evidence is recorded separately from valid scientific
disagreement. Replay completeness is recorded only after validation of a cell.
These are statically reviewed corrections, **not executed or certified checks**.
The historical problem fingerprint covers M/y/config/support/solver settings;
the full input-file SHA256 seal additionally binds all saved field/recovery arrays.

Expanded negative tests cover missing required artifacts, duplicate artifact IDs,
duplicate manifest/hash records, invalid SHA256 values, malformed/incomplete field
payloads, nonfinite currents, invalid numerical types, missing/invalid diagnostics,
frozen-input digest mismatches, changed solver settings, noncanonical paths, and
false scientific acceptance labels. Their execution remains pending.

On this reviewed source, targeted pytest, full pytest, compileall, analytical CLI
validation, a fresh quick experiment, output checks, independent quick audit,
README test_and_record and reproduce_check, the independent field-reference test
invocation, a fresh Phase 2C production repeat, and the STEP 38 verifier were each
attempted. **Every invocation exited 103 before Python startup** because the
existing .venv launcher cannot find its Python311 base interpreter. Zero Python
tests or numerical validation stages executed. No environment was replaced and no
dependencies changed. The prior D/attempts and source-hash records describe the
earlier source, not these corrected files. STEP 38C command outcomes are recorded
here and in the review tool transcript; D was not overwritten. Git diff --check
passed, the staging area remained empty and .venv remained ignored.

Final targeted pytest and compilation were attempted again after code edits;
both exited 103 before startup. SHA256 of the reviewed verifier is
`b0065231738c6d6eb8d3bf428c8d7faff64229106b9b66a19dd1eba6cea61676`;
the dedicated test file is
`7a8c5b8ac7200bbd00baaaaf7d1980aabf92607ec2ef52cca62467642085607f`.
The existing `tests/test_physics.py` and `tests/test_refinement.py` invocation also
exited 103. An earlier invocation naming `test_independent_field_reference.py`
did not start Python; that filename is absent and provides no test evidence.

Publication readiness is **BLOCKED** pending host execution of the corrected
source and complete required gates, authenticated original archives, resolution
of provenance/manifest gaps, and investigation of historical numerical failures.
Scientific comparison = **FAIL**; production acceptance = **FAIL**; numerical
causal root cause = **INCONCLUSIVE**; overall scientific status = **PARTIAL**.
The unchanged rtol=1e-11, atol=1e-13, refinement limit=1e-4 and 512-segment
geometry remain mandatory. No controlled evidence uniquely attributes the
differences to OS, NumPy, SciPy, BLAS, hardware dispatch or cancellation alone.

Use the reproduction commands below on the Windows host with the restored
existing environment. Preserve a fresh verifier output even when it exits 2 for
known incomplete evidence. Run README fixed-path recording/reproduction commands
only in the source-only diagnostic copy described below. The next numerical
attribution experiment must hold serialized inputs, interpreter, hardware dispatch
and BLAS fixed, vary one factor at a time, and retain currents, solver termination,
KKT/objective, fixed-current fields, and high-precision field-to-ratio evaluations.
Archive authentication is a separate evidence-acquisition prerequisite, not a
numerical causality experiment.

## Research question and scope

Can the supplied GitHub-hosted evidence be independently authenticated, and do
four numerical environments reproduce the same optimization and recovery outputs
at rtol=1e-11 and atol=1e-13? Can reciprocal replay separate input generation,
field evaluation, solver outputs and recovery-ratio amplification?

AGENTS.md, README.md, EXECUTION_STATUS.md, REFINEMENT_DIAGNOSIS.md and the STEP 34–36
reports were read. Work stayed in this checkout on existing feature branch
`codex/phase2d-upstream-attribution`, HEAD
`971e54da77efb2ebea04464006967ec7eab53f6f`. No production files, workflows,
historical results, tolerances, equations, objectives, bounds or physical
constraints were changed. Nothing was staged, committed, pushed, merged or
dispatched. GitHub CLI configuration was neither inspected nor bypassed.

Evidence root E:
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/`.
Fresh diagnostic root D: `results/phase2d/step38-diagnostic-20261101/`.
Paths below relative to E or D identify actual retained evidence. The implementation
is `scripts/phase2d_step38_verify.py`; adversarial tests are
`tests/test_phase2d_step38_verify.py`. No additional dependency was installed.

## Independent acceptance criteria

| Criterion | Executed result | Limits |
|---|---|---|
| LOCAL_FILE_INTEGRITY | 1,096 downloaded-file hashes and 2,503 historical baseline hashes match | Hash lists are supplied local claims; no transport authentication follows |
| Internal manifest completeness | FAIL: 54/58 exact; four incomplete | No listed-member hash mismatch; omitted members still reject exact coverage |
| GITHUB_RUN_PROVENANCE | Live connector corroboration, with one commit-list omission | Artifact association is independently corroborated; complete workflow/run attestation remains incomplete |
| ORIGINAL_ARCHIVE_AUTHENTICATION | INCOMPLETE: zero original ZIP byte digests verified | Extracted file hashes do not establish original ZIP digest |
| SCIENTIFIC_REPRODUCIBILITY | FAIL | Saved-record discrepancies reproduced; new solves and high-precision rerun blocked |

`D/hash-checks.json`, `manifest-checks.json`, `source-checks.json`,
`artifact-inventory.json`, `runs.json`, `replay-records.json`, `comparisons.json`
and `summary.json` contain machine-readable executed checks. These were computed
with PowerShell and .NET, independently of the historical comparison scripts.
The new Python implementation has **not executed**. Its expected behavior must
not be confused with observed PowerShell results.

## Hosted provenance and source identity

Read-only connected GitHub calls fetched commit-filtered workflow runs, artifact
inventories for all four run IDs and jobs for run 41256776296. Raw connector
responses are preserved as `D/live-<run>.json`, `art-<run>.json` and
`jobs-41256776296.json`. No hosted workflow was dispatched.

| Run | Supplied source SHA | Artifacts | Run evidence |
|---|---|---:|---|
| 41195815229 | ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 | 5 | Live commit query finds completed/failure, workflow 402677493, “Phase 2D investigation (unchanged scientific gates)” |
| 41231422708 | 11c2b1347c7b5359bec0a56e95cc2aa46f03660c | 7 | Live commit query finds completed/failure, workflow 402952506, upstream attribution |
| 41256776296 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 | 17 | Supplied metadata says completed/failure; live artifact associations and direct jobs corroborate run and expected-head replay arguments; commit-filtered listing omits this run |
| 41257645149 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 | 17 | Live commit query finds completed/failure, workflow 403150023, “Phase 2D STEP 33 controlled causal attribution” |

The connector returns first pages only. The commit-filtered listing for
41256776296 instead includes upstream run 41256779366; this is not substituted
for the requested run. Direct jobs show four successful captures, four successful
replays and a failed compare job with explicit `--expected-head cf77cf...`.
The missing run-list entry leaves workflow-ID attribution for that run incomplete.
The supplied metadata does not itself contain a workflow ID/path. Artifact head
associations do not cryptographically attest which code ran on a runner.

For the two STEP 33 runs, **824 source-path/cohort records** independently match
SHA256 of bytes read from local Git commit objects, with zero mismatches.
All 32 replay source-map files equal their corresponding capture source map.
This authenticates consistency with local Git objects, not hosted execution
or runner hardware. Earlier runs' full source maps were not independently
rehashed against Git in this executed diagnostic; do not extend the 824-record
result to them. Live artifact associations corroborate their recorded commit IDs.

## Artifact inventory, missing and incomplete evidence

All **46 indexed artifacts** have local extracted directories. All 46 live
metadata records match supplied ID/name, digest, size, creation time, expiration
time and expiration flag. None is marked expired at this observation. Complete
IDs, names, times and digests are in `D/artifact-inventory.json` and E's original
`github-hosted/<run>/artifact-index.json`.

| Run | Available names / families | Expiration window recorded |
|---|---|---|
| 41195815229 | phase2d-{windows-reference,linux-reference,linux-numpy-sensitivity,linux-scipy-sensitivity}; phase2d-cross-platform | 2026-11-14 |
| 41231422708 | upstream-{four cohorts}; upstream-comparisons; upstream-sealed; dependency-seal | 2026-11-30 |
| 41256776296 | four captures, four replays, eight dependency artifacts, one comparison | 2027-01-30 |
| 41257645149 | four captures, four replays, eight dependency artifacts, one comparison | 2027-01-30 |

Missing inventory: original archive bytes for all 46 artifacts; complete direct
workflow identity attestation for 41256776296; fresh executed final-source Python
validation; independently executed high-precision and sealed-problem semantic
fingerprint recomputation. Earlier protocols do not supply the STEP 33 16-cell
matrix and must not be represented as having it. No indexed artifact is proven
expired or absent locally. Unavailable archive bytes are different from an
expired GitHub artifact.

The four incomplete manifests belong to run 41195815229, artifact IDs
13040657341, 13040832447, 13041012667 and 13041267164. Each lists 59 members
and omits `committed-reference-comparison.json`. Listed-member digests match.
The omitted files match the supplied downloaded-file inventory, but exact
internal-manifest coverage still fails. Historical evidence was not repaired.

A connected download of artifact 13063239980 returned a reusable ZIP file
reference. Transfer to this checkout failed with “Unable to connect to the remote
server” (`D/archive-download-error.txt`). No original archive was locally hashed;
neither a successful connector response nor the advertised SHA256
`15ee0f5083d98f3445f3a96ba4400bbf5bd5dac7795664d1bd62effe2e18dfe1`
is treated as verified archive bytes. Signed temporary URLs are not copied into
the scientific report.

## Four-environment comparison

For both STEP 33 runs, `D/environments.json` preserves full platform, executable,
package, numerical build, loaded threadpool and environment-variable records,
each linked to the original environment-file SHA256.

| Worker | Python | NumPy | SciPy | Loaded NumPy / SciPy OpenBLAS versions |
|---|---|---|---|---|
| Windows reference | 3.11.9 | 2.4.6 | 1.17.1 | 0.3.31.188.0 / 0.3.30 |
| Linux reference | 3.11.17 | 2.4.6 | 1.17.1 | 0.3.31.188.0 / 0.3.30 |
| Linux NumPy sensitivity | 3.11.17 | 2.3.5 | 1.17.1 | 0.3.30 / 0.3.30 |
| Linux SciPy sensitivity | 3.11.17 | 2.4.6 | 1.16.3 | 0.3.31.188.0 / 0.3.29.dev |

All recorded pools have one thread. Architecture dispatch is confounded:
41256776296 Windows reports SkylakeX and Linux reference Haswell;
41257645149 Windows reports Haswell and Linux reference SkylakeX. Sensitivity
workers report Haswell. Windows and Linux use different interpreter patch
versions and binaries; changing a library also changes its bundled BLAS.
These cohorts do not isolate OS, NumPy, SciPy or BLAS as a unique causal factor.
Metadata is a runner's self-report, not independently measured hardware.

The preserved problem specifies bounded ridge least squares, SciPy
`lsq_linear`, TRF, implicit exact least-squares solver, tol=1e-12 and
max_iter=1000, normalized bounds [-1,1], imax=3000 A and ridge=1e-6.
The independent verifier fingerprints M, y, config, support, fault index,
solver arguments and implementation labels. Its semantic fingerprint checks
remain unexecuted. Executed checks establish byte seals and source-map equality.

Saved diagnostics include solver termination, initialization and rounding
probes, singular values, effective rank, projected gradient and objectives.
`D/replay-records.json` retains these without asserting that reported diagnostics
are independently recomputed. Production disturbance/scenario records in older
artifacts remain subject to their original comparisons; STEP 38 runs no new
scenario generation or minimax optimization.

## Reciprocal replay and discrepancies

Both STEP 33 runs contain **16/16** required origin/worker records: each of the
four captured origins on all four workers. All 32 result files have fresh SHA256
references in `D/replay-records.json`. Every replay input file matches its
capture SHA256 and both capture and replay seals. This explicitly includes
Windows→Windows, Windows→Linux, Linux→Windows and Linux→Linux.
Within a fixed origin the serialized inputs are identical across workers.
The four captured origins are not assumed identical to one another.

The comparison reference is the Windows worker on the **same origin**, with
12 nonself worker comparisons per run. All dense, row3 and row4 current-vector
comparisons pass: **72/72**. Passing current tolerances do not imply bitwise
identity or recovery-ratio reproducibility. All failed saved-ratio comparisons
are retained individually in `D/comparisons.json`; none is suppressed.

| Run | Failed row3 comparisons | Failed row4 comparisons | Total / 24 |
|---|---:|---:|---:|
| 41256776296 | 12 | 9 | 21 |
| 41257645149 | 10 | 1 | 11 |

Maximum decoded current differences are 2.04636307898909e-12 A and
2.8279600883252e-12 A respectively. Saved fault diagnostics have rank 23,
condition approximately 1.94679, status 3 and zero iterations, consistent
with the recorded unconstrained-optimal termination; this is retained metadata,
not a new solve.

This is independent arithmetic on decoded original binary64 currents and saved
ratio scalars, not a rerun of the optimizer. It reproduces the documented
disagreement without establishing its originating mechanism.

Independent decoded saved-field comparison completed for eight components:
dense fixed-current Bxyz, original Bxyz, projected A, row3/row4 fixed-current
and frozen-current Bxyz, and unit-coil Bxyz. **192/192 nonself component checks**
have maximum numerical difference zero (256/256 including 64 self checks).
Every comparison is on a fixed origin and bound to both original fields-file
SHA256 values in `D/fixed-field-comparisons.json`; `field-summary.json` records
the total. This compares saved field evaluations; it is not a fresh independent
Biot–Savart computation or proof of optimized-current reproducibility.
The first slow PowerShell-only decode scan was stopped before emitting results;
`field-initial-scan.txt` records this. The equivalent .NET decoder in retained
`inspect-fields.ps1` completed and supplied these measurements.

Earlier original-run failed scalar records are separately recomputed and
retained in `D/early-run-failures.json`, with source-file SHA256 and unchanged
tolerance classifications. For example, run 41195815229
`artifact-13040618382/cross-platform.json` records row3 reference
-0.414688997029067 versus -0.4146889970636461 (difference about 3.458e-11),
and row4 0.16726624849972482 versus 0.16726624849716587 (about 2.559e-12).
Duplicate metric/evidence paths are distinct recorded failures, not independent
physical experiments. Fixed-current agreement alone cannot validate optimization.
The early-run inventory contains 16 failed scalar-path records for 41195815229
and six for 41231422708 across their available comparison files; repeated files
and nested metric paths must not be counted as independent experiments.

## Conditioning, KKT and recovery ratio

Saved STEP 33 dense diagnostics show full rank 24, condition about 1.94679,
success=true, status=3, nit=0, “The unconstrained solution is optimal.”
The 23-current fault supports and saved active masks/termination data must be
read per case. These observations do not support a claim of severe matrix
ill-conditioning, nonuniqueness or demonstrated bound switching.
They also do not establish that floating-point solver paths are identical.

All 96 retained solve diagnostics report success, status 3 and zero iterations;
all 32 dense cases have rank 24 and all 64 fault cases rank 23. Reported condition
numbers span 1.9467914804478408–1.9467914804478432; maximum reported optimality
is 2.1700355451389634e-18 and projected-gradient maximum 3.4694469519536142e-18.
`D/saved-conditioning.json` retains singular values, active masks and objectives,
and `saved-conditioning-summary.json` retains these summaries. These are
independently inspected **saved diagnostics**, not freshly recomputed KKT or
spectral measurements.

For R=(L-P)/(L-B), direct differentiation gives

    dR = ((1-R)dL - dP + R dB)/(L-B).

The recorded row3 denominator is approximately 5.4665e-11 T and row4 denominator
approximately 5.2207e-10 T. Small absolute field/current changes may therefore
amplify in R even when current vectors pass their own tolerance. Numerator
cancellation also matters; negative row3 recovery is not a recovery benefit.
This establishes an algebraic sensitivity pathway, not a unique originating
OS/library/BLAS mechanism. Re-evaluating only the final ratio at high precision
cannot force different optimized current vectors to agree.

An executed binary64 controlled probe uses the three **rounded saved RMS
scalars**, independently of the saved residual-energy ratio implementation.
Across 64 row records, row3 denominator condition ranges from 948121.188429
to 948121.188487 and numerator condition reaches 2286346.17733. Row4 denominator
condition ranges from 99276.9266869 to 99276.9266875 and numerator condition
reaches 593531.332931. Increasing only the lost RMS scalar L by one representable
binary64 step changes this recomputed ratio by up to 8.76825e-11 (row3) and
5.40429e-12 (row4). `D/rounded-rms-sensitivity.json` binds every probe to its
result-file SHA256; `rounded-rms-summary.json` contains extrema.
These are controlled final-scalar perturbations, not current-vector, geometry,
scenario or disturbance interventions. Rounded-RMS recomputation is not a
high-precision reference for the residual-energy metric and does not explain
the observed solver-current differences. An initial PowerShell variable-name
collision produced no measurements; the failure is retained in
`rounded-rms-initial-failure.txt`, and the corrected probe completed.

The new verifier implements direct 60/90-digit Decimal conversion of saved
binary64 matrices, currents, disturbance and weights; RMS, numerator,
denominator, cancellation condition factors and derivatives; and direct-residual
90-digit KKT/objective/feasibility checks. These are candidate verification,
not a high-precision optimization solve or interval certificate. They have not
run in STEP 38. Existing STEP 34 reports contain earlier high-precision evidence
(precision differences below 1.47e-53, saved ratio errors below 6.32e-16,
KKT maxima below 2.18e-18); those are **historical claims reviewed here**, not
new independently executed STEP 38 measurements.

New controlled scenario/disturbance substitutions, matrix singular-value
recomputation, high-precision solves and one-factor solver/library interventions
remain unexecuted. No measurements are invented for these experiments.

## Implementation and exact validation outcomes

The standard-library verifier rejects duplicate/nonfinite JSON, malformed
binary64 payloads, unsafe paths, empty/incomplete manifests, missing required
artifact names, incorrect run/source identities, source Git-blob hashes,
sealed-input and complete-problem fingerprint inconsistencies. It checks every
available replay cell and preserves per-comparison failures. Missing evidence
is an error separate from numerical disagreement; fresh output directories
are mandatory. Exit 2 denotes incomplete/error evidence and exit 1 retained
scientific disagreement. No path promotes historical production acceptance.
Live metadata retrieval remains a separately retained provenance observation;
the offline verifier does not pretend that replaying downloaded JSON is a new
GitHub authentication.

Tests cover malformed JSON, incomplete and tampered manifests, path escape,
missing files, malformed binary64, unchanged tolerances, analytical ratio/KKT
examples, absent evidence and solver-setting fingerprint changes. Tests were
created but **zero Python tests executed**.

| Attempt | Exact observed outcome |
|---|---|
| Targeted STEP 38 pytest | Exit 103 before interpreter startup |
| Complete pytest regression | Exit 103 before interpreter startup |
| compileall src scripts tests | Exit 103 before interpreter startup |
| Analytical CLI validation | Exit 103 before interpreter startup |
| Fresh quick experiment | Exit 103 before interpreter startup |
| Quick output checks | Exit 103 before interpreter startup |
| Independent quick audit | Exit 103 before interpreter startup |
| Independent field-reference tests | Exit 103 before interpreter startup |
| Phase 2C complete production repeat verifier | Exit 103 before interpreter startup |
| New STEP 38 verifier | Exit 103 before interpreter startup |
| Download/historical SHA256 checks | 3,599/3,599 match |
| Exact manifest checks | 54/58; four incomplete, zero listed-member mismatches |
| STEP 33 Git source hashes | 824/824 match |
| Reciprocal input seals/source maps | 32/32 match |
| Decoded fixed-current field components | 192/192 nonself pass; zero numerical difference |
| Git fsck --full --no-reflogs | Exit 0 |
| Git diff --check; staged diff; .venv ignore | Pass; empty index diff; .venv ignored |

`D/attempts.json` preserves executable, full argument arrays and exit codes;
individual `attempt-*.log` files preserve startup errors. The .venv launcher
cannot find its configured Python311 base interpreter. No alternate interpreter,
environment recreation or dependency change was used. PowerShell 7's app alias
also failed to start; Windows PowerShell command mode supplied the executed
forensic checks. Its saved diagnostic script and source hashes allow review.
`D/final-preservation-summary.json` independently rechecks all 3,599 original
hash records after analysis: zero mismatches. `final-preservation.json` retains
each result. No historical comparison was overwritten.

README scripts with fixed historical output paths were not run over existing
results. Baseline README full reproducibility remains blocked in addition to
the explicitly attempted fresh Phase 2C full repeat. Compilation and unit tests,
even if they later pass, cannot change the scientific verdict by themselves.

## Reproduction and next experiment

After restoring the existing Python 3.11 installation externally, from this
checkout, choose a fresh output directory:

```powershell
$py = '.\.venv\Scripts\python.exe'
$out = 'results/phase2d/step38-repeat-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
& $py -m pytest -q tests/test_phase2d_step38_verify.py
& $py -m pytest -q
& $py -m compileall -q src scripts tests
& $py scripts/phase2d_step38_verify.py --evidence results/phase2d/step38-independent-verification-20261101-084216-7bda80b7 --output "$out/verification"
& $py -m stellarator_robust.cli validate
& $py -m stellarator_robust.cli run --config configs/quick.json --output "$out/quick"
& $py scripts/check_outputs.py "$out/quick"
& $py scripts/audit_quick.py "$out/quick"
& $py scripts/phase2c_verify.py --output "$out/production"
git diff --check
git fsck --full --no-reflogs
```

The verifier is expected to reject the four incomplete historical manifests;
preserve that result. Do not remove files or rewrite manifests to obtain a pass.
For README fixed-path test_and_record.py and reproduce_check.py, use a fresh
source-only isolated diagnostic copy inside this research checkout, bound to
the same source hashes, and never overwrite historical outputs. All required
gates need actual result-SHA-bound passing records before checkpoint verification.

Next scientific experiment: obtain and independently hash original archive bytes
against live artifact digests; resolve the run-list/workflow identity gap; run
the new verifier and focused/full tests in the existing Python environment.
Then replay one fixed serialized M/y/support/config on controlled workers with
matched interpreter, hardware dispatch and BLAS builds. Vary one factor at a
time; preserve solver initialization/termination, currents, KKT, fixed-current
fields, high-precision field-to-R evaluation and controlled disturbance/scenario
substitutions. Compare every row under the original thresholds.

The 1e-4 refinement gate and 512-segment quick geometry remain unchanged. These
finite-scenario minimax and small holdout studies establish neither general
robust outperformance nor continuum peak, confinement or device validation.
Historical numerical discrepancies and incomplete milestones remain unresolved.
