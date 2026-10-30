# Phase 2 clearance comparison repair

The requested sub-ULP comparison correction is implemented. Full Linux
reproducibility remains **BLOCKED**, with scientific status **PARTIAL**. No
production geometry, Biot–Savart calculation, objective, solver setting,
experimental configuration, clearance safety constraint or numerical reference
was changed. PRs #1, #2 and #3 must remain open and unmerged.

Preflight found the exact authorized research root and origin
https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git,
branch codex/phase2-ci-evidence-validation, clean tree, and HEAD/ancestor
e30d2f85c571faa2bc7d95b25c97f3ab9859c927. The website repository was not accessed.
GitHub CLI configuration was not accessed; the connected GitHub app supplied
PR/run metadata and the original failure artifact.

The original Linux run is
https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/40977794679.
Both hosted smoke jobs passed; full-phase2 failed. Phase 1 workflow run
40977794558 passed. PR #3 was observed open and unmerged, targeting the Phase 2
branch at ad1ca528. These observations describe the original e30d2f8 run, not a
successful run of this repair.

The reported failure was an exact comparison of a derived geometric measurement:
/scenarios/holdout/1/sampled_clearance_m, 0.38888759185268096 versus
0.3888875918526809, absolute difference 5.551115123125783e-17 m. Random draws are
inputs; sampled clearance is computed from the moved polygon geometry. Only
that leaf in validated holdout/training records now uses existing rtol=1e-11,
atol=1e-13. Configuration, seeds, perturbations, field names, input types and
array structure remain exact. Nonfinite/invalid values and missing fields fail.
Every nonzero accepted or rejected numeric difference retains its path and
absolute/relative magnitude. The derived measurements are compared, not excluded.

Regression coverage includes the actual reported values, training-record
clearance, identical inputs, sub-tolerance changes to translations/rotations/gain/
offset, materially changed clearance, malformed/missing fields, NaN/infinities,
wrong scalar types, a clearance-named configuration field, and broken evidence
links. The full final suite passes 72 tests. Analytical validation, manifest
refresh, Phase 2 saved-evidence smoke and compilation pass locally on Windows
Python 3.11.9. These checks do not establish full Linux reproducibility.

## Additional failure exposed by the real artifact

The downloaded ZIP's SHA256 matches GitHub's published artifact digest:
befcc90ca3bc461e22b08e379bf1660bab93efe568dd18d8d6fae2fe272c6d14.
Original artifact ID: 12944135712. No artifact contents were executed.
Offline replay uses metadata already runtime-validated in the failed Linux
comparison, cross-checking its execution commit/Python record; it does not
substitute Windows runtime metadata or claim a new Linux execution.

After accepting the reported rounding case, the complete archived comparison
correctly fails at /scenarios/holdout/9/sampled_clearance_m:
reference 0.3894433457841317, Linux 0.38944327335107365,
absolute difference **7.243305805149092e-08 m**. This exceeds the unchanged
numerical tolerance. A regression test explicitly preserves this rejection.

An independent diagnostic found zero changed random perturbation inputs and
153 remaining violations of the existing equality/tolerance rules: eight
clearance measurements and 145 peak-search trace fields. Examples include
angles differing by 5.650068490847815e-08 rad and nfev=141 versus 138. These
fields remain rejected; no trace fields or scientific coordinates were excluded.
The inventory does not establish that every discrepancy has the same cause.

For scenario 9, coil 9's local normalized normal has tied x/y magnitudes:
[-0.3535533905932737, -0.3535533905932737, 0.8660254037844388]. Production
circle() selects a basis using argmin(abs(n)). A diagnostic-only alternate basis
axis 1 instead of local axis 0 changes the polygon phase and yields global
sampled clearance 0.38944327335107376 m, within 1.1102230246251565e-16 m of
Linux. This strongly identifies unstable basis selection as the source of this
clearance discrepancy. The diagnostic constructs an alternate polygon only
for analysis; production model.py and all feasibility constraints are unchanged.
A deterministic geometry/trace-validation redesign needs separate scientific
review; it is not hidden inside the requested clearance comparison exception.

## Reproduction and preservation

After downloading the original artifact into an ignored local directory:

```powershell
.\.venv\Scripts\python.exe scripts/replay_clearance_failure.py --artifact results/ci/clearance-repair/failed-linux-40977794679.zip
# Expected current result: exit 1 at scenario 9; the original scenario 1 passes.
.\.venv\Scripts\python.exe scripts/diagnose_clearance_artifact.py --artifact results/ci/clearance-repair/failed-linux-40977794679.zip
```

All 36 numerical/audit evidence files are byte-preserved against e30d2f8,
accounting explicitly for Git's historical Phase 1 text checkout filtering.
Study SHA256 remains
395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.
Only commands.json (executed expanded test record) and manifest.json (source and
command fingerprints) are refreshed. Exact hashes and diagnostic facts are in
PHASE2_CLEARANCE_REPAIR_EVIDENCE.json. Original local full-run records and the
failed Linux ZIP/replay/inventory are retained; no failed evidence was removed.

The larger research preset was not run. All four tested minimax fits still have
worse synthetic holdout RMS than nominal. Small shared holdouts do not establish
population robustness; local peaks have no global certificate. Confinement,
external-code, correlated-error and broader scientific validation remain pending.

Publication updates the existing branch/PR #3 only. If Git push is unavailable,
run this in ordinary authenticated PowerShell; do not create another PR:

```powershell
git push origin codex/phase2-ci-evidence-validation
```

A new hosted run must be observed before any new job is labelled PASS. The known
additional discrepancies are expected to keep the strict full job red until
separately resolved; no successful cloud checkpoint is claimed by this repair.
