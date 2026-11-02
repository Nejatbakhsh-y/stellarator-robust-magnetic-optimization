# STEP 45 final numerical root-cause investigation

Date: 2026-11-02. **Implementation prepared; numerical execution INCOMPLETE.**
Scientific comparison **FAIL**; causal root cause **INCONCLUSIVE**; original
archive authentication **INCOMPLETE**; production acceptance **FAIL**; overall
scientific status **PARTIAL**. This is not a verified research checkpoint.

## Source commit and execution environment

Baseline and starting HEAD: `3025749c1107acf8989231c91a4ed291d4cc81be`.
Branch: `codex/phase2d-upstream-attribution`. Four new deliverables are local and
uncommitted. No production source, old workflow, tolerance, historical result or
reference solution was changed. Nothing was staged, committed, pushed, merged,
force-pushed or dispatched. GitHub CLI configuration was not inspected.

AGENTS.md, README, execution status, STEP39/40/41/42/44 reports, the earlier
diagnostic and replay implementations and regression contracts, production
`optimize.py`, field/recovery/capture code, and current scientific workflows were
reviewed. Existing STEP40 QR and STEP42 capture/replay work is reused explicitly;
it is not represented as a newly invented independent arithmetic implementation.

The existing `.venv/Scripts/python.exe` cannot start in this restricted Windows
process. Its message identifies the configured Python311 base executable as
unavailable. Earlier STEP42 documentation records an access denial. This does
not establish that the external controlling host's Python installation is broken.
The environment was neither replaced nor reconfigured. Python/NumPy/SciPy and
loaded BLAS versions cannot be freshly observed here. No Python test pass,
compilation success, new SciPy solution or executed Decimal reference is claimed.

Fresh session records are under
`results/phase2d/step45-20261102-044425-eb1b392a/session-validation/`.
The PowerShell integrity check executed: **3,599 retained inventory entries,
zero SHA256 mismatches**. This is extracted/local byte integrity, not archive
authentication or a rerun of the strict Python semantic validators.

## Original evidence inventory and authentication

The authoritative local evidence root remains
`results/phase2d/step38-independent-verification-20261101-084216-7bda80b7/`.
The retained STEP38 inventory reports 46 extracted artifacts; earlier reports
identify four incomplete early manifests and a workflow-identity gap for
41256776296. Fresh connected GitHub metadata resolves the workflow identity
below; it does not repair the incomplete early manifests or authenticate ZIPs.

| Historical run | Retained source commit |
|---|---|
| 41195815229 | ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7 |
| 41231422708 | 11c2b1347c7b5359bec0a56e95cc2aa46f03660c |
| 41256776296 | cf77cf5466beadec7bd273e5c72ce9732cf253a7 |
| 41257645149 | 1cd635c5fc8a0b4bc5ee70e13b7298cdb66318f9 |

Fresh connected GitHub GETs confirm all four run IDs, HEAD commits and completed
failure conclusions. Workflow identities are respectively 402677493
(`phase2d-cross-platform-reproducibility.yml`), 402952506
(`phase2d-upstream-attribution.yml`), and 403150023 for both later runs
(`phase2d-step33-causal.yml`). This closes the previously unresolved metadata
workflow identity of 41256776296 without rewriting its historical assessment.
The response summaries, 46 artifact metadata records (5/7/17/17), job/step
summaries and four decoded comparison-job logs are saved separately in the
session evidence directory. Artifact metadata is a first-page response, checked
against the retained local identities, not a byte download.

The connector returned an original-download file reference for artifact
13063239980. Downloading those bytes into the checkout failed with
`System.Net.WebException`, exit 2. No ZIP hash or extracted-original authentication
was therefore obtained; the other original ZIP byte retrievals were not completed.
Metadata reports `expired=false`; unavailable to this process does not mean
expired or absent on GitHub. Original archive-byte authentication remains
**MISSING_EVIDENCE**. Extracted-file hashes cannot resolve this gap. The fresh
`source-only-baseline.zip` is explicitly a reconstructed `git archive HEAD`
software-validation input, never an original GitHub artifact.

## Failure classification and existing verified work

