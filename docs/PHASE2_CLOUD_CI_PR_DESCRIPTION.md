# Phase 2 cloud CI pull request

Add automatic full Phase 2 reproducibility on PRs targeting
codex/phase2-peak-robustness-uq. Preserve the existing Phase 1 workflow and numerical
checkpoint. Add Linux/Windows saved-evidence smoke checks, a complete Linux fresh
study plus repeat/regression/audits, strict provenance-aware checkpoint comparison,
and always-attempted failure/success artifact uploads with 14-day retention.

The full pipeline runs in a detached disposable worktree. Numerical tolerances
remain rtol=1e-11, atol=1e-13; the 1e-4 segment gate is unchanged. Runtime metadata
is validated and recorded separately. Historical Phase 1 line endings are checked
against Git's filtered blob and its hash-linked frozen input is restored only in
the disposable runner worktree after semantic/hash validation.

Local checks: final suite 34 passed; complete numerical overlay pipeline passed
with its recorded 30-test snapshot, audits and hash-linked PASS/PASS/PARTIAL gate.
Details are in PHASE2_CLOUD_CI_VALIDATION.md. Remote CI is pending;
no actual Actions success is claimed. Scientific status remains PARTIAL: all four
minimax fits worsen the tested holdout RMS; peaks have no global certificate.
Broader uncertainty, external-code and confinement validation remain unfinished.

Base: codex/phase2-peak-robustness-uq at
ad1ca5285a20717a03c202c31e5d4a5d2152412c.
Head: codex/phase2-ci-evidence-validation. Leave PRs #1 and #2 open and unmerged.
