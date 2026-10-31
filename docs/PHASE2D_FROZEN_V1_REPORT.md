# Phase 2D frozen-input investigation, version 1

Scientific status: **PARTIAL**. Production cross-platform agreement remains
**unresolved**. This continuation adds diagnostic implementation, not a verified
scientific correction. Earlier uncommitted work and reports are retained.

## Verification and preservation

Repository and remote are the requested research repository. Branch:
`codex/phase2d-cross-platform-reproducibility`; HEAD:
`5a415c457e9f60c983a52d309a242583d73b40b6`. Ancestry passed. No reset, merge,
force push, website access, commit or publication was performed here.

The user reports an independent regular-Windows-PowerShell verification of
**127 pytest tests and compilation PASS**, with all **247 preserved files**
verified. That is the existing host checkpoint, not an execution claim by this
continuation. One direct pytest invocation through the prescribed `.venv`
launcher here failed before Python startup with a configured-interpreter access
error. It executed zero tests. No alternate interpreter, permission workaround,
execution-policy change or repeated environment troubleshooting was attempted.
The regular host environment should be used as already verified.

All 247 original files were rehashed successfully here. Before development,
all 26 preexisting uncommitted files were copied and hash-checked under
`results/phase2d/continuation-snapshot-20261031/`; `inventory.csv` records their
original paths, lengths and SHA-256. These include the earlier reports, scripts,
tests, workflow, failure records, 84-reference audit and 24 swap records.
Existing production model/optimization files and historical research results
were not edited. The new fixture copies raw JSON bytes without reserialization.

## Stronger attribution from the existing independent references

The earlier archived 90-digit input-swap experiment distinguishes the model
block (normal-response matrix, disturbance and weights) from the current block
(pre/frozen/recovered commands). This continuation inspected those results;
it did not rerun their field calculations. Differences below are 28-digit
decimal subtractions of their 90-digit reference strings, rounded for display.
Full summary strings and scope are in `frozen-v1-archived-attribution.json`.

| Linux reference versus Windows | Row 3, failed coil 3 | Row 4, failed coil 6 |
|---|---:|---:|
| Both model and currents changed | -3.45789029367831418e-11 | -2.5591445872421532e-12 |
| Only current block changed | -3.45644943707010878e-11 | -2.5561376301674068e-12 |
| Only model block changed | -1.44085660820166e-14 | -3.0069570747662e-15 |
| Coupled interaction | approximately -3.74e-26 | approximately 1.98e-26 |

The Linux NumPy-sensitivity cohort has the same archived values. The SciPy
sensitivity cohort has smaller archived total reference gaps:
`-2.4425646819367632e-12` and `-1.2342668942759312e-12`, respectively.
Those reference gaps are distinct from subtraction of rounded saved binary64
metrics; the original four failed JSON paths remain preserved.

Thus the current block accounts for approximately 99.96% and 99.88% of these
reference gaps. Each saved compensated metric already agrees with its own
worker's high-precision reference. Replacing only the final arithmetic with
more precision cannot reconcile the different optimizer-generated inputs.
Small projected gradients are not a ratio-error certificate.

**Established mechanism:** sensitivity of the recovery ratio to differing
computed coil currents dominates these two archived failures. **Not yet
established:** whether that current drift originates primarily in regenerated
training-field inputs, initial least-squares arithmetic, or subsequent solver
steps. The archived normal-response matrices cannot establish agreement of
all three raw Cartesian field components. No BLAS/vendor-specific claim or
production correction is justified until the controlled tests execute.

The installed SciPy `lsq_linear.py` source was reviewed: dense `exact` mode
initializes through `np.linalg.lstsq(A,b,rcond=-1)` and returns the unconstrained
solution with status 3 and zero bounded iterations when it is in bounds. This
is source evidence of the available path, not proof that every archived solve
took it. The new runner records the actual initial calls and termination.

## Frozen benchmark and independent calculations

`benchmarks/phase2d-frozen-v1/` has an 11-file SHA-256 manifest: recorded
25-coil/512-vertex geometry, eight raw worker model/current files, the original
247-entry source inventory, and a versioned descriptor. Eight prescribed exact
rational Cartesian probes remove trigonometric grid-generation differences.
Geometry and current files are copied byte-for-byte. No geometry is regenerated
for the primary raw-field comparisons. A separate native control regenerates
the original 10-by-24 training mesh and records its entire inputs.

The independent field reference uses the tangent/perpendicular finite-wire
integral, not the production endpoint-cross formula. For segment length L,
unit tangent e, projection z=e dot r, perpendicular vector rho, its contribution
is `C I (e cross rho)/|rho|^2 * [z/sqrt(|rho|^2+z^2)
 - (z-L)/sqrt(|rho|^2+(z-L)^2)]`. C is the recorded conventional binary64 1e-7.
It uses Decimal at 80/110 digits and the unchanged 1e-4 m near-wire rejection.
This is an independent evaluation of the same finite polygon; it is neither
a smooth-loop replacement nor a continuum/global-peak certificate.

