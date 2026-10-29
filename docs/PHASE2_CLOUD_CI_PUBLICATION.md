# Phase 2 CI publication handoff

Run in ordinary authenticated PowerShell outside Codex. GitHub configuration was not accessed in Codex.


```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
git branch --show-current
git status --short
git push -u origin codex/phase2-ci-evidence-validation
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base codex/phase2-peak-robustness-uq --head codex/phase2-ci-evidence-validation --title 'Add full Phase 2 cloud validation with evidence artifacts' --body-file docs/PHASE2_CLOUD_CI_PR_DESCRIPTION.md
gh pr checks codex/phase2-ci-evidence-validation --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --watch
gh run list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --workflow phase2-scientific-validation.yml --branch codex/phase2-ci-evidence-validation
```

Record the actual PR/run URLs and all Linux/Windows job conclusions before marking
remote validation verified. Do not merge any PR as part of this handoff.
