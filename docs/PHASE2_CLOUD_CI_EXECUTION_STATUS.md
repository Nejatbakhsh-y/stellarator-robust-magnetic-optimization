# Phase 2 cloud CI execution status

Latest clearance repair: PR #3 is open. Original hosted smoke jobs and Phase 1 CI passed; full Phase 2 run 40977794679 failed. The derived-rounding exception is fixed, but offline artifact replay reveals an additional out-of-tolerance geometry discrepancy and peak-trace mismatches. Full Linux reproducibility remains BLOCKED; science remains PARTIAL. See PHASE2_CLEARANCE_REPAIR.md and its evidence JSON. No new hosted success is claimed.

The following is the preserved historical local implementation checkpoint, written before PR #3 publication:


Implementation and the complete local overlay pipeline passed; remote CI is PENDING.
No PR or Actions run has been created or observed in this session. GitHub CLI
configuration is prohibited by AGENTS.md and was not accessed or bypassed.
PRs #1 and #2 and the website repository were not accessed.

Preflight: authorized root is
C:/Users/nejat/TheaResearchWorkspace/stellarator-robust-magnetic-optimization.
Origin exactly matches
https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git.
Initial branch codex/phase2-peak-robustness-uq and HEAD
ad1ca5285a20717a03c202c31e5d4a5d2152412c matched the required published base.
The working tree was clean (git status --porcelain=v1 --untracked-files=all).
The prompt's literal --all status option is unsupported by Git; the equivalent
--untracked-files=all was used. The new requested feature branch was created
with approved .git write access. Existing venv Python 3.11.9 required approved
access to its installed base runtime. No runtime was replaced; .venv is ignored.

Published study SHA256 remains
395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.
The raw Phase 2 evidence attribute remains -text whitespace=cr-at-eol.
Phase 1 and Phase 2 numerical records are preserved. Only commands.json and
manifest.json are refreshed to bind the expanded tests and implementation;
no saved numerical study, regression output, training audit or repeat is replaced.
The refresh does not represent a new scientific calculation.

Retained implementation failure: the first local full-run attempt stopped during
reference preflight with 'published numerical reference changed:
results/quick/results.json'. Investigation identified existing CRLF checkout
versus LF Git blob, rather than changed numerical data. The implemented filtered
blob and frozen-input checks are documented in PHASE2_CLOUD_CI_METHODS.md. No
numerical gate was weakened. The first YAML availability probe failed because
PyYAML was absent; PyYAML 6.0.3 was installed into the existing venv with approval.

The full local overlay run tests uncommitted source over the published base in an
isolated disposable worktree; it is not a GitHub Actions run. Actual clean Linux
and Windows remote results remain pending. Scientific status remains PARTIAL.

Base source tree object: b6e239d754bed282a55c0a9599759be0a29cba1a.
Phase 1 checkout and frozen-input SHA256:
83162de245bfa5f64fad773f0c8212ccb04d2ae8af8287c03589fd8ee8374889.
A clean initial tree at the exact base ties all initial source/config files to
that tree; final manifest entries bind the changed implementation separately.

Initial implementation commit: 62aac8ade5fd76f3f9ae49bf40f006576c0687f8.
A fresh detached Windows checkout with core.autocrlf=true passed the committed
smoke checks (32 tests, manifest, reference bytes and saved gate), and remained
clean. Actual GitHub-hosted Linux/Windows jobs are still pending.

Reporting correction: phase2_reports.py now extracts the passing test count from
the actual command record. The fixed historical '17 passed' text would be false
for new CI runs. The report script was also copied into the disposable local
worktree before its manifest/report stages; it changes no scientific computation.
The repeated experiments retain the original scientific code. Final diagnostics
and preflight-completeness tests were added after the long run started, so its
snapshot test count is 30, while the final checkout suite is 34. Final report
fingerprints record the reporting correction; numerical evidence stays unchanged.

Completed full local overlay pipeline: all eight outer stages returned 0; all
seven inner regression/repeat commands returned 0. The expected negative child
returned 1. Fresh/reference and repeat comparisons passed with no nonzero
scientific numeric differences, unchanged 1e-11/1e-13 tolerances, and exact
scenario/configuration identity. Independent training checks passed; maximum
numerical dual gap 3.839244037701778e-11. Final gate PASS/PASS/PARTIAL.
Fresh study SHA256:
c5af7c1db7edf620c08f19d8793e1f892407ab9ceef0b95bdfd7cf3b141132e6.
All 36 preserved numerical/audit files still match base Git data; only the two
provenance records are refreshed. The generated validation report's test count
is now derived from executed commands. Full local records and exact source,
metadata, workflow and report hash changes are in PHASE2_CLOUD_CI_LOCAL_VALIDATION.json
and PHASE2_CLOUD_CI_HASH_REVIEW.json. Final checkout suite: 34 passed; the full
run's initial snapshot: 30 passed. Actual hosted CI and publication remain pending.
