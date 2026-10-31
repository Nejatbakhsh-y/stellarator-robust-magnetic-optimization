# Phase 2D controlled publication review, 2026-10-31

Scientific status: **PARTIAL**. Local execution evidence is verified against
its manifests; hosted Phase 2D Windows, Linux and comparisons are **PENDING**.
This review supersedes earlier execution-status statements in the retained
Phase 2D reports. It does not assert a new scientific calculation in this session.

Repository: `Nejatbakhsh-y/stellarator-robust-magnetic-optimization`.
Branch: `codex/phase2d-cross-platform-reproducibility`.
HEAD: `5a415c457e9f60c983a52d309a242583d73b40b6`.
The complete initial working tree was reviewed; only `.gitattributes` and README
were tracked modifications. Phase 2D implementation, fixtures and records were
untracked. Historical tracked production code, configurations and results have
no diff. `.venv/` remains ignored.

## Verified recorded local execution

`results/ci/phase2d-controlled-20261031-060324/` contains 13 recorded steps,
all exit code zero. Logs show 18 frozen-input tests and 145 complete regression
tests passed. Compilation, analytical validation, frozen preparation/Windows
worker, independent references, production quick/study, output checks,
independent numerical audit, separate quick/study repeat, training audit,
fault audit and final integrity checks passed in those records. The nine
production execution stages also have return code zero.

All 92 files listed by the execution manifest match SHA256. Its digest is
recorded in `results/phase2d/publication-review-20261031/review.json`.
The independently passing quick audit binds to result SHA256
`6371be978f9bb1356a667b19a3edee3c2e8d6a7da1090cc6c9b3dbd75fbfcf48`;
study gate/integrity bind to
`acbfabd96f2b8af249775b3a147226f79e272fffdc2a560d4236e9da9a953e10`.
Repeat comparison is PASS at rtol=1e-11, atol=1e-13.

All six frozen calculation-source raw hashes match the current checkout.
All 68 production fingerprints match using the existing recorder's documented
CRLF-to-LF normalization for Python, configurations and `.gitattributes`.
A preliminary raw-byte check differed on nine such paths; normalization
resolved all nine, without modifying any files or hashes.
The recorded source tree was dirty and the HEAD is a base commit, not an
immutable commit containing these additions. A clean committed hosted run
remains necessary. A fresh `.venv` version check here failed before interpreter
startup; no substitute runtime or permission workaround was used.

## Preservation and source review

Rehashed all 247 original files against original inventory lengths and SHA256;
the tree has exactly those files plus its inventory. All 26 original continuation
snapshot files match their inventory. All 41 controlled-continuation manifest
entries match, including original diagnostic source snapshots. Both fixture
manifests match (11 base and 13 sealed entries). No original evidence was edited.

The latest execution is also preserved in the new `local-execution.zip` beside
`review.json`; all 93 archived files (92 entries plus manifest) were independently
hashed from ZIP streams against the originals. The archive digest is in the
review record. Original 247-file evidence remains at its existing local path;
authenticated ZIP membership/provenance and external durable archival
preservation are still limitations. This new ZIP archives the latest execution,
not the historical 247-file collection.

Reviewed every active Phase 2D source: frozen runner, Decimal diagnostic module,
Python investigation, preserved PowerShell/C# investigation, controlled host
runner, both test modules, and both workflows. The historical PowerShell runner
is investigation-only and does not constitute a fail-closed scientific gate;
use the current Python frozen worker and comparators for acceptance.
Reviewed both tracked diffs and all eight Phase 2D handoff/method reports.
Earlier reports contain superseded blocked/unexecuted statements and obsolete
frozen-run arguments; retain them as history and use the controlled runner.

The frozen workflow has Python 3.11 cohorts Windows/Linux reference
(NumPy 2.4.6, SciPy 1.17.1), Linux NumPy sensitivity (2.3.5, 1.17.1), and Linux
SciPy sensitivity (2.4.6, 1.16.3). One preparation artifact supplies identical
sealed inputs and contract to all four. The fixture manifest is pinned to
`d91d8add4c46ee29e1f954c5ad4bae4c870c2a10e371d0803d13d1829949c683`.
Workers enforce platform, dependency versions, source hashes and contract hash.
Comparison requires complete passing workers, matching sources, inputs,
contracts and checkout SHAs, and the expected Windows/Linux cohort pair.
Out-of-tolerance scientific differences and missing/tampered evidence fail.
The full production workflow separately regenerates native inputs; these are
deliberately not claimed identical sealed inputs. Its unchanged comparisons
remain mandatory. No scientific gates were weakened: rtol=1e-11, atol=1e-13,
refinement=1e-4, original current bounds/ridge/solver settings retained.