- **A — implementation/infrastructure:** STEP44 established a derived
  PowerShell Decimal-to-Double serialization defect and ignored-file-dependent
  software fixtures. The committed portable fixture repair is separate from
  numerical acceptance. The user reports STEP44 hosted runs 41371734831 and
  41371741200 successful; they were not independently re-observed here.
- **B — numerical reproducibility:** retained exact-input reciprocal comparisons
  have recovery ratios outside the original tolerance. Tiny current differences,
  fixed-current field agreement, and small KKT residuals do not remove these
  failures. A particular OS, library or instruction is not proven responsible.
- **C — scientific acceptance:** production acceptance remains FAIL because
  required numerical/provenance gates remain unmet. No physical-model acceptance
  or confinement validation follows from these reduced-order calculations.

This does not classify every failed STEP32/33 workflow job as A. A run may contain
multiple failure classes; missing logs/provenance remain unresolved. Repairing a
software fixture cannot reclassify the retained numerical comparisons.

Fresh historical comparison-job logs confirm unchanged scientific-comparison
exits, rather than package/setup failures: run 41195815229 records four
scientific differences per failed reference/SciPy contrast; run 41231422708
records failed upstream/production comparisons; both later STEP33 runs have
successful capture/replay jobs and a comparison step exiting 1. These fresh
remote observations support classification B for the recorded cross-environment
comparison failures, with C acceptance consequences. They do not establish a
specific upstream numerical cause. The requested STEP32-specific historical run
identity is not among these four (the later two are STEP33); its separate earlier
implementation/workflow failures remain governed by their retained diagnoses.

The exact STEP44 one-ULP adapter defect is already documented and repaired:
original `-0.41468899707880597` versus derived `-0.414688997078806` in the latest
Windows-origin/Linux-reference row3 candidate. That cell itself passed the
scientific tolerance. Its repair does not explain the eleven failed comparisons.
No additional production numerical defect was independently demonstrated here.

## Mathematical invariants and input identity verification

The objective is `0.5*||Mx-y||^2` with bounds `-1 <= x <= 1`:

```
M = [diag(sqrt(w))*D_S; sqrt(1e-6)*Identity]
y = [-diag(sqrt(w))*d; 0]
I = 3000*x A
```

TRF, exact least-squares dispatch, tol=1e-12, max_iter=1000, physical bounds
±3000 A, ridge=1e-6, rtol=1e-11, atol=1e-13, refinement=1e-4,
recovery guard=1e-15 T and 512 quick segments are unchanged. No rounded
currents, ratio quantization, model substitution or modified reference is used.

The new driver calls STEP42 `load_capture`: original input-file SHA256 and
canonical problem seal, Git source maps, complete configuration/support checks,
matrix reconstruction and exact M/y equality precede solving **saved binary64
M/y**. The solver records retain normalized and physical current bytes, M/y
hashes, objectives, certificates, termination, support and conditioning. A new
first-differing saved/fresh normalized-current coordinate is recorded by bits;
this identifies an observable output divergence, not the internal instruction
where rounding first differs. Existing tolerant D/d reconstruction is not
misrepresented as a new bytewise reconstruction proof.

## Four-environment comparison and hosted experiment status

The new workflow has the exact name
`Phase 2D STEP 45 independent causal validation`, runs on pushes to the specified
feature branch, and uses Python 3.11 in all required environments:

| Cohort | OS | NumPy | SciPy | Fresh execution here |
|---|---|---|---|---|
| windows-reference | Windows | 2.4.6 | 1.17.1 | NOT EXECUTED |
| linux-reference | Linux | 2.4.6 | 1.17.1 | NOT EXECUTED |
| linux-numpy-sensitivity | Linux | 2.3.5 | 1.17.1 | NOT EXECUTED |
| linux-scipy-sensitivity | Linux | 2.4.6 | 1.16.3 | NOT EXECUTED |

