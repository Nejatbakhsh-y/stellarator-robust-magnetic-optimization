# Controlled four-cohort continuation

Scientific status: **PARTIAL**. Production cross-platform root cause remains
unresolved. This report supersedes execution instructions for the frozen worker
in the earlier v1 host document; earlier reports and original evidence remain.

## Gate record

| Gate | Status | Evidence / limitation |
|---|---|---|
| Checkout preflight | PASS | Requested origin and existing branch; HEAD `5a415c457e9f60c983a52d309a242583d73b40b6`; dirty checkout recorded before edits |
| Original Windows manifest and source attribution | PASS | All six `windows/sources.json` hashes matched the pre-edit checkout; two diagnostic sources subsequently edited and their original bytes retained |
| Frozen input preservation | PASS | Both base and sealed fixture manifests verified using host PowerShell SHA-256; sealed inputs copied without reserialization |
| Historical preservation | PASS | All 247 original files locally present and match inventory hashes and lengths; original Phase 2C failures retained |
| New tests / full pytest / compilation | PENDING | Prescribed `.venv` launcher failed before interpreter startup; zero tests executed here |
| Independent new field / bounded checks | PENDING | Added implementation and regressions require actual Python execution |
| Full quick / audit / output / repeat pipeline | PENDING | Fresh execution required; prior evidence cannot verify changed diagnostic sources |
| Four hosted workers / comparison | PENDING | No new runs executed or retrieved; actual Phase 2D workflow URLs unavailable |
| Commit / publication | PENDING | No staging, commit, push or PR action; staged file list empty |

Machine-readable evidence and exact before/after hashes are under
`results/phase2d/controlled-four-cohort-20261031/`. The recorded HEAD is the base
checkout SHA, **not a tested immutable commit**. No commit containing these edits
has been tested. The original Windows experiment explicitly records
`environment.source_dirty=true`; its six source hashes provide narrower source
attribution than a complete clean-tree provenance claim.

## Inputs and controls

The original `benchmarks/phase2d-frozen-v1/` remains unchanged. The already
executed Windows host's `shared-inputs/` is copied byte-for-byte to
`benchmarks/phase2d-sealed-v1/`, retaining the original seal metadata and all M/y.
Its pinned manifest SHA-256 is
`d91d8add4c46ee29e1f954c5ad4bae4c870c2a10e371d0803d13d1829949c683`.
No worker regenerates geometry, probes, nine current sets, original solver M/y,
or tolerances. `prepare` checks this pin and packages the existing bytes once.
Calculation files have byte-preserving Git attributes to avoid checkout newline
differences across operating systems.

The preparation job creates a source contract and freezes a **separate**
single-actuator diagnostic M/y. It projects the existing dense augmented system
onto actuator 0 and scales the disturbance by a recorded exact power of two,
large enough to require the original +/-3000 A bound. Ridge and solver settings
remain unchanged. The solution has an analytical one-dimensional clipped
least-squares reference. This stress case does not replace any original frozen
solve or historical physical objective. Workers must show success, positive
bounded iterations, an active bound, and agreement with that reference under
the original gates. This case is implemented but **unexecuted** here.

The preparation job publishes the execution-contract SHA-256 as a job output;
every worker verifies it, the fixture pin and all six calculation-source hashes
before calculating. Actual Python, platform, NumPy and SciPy are checked by the
runner. The matrix is Windows/Linux reference (NumPy 2.4.6, SciPy 1.17.1), Linux
NumPy sensitivity (2.3.5, 1.17.1), and Linux SciPy sensitivity (2.4.6, 1.16.3),
all Python 3.11. These are configured versions, not observed hosted versions.

Records retain raw Cartesian components, pointwise totals, reference errors,
parsed binary64 input hashes, native training geometry/M/y, least-squares
initialization, singular values, currents, objectives and verbose bounded
iteration tables. The comparison keeps every differing leaf, including
within-tolerance differences, and fails on incomplete evidence, source/input
mismatch, wrong cohort pairs or differing checkout SHAs. Missing comparison
evidence produces a machine-readable FAIL record. Solver internal per-iterate
vectors are unavailable from the public API; verbose tables are the trajectory
evidence, not a claim to have captured every internal vector.

