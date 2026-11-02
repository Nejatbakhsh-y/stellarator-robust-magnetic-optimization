# STEP47 independent scientific evidence assessment

2026-11-02. **Scientific comparisons FAIL; production acceptance FAIL; overall
scientific status INCOMPLETE; unique numerical root cause INCONCLUSIVE.** This
assessment closes the available local inventory review, not scientific
acceptance. Fresh independent numerical execution and software validation could
not start. No verified research checkpoint is claimed.

Requested source: `4177d52f1ac68f869147c2e3e02e1f8b876546d0`; local HEAD matches
exactly. Work remains on feature branch `codex/phase2d-upstream-attribution`.
Applicable checkout instructions were read from `AGENTS.md`; Git lists no other
tracked AGENTS.md. No production source, configuration, original result,
historical classification, numerical gate or solver setting was edited. No
staging, commit, push, merge, GitHub CLI configuration inspection or PR #7 action
was performed. The three deliverables remain unstaged new files as requested.

All generated evidence is beneath
`results/phase2d/step47-20261102-100432-7e05bcf1/independent/`, which Git confirms
is ignored. These JSON records were generated with PowerShell and .NET, without
substituting a Python environment. The new Python diagnostic was attempted but
did not execute. Its absence is not a passing numerical result.

## Original acceptance requirements

The comparison limits remain `rtol=1e-11`, `atol=1e-13`; refinement remains
`1e-4`; the recovery denominator guard remains `1e-15 T`. The production quick
geometry remains 512 segments. The original failed 256-segment refinement audit
and its diagnosis are preserved. Physical current bounds remain +/-3000 A.
The fixed-support objective is the original weighted ridge least squares,
with normalized box bounds [-1,1]. Solver settings remain `lsq_linear`,
`method='trf'`, `lsq_solver='exact'`, `tol=1e-12`, `max_iter=1000`.
No diagnostic solver replaces production optimization.

Software test success, field agreement at finite probes, approximate KKT
stationarity and successful workflow subjobs cannot substitute for the original
scientific comparisons or full reproducibility requirements. Finite-scenario
minimax and a 24-scenario holdout do not establish general robust outperformance,
physical-model accuracy or plasma confinement.

## Evidence authentication and scope

The four supplied run records all identify attempt 1, requested head `4177d52...`,
and workflow conclusion failure:

| Experiment | Run | Listed artifacts | Downloaded artifact directories |
|---|---:|---:|---:|
| STEP32 | 41465448215 | 17 | 17 |
| STEP33 | 41465448226 | 17 | 17 |
| STEP45 | 41465448239 | 17 | 12 |
| Upstream attribution | 41465460206 | 20 | 20 |

The lists contain 71 entries in total. Listed count equalling downloaded count
does not authenticate an archive or establish completeness of its contents.
`original-archive-authentication.json` retains each artifact ID and metadata
digest separately from extracted-directory availability. There are **zero
original ZIP files** under the supplied evidence directory. Original ZIP-byte
authentication therefore remains missing for every listed artifact. Neither
GitHub metadata, a recorded download status nor extracted-file hashes prove the
original ZIP SHA256. No network re-download or origin attestation was performed.

`extracted-manifest-checks.json` independently verifies **984 of 984** available
manifest file references against SHA256 of actual extracted bytes; none fails.
These include inputs, environments, saved results and comparison records.
Separately, all **28 STEP45 output-manifest references** match their extracted
bytes (`output-manifest-checks.json`), for 1012 passing manifest references in
total. These are references, not necessarily unique files.
All eight additional production quick/study result seals in supplied
`integrity.json` records match (`production-result-seal-checks.json`).
`input-seal-checks.json` verifies all **14 adjacent original inputs.json seals**;
all match. Comparison-bundle input inventories also reference capture manifests
that are absent at those relative locations; these inventories are not extra
captured solver inputs and were not rebound to another directory. An initial
PowerShell inventory attempt encountered these missing relative targets; its
corrected adjacent-input check is the final input-seal record. This is missing
coverage, not demonstrated file corruption.

`historical-before.json` fingerprints all **1114** original supplied files.
`historical-preservation.json` verifies their hashes remain unchanged. Existing
tracked files and the Git index also remain unchanged. Historical failure logs
are retained byte for byte.

The following comparison files are bound to actual extracted bytes:

| Record | SHA256 |
|---|---|
| STEP32 comparison/assessment.json | `f0cdf5cd88edadf7b7f31f70de5d51cc64fd009ce676e9b4ea309515382bc472` |
| STEP33 comparison/assessment.json | `7fac12239907eb037c4bf56671fde4e9d9069c9c67973ee3fce93e636ddbdacd` |
| STEP45 step45-comparison/recovery-comparisons.json | `fce88063502fa2f1f12ed9af733a50642d242149b42cb08cc9eaa9ea92ae24e7` |
| Upstream step42-comparison/comparison.json | `6ed7dadeb0913b5f7c689be8662e77ccdbf5d327cbe07415d0f21b0e73df7144` |

