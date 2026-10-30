# Phase 2C publication handoff

Use these commands in ordinary authenticated PowerShell if connected PR creation
is denied. GitHub CLI configuration inside Codex is prohibited and is not accessed
or bypassed. Keep existing PRs #1-#4 open and unmerged.

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
git branch --show-current
git status --short
git log -1 --format=%H
git push -u origin codex/phase2c-stable-fault-metrics
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/phase2b-deterministic-geometry --head codex/phase2c-stable-fault-metrics --title 'Phase 2C: stable fault metrics and exhaustive reproducibility evidence' --body-file docs/PHASE2C_PR_DESCRIPTION.md --draft
gh pr checks codex/phase2c-stable-fault-metrics --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --watch
gh run list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --workflow phase2c-stable-fault-metrics.yml --branch codex/phase2c-stable-fault-metrics
```

A new stacked PR triggers the dedicated workflow. Record completed job outcomes
for its exact head SHA. Do not infer success from worker execution preceding a
failed comparison, or from the local Windows runs. Scientific status remains
PARTIAL even if all four hosted workers and cross-platform comparisons pass.