## Baseline and unresolved attribution

The existing local Windows record is `FIXED_INPUT_SUBBENCHMARK_PASS` with
scientific status PARTIAL. Its three saved solves have `nit=0`: each accepts
unconstrained initialization. They do not validate bounded optimizer dynamics.
The independently audited ZIP findings supplied by the user (600 unit-component
and 432 total-component checks; reference errors up to 1.513e-21 T and
4.984e-19 T; NumPy solution differences around 3e-16) are baseline evidence,
not independent recalculations performed in this continuation.

The named `Phase2D_Windows_Scientific_Evidence.zip` was not found in this
checkout. Its exact archive bytes, ZIP provenance and membership were therefore
not reverified here. Its local 18-file host tree is available. All six declared
Windows calculation sources were available at preflight; none is missing.
A complete immutable snapshot of every file in the dirty Windows source tree
and original installed dependency source trees is not supplied by those six
hashes. Original internal bounded iteration vectors are absent (the original
solves had no bounded iterations). No hosted Phase 2D worker sources, logs or
results are available to compare yet.

Raw field drift, native regenerated-training drift, least-squares arithmetic,
and bounded dynamics remain separate attribution questions. The original fault
3/4 ratio failures and negative small-holdout robustness conclusions stand.
Neither a fixed-input PASS nor a one-actuator stress diagnostic overrides an
independently failing full-production comparison. Refinement remains 1e-4;
finite-scenario minimax is not a general robustness or confinement certificate.

## Ordinary Windows PowerShell handoff

Run from the existing host environment without changing execution policy or
installing another interpreter:

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
& .\scripts\phase2d_controlled_host.ps1
```

The script uses only `.venv`, fresh output paths, captured exit codes and logs,
strict worker manifests, original Windows evidence verification, new reference
checks and the full production quick/study repeat pipeline. It stops at a
failed step and preserves evidence. Inspect every result before publication.
The earlier archive-investigation command remains available in
`PHASE2D_FROZEN_V1_HOST_COMMANDS.md`; its documented exit 1 is not a science PASS.

GitHub CLI configuration is prohibited in this session by AGENTS.md. Hosted
execution requires external publication after host checks and code review.
From ordinary authenticated PowerShell, review `git diff`, all untracked files,
the complete prospective staged list and preservation records first. Stage only
explicit reviewed paths; never `.venv`, downloaded ZIPs or historical evidence.
After an approved local commit, normal commands are:

```powershell
git diff --cached --name-status
git diff --cached --check
git commit -m 'Add controlled frozen-input validation diagnostics'
git push -u origin codex/phase2d-cross-platform-reproducibility
gh pr list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --head codex/phase2d-cross-platform-reproducibility
# Only if no Phase 2D PR exists:
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/phase2c-stable-fault-metrics --head codex/phase2d-cross-platform-reproducibility --draft --title 'Controlled Phase 2D frozen-input diagnostics (PARTIAL)' --body-file docs/PHASE2D_CONTROLLED_FOUR_COHORT.md
gh workflow run phase2d-frozen-inputs.yml --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --ref codex/phase2d-cross-platform-reproducibility
gh run list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --workflow phase2d-frozen-inputs.yml --branch codex/phase2d-cross-platform-reproducibility
# Set this to the actual newly dispatched run ID, then inspect/download it:
gh run view $runId --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --log
gh run download $runId --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --dir "results/ci/hosted-$runId"
```

Manual dispatch may require the workflow to exist on the remote default branch;
the configured Phase 2C-targeted PR trigger is the alternative. Do not merge to
enable dispatch. Record the actual tested checkout SHA and run URL from the
observed jobs, and inspect all four artifacts plus comparisons before updating
any status. No workflow YAML or old Windows result constitutes hosted success.