The STEP45 comparison directory uses `output-manifest.json` with an `outputs`
map, rather than a plain `manifest.json`. Its recovery result SHA above matches
that original extracted output seal. This verifies extracted bytes against the
supplied seal, while original archive authentication remains incomplete. Every
original file's local fingerprint is available in the preservation inventory.

Five STEP45 artifact directories are absent: Windows and NumPy-sensitivity
captures, Linux-reference diagnostics, and Linux-reference and SciPy-sensitivity
capture dependency records. `download-status.txt` says
`UNAVAILABLE_OR_INCOMPLETE`. Missing extracted evidence is not proof that a
hosted job never produced it.

## Source and environment identity

Twenty source-sha256 records identify the requested commit. Their 131 distinct
source-file hashes match the exact Git blob bytes at that commit. This check
uses binary process output, avoiding shell newline conversion. See
`source-git-blob-checks.json`, `source-map-identities.json` and
`source-assessment.json`.

Four **upstream STEP42 captures** instead record source commit
`8d87244eb07b7ff6e811596728441aee8b2fd618`. Its Git commit object is unavailable
locally (`git cat-file -e` fails). Thus the upstream run's requested head does
not authenticate every nested numerical capture as requested-source evidence.
These four captures retain their older identity; they are not relabelled or
discarded. In `source-git-blob-checks-all-identities.json`, 131 requested-source
probes succeed and 131 older-source probes cannot authenticate. Empty stdout
SHA256 in failed Git probes identifies an unsuccessful command's empty output,
not a historical source-file digest or proof of corrupted evidence. Overall
source authentication is incomplete, despite verified requested-source blobs.

The provenance gap extends beyond those four captures: **all 27 environment
records supplied under the upstream run directory** identify `8d87244...`.
This includes the upstream seal, workers, STEP42 workers and comparisons;
production execution records also identify that older source. The other 52
environment records identify `4177d52...`. The upstream run metadata and its
extracted numerical artifacts therefore have different source identities.
The origin of that association is unresolved without authenticated original
archives; it must not be called a numerical implementation defect or accepted
as a current-source experiment merely because the run metadata has that head.

`environment-inventory.json` retains 79 supplied environment records, including
nested historical records. Their NumPy/SciPy version pairs are 2.4.6/1.17.1
(45 records), 2.3.5/1.17.1 (17), and 2.4.6/1.16.3 (17). These are repeated
artifact records, not 79 independent machines. Captured current Linux Python
reports 3.11.17; historical Windows records include 3.11.9. Versions must remain
attached to each record's source and path, rather than assigning one Python or
BLAS version to the whole investigation. Loaded threadpool and numerical build
records are available in original environments. They are recorded measurements,
not new independent loaded-library checks on this host. OS and package cohorts
also change bundled kernels; they do not uniquely isolate SciPy, NumPy, BLAS,
CPU dispatch, FMA or a LAPACK driver.

## Scientific comparisons, with the fault rows separated

The following counts were independently extracted from supplied result records;
the numerical values themselves have **not** been freshly recomputed here.
`reported-comparison-summary.json` binds STEP32/33 counts to result-file hashes.

| Supplied comparison | Row3 ratio failures | Row4 ratio failures | Current comparisons failing | Field comparisons failing |
|---|---:|---:|---:|---:|
| STEP32 | 12 | 12 | 0 / 36 | 0 / 96 |
| STEP33 | 10 | 1 | 0 / 36 | 0 / 96 |
| STEP45 reciprocal recovery records | 40 / 64 | 28 / 64 | Not newly recomputed | Not newly recomputed |
| Upstream STEP42 comparison | 12 / 16 | 0 / 16 | 0 / 48 | Not newly recomputed |

STEP32/33 have 12 ordered nonself cohort comparisons, each with three current
vectors and eight field arrays. Passing tolerance does not imply identical
bits. The upstream STEP42 comparisons use older-source captures and cannot
replace requested-source acceptance. STEP45 deliberately retains historical
FAIL even when diagnostics complete; exit 1 alone is not a new solver defect.
Its sealed coordinator status says diagnostic COMPLETE, root cause INCONCLUSIVE,
evidence authentication INCOMPLETE and production FAIL. That supplied status is
not a claim that this new STEP47 implementation executed successfully.

Row3 means active fault row 3, failed coil index 3; row4 means active fault row 4,
failed coil index 6. These identities must be independently rechecked against
the captured active list, not confused with the same coil index in both cases.
In representative STEP45 Windows-origin/Linux-reference records:

| Quantity | Row3 | Row4 |
|---|---:|---:|
| Saved high-precision reference ratio (rounded here) | -0.414688997029067 | 0.167266248499725 |
| Denominator L-B, T | 5.46648534046e-11 | 5.22068671047e-10 |
| Denominator cancellation factor | 948121.1885 | 99276.9267 |
| Recorded current-only contribution to delta R | -4.33043911186e-11 | -5.08002800545e-12 |
| Recorded matrix/disturbance/weight contributions | 0 / 0 / 0 | 0 / 0 / 0 |

