# Phase 2B publication handoff

Use ordinary authenticated PowerShell if publication inside Codex is blocked.
GitHub CLI configuration was not inspected or bypassed. Do not merge any PR.

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
git branch --show-current
git status --short
git log -1 --oneline
git push -u origin codex/phase2b-deterministic-geometry
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/phase2-ci-evidence-validation --head codex/phase2b-deterministic-geometry --title 'Phase 2B: deterministic geometry and versioned reproducibility' --body-file docs/PHASE2B_PR_DESCRIPTION.md --draft
gh pr checks codex/phase2b-deterministic-geometry --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --watch
gh run list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --workflow phase2b-deterministic-geometry.yml --branch codex/phase2b-deterministic-geometry
```

The new stacked PR triggers the full workflow; do not rely on initial manual
dispatch for a workflow absent from the default branch. Record real run URLs,
commit SHAs and completed job conclusions. Keep original PRs #1–#3 open and
unmerged. Science remains PARTIAL even after tested numerical agreement.
