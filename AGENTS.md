# Research continuation

Work only in this research checkout. Never inspect or modify the website repository or unrelated projects. Use the existing `.venv` Python 3.11 environment. Preserve existing work and keep `.venv/` ignored. Use a feature branch; do not merge, force-push or rewrite history.

The original 256-segment refinement audit failed. Its diagnosis is retained in `docs/REFINEMENT_DIAGNOSIS.md`. Keep the 1e-4 refinement acceptance limit; do not relax numerical gates to obtain a pass. Quick production geometry now uses 512 segments.

Before claiming a research checkpoint verified, run the README tests, analytical validation, quick experiment, independent audit, output checks and full reproducibility check. Reports require passing records tied to the result-file SHA256. Preserve failed audit evidence and report limitations. Describe finite-scenario minimax and small holdout samples accurately; never presume robust outperformance or confinement validation. See `docs/EXECUTION_STATUS.md` for incomplete milestones.

GitHub CLI configuration is denied in this environment. Do not inspect or bypass its security restrictions. Continue local work; provide ordinary PowerShell publication commands if needed.
