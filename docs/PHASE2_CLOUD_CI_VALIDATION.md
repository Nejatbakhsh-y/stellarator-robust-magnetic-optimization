# Phase 2 cloud CI local validation

Local checks use the existing Python 3.11.9 venv on Windows. Remote Actions status
is PENDING; no PR URL or run URL was observed. Linux numerical agreement and the
actual new Windows job remain unverified until publication.

Completed commands (exit 0 unless stated):

- python -m pytest -q: 32 passed (17 historical tests plus 15 new cases).
- python -m stellarator_robust.cli validate: analytical loop checks passed.
- python scripts/phase2_failure_check.py: PASS; invalid-evidence child exited 1,
  rejecting missing evidence and corrupt hash as required.
- python scripts/phase2_refresh_manifest.py: PASS; 32 tests, numerical records
  preserved, expanded source fingerprints and command record refreshed.
- python scripts/phase2_cloud_ci.py --smoke: PASS; reference hashes, manifest,
  pytest and saved scientific gate all passed.
- python scripts/phase2_gate.py: software PASS, Phase 1 regression PASS,
  scientific PARTIAL, no failed checks; linked study SHA256
  395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.
- python scripts/phase2_reports.py: six hash-linked historical reports generated;
  they remain unchanged from the base.
- python -m compileall -q src scripts tests: PASS.
- PyYAML 6.0.3 parse and assertions: correct target branch, jobs, read-only
  permissions and checkout credential restrictions. actionlint was not required.
- Byte-for-byte preservation: 36 evidence files passed against base Git data;
  Phase 1 text uses the filtered base blob. See PHASE2_CLOUD_CI_HASH_REVIEW.json
  for every preserved hash and changed manifest entry.

The complete local overlay run is in progress. Its logs and structured execution
record are under ignored results/ci/phase2-cloud; its disposable worktree and
full scientific evidence are retained under results/reproduction/cloud-work.
That run is explicitly a local overlay of the published base, not remote CI.
Artifact-output separation and failure-report persistence were tightened after
its start; those final plumbing changes were covered by the final 32-test,
smoke, compilation and YAML checks. No scientific calculation was changed.

The initial preflight newline rejection and missing YAML parser are retained in
PHASE2_CLOUD_CI_EXECUTION_STATUS.md. Neither was hidden by changing tolerances.
Scientific limitations and negative robustness findings remain as documented in
PHASE2_CLOUD_CI_LIMITATIONS.md.
