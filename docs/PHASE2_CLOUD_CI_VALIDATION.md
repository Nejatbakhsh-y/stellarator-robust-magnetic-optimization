# Phase 2 cloud CI local validation

Implementation is locally checked. Remote GitHub Actions status is **PENDING**:
no new PR or run URL was created or observed. The complete local overlay pipeline
passed; its core numerical code is unchanged. The final checkout passes 34 tests
(17 historical plus 17 new cases). The long run started with a 30-test snapshot;
subsequent diagnostic/preflight/report changes were separately checked. These
are local results, not proof of the final workflow on a hosted Linux runner.

Executed checks, all exit 0:

- pytest: final suite **34 passed**; long-run snapshot **30 passed**.
- Analytical CLI validation; fresh Phase 1 quick experiment; output checks;
  independent audit with all nine gates; complete second Phase 1 experiment;
  historical numerical comparison.
- Two complete Phase 2 quick studies; fresh/checkpoint and repeated-study
  comparisons at unchanged rtol=1e-11, atol=1e-13. Both comparisons have no
  nonzero scientific numeric differences. Configuration/scenario records match
  exactly. Git/Python/dirty metadata and four solver timings are validated and
  recorded separately, not treated as scientific differences.
- Independent training replay/numerical dual audit: all checks pass. Largest
  numerical primal-dual gap: **3.839244037701778e-11**.
- Invalid-evidence rejection: parent exit 0, deliberately invalid child exit 1.
- Manifest refresh, final gate and six reports. Gate: software PASS,
  Phase 1 regression PASS, scientific **PARTIAL**, no failed checks.
- Final source compilation; PyYAML 6.0.3 syntax/structure checks including PR
  trigger, read-only permissions, credential removal, 160/180-minute compute/job
  limits and always-attempted direct failure uploads. actionlint was not used.
- Byte-for-byte preservation of **36** numerical/audit evidence files against
  base Git data, using Git's filtered blob for historical Phase 1 text. Only
  commands.json and manifest.json are refreshed. See the hash review JSON.
- git diff --check and staged diff checks pass.

Original study SHA256 remains
`395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258`.
Fresh local study SHA256 is
`c5af7c1db7edf620c08f19d8793e1f892407ab9ceef0b95bdfd7cf3b141132e6`.
The difference is attributable to recorded provenance/timing, not scientific
numeric changes. Both passing comparisons and all audit links are retained in
[the local validation record](PHASE2_CLOUD_CI_LOCAL_VALIDATION.json).

The full local run used an explicit overlay on detached base commit ad1ca528.
Final error-report persistence, artifact separation, exact-record diagnostics and
manifest-completeness checks were covered by the final suite and saved gate;
the final comparator also consumed the actual completed studies successfully.
The report template was corrected to derive its test count from the passing
command record: 30 in that worktree, 34 in the final checkout. Numerical tables
and scientific conclusions did not change. No scientific calculation was edited.

A fresh committed Windows checkout at
`62aac8ade5fd76f3f9ae49bf40f006576c0687f8`, with invocation-scoped
core.autocrlf=true, passed 32 tests and reference/manifest/gate checks and remained
clean. Its numerical evidence bytes survived checkout unchanged. Actual hosted
Windows/Linux jobs remain pending. No persistent Git setting was changed.

Local raw logs/results are retained under ignored results/ci/phase2-cloud/ and
results/reproduction/cloud-work/; the clean Windows logs are under
results/reproduction/windows-checkout/results/ci/phase2-cloud/smoke/.
The initial newline rejection and missing YAML parser are documented in the
execution status. No failed numerical evidence was deleted or gate relaxed.
Scientific limitations and all four negative robustness findings remain PARTIAL.
