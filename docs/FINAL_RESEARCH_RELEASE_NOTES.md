# Robust Optimization and Independent Validation of Stellarator Planar-Coil Magnetic-Field Models ? Research Demonstration

Finalization status, 4 November 2026: UNPUBLISHED. Intended tag:
`research-demonstration-v1.0`. Live checks at source commit `a538629` show
three failed PR workflows, a draft PR with no submitted reviews, inaccessible
base-branch protection details and no integration into `main`. Both the intended
tag and release returned HTTP 404. No tag or release was created. The 973-test
result below remains historical local evidence, not current CI success.

Prepared release-note draft; unpublished. Reviewed source: `f1c3309b9c8887a29c6be22f2de4caa575f4c732`. Intended tag: `research-demonstration-v1.0`. No tag has been created, overwritten or moved. Publish only after PR merge and default-branch verification, with all specified checks and reviews satisfied.

This release represents a completed research demonstration with documented limitations. It does not establish full scientific acceptance or production readiness.

Research demonstration: COMPLETE WITH DOCUMENTED LIMITATIONS

Full scientific acceptance: NOT ESTABLISHED

Production acceptance: FAIL

The independent synthetic benchmark combines Biot-Savart response modeling, bounded ridge fitting, sparse support selection/refitting, finite-scenario minimax optimization, paired uncertainty evaluation and static single-coil recovery. Final materials include the [README](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/blob/f1c3309b9c8887a29c6be22f2de4caa575f4c732/README.md), [research report](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/blob/f1c3309b9c8887a29c6be22f2de4caa575f4c732/docs/FINAL_RESEARCH_DEMONSTRATION_REPORT.md), [ten-slide Markdown presentation](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/blob/f1c3309b9c8887a29c6be22f2de4caa575f4c732/docs/FINAL_RESEARCH_PRESENTATION.md), [portfolio summary](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/blob/f1c3309b9c8887a29c6be22f2de4caa575f4c732/docs/FINAL_RESEARCH_PORTFOLIO_SUMMARY.md) and [completion record](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/blob/f1c3309b9c8887a29c6be22f2de4caa575f4c732/docs/FINAL_DEMONSTRATION_COMPLETION.md). These source-pinned URLs also work when these notes are copied into a future GitHub release body.

Historical dense fitting reduced fine-grid RMS from 30.95589774 to 25.91442556 microtesla. Sparse tradeoffs were demonstrated. On the original 24 paired holdouts, robust fitting worsened matched-nominal mean RMS by 0.006260212 microtesla. Sampled minimax optimization and small holdouts do not establish generalized robustness. Recovery-ratio comparisons remain unresolved; numerical root cause is inconclusive and independent scientific validation is incomplete. No plasma confinement, equilibrium, continuum-peak or hardware validation is established.

The original failed 256-segment refinement evidence is preserved. Quick geometry uses 512 segments and the acceptance limit remains `1e-4`. Historical audit and reproducibility records remain bound to their original result SHA256; no new numerical checkpoint was verified for this release preparation.

Research objectives are constrained normal-field correction, sparse current/support tradeoffs, sampled robustness and static fault sensitivity on a prescribed synthetic torus. The mathematical framework uses area-weighted surface RMS, dimensionless response matrices, box-constrained least squares and a finite-scenario convex minimax epigraph. Current gain/offset perturbations and rigid coil displacements are evaluated with paired synthetic scenarios; small holdouts do not certify population tails.

Forward-model verification historically used analytical loop center/axis fields, independent polygon midpoint and smooth-circle integration, and segment/grid refinement. Independent validation also used derivative/support checks, recorded-input high-precision probes and SHA256-bound repeat records. These methods have bounded scope; full independent magnetic-field validation is incomplete. Cross-platform recovery-ratio discrepancies remain unresolved, and the three currently observed hosted workflows failed. No unique OS, NumPy, SciPy or BLAS root cause is established.

Final deliverables are the repository README and the report, presentation, portfolio summary and completion record linked above. The presentation is a ten-slide Markdown manuscript; no rendered deck is certified. Research demonstration completion coexists with full scientific acceptance NOT ESTABLISHED and production acceptance FAIL. No physical confinement, equilibrium or engineering acceptance is established.

The 4 November 2026 publication continuation confirmed that the existing Python 3.11.9 environment works outside the filesystem sandbox; earlier exit 103 reflected access restrictions, not established interpreter absence. Local regression execution passed 961 tests with two warnings; dependency consistency and analytical loop validation passed. No new standalone quick experiment/audit/output/full-repeat checkpoint was executed. No environment replacement or dependency change was needed.

Hosted failures have distinct causes: an unprovisioned original-archive manifest blocks pytest and cascades through production stages, while separately executed reciprocal replay comparisons retain a numerical FAIL. Authenticated artifacts from run 41633435313 contain 48 passing current-vector records and 24 failing recovery-ratio records out of 32. Shared inputs and reference/self comparisons are not independent trial counts. These findings do not establish a unique upstream numerical cause or production acceptance.

Publication remains blocked by hosted evidence provisioning, numerical disagreements, incomplete scientific verification, independent review and integration into the default branch. PR #7 targets a feature branch rather than main. Historical links to ignored local-only evidence also require a reviewed archival distribution strategy. See [release readiness](FINAL_RELEASE_READINESS.md) for actual test outcomes, review scope and remaining blockers. No release, tag, merge or production-readiness claim is made. Public availability grants no open-source license; none has been selected. This is independent work with no Thea Energy employment, collaboration, endorsement or validation.

The subsequent infrastructure correction adds explicit, digest-pinned historical
archive provisioning before CI regression/verifier jobs, without skipping tests
or changing historical bytes. All 71 local originals and their current remote
metadata associations verify. GitHub artifact expiration remains a retention
limitation, not grounds for substituting newly generated evidence. The corrected
local suite passed 973 tests with two warnings. Analytical validation and local
sealed-input gates passed; a same-OS frozen repeat was byte-identical. No new
local Linux execution or complete standalone research checkpoint is claimed.

Run 41870669468 independently retains 23/32 failed recovery-ratio comparisons,
while all 48 current records pass; the earlier 24/32 record is preserved as a
separate run. Four-way and high-precision checks support amplification by small
denominators but do not identify a unique upstream defect. No production
numerical correction is justified. Hosted verification of the infrastructure
correction remains a separate requirement. All release prerequisites and the
three scientific dispositions above remain unchanged; these notes are unpublished.
