# Phase 2B execution status

Implemented and locally executed; hosted validation is PENDING until observed.
Scientific status is PARTIAL. No cross-platform success is inferred from local
Windows results. The separate branch is codex/phase2b-deterministic-geometry,
based on codex/phase2-ci-evidence-validation at
72c70995b7e6c2f56ec6fad4fa07fd73930e3370. Preflight verified the authorized root,
exact Nejatbakhsh-y/stellarator-robust-magnetic-optimization origin, ancestry and
clean working tree. AGENTS.md and the prior scientific/CI/repair docs were read.
No website repository was accessed. Existing .venv Python 3.11.9 was used; .venv
remains ignored. GitHub CLI configuration is prohibited and was not accessed.

The complete local version 2 pipeline passed: tests and analytical CLI; fresh
quick run and output checks; independent nine-gate audit; complete Phase 2 study;
second quick and complete Phase 2 study; strict numerical repeat; independent
training replay/dual audit; and candidate smooth-circle/refinement checks.
All 38 original Phase 1/2 evidence files, including commands and manifest, are
unchanged. Version 2 records are isolated under results/phase2b/ with raw hashes.
The initial numerical pipeline ran an 84-test snapshot. Later evidence-contract
and independent analytic/scale tests are separately recorded in final-tests.log;
no calculation source changed after that full numerical run. At-run fingerprints
are preserved alongside the final validator fingerprints; finalization verifies
identical calculation-file fingerprints before allowing the refresh.

An actual separate legacy quick run, repeat, output checks and independent audit
also matched the frozen historical scientific groups on this Windows machine.
Those logs/records are under ignored results/ci/phase2b-legacy/; the original
results/quick and results/phase2 were never regenerated. This does not resolve
legacy-v1 cross-platform failures or replace their scientific evidence.

The investigation retains all 145 original peak discrepancies. Initial geometry
plane auditing failed at 3.484410128301612e-14 m because an ordinary 512-term mean
biased the center of a translated polygon. That failed measurement is retained
in investigation/initial-geometry-audit-failure.json. Antipodal center recovery,
checked against independently declared center/radius/normal, resolved the audit
without changing production geometry or relaxing an acceptance threshold.

The historical Linux study was copied as exact raw bytes from SHA256-verified
artifact 12944135712 (run 40977794679). Its original failing comparison and all
later diagnoses remain available; old failures are not relabeled as PASS.
The local version 2 study SHA256 is
c8f1cf9df1cdc6fb8eb5ab8595ede2015aee4647671d98142205ec1ec8f2a960.
The original Phase 2 study remains
395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.

Publication must use a new stacked PR targeting codex/phase2-ci-evidence-validation.
Do not merge or modify PRs #1–#3. A new PR is needed to trigger the dedicated full
workflow; manual dispatch is optional and is not relied on for first execution.
Observed hosted results must be reported separately from this local checkpoint.
Recorded elapsed times are wall-clock measurements, not CPU performance claims.

Post-commit verification: a separate clean Windows checkout of implementation
commit c0660b233cd61638508e6fa663ff13df9c5db326, with core.autocrlf=true,
passed all 94 tests. Original-evidence preservation, the complete-stage contract,
raw manifest, strict first/repeat comparison, and portable source fingerprints
also passed; the checkout remained clean. This is Windows verification only.

The implementation branch was successfully pushed. Stacked draft PR creation
through the connected GitHub integration failed with HTTP 403, Resource not
accessible by integration. No new PR was created by this session, and no
PR-triggered workflow runs were returned for the implementation commit. Hosted
Windows/Linux and dependency-version comparisons remain PENDING. See
PHASE2B_PUBLICATION.md for exact authenticated PowerShell handoff commands.