Four captures feed four workers using existing STEP33 capture and STEP42 replay.
Capture/worker directory normalization preserves cohort identity. All artifacts
are restricted to the current run and attempt; names include both identities.
The comparison additionally verifies complete worker manifests, Python version,
HEAD, current source fingerprints, input identities, thread counts and inherited
solver certificates before accepting any fresh comparison record. It requires
the actual captures again for controlled current swaps. All directed recovery
contrasts include Windows→Windows, Windows→Linux, Linux→Windows, Linux→Linux
and direct sensitivity-cohort contrasts. No missing cohort is replaced by data
from the comparator host. SHA equality is required, not approximate input equality.

Artifacts upload with `if: always()`. Scientific exits remain nonzero, with no
`continue-on-error` or shell success conversion. Consequently even a completed
fresh diagnostic comparison cannot turn the retained production FAIL into a
green scientific acceptance job. This workflow has not been dispatched here.

## Independent high-precision solver reference and numerical kernel attribution

The new driver reuses STEP40 twice-orthogonalized scalar Decimal QR at 60 and
90 significant digits, avoiding normal equations. It records independent
gradient/objective checks, interior-bound margin, and rank/conditioning. Boundary
or rank-limited QR is NOT_CERTIFIED, never asserted as a bounded reference.
Full rank with an interior optimum justifies uniqueness for the captured
fixed-support least-squares problem; it does not establish binary64 identity.

Same-M/y SciPy LAPACK `gelsd`, `gelss`, and `gelsy` controls retain binary64
vectors, returned rank/spectra, independent 90-digit projected KKT certificates,
and error against Decimal QR. They are diagnostic SVD/QR controls, not substituted
production optimizers. NumPy `lstsq(rcond=-1)` bytes and actual SciPy solver-source
dispatch lines/source digest are recorded instead of assuming dispatch from a
library name. NumPy/SciPy configuration and loaded threadpool provenance are
inherited from STEP42 environment recording under one-thread limits.

These controls are **prepared, not executed**. They do not establish attribution
to array allocation, SVD, QR, BLAS, reduction order, FMA, CPU dispatch, thread count,
or OS. No disassembly, instrumented kernel trace, CPU-feature intervention,
alternate BLAS rebuild or isolated FMA intervention was performed. Pinning one
thread is a control, not proof that thread count caused an old discrepancy.
Version cohorts jointly change bundled dependencies; their differences cannot
alone identify one internal numerical kernel.

## Fault row 3 analysis

Zero-based failed coil 3 is checked separately. Retained STEP40 independent
fine-grid evaluation at saved currents gives representative
`R=-0.4146889970809171094992892896548706787...`; production saved
`R=-0.41468899708091722`. The negative value is not a recovery benefit.
Rounded saved RMS values give L-B≈5.466485340356966e-11 T and
L-P≈-2.266891323499066e-11 T, with dR/dL≈2.587931566676031e10/T.
The latest inventory has ten row3 failures; the preceding inventory has twelve.
These are **retained prior measurements**, not fresh STEP45 recomputations.
The new driver separately retains original/fresh currents, independent references,
field-derived RMS/recovery, guard evaluation, current swaps and nonlinear remainder.

## Fault row 4 analysis

Zero-based failed coil 6 is independently checked. The analogous retained
high-precision ratio is `0.1672662484975028316716501674920593179...`;
saved production `0.16726624849750296`. Rounded RMS gives
L-B≈5.220686710494032e-10 T, L-P≈8.732446806741898e-11 T and
dR/dL≈1.595065549179688e9/T. One latest and nine preceding comparisons fail.
The denominator is above the original guard, as for row3. A row3 diagnosis is
not a row4 resolution; all driver controls run independently for both faults.

## Recovery-ratio sensitivity and intervention interpretation

For N=L-P and G=L-B, quotient differentiation yields

```
dR = [G*(dL-dP)-N*(dL-dB)]/G^2
   = [(P-B)*dL-(L-B)*dP+(L-P)*dB]/(L-B)^2
```

In B,L,P order the gradient is `[N/G^2,(P-B)/G^2,-1/G]`.
At (1,3,2) it is exactly `[1/4,1/4,-1/2]`. Existing independent rational
derivative tests and fresh portable tests retain the correct sign and guard.

