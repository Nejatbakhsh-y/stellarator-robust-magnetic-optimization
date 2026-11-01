# STEP 33 execution protocol

Production FAIL and overall PARTIAL remain independent of diagnostic exit codes.
Use only the existing research checkout and .venv Python 3.11. The current Codex
host cannot start its configured base interpreter; ordinary host repair is
required before executable validation. Do not replace the environment or relax
acceptance gates to obtain a pass.

Run on an ordinary PowerShell 7 host, with a fresh output directory:

```powershell
$evidence = 'results/phase2d/step32-host-20261031-183500-a1965e0d'
$output = 'results/phase2d/step33-host-' + [guid]::NewGuid().ToString('N')
.\scripts\phase2d_step33_host.ps1 -EvidenceRoot $evidence -OutputRoot $output
```

The default does not access GitHub CLI, stage, commit, push or dispatch. It checks
repository/branch identity, Python/dependencies, all regressions, compilation,
analytical validation, complete STEP 32 local integrity, source/solver inputs,
historical evidence, a fresh capture and local controlled replay. The production
verifier runs fresh quick, output checks, independent audit, study, full repeat,
training audit and result-hash links, followed by fault/legacy audits,
investigation and finalization. Native exits and logs are retained. Failed
preflight stops dependent stages; missing stages cannot pass. Files under the
supplied evidence root and all preexisting research files are checked for
preservation; Git diff/index/object checks are retained.

Direct commands, always using fresh, disjoint output paths:

```powershell
.\.venv\Scripts\python.exe scripts/phase2d_step33.py assess --inputs $evidence --output results/phase2d/step33-assessment-fresh
.\.venv\Scripts\python.exe scripts/phase2d_step33.py capture --output results/phase2d/step33-capture-fresh
.\.venv\Scripts\python.exe scripts/phase2d_step33.py local --inputs results/phase2d/step33-capture-fresh --output results/phase2d/step33-local-fresh
```

The diagnostic workflow is `.github/workflows/phase2d-step33-causal.yml`.
Four independent captures and four replay workers (each consuming all four
captures) yield sixteen origin/solver combinations. Cohorts remain Windows
reference (NumPy 2.4.6/SciPy 1.17.1), Linux reference (same versions), Linux NumPy
sensitivity (2.3.5/1.17.1), Linux SciPy sensitivity (2.4.6/1.16.3).
Complete dependency installer records, resolver provenance and worker artifacts
are retained. Comparison requires exact input bytes, fingerprints, expected
commit, source equality, valid numerical records and cohort environments.
Missing artifacts/records are evidence failures, never scientific PASS.

A=Windows input/Windows solver, B=Windows input/Linux solver,
C=Linux input/Windows solver, D=Linux input/Linux solver. Report paired solver
and generation contrasts and interaction, alongside support identity, objective,
KKT, active-set, feasibility and field/ratio differences. Do not attribute a
continuous solver effect across different supports without qualification.
Fixed-current fields compare all components; new independent component/vector
summaries cover only the two established probes per polygon. High precision
does not recover unrecorded intermediate arithmetic.

`assess` checks complete host/capture/local manifests, sealed input, numerical
schema, solver records and residual-based Decimal KKT on saved candidates.
Capture/replay/compare reuse STEP 32 explicitly; this is not a second independent
implementation of the entire experiment. The new independent candidate KKT
calculation uses direct residuals, exact binary64 conversion and bound signs at
60/90 digits. Coordinate and BVLS cross-checks retain the box; normal equations
are not used as the independent constrained certificate. Perturbation probes
retain bounds, regularization and production stopping rules.

Retain recovery numerator/denominator, B/L/P, guard status, 60/90-digit checks,
current/model/weight swaps, support decisions and differential nonlinear
remainder. Preserve every historical failure. Exit 0 means diagnostic execution
completed, exit 1 means completed comparison FAIL, exit 2 means execution or
evidence failure. It never upgrades production acceptance.

Publication is a separate explicit host invocation:

```powershell
$output = 'results/phase2d/step33-publish-' + [guid]::NewGuid().ToString('N')
.\scripts\phase2d_step33_host.ps1 -EvidenceRoot $evidence -OutputRoot $output -PublishDiagnostic
```

Do not execute that command in the Codex implementation stage. The host requires
all local gates, original archive authentication, exact repository/branch and
draft PR #7 remote-head identity. It inventories explicit source/test/report/
workflow paths including uncommitted STEP 31/32 dependencies and the development
dependency declaration. No result trees or historical evidence are staged.
Unrelated staged changes, changed preexisting bytes, missing files or failed
integrity stop publication. Only the current research branch is pushed, without
force; the existing draft PR updates through its branch. No merge, PR #6 edit,
PR creation or workflow dispatch is performed. The host polls the push-triggered
committed workflow, authenticates artifact ZIP digests, requires all workers and
reruns the scientific comparison. Pending/missing output is INCONCLUSIVE;
completed failed numerical comparisons remain FAIL. Production FAIL does not
prevent accurate diagnostic publication, but prevents a production PASS claim.
