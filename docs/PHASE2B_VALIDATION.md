# Phase 2B validation record

Local status: PASS for the versioned numerical contract; scientific status PARTIAL.
Hosted status: PENDING until actual job conclusions are observed. See execution
status for the distinct original-source snapshot and final evidence-test counts.

- Final complete suite: 94 passed, return code 0; results/phase2b/final-tests.log.
- Initial full numerical pipeline suite: 84 passed, return code 0.
- Analytical CLI: return code 0.
- New quick runs and output checks: both executed; strict numerical repeat PASS.
- Independent new quick audit: all nine gates PASS at unchanged thresholds.
- Two complete new Phase 2 studies: PASS at rtol=1e-11, atol=1e-13, including all
  new scientific coordinates, fields, moves, fixed budgets and scenario records.
- Independent training replay/numerical dual audit: all five checks PASS.
- Smooth-circle candidate replay and 512-segment relative 1e-4 gates: PASS.
- New circle frames: orthogonality, handedness, input normal, radius, perimeter,
  centers and plane independently checked; one-ULP tie perturbation stays below
  1e-14 m in the corrected indexed vertices while legacy vertices jump >0.1 m.
- Independent scalar point-to-segment clearance and analytic loop tests: PASS.
- NM field re-evaluation and finite 20/28-level sensitivity: executed, retained;
  all three best-field gaps to NM are below 1.18e-14 T; 20/28 fields are identical.
- Legacy standalone quick, output checks, independent audit, second quick and
  historical comparison: PASS on Windows; records in results/ci/phase2b-legacy/.
- All 38 original numerical/audit/command/fingerprint files: exact-byte preserved
  against base 72c7099, with explicit historical Phase 1 Git checkout filtering.
- Raw new evidence manifests, executed command/result links and unchanged
  calculation-file fingerprints: PASS. Unknown metadata, incomplete workers,
  changed currents, changed hashes/input copies and tampered manifests fail tests.
- Python compilation and YAML syntax/trigger/security structure: PASS.
- Git whitespace/staged review is required immediately before committing.

All original 145 peak discrepancies remain failures in the archived v1
comparison. The complete category inventory, raw inputs, conditional curvature
analysis, NM traces and all refinement results are retained, not replaced by
rounded summaries. A comparison of diagnostic NM coordinates is not reported
as an exact reproduction claim. Their physical field values remain graded, and
all primary v2 finite-search coordinates are strictly compared.

New study SHA256:
c8f1cf9df1cdc6fb8eb5ab8595ede2015aee4647671d98142205ec1ec8f2a960.
Old study SHA256, unchanged:
395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.

The hosted workflow runs fresh calculations and repeats, not just saved gates.
Windows/Linux reference jobs and independent one-factor NumPy/SciPy cohorts
must finish before their results can be called PASS. A separate cross-platform
job consumes the actual worker artifacts. No hosted result is inferred here.
