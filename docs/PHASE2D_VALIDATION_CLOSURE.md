# Phase 2D validation closure — 2026-10-31

Software publication readiness: **BLOCKED pending execution and evidence preservation**.
Historical production cross-platform status: **FAIL**. Upstream numerical root
cause: **INCONCLUSIVE**. Scientific scope: **PARTIAL**. No current checkpoint is
verified. This report supersedes earlier readiness statements, not historical
measurements. STEP 17's standalone audit record was not supplied in this checkout;
the blocking categories below are those specified in the remediation request and
recorded in `PHASE2D_REVIEW_REMEDIATION.md`.

Checkout HEAD is `ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7`, branch
`codex/phase2d-upstream-attribution`. The index already contained ten additions;
seven have newer working-tree corrections. Those corrections must accompany any
future publication. Nothing was staged, unstaged, committed, pushed or dispatched.

## Findings and exact corrections

| Blocking finding | Final implementation / regression coverage |
|---|---|
| Rehashed incomplete solver outputs could pass inventory-only checks | `validate_inputs` and `validate_solve` require the actual producer's dense, row3 and row4 cases, both solver outputs, every current vector and diagnostic object. The producer fixture exercises `capture`, `solve_inputs`, `field_replay`, `independent_field_checks` and the JSON writer. Mutation cases cover absent currents/diagnostics/cases, empty solver and missing files. |
| Malformed binary64 and wrong dimensions | `unpack` requires exactly shape/hex, nonnegative integer dimensions, canonical lowercase hex, exact byte count and finite decoded values. Config-driven dimensions are 240 coarse points, 960 fine points, 24 coils, 512 vertices, and 24/23 solver columns. Truncated, extra-dimensional, malformed hex, nonfinite and six standalone serialization tests cover these checks. |
| Incomplete optimizer/termination and numerical diagnostics | Complete status/success/message/nit/cost/optimality/active-mask records, bounded currents, failed-coil zero, residuals, projected gradients, ranks/spectra/conditioning, driver vectors, repeat/rounding summaries and reference/recovery evidence are required. Recorded algebra is checked at unchanged tolerances; Decimal solver certificates are replayed. Missing termination/residual/reference and recovery corruption tests apply even to non-PASS workers. |
| Contradictory scientific labels | Recompute worker checks and require exact agreement with producer classification. Preserve executed complete FAIL/INCONCLUSIVE classifications. `test_complete_executed_nonpass_evidence_retains_classification` retains FAIL; `false_pass` and unknown-status mutations reject relabeling. Active-bound reference tests retain INCONCLUSIVE. |
| Fingerprints, manifest and artifact gaps | Require all ten worker files plus manifest, exact manifest coverage and SHA256, source equality to comparison checkout, external input digest, and exact serialized input equality across workers. Existing tests cover missing/empty/altered manifests, wrong hashes, extra files, fingerprints and signed zero. A local manifest proves integrity, not authenticity. |
| JSON ambiguity/nonfinite evidence | Strict JSON loader rejects duplicate keys, NaN/Infinity and exponent overflow. Rehashed duplicate-key and nonfinite-JSON tests remain required. |
| Uncontrolled malformed-structure exceptions remained | This continuation adds the public `verify_worker` boundary translating structural KeyError/TypeError/IndexError/AttributeError, overflow and Decimal errors into ValueError. FileNotFoundError remains distinguishable; system/execution failures are not indiscriminately swallowed. All rehashed-negative tests now require ValueError rather than accepting accidental structural exceptions. New null-diagnostics, null-field-inventory and invalid-Decimal mutations cover the boundary. |
| Comparison counters could exceed actual solver size | This continuation bounds repeat, rounding and reference-solver failure counts by the actual case size and rejects a positive failure count with zero maximum error. Added impossible-repeat/rounding/reference-count mutations and a focused comparison-record test cover this gap. No unsaved replay is invented. |
| Environment provenance keys could contain malformed values | This continuation validates producer string fields, the complete four-key thread environment, optional positive CPU count and threadpool list/string envelope. Added bad-environment-type and bad-threads mutations. Optional unavailable metadata remains allowed exactly as emitted by `environment`. |
| Hosted pipeline omitted required production stages / dependency provenance | Final working-tree workflow includes production verify, independent fault audit, legacy comparison, geometry investigation and finalization, in order. Dependency installer pins tested packages with cohort substitutions, wheel-only resolution, version checks, pip check, logs and a success/failure SHA256 manifest. Workflow contract regression checks four cohorts, stage order, restricted permissions and checkout/upload controls. |
| Publication inventory omitted necessary files and evidence | Dependency script and review remediation report are required. The exact fourteen-path code/review inventory below includes this closure and the new available-evidence manifest. Cited scientific records require a separate durable bundle; ignored directories are insufficient. |