For each same-capture comparison, independent 90-digit field/RMS evaluation
changes currents alone and separately swaps dense/recovered vectors. A,b,w
contributions are exactly zero **only within those identical-input controls**.
The code retains the exact current-intervention delta, aggregate binary64
field/RMS/quotient-evaluation delta and closure remainder. Pure reduction-order
contribution is explicitly NOT_ISOLATED: matrix products, summations, roots and
quotient arithmetic change together. Claiming a reduction-only cause would
exceed this control. The derivative prediction and nonlinear remainder form a
separate first-order decomposition; the nonlinear remainder is not double-counted
as another addition to the already exact current-intervention effect.

Historical ratio failures persisting at high precision distinguish solver-current
effects from mere final ratio rounding. Successful downstream decomposition
does not identify the unique upstream operation producing those currents.

## Independent field validation and historical failure preservation

Prior STEP39/40 fixed-current field and independent segment-integral checks are
retained. They are not rerun here; no new field-validation pass is claimed. The
original 256-segment failed audit remains untouched. STEP45 changes no equations,
geometry, scenarios, objectives, SLSQP/minimax behavior or magnetic-field code.

Eleven latest, 21 preceding and 22 earlier scalar-path failures remain separate
inventories. The driver uses STEP44's pinned source-bound correction adapter and
strict retained classification binding; arbitrary scalar/hash changes are errors.
Existing corrected decimal serialization is never applied to original evidence.
Pre/post snapshots detect source evidence changes during an assessment. Session
PowerShell checks compare the original retained SHA inventories independently.

## Regression results and permanent verification procedure

New portable tests cover QR/SVD driver checks, exact binary64 transport,
independent KKT, both faults, one-ULP current changes, derivative/guard/tolerance
boundaries, isolated outputs, changed history bytes, corrupt manifests,
missing cohorts, inconsistent Python/source provenance and false acceptance.
Existing STEP32/33/39/40/41/42/44 tests retain detailed matrix/support/settings,
historical binding and adversarial coverage. Synthetic portable tests never
authenticate historical originals. Passing pytest alone cannot establish science.

Targeted tests, full pytest, compileall, pip check, analytical validation, CLI
investigation and source-only regression/README numerical gates were attempted
using the required existing `.venv`; Python startup blocks them. Inspect
`validation-attempts.json` and individual logs for exact commands/exits. No tests
were collected. A source-only baseline archive plus the STEP45 overlay is a
software portability rehearsal, not proof of an independent clean Git checkout.
Final-source software and numerical validation on the controlling host remains
mandatory. Run the full README sequence in an isolated checkout so its default
output paths cannot replace historical evidence, then verify hash-bound records.

Use a new output directory on each host execution:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_step45_rootcause.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts tests
.\.venv\Scripts\python.exe -m pip check
$out = Join-Path $PWD ('results/phase2d/step45-host-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe scripts/phase2d_step45_rootcause.py --root $PWD --output $out
$scientificExit = $LASTEXITCODE
Get-Content (Join-Path $out 'status.json')
git diff --check
```

CLI exit 2 means incomplete/invalid execution or evidence; exit 1 means completed
diagnostics with retained scientific FAIL/PARTIAL. There is no acceptance bypass.
Outputs include the seven requested records plus one justified noncircular
output manifest sealing all other records and diagnostic source fingerprints.
Input manifests seal bytes actually observed and cannot authenticate their origin.

## Final verdict and remaining scientific blockers

No new uniquely justified production correction exists on this session's evidence.
Diagnostic status INCOMPLETE; scientific comparison FAIL; causal root cause
INCONCLUSIVE; evidence authentication INCOMPLETE; production acceptance FAIL;
overall scientific status PARTIAL.

Remaining work requires functioning Python execution, actual fresh four-cohort
hosted evidence, original archive-byte/metadata authentication where available,
resolution of provenance/manifest gaps, finer controlled kernel interventions,
and final-source README/clean-checkout gates bound to fresh result SHA256.
Unavailable originals remain MISSING_EVIDENCE; no software workaround can
authenticate them. Finite-scenario minimax and small holdouts do not establish
robust outperformance, continuum maxima, engineering feasibility or confinement.
