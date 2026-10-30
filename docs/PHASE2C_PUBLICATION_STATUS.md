# Phase 2C publication and final verification

Implementation commit: `c907b400e1f0a215806459546498285cad145af1`.
It was committed and normally pushed to
`codex/phase2c-stable-fault-metrics`, based on Phase 2B commit
`74fddfe3a2a7cf95ee334f8bc1ec7757ef22c379`. No existing branch was rewritten;
no force push or merge was performed. The original working tree was clean and
repository/remote/ancestry checks passed. No website repository was accessed.

A separate clean Windows checkout of the implementation commit, with
`core.autocrlf=true`, passed all 111 tests. Its complete-worker contract,
raw-byte manifest, actual first/repeat numerical comparison, all 104 preservation
hashes and portable source fingerprints also passed. The checkout remained clean.
This is additional Windows verification, not Linux verification.

The connected GitHub integration rejected creation of the requested stacked draft
PR with HTTP 403, `Resource not accessible by integration`. The requested base was
`codex/phase2b-deterministic-geometry`. No new PR was created by this session.
The repository push was successful; PR creation is a separate permission.
GitHub CLI configuration was neither inspected nor bypassed, and no alternative
permission route was attempted. Use the exact ordinary authenticated PowerShell
commands in PHASE2C_PUBLICATION.md to create the draft and watch actual jobs.

Hosted Phase 2C status: **PENDING** for Windows reference, Linux reference,
Linux NumPy sensitivity, Linux SciPy sensitivity and cross-platform comparison.
No completed result for these new jobs is claimed. Historical run 41044895641
remains FAILED in all five jobs; its exact artifacts and reported failures are
preserved. Existing PRs #1-#4 were not modified or merged.

## Exact implementation files

Modified existing files:

* `.gitattributes`: raw-byte preservation for the new evidence namespace.
* `README.md`: versioned reproduction commands and report links.
* `src/stellarator_robust/experiments.py`: explicit opt-in stable evaluation and
  additional fault currents/residual/energy evidence.
* `src/stellarator_robust/ci_evidence.py`: optional comparator injection; original
  default scalar comparisons and tolerances remain unchanged.
* `src/stellarator_robust/phase2b.py`: optional benchmark/comparator injection;
  original Phase 2B defaults remain unchanged.

New source, configuration and automation files:

* `src/stellarator_robust/fault_metrics.py`
* `src/stellarator_robust/phase2c.py`
* `configs/phase2c_quick.json`
* `configs/phase2c_study.json`
* `scripts/phase2c_verify.py`
* `scripts/phase2c_fault_audit.py`
* `scripts/phase2c_legacy_compare.py`
* `scripts/phase2c_inventory.py`
* `scripts/phase2c_probe.py`
* `scripts/phase2c_compare.py`
* `scripts/phase2c_finalize.py`
* `scripts/phase2c_report.py`
* `tests/test_phase2c.py`
* `.github/workflows/phase2c-stable-fault-metrics.yml`

New documentation is under `docs/PHASE2C_*`; complete new numerical data, logs,
original ZIP archives, configurations/provenance, reference inputs, manifests and
source fingerprints are under `results/phase2c/`. The implementation commit's
102-file changeset enumerates every evidence file. Subsequent commits record
publication status and correct aggregate geometry/NM subsection failure labels
that could otherwise say PASS while the overall collected comparison failed.
A reporting regression now verifies both failing subsection labels and the
nonzero command outcome. The final complete suite passes 112 tests; compilation,
integrity, strict repeat and all 104 preservation checks pass. The checker-only
source fingerprints, test log, manifest and generated report were refreshed;
the original at-run fingerprints remain preserved. All nine calculation-file
hashes and every numerical result byte are unchanged. In particular, quick SHA
`ba6f27db86176606a82e360220e2e96f250976bfc2774be167ab746ccc1914e5`
and study SHA
`20f28ceb4a195c15c04d5ec3b36bc95ae65399cc540d8782eb593fc1fce63eca`
are unchanged. The earlier 111-test clean-checkout record above describes its
explicit implementation commit; the final reporting regression is additional.

`model.py`, `optimize.py`, `peak.py`, uncertainty generation, solver settings,
objectives, physical constraints, original configurations and all historical
Phase 1/2/2B evidence are unchanged. Science remains **PARTIAL**, including the
negative holdout findings and lack of global-peak/device/confinement validation.
