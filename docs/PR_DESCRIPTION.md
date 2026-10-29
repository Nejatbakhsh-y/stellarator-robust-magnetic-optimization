## Reduced-order research checkpoint

Implement a reproducible synthetic planar-coil normal-field correction pipeline: exact straight-segment Biot–Savart, bounded dense fits, two sparse selection methods with refitting, finite-scenario minimax optimization, paired current/placement uncertainty and static single-coil recovery.

The first segment-refinement audit failed because 128→256 segments changed RMS by 2.47e-4, above the 1e-4 limit. Increase quick geometry resolution to 512 without relaxing the gate; add an independently integrated smooth-circle reference, six refinement levels, measured convergence orders and durable pass/fail audit records.

Verified locally on Python 3.11.9:

- 11 automated tests passed; analytical CLI, all nine independent audit gates and output checks passed.
- Observed asymptotic segment convergence order approximately 2.0000; 512-segment residual relative error 2.07e-5.
- Full repeated experiment matched all compared numerical results and statuses; maximum current/holdout RMS differences were zero.
- Eight figures, structured full precision results and generated technical reports are included.

Robust holdout mean RMS was **worse** than the support-matched nominal fit by 0.006260212 microT in 24 paired scenarios. No robustness improvement, confinement performance or device validation is claimed. Fine-grid RMS converges to the stated threshold, but sampled peak field remains unresolved. Larger studies and external-solver comparisons are pending. Remote GitHub Actions status must be checked after publication; no remote success is claimed here.

Independent synthetic research; no affiliation with or validation by Thea Energy. No proprietary geometry or website changes. Leave this PR unmerged for owner review.