Every Bx, By and Bz value is retained per coil and probe. Fixed dense, matched,
robust and two-outage current cases also record direct-current compensated sums
and unit-field-scaled compensated sums. Component absolute errors in tesla,
component relative errors, vector relative errors and acceptance thresholds are
reported. Relative error at exact zero is undefined, recorded as null; the
absolute gate still applies to every component. Precision convergence is checked
separately from the unchanged scientific rtol=1e-11, atol=1e-13 gates.

A designated Windows prepare job assembles the augmented fine-grid diagnostic
least-squares matrices and RHS **once**, seals them, and uploads one common
artifact. Every cohort downloads identical bytes and verifies their manifest.
Canonical little-endian binary64 hashes of the parsed vertices, probes, current
vectors and solver matrices/RHS are also compared exactly, so byte-identical JSON
is not the only check on the actual numerical inputs.
This avoids falsely treating independently rounded square roots or weight
assembly as identical optimizer inputs. The fine-grid solve is a separately
identified diagnostic, not the historical coarse-grid production fit.

Each solve records initial NumPy least-squares calls (input byte hashes,
initial solutions, ranks and singular values), verbose trajectory, final
currents, objective, optimality, active mask, status, iterations and solver
source hash. Zero iterations means no invented trajectory. If a bounded
iteration occurs, its public verbose table is retained; complete internal
iterate vectors are not available from that public API and remain a limitation.
Independent 90/120-digit pivoted normal-equation solutions provide references
only when precision agrees and the solution is strictly inside existing bounds.
Squared conditioning is acknowledged; these are not interval certificates.

Native training-mesh solves record their full matrices/RHS, geometry, coordinates,
weights and archived-current comparisons separately. This control and the
common-input solve distinguish regenerated model differences from solver
arithmetic. The two affected archived ratios are recomputed with compensated
arithmetic and independent 80/110-digit direct RMS references, retaining all
four model/current swap combinations for each Linux cohort.

## Implementation and hosted preparation

New implementation:

* `src/stellarator_robust/frozen_diagnostics.py`: independent references,
  component errors, complete comparisons and frozen-input integrity.
* `scripts/phase2d_frozen.py`: fresh-only seal/run/compare commands,
  instrumentation, native controls, references and retained failure artifacts.
* `tests/test_phase2d_frozen.py`: closed-form polygon field, winding, component
  gates at zero, nonfinite/clearance rejection, reference solves, frozen input
  tampering, immutable outputs and failed-worker comparison inventory.
* `.github/workflows/phase2d-frozen-inputs.yml`: Windows seal, four numerical
  cohorts, all three Linux-versus-Windows comparisons and always-attempted
  evidence upload. Existing Phase 2D production workflow is preserved unchanged.
* `.gitattributes`: preserve raw bytes for new frozen/evidence namespaces.

All new code/tests and this workflow are **unexecuted here**. Static review and
hash verification are not pytest, compilation, field/reference convergence or
hosted results. A passing fixed-input subbenchmark is explicitly named
`FIXED_INPUT_SUBBENCHMARK_PASS`, with scientific status PARTIAL. It cannot turn
the known failing production comparison into a PASS. Failed-but-complete worker
records still get an exhaustive raw comparison; missing/invalid workers fail.
Metadata, native controls and solver traces remain explicitly inventoried,
while common-input fields, currents and objectives receive unchanged gates.

Connected GitHub metadata now confirms PR #5 is open/unmerged, with head
`5a415c4...` and synthetic merge commit `23279366436b37a6c6715556ff266f1384d183ce`.
That explains the recorded worker checkout SHA; it is consistent with this PR's
checkout. The run metadata and original artifact IDs/digests were retained in
`frozen-v1-github-metadata.json`. The supplied extracted bytes have not yet been
authenticated against those ZIP contents. Hash consistency and origin
authentication remain separate claims. No PR was changed or merged.

GitHub independently confirms the completed **Phase 2C** run 41061184709:

| Actual job | Conclusion |
|---|---|
| Windows reference | success |
| Linux reference | failure |
| Linux NumPy sensitivity | failure |
| Linux SciPy sensitivity | success |
| Cross-platform | failure |

The API job records are in `frozen-v1-hosted-job-outcomes.json`. These actual
outcomes do not constitute execution of the new Phase 2D workflow, which remains
unexecuted. The known Linux failures must not be relabeled as successful.

## Remaining blockers and conclusions

1. Execute the new tests, compilation, independent raw-component/reference
   calculations and instrumentation in the already working Windows host.
2. Inspect their actual outputs; fix implementation defects before publication.
   No new raw-field numbers or optimizer replay results can be reported yet.
3. Run the four hosted environments against the same sealed input artifact.
   All Phase 2D hosted outcomes remain NOT RUN / unverified here.
4. Attribute residual current drift using those controls. Only then consider
   a mathematically justified, explicitly versioned production correction.
5. Match supplied extraction bytes to authenticated original ZIPs and arrange
   durable preservation of all 247 originals before publication. They remain
   untouched locally; the frozen fixture contains only the required raw subset.

No numerical tolerance, field model, solver setting, objective, constraint,
training cohort, historical reference or negative robustness result was changed.
Finite-scenario/small-holdout limitations, lack of global peak certification,
external-code and confinement validation remain. Exact host commands follow
in PHASE2D_FROZEN_V1_HOST_COMMANDS.md. This report supersedes earlier suggestions
to reinstall or generally troubleshoot the already working host interpreter.
