# Phase 2D publication status and handoff

Status: **PARTIAL**. No publication or hosted Phase 2D success is claimed.
PR #5 has not been modified or merged. GitHub CLI security restrictions
were respected; no configuration or credentials were inspected.

Do not publish this as a verified scientific correction. Restore Python 3.11,
finish independent attribution and the exhaustive discrepancy inventory,
implement only a justified versioned correction, execute all README and Phase
2D gates, and review the resulting evidence before committing a checkpoint.
Preserve original downloaded evidence and every failed hosted run.

The current additions are an incomplete investigation, a compiled reference
helper with one smoke check, and an unexecuted investigation workflow.
The input artifacts are in ignored `results/ci/`; review their provenance and
arrange durable archival preservation before publication. A summary hash is
not a substitute for preserving all original evidence files.

After all required work and validation, ordinary authenticated PowerShell
publication commands (not executed here) are:

```powershell
git status --short
git diff --check
git diff
git add scripts/phase2d_reference.cs scripts/phase2d_investigate.ps1
git add .github/workflows/phase2d-cross-platform-reproducibility.yml
git add docs/PHASE2D_*.md results/phase2d
git commit -m "Document Phase 2D investigation and validation status"
git push -u origin codex/phase2d-cross-platform-reproducibility
gh pr create --draft --base codex/phase2c-stable-fault-metrics --head codex/phase2d-cross-platform-reproducibility --title "Phase 2D reproducibility investigation (PARTIAL)" --body-file docs/PHASE2D_RESULTS.md
gh run list --branch codex/phase2d-cross-platform-reproducibility
```

Use gh only where it is permitted. Inspect actual worker and dependent
comparison results, download unsuccessful-run evidence, verify its provenance
and retain immutable originals. Never force push, merge PR #5, or replace
negative findings with a positive robustness claim.

## Python continuation handoff

Once the current session can execute the configured Python 3.11 runtime,
run the new runner through the existing environment (no PowerShell policy
change is needed):

```powershell
.\.venv\Scripts\python.exe scripts/phase2d_investigate.py --output results/phase2d/python-investigation
.\.venv\Scripts\python.exe -m pytest -q
```

The investigation deliberately returns 1 even after completing its reports
while correction/reproducibility remains unresolved. Read `reference-audit.json`
and its manifest rather than treating output creation as a scientific PASS.
An exception or missing report is also a failure. Complete the remaining
README and Phase 2D calculations and independent gates before claiming a
verified checkpoint. Include `scripts/phase2d_investigate.py` and
`tests/test_phase2d_investigation.py` in the eventual reviewed commit.
No commit was created from unexecuted tests in this continuation, and the
PowerShell/C# originals and all original input evidence remain preserved.

## 2026-10-30 remediation continuation

Latest execution status: **PARTIAL / local execution blocked**. See
[the versioned remediation record](../results/phase2d/remediation-20261030-193501/STATUS.md)
for exact commands, historical hashes, I/O changes and outstanding phases. The
current attempt executed zero tests: the required .venv launcher exited 103 before
Python startup. All 247 preserved inputs match their hashes. Existing investigation
records contain 84 agreed/converged audits and 24 swaps, with zero manifest hash
mismatches; they were inspected, not recalculated here. Earlier statements that
swaps were merely prepared describe the earlier attempt and are superseded by
this inspection of the preserved investigation. No physical or numerical correction,
new hosted pass, verified checkpoint, commit or publication is claimed.