Both denominators exceed the unchanged guard. Row3's negative recovery is not
a recovery benefit. The guard prevents nearly zero absolute denominators; it
does not certify quotient conditioning. For R=(L-P)/(L-B), the exact gradient
in B,L,P order is `[(L-P)/(L-B)^2, (P-B)/(L-B)^2, -1/(L-B)]`.
Cancellation can amplify small current or field differences beyond the ratio
gate even when the current gate passes. This analytic pathway does not establish
a unique implementation defect. The supplied STEP45 records explicitly say
field products, reductions, roots and quotient were evaluated together; their
aggregate binary64 contribution is not an isolated reduction-order experiment.

The previously documented STEP44 one-ULP derived-record serialization issue and
superseded STEP39 derivative-sign diagnostic are historical diagnostic issues,
not new production Biot-Savart defects established by STEP47. Genuinely failing
scientific comparisons remain FAIL; no values or thresholds were changed to
obtain agreement. No unique new numerical implementation defect is demonstrated.

## Independent implementation and blocked execution

`scripts/phase2d_step47_evidence.py` supplies strict JSON/digest/path validation,
Git blob checks, binary64 decoding and exact reconstruction of
`M=[sqrt(w) D_support; sqrt(ridge) I]`,
`y=[-sqrt(w) d; 0]`. It checks original scaling, configuration, fault identities,
supports, bounds and solver arguments before numerical execution. It repeats
the original TRF solve without using saved vectors as initialization.

Independent arithmetic explicitly reuses STEP46's scalar Decimal Householder
QR at 60/90 digits, direct residual/gradient, box KKT and projected-gradient
certificate, physical-current field products and recovery sensitivities. It
adds an independent scalar finite-segment Biot-Savart integral with original
wire clearance, testing all 25 polygons at two points on each of the training
and fine grids. These geometry probes are sampled validation, not a full-grid
certificate. QR outside the box or rank deficient is not a bounded reference;
precision convergence is empirical rather than a rigorous interval bound.

Cross-capture controls compare current vectors, exact M/y identity, current-only
changes with fixed A/b/w, and matrix changes at fixed currents. Different
generated matrices are explicitly distinguished from identical-input solves.
Original saved-result quotient binding is explicitly incomplete; a new quotient
never replaces a saved failing result. Box KKT quality certifies only the
captured fixed-support problem, not the broader minimax optimization or a bound
on recovery-ratio error. Missing ZIP provenance and full acceptance gates keep
the program's exit status 2 and scientific status incomplete even if its local
numerical diagnostics later execute.

Portable tests use deterministic hashes, malicious/missing manifests, strict
JSON fixtures, an analytic square-loop field, a small QR problem, bound KKT,
the exact recovery guard and signed-zero payloads. They require no local
historical archive and cannot manufacture a scientific PASS.

All ten initial execution attempts and nine post-edit repeats in
`validation-attempts.json` returned
**103 before Python startup**, with:

```text
No Python at '"C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe'
```

Attempts included targeted pytest, complete pytest, compilation of src/scripts/
tests, `pip check`, analytical validation, STEP47 `--numerical`, quick experiment,
output checks, independent audit and the full reproducibility script. No tests
were collected, compilation and dependency integrity remain unverified, and no
fresh solver, KKT, field or recovery calculation ran. The existing `.venv` was
preserved and remains ignored. No replacement interpreter was used.
Git whitespace checks succeed, but do not establish Python correctness.

After the existing environment works, execute into a fresh ignored child:

```powershell
.\.venv\Scripts\python.exe scripts/phase2d_step47_evidence.py --numerical --output results/phase2d/step47-20261102-100432-7e05bcf1/python-fresh
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step47_evidence.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts tests
.\.venv\Scripts\python.exe -m pip check
```

## Final status fields

| Field | Assessment |
|---|---|
| diagnostic_status | INCOMPLETE: inventory review executed; independent numerical runtime blocked |
| source_authentication | INCOMPLETE: requested-source blobs verified; four older captures unbound to available Git object |
| artifact_authentication | INCOMPLETE: 1012 extracted manifest references and 14 adjacent input seals match; original ZIPs absent; STEP45 coverage missing |
| solver_reproducibility | INCOMPLETE: supplied small current differences/quality records do not replace new independent solves |
| field_validation | INCOMPLETE: supplied comparisons pass; new independent geometry calculation did not run |
| recovery_ratio_validation | INCOMPLETE: supplied genuine FAILs preserved; fresh high-precision calculations did not run |
| numerical_root_cause | INCONCLUSIVE: conditioning pathway supported; unique numerical defect not established |
| scientific_comparison | FAIL |
| production_acceptance | FAIL |
| overall_scientific_status | INCOMPLETE |
| remaining_blockers | Working required Python 3.11 environment; passing targeted/full tests, compilation and dependency check; original ZIP-byte authentication; missing STEP45 artifacts; exact older-source Git identity; fresh matrix reconstruction, solves, KKT and geometry/recovery checks; original saved-result binding; original comparison failures; final-source README and full-repeat gates; controlled unique-cause attribution |

Missing evidence is explicitly incomplete. The present investigation does not
satisfy every original scientific acceptance requirement and cannot mark
scientific PASS.
