# Publication handoff

The branch is prepared for owner review after local verification. GitHub CLI configuration access is denied inside the execution environment. Do not bypass that restriction. No remote push, PR or CI result is claimed.

Run from **ordinary Windows PowerShell**:

```powershell
Set-Location 'C:\Users\nejat\TheaResearchWorkspace\stellarator-robust-magnetic-optimization'
git status --short
git branch --show-current
git remote get-url origin
gh api user --jq .login
gh repo view Nejatbakhsh-y/stellarator-robust-magnetic-optimization --json nameWithOwner,isPrivate,defaultBranchRef
```

Confirm a clean worktree, branch `codex/stellarator-research-v1`, the exact authorized origin, identity `Nejatbakhsh-y`, public visibility and default branch `main`. Stop on any mismatch. Then:

```powershell
git push -u origin codex/stellarator-research-v1
gh pr list --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --head codex/stellarator-research-v1
```

If no PR already exists for this branch, create one:

```powershell
gh pr create --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --base main --head codex/stellarator-research-v1 --title 'Synthetic planar-coil optimization with independent refinement checks' --body-file docs/PR_DESCRIPTION.md
gh pr checks --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization
```

Keep the PR unmerged. Pending checks are not passes. No releases or publicity claims are part of this checkpoint.