The earlier working-tree fixes were inspected and retained. No new producer-only
field is required. The run CLI's optional explanatory `note` is not mandatory
scientific data. Valid producer-generated evidence remains covered by the positive
test, but acceptance has **not been demonstrated by execution here**.

## Workflow execution readiness

The four original Python 3.11 cohorts are Windows NumPy 2.4.6/SciPy 1.17.1,
Linux 2.4.6/1.17.1, Linux 2.3.5/1.17.1 and Linux 2.4.6/1.16.3. Full Git history,
LF checkout controls, one-thread numerical settings and `persist-credentials:
false` remain configured. Permissions remain `contents: read`; no privileged
pull-request event was introduced.

Workers download one sealed input and verify its externally supplied SHA256.
The comparison job verifies worker inventories/hashes and byte-identical inputs,
then runs all three diagnostic and all three full-production comparisons. Later
scientific stages/comparisons run with `always()` so an earlier failure does not
hide them. No `continue-on-error` masks failures. All uploads run on failure and
use `if-no-files-found: error`. Dependency-only partial uploads cannot satisfy
downstream worker/production evidence requirements. Full production verification
includes quick, output checks, independent audit, study, full quick/study repeat
and training audit; diagnostic agreement cannot replace these stages.

Static configuration is prepared; execution readiness remains **INCONCLUSIVE**.
Wheel availability, YAML regression, finalization and all four numerical runs
remain unexecuted. Actions use version tags, hosted images and Python minor-version
selection, not immutable action/image/patch pins. Resolver reports are provenance,
not a reviewed wheel-hash allowlist.

A read-only `git ls-tree` attempt for historical source commit
`babc88ccd5086b5ec3a6e1c215524636d86b3580` failed with `not a tree object` here.
That historical object is **unavailable locally**. Historical source verification
must fail until the actual object is available; no object was fetched or fabricated.
Full checkout history in Actions is necessary, but cannot guarantee that an
unreachable historical object remains available upstream.

## Exact recommended commit inventory

Use final working-tree versions after review; this is a recommendation, not a
staging operation. Preserve unrelated work and exclude temporary results/backups.

```text
.github/workflows/phase2d-upstream-attribution.yml
docs/PHASE2D_ATTRIBUTION_RUNBOOK.md
docs/PHASE2D_HOSTED_INVESTIGATION_41195815229.md
docs/PHASE2D_UPSTREAM_ATTRIBUTION_REPORT.md
docs/PHASE2D_REVIEW_REMEDIATION.md
docs/PHASE2D_VALIDATION_CLOSURE.md
docs/PHASE2D_EVIDENCE_BUNDLE_MANIFEST.json
scripts/phase2d_dependencies.py
scripts/phase2d_field_reference.cs
scripts/phase2d_hosted_attribution.ps1
scripts/phase2d_upstream.py
scripts/phase2d_upstream_host.ps1
src/stellarator_robust/upstream_attribution.py
tests/test_upstream_attribution.py
```

Execution also requires the existing tracked package modules/tests, pyproject,
requirements-tested, `.gitattributes`, quick/study configs, scripts
`phase2c_verify.py`, `phase2c_fault_audit.py`, `phase2c_legacy_compare.py`,
`phase2b_investigate.py`, `phase2c_finalize.py`, `phase2c_compare.py`,
`phase2_study.py`, `phase2_training_audit.py`, `check_outputs.py`, `audit_quick.py`
and `phase2d_reference.cs`, and committed historical archives/inventories including
`inventory.json.gz`. These are existing repository dependencies, not new staging
recommendations. Preserve their original Git objects and archive bytes.

## Precise durable evidence requirements

