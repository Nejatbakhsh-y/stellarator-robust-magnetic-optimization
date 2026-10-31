# Phase 2D results

Scientific status: **PARTIAL**; numerical cross-platform agreement remains
**FAIL** in the supplied Phase 2C evidence. No Phase 2D hosted outcome exists
in this session.

Rechecked checkout: requested branch
`codex/phase2d-cross-platform-reproducibility`, baseline HEAD
`5a415c457e9f60c983a52d309a242583d73b40b6`. The branch was supplied by the
user and was not recreated. Initial working tree was clean.

All 247 entries in the user-supplied SHA256 inventory matched their local
file hashes and lengths. The evidence is under
`results/ci/phase2d-inputs/run-41061184709/`; it was not overwritten.
`results/phase2d/archive-review.json` retains environments, recorded failures,
selected original high-precision audit records and source-data hashes.
The raw scientific differences and all metadata remain in the input artifacts.
This is not yet an exhaustive newly generated field inventory.

| Archived worker | NumPy | SciPy | Recorded OS | Cross-cohort comparison |
|---|---|---|---|---|
| Windows reference | 2.4.6 | 1.17.1 | Windows 10 build 26100 | reference |
| Linux reference | 2.4.6 | 1.17.1 | Linux, glibc 2.39 | FAIL |
| Linux NumPy sensitivity | 2.3.5 | 1.17.1 | Linux, glibc 2.39 | FAIL |
| Linux SciPy sensitivity | 2.4.6 | 1.16.3 | Linux, glibc 2.39 | PASS |

These are observations of supplied records. Each worker reports calculation
pipeline PASS; that does not override failed cross-platform comparisons.
All workers record source commit `23279366436b37a6c6715556ff266f1384d183ce`,
which is unavailable in the local Git object database. Its source provenance
has not been authenticated against the requested GitHub run.

The supplied extracted files contain no original artifact ZIP digests or
authenticated run metadata. Local SHA verification establishes consistency
with the supplied inventory, not independently authenticated GitHub origin.

Phase 1/2/2B/2C numerical evidence remains unchanged against the baseline
according to `git diff --exit-code <baseline> -- results` before new Phase 2D
records were added. Existing finite-scenario minimax results, small synthetic
holdouts and negative robustness findings remain valid limitations. No global
peak certificate, confinement validation or robust outperformance is claimed.

## Python continuation

The supplied branch and all earlier untracked work were preserved. Added
`scripts/phase2d_investigate.py` and
`tests/test_phase2d_investigation.py`; these have not run successfully.
New command records are in `results/phase2d/resume-access-checks.json`.
Earlier reports and result records have been retained rather than overwritten.

The user reports that Python 3.11.9 is installed and the virtual environment
repaired. This session still cannot access the configured base interpreter:
the virtual-environment launcher returns 103, while a direct path existence
check returns Access is denied. The earlier suggestion that Python must be
missing is therefore not established; sandbox access may be the blocker.
All 247 original inventory entries were rechecked successfully after the
Python implementation was added. Historical Phase 1/2/2B/2C tracked results
still have no diff against the requested baseline.

## 2026-10-30 remediation continuation

Latest execution status: **PARTIAL / local execution blocked**. See
[the versioned remediation record](../results/phase2d/remediation-20261030-193501/STATUS.md)
for exact commands, historical hashes, I/O changes and outstanding phases. The
current attempt executed zero tests: the required .venv launcher exited 103 before
Python startup. All 247 preserved inputs match their hashes. Existing investigation
records contain 84 agreed/converged audits and 24 swaps, with zero manifest hash
mismatches; they were inspected, not recalculated here. Earlier statements that
swaps were merely prepared describe the earlier attempt and are superseded by
this inspection of the preserved investigation. No physical or numerical correction,
new hosted pass, verified checkpoint, commit or publication is claimed.