## Controlled publication handoff

No staging, commit, push, PR mutation or workflow dispatch was performed.
The supplied filesystem permissions expose `.git` read-only; GitHub CLI
configuration access is prohibited by AGENTS.md. No bypass was attempted.

`results/phase2d/publication-review-20261031/staging-paths.txt` is the explicit
51-path prospective staging plan. It includes implementation, both fixtures,
retained method reports, current review and the archived latest execution.
It excludes `.venv`, ignored CI trees and all original historical evidence and
snapshot directories. Excluded untracked work must remain on disk. The status
snapshot was captured before this document was created; obtain fresh status
before staging. Perform the following only from ordinary authenticated Windows
PowerShell with normal repository write permissions:

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
$ErrorActionPreference = 'Stop'
if ((git branch --show-current) -ne 'codex/phase2d-cross-platform-reproducibility') { throw 'Wrong branch' }
if ((git rev-parse HEAD) -ne '5a415c457e9f60c983a52d309a242583d73b40b6') { throw 'HEAD changed; review again' }
git status --short --untracked-files=all
git diff --check
if ($LASTEXITCODE) { throw 'Whitespace check failed' }
$paths = @(Get-Content results/phase2d/publication-review-20261031/staging-paths.txt)
$paths
# Review this exact list and archive digest before staging.
if (@(git diff --cached --name-only).Count) { throw 'Index already contains work; review separately' }
foreach ($path in $paths) {
    git add -- $path
    if ($LASTEXITCODE) { throw "Staging failed: $path" }
}
git diff --cached --name-status
git diff --cached --check
if ($LASTEXITCODE) { throw 'Staged whitespace check failed' }
git diff --cached
# After reviewing the complete staged content:
git commit -m 'Add controlled Phase 2D frozen-input reproducibility diagnostics'
if ($LASTEXITCODE) { throw 'Commit failed' }
git push -u origin codex/phase2d-cross-platform-reproducibility
if ($LASTEXITCODE) { throw 'Push failed' }
$repo = 'Nejatbakhsh-y/stellarator-robust-magnetic-optimization'
gh pr list --repo $repo --head codex/phase2d-cross-platform-reproducibility
# If no matching PR exists, create one draft; otherwise inspect that PR first.
gh pr create --repo $repo --base codex/phase2c-stable-fault-metrics --head codex/phase2d-cross-platform-reproducibility --draft --title 'Phase 2D controlled reproducibility diagnostics (PARTIAL)' --body-file docs/PHASE2D_PUBLICATION_REVIEW.md
gh workflow run phase2d-frozen-inputs.yml --repo $repo --ref codex/phase2d-cross-platform-reproducibility
gh workflow run phase2d-cross-platform-reproducibility.yml --repo $repo --ref codex/phase2d-cross-platform-reproducibility
gh run list --repo $repo --branch codex/phase2d-cross-platform-reproducibility --limit 20
# For each actual run ID returned above:
$runId = Read-Host 'Actual run ID to inspect'
gh run view $runId --repo $repo --log
gh run download $runId --repo $repo --dir "results/ci/hosted-$runId"
```

Manual dispatch may require the workflow on the default branch; use the
configured Phase 2C-targeted PR event if necessary. Do not merge to enable it.
Inspect the actual checkout SHA, all four worker results, three comparisons,
logs and manifests for each workflow; preserve unsuccessful runs too.

## Scientific conclusion

Hosted Windows: PENDING. Hosted Linux reference/NumPy/SciPy: PENDING.
Hosted Phase 2D cross-platform comparisons: PENDING; none retrieved here.
Historical production fault-ratio failures for rows 3/4 remain scientific
failures. A local fixed-input PASS or bounded stress diagnostic does not resolve
them. Upstream current drift attribution and any justified production correction
remain open. Finite-scenario minimax and small synthetic holdouts do not establish
general robust outperformance, continuum peak convergence or confinement.