`PHASE2D_EVIDENCE_BUNDLE_MANIFEST.json` inventories **295 actually available files**:
247 original supplied historical files, 31 local hosted-investigation diagnostics
and 17 preflight records. Each entry specifies original relative path, byte length,
SHA256 and provenance qualification. Originals were only read and hashed. The
manifest is a bundle plan; no originals were copied or altered and no durable
archive was published. Publish the manifest alongside a separately preserved
verbatim bundle and record that archive's actual digest when one exists.

Historical source ID is the reported `babc88c...` full ID above. Investigation
source HEAD is `ecad1a2...` above with dirty additions; retain at-run source
fingerprints and code bytes, not just HEAD. Original commands, return codes and
numerical environments are retained in each worker's `execution.json`, result
metadata, `training-and-settings.json`, and inventoried diagnostic/preflight
execution-attempt JSON/logs. Preserve those complete records rather than inferring
commands from successful-looking summaries. The ordinary diagnostic entry point
is `scripts/phase2d_hosted_attribution.ps1`; some one-off binary64 diagnostics are
documented only by saved logs/source hashes. A complete executable source for every
historical interactive command is **not established**.

Preserve all failed comparisons, especially `all-failed-comparisons.json`, original
committed-reference comparisons and cross-platform/SciPy comparisons. Preserve
binary64 references/block swaps/current vectors/field probes, input matrices,
settings/source equality and conditioning records. Retain preliminary Decimal-cast
records with their superseded qualification; do not replace them. Preserve the
256-segment failure and committed Phase 2B/2C archives separately in Git.

Run 41195815229 is the locally reported historical attribution, **not newly
authenticated hosted provenance**. Original authenticated archives, their verified
digests, artifact/job/attempt IDs and the exact executed workflow bytes/commit
remain unavailable or unauthenticated. The new workflow has never executed here.
The separately saved `frozen-v1-github-metadata.json` describes other/frozen runs;
it must not authenticate run 41195815229 by association. No hosted success is
invented. Durable bundle completion and external authentication remain blockers.

## Actual validation and remaining defects

Executed in this continuation: working-tree and staged `git diff --check` PASS;
both PowerShell scripts parse with zero errors; `.venv/` remains ignored; all 247
historical files match the prior SHA256 baseline. The index was compared to the
saved original staged-entry inventory. No historical file was copied or changed.

The following existing-environment attempts each exited **103 before Python
startup**: `-m pytest -q`, `-m compileall -q src scripts tests`, and
`-m stellarator_robust.cli validate`. The launcher reports no base Python at
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`.
This is an environment startup limitation, **not demonstrated sandbox denial**
and not an executed regression/scientific failure. No alternate interpreter,
security bypass or environment recreation was used. GitHub CLI restrictions were
not inspected or bypassed.

Not executed: producer positive fixture, negative regressions, automated YAML
contract, quick experiment, independent audit, output checks, full reproducibility,
dependency installation and hosted workflow. No result SHA256 has a new complete
passing validation record. Summary-only repeat/rounding diagnostics cannot attest
unsaved solve traces. Local hashes cannot authenticate origin; independent field
checks use two probes per polygon. Runtime defects remain possible. The controlled
boundary does not claim resource limits for hostile arbitrarily large inputs.

On the functioning host, from this checkout, use the existing environment:

```powershell
$py = '.\.venv\Scripts\python.exe'
& $py -m pytest -q
if ($LASTEXITCODE) { throw 'Regression failure; retain logs' }
& $py -m compileall -q src scripts tests
if ($LASTEXITCODE) { throw 'Compilation failure' }
& $py -m stellarator_robust.cli validate
if ($LASTEXITCODE) { throw 'Analytical validation failure' }
.\scripts\phase2d_upstream_host.ps1
```

The host script uses fresh output roots for all required numerical stages. Do not
run hardcoded README helpers over original historical result paths. Retain the
fresh result hashes, failed attempts and full gate records. No publication action
is authorized by these commands.

No production optimization/field calculation was changed. `rtol=1e-11`,
`atol=1e-13`, refinement limit `1e-4`, 512-segment quick geometry, physical
constraints, current bounds, solver settings and objectives remain unchanged.
Finite-scenario minimax and small holdouts do not establish robust outperformance
or confinement validation. Software remediation awaits runtime verification;
historical scientific FAIL and causal INCONCLUSIVE remain separate conclusions.
