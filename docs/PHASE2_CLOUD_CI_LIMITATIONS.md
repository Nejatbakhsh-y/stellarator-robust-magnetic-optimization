# Phase 2 cloud CI limitations

Scientific status remains PARTIAL. All four finite-scenario minimax fits worsened
holdout RMS under the tested synthetic scenarios; Phase 1's negative finding is
preserved. Two training seeds, two training counts and 64 shared IID holdout draws
do not establish population robustness or tail superiority. Local peak searches
and shifted grids provide lower bounds, with no global continuum certificate.
Numerical dual checks are not interval proofs. There is no confinement/device,
external-code, correlated-error or current-budget-matched validation. The larger
research preset has not run.

A green workflow means the explicitly implemented software and scientific evidence
gates passed. It does not promote scientific status to PASS. The local clean Windows checkout passes the saved-evidence checks. Linux numerical
agreement and actual GitHub-hosted Windows portability remain pending until
the remote jobs are observed. Current dependency
ranges can expose new SciPy/NumPy differences. Such differences must fail with
unchanged numerical tolerances and be investigated, not silently accepted.

No remote authentication was attempted: repository instructions prohibit inspecting
GitHub CLI configuration. PRs #1 and #2 remain untouched. Publication and actual
remote CI observation require the authenticated ordinary PowerShell handoff.
