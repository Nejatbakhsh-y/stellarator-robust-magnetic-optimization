# Phase 2D scientific review remediation — 2026-10-31

Overall science remains **PARTIAL**. Production cross-platform reproducibility
remains **FAIL**. Upstream root cause remains **INCONCLUSIVE**. These are local
working-tree corrections, not a verified numerical checkpoint or publication.

## Baseline and scope

The branch was and remains `codex/phase2d-upstream-attribution`; HEAD is
`ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7`. All ten originally staged files
were inspected, together with AGENTS.md, the complete attribution workflow,
Windows-host automation, README commands, execution status, production verify,
fault audit, legacy comparison, geometry investigation, finalization and
comparison contracts. No branch/index/history/publication operation was made.

The full baseline porcelain-v2 status, staged raw diff and HEAD are retained in
`results/phase2d/review-remediation-20261031/baseline-{status,index,head}.txt`.
The baseline status excludes only the newly created remediation evidence folder.
All original staged blobs remain identical in the index; corrections are unstaged.
Preexisting untracked work was retained. `.venv/` remains ignored.

## Findings and corrections

| Finding | Exact correction and review locations |
|---|---|
| Hosted production sequence incomplete | `.github/workflows/phase2d-upstream-attribution.yml:79` adds the existing legacy comparison, geometry investigation and finalization commands after production verification and fault audit, using documented fresh-root arguments. Each runs even after prior failure; failures remain job failures. |
| Historical objects unavailable in shallow checkout | All three checkout steps now use `fetch-depth: 0`, `persist-credentials: false`; permissions remain only `contents: read` (`workflow:27`, `:65`, `:101`). |
| Historical provenance confused with local integrity | `upstream_attribution.py:89` checks the complete at-run source inventory and SHA256 against the specified original Git commit; `phase2d_upstream.py:63` exposes a historical review command. Missing objects/evidence fail; absent authenticated archive/run evidence explicitly remains INCONCLUSIVE with nonzero exit. No artifact is regenerated or substituted. |
| Loose dependency setup and insufficient provenance | New `scripts/phase2d_dependencies.py:9` installs exact tested dependencies with only the specified cohort NumPy/SciPy substitutions, pins build/reference/YAML tooling, forbids source-package fallback, checks installed versions and `pip check`, and retains requirements, pip logs, resolver download hashes, Python and numerical environment records. The four original cohorts and Python 3.11 are unchanged. |
| Raw source fingerprints could differ from checkout EOL conversion | Workflow environment at line 12 fixes hosted Git checkout EOL behavior consistently before checkout. Raw SHA256 records include source, scripts, configs, tests, workflows and dependency/project files. No numerical source algorithm was changed. |
| Empty/incomplete or altered evidence could reach comparison | `upstream_attribution.py:116` requires the complete worker file inventory, all manifest hashes, exact array/case/result/field inventories, environment/commit/source provenance, and consistency of PASS labels with solver and independent reference evidence. |
| Solver input identity was only parsed-object equality | `upstream_attribution.py:81` verifies both input hashes against the upstream seal and exact serialized bytes before controlled result comparison. `phase2d_upstream.py:35` preserves the original input bytes; workflow and host comparisons now pass the original seal digest. Signed zero cannot disappear through JSON numeric equality. |
| Historical diagnostic recorded hash failures but continued | `scripts/phase2d_hosted_attribution.ps1:54` requires the complete 59-entry historical worker inventories, checks actual file coverage, writes FAIL records and stops on hash mismatches. Successful local integrity still does not claim archive authentication. |
| Required uploads could silently find no evidence | Every upload now has `if-no-files-found: error` and `if: always()`. Dependency setup diagnostics are retained as well. Worker upload roots still match all downstream `upstream-worker` and `upstream-production` download paths. |
| Host rejected the requested branch | `scripts/phase2d_upstream_host.ps1:4` now checks the specified attribution branch without switching branches; line 49 supplies the required comparison digest. |
| Missing regression coverage | `tests/test_upstream_attribution.py:73` onward covers absent/empty/altered manifests, rehashed incomplete results, input fingerprints and signed zero, missing CLI comparisons and retained FAIL records, historical source substitution, unchanged historical outputs, independent references, and the parsed workflow's complete production sequence, cohorts, permissions, checkout and upload contracts. |

Scientific acceptance is unchanged: `rtol=1e-11`, `atol=1e-13`, refinement
limit `1e-4`, 512-segment quick production geometry, physical constraints,
current bounds, original field calculations and solver termination settings.
Independent Decimal references still reject active bounds as INCONCLUSIVE;
they do not substitute unconstrained solutions for constrained validation.
Negative recovery, historical fault failures and the failed 256-segment audit
were retained. No robust outperformance or confinement claim is made.

## Actual checks

| Check | Actual result |
|---|---|
| PowerShell parser, both modified `.ps1` scripts | **PASS**, zero parser errors |
| C# finite-wire reference compilation with Add-Type | **PASS** |
| `git diff --check` | **PASS**; only informational checkout EOL warnings |
| Historical preservation | **PASS**, all 247 original file SHA256 values unchanged |
| Branch/index preservation | **PASS**, same branch and all ten staged blob IDs unchanged |
| `.venv` pytest | **INCONCLUSIVE**, launcher exit 103 before Python startup |
| `.venv` compileall of src/scripts/tests | **INCONCLUSIVE**, launcher exit 103 |
| `.venv` analytical validation | **INCONCLUSIVE**, launcher exit 103 |
| `.venv` fresh-root production verifier | **INCONCLUSIVE**, launcher exit 103 |
| YAML structure | Manually reviewed; automated BaseLoader workflow contract added, **INCONCLUSIVE** until Python executes |
| Four hosted environments and wheel availability | **INCONCLUSIVE**, not dispatched or executed |

The configured base interpreter is unavailable at
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`.
This is the observed startup failure, not a demonstrated scientific test failure
or proof of a specific sandbox denial. No alternate interpreter, environment
recreation or execution-policy/security bypass was attempted. Exact commands,
logs and exit codes are in `review-remediation-20261031/python-attempts.json`.
The downstream quick, output, independent audit, study and full repeat checks
did not run. No current-result SHA256 has a complete passing validation record.

## Readiness and remaining deficiencies

The working tree is ready for another **independent code review**, with execution
limitations explicit. It is **not ready for scientific acceptance or publication**.
The Python regression suite, compilation, YAML contract and all required numerical
gates must execute on the existing functioning Python 3.11 host environment.
GitHub Actions is statically prepared, with its original restricted PR target and
types unchanged, no `pull_request_target`, and read-only contents permission;
hosted readiness remains INCONCLUSIVE pending actual execution.

Historical archive authentication is still unavailable for the supplied 247-file
download. The new historical command cannot yield overall PASS until authentic
run/archive evidence is supplied and separately checked. Self-reported manifests
and Git source equality are insufficient. Dependency versions are pinned and
resolved wheel hashes recorded, but no independently reviewed platform wheel
hash allowlist or hosted installation result is claimed. Hosted OS images,
Python patch versions and underlying BLAS builds are recorded rather than frozen.

Additional publication inputs are required: the new dependency setup script and
this remediation report must accompany the selectively restaged corrections.
The ignored local historical download is not a substitute for authenticated
publication evidence. No other implementation file is currently known to be
missing; execution may reveal further defects. No staging, commit, push, PR,
workflow dispatch, merge or historical-output overwrite was performed.

## Final scientific payload remediation (this continuation)

The earlier inventory-only remediation was insufficient. A rehashed worker could
still contain truncated/incorrectly shaped current arrays, malformed binary64,
missing termination records, empty reference/conditioning/recovery diagnostics,
or inconsistent status labels. Non-PASS workers skipped much of the old checking.
JSON duplicate keys, exponent overflow and extra array attributes were unchecked.
These are evidence-validation defects; the historical numerical FAIL is unchanged.

`upstream_attribution.py` now validates every worker JSON object before numerical
comparison, with unique keys and finite JSON numbers. Binary64 requires exactly
`shape` and `binary64_le`, integer nonnegative dimensions, canonical lowercase hex,
exact eight-byte element counts and finite decoded values. Required object keys
come from `capture`, `solve_inputs`, `field_replay`, `independent_field_checks`,
`environment`, and `stable_recovery`; no scientific producer output key was added.
The experiment's actual quick configuration determines all dimensions (240 coarse
points, 960 fine points, 24 coils, 512 vertices, 24/23 solver columns).

The verifier checks all three cases in both solver outputs, full current vectors,
bounds and failed-coil zero, the recorded support and unchanged solver arguments,
scaled and augmented inputs, termination status/success/message/iterations/cost/
optimality/active masks, residuals, projected gradients, singular values, ranks,
condition numbers, all driver/rounding/repeat records, reference certificates,
training diagnostics, and complete recovery evidence tied back to saved currents
and fine-grid inputs. It replays Decimal reference certificates from saved M/y;
a fabricated INCONCLUSIVE reason cannot substitute for an unavailable reference.
It checks all frozen fields, fixed-current field assembly, independent probe
coordinates, reference dimensions, production comparisons and derived statuses.
Current scaling can round fit.x, so pre-scaling diagnostics use the unchanged
numerical bounds rather than demanding impossible recovery of the original bits.
Exact solver-input byte equality remains a separate mandatory requirement.

All this applies to complete FAIL/INCONCLUSIVE workers as well as PASS workers.
Only the producer's actual complete gate results determine worker status. Missing
or malformed evidence is rejected, rather than becoming a scientific result.
The comparison CLI now labels rejected evidence MISSING or INVALID, while an
executed comparison of complete evidence is COMPLETE with its own PASS/FAIL.
The dependency setup script now also writes a SHA256 manifest on success/failure.
Local hashes establish integrity only, not external authenticity.

New tests use a module fixture built by the real capture/solve/field producers
and serialized through the real writer. Only its declared environment envelope is
adapted for the hosted-cohort contract; these are not hosted execution records.
One positive test accepts complete output, and another retains complete executed
solver failure as FAIL. Twenty-three mutation cases test rehashed incomplete or
inconsistent evidence, covering all fifteen requested negative categories plus
missing residual/reference payloads, recovery references, comparison objects,
unknown status, duplicate JSON keys and JSON overflow. Six additional cases test
malformed float64 dimensions, byte counts, whitespace and infinity. Existing
active-bound reference tests retain INCONCLUSIVE, never an unconstrained PASS.

### Actual validation and limits

* PASS: `git diff --check`; both host PowerShell files parse with zero errors;
  `.venv/` remains ignored; all 247 historical files still match the before hashes;
  all original index entries and HEAD remain unchanged.
* INCONCLUSIVE: full pytest, compileall and analytical validation each attempted
  with the existing `.venv` and each exited 103 before Python started. The launcher
  reports its configured base Python missing. This is not a demonstrated sandbox
  denial or a failed scientific test. No alternate interpreter or bypass was used.
* NOT EXECUTED: producer fixture, negative tests, fresh quick/output/independent
  audit/full repeat, dependency resolver, YAML test, and hosted experiments. No
  verified current-result SHA256 or completed research checkpoint is claimed.

Local review records are `results/phase2d/final-validation-{baseline,
python-attempts,integrity}.json` and `final-validation-staging-paths.txt`.
They are temporary diagnostic records, excluded from the staging recommendation.
The numerical code remains unexecuted here; runtime defects cannot be ruled out.
Reference replay and consistency checks are not adversarial execution attestation
or an independent proof of all solver iterations. Summary-only repeat/rounding
diagnostics cannot independently reconstruct an unsaved second solve trace.

### Hosted workflow and clean-checkout inventory

The complete workflow was reviewed. Four original Windows/Linux/cohort combinations,
Python 3.11, single-thread settings, full Git history, LF checkout controls,
read-only permissions, strict input seals, all three diagnostic comparisons,
all three independent production comparisons, and production verify/fault audit/
legacy comparison/investigation/finalization remain required. Comparison steps
use `always()` after the first; exceptions/nonzero exits are not swallowed.
Every upload uses `if-no-files-found: error`. Even if a partial worker upload
contains dependency logs only, downstream required-file checks fail. No workflow
was changed in this continuation, dispatched, or claimed successful.

The 16 direct existing entry-point dependencies were checked in parent HEAD:
`pyproject.toml`, `requirements-tested.txt`, `.gitattributes`, both phase2c configs,
`phase2c_verify.py`, `phase2c_fault_audit.py`, `phase2c_legacy_compare.py`,
`phase2b_investigate.py`, `phase2c_finalize.py`, `phase2c_compare.py`,
`phase2_study.py`, `phase2_training_audit.py`, `check_outputs.py`, `audit_quick.py`,
and `phase2d_reference.cs` (scripts under `scripts/`). Existing package modules,
tests and committed legacy benchmark data are also required; they are in HEAD.
`preserve_previous` and finalization depend on the committed Phase 2B objects and
Phase 2C history archives/inventories, including `inventory.json.gz`; full history
and those tracked files are mandatory. The ignored 247-file download is required
only by historical/local-host investigation, not the new hosted worker pipeline.

Exact tested dependency pins, wheel-only installation, installed-version checks,
`pip check`, resolver reports, runtime metadata and dependency manifests provide
auditable provenance. They do not establish wheel availability/compatibility on
the four hosted environments until installation executes. Already installed
packages may lack a download entry in pip's resolver report. There is no reviewed
wheel-hash allowlist, action commit pinning, immutable runner image or Python patch
pin; these are provenance/reproducibility limits, not a reason to loosen gates.

Recommended final commit/staging inventory is exactly these twelve paths, using
their final working-tree versions after review. **Nothing was staged.**

```text
.github/workflows/phase2d-upstream-attribution.yml
docs/PHASE2D_ATTRIBUTION_RUNBOOK.md
docs/PHASE2D_HOSTED_INVESTIGATION_41195815229.md
docs/PHASE2D_UPSTREAM_ATTRIBUTION_REPORT.md
docs/PHASE2D_REVIEW_REMEDIATION.md
scripts/phase2d_dependencies.py
scripts/phase2d_field_reference.cs
scripts/phase2d_hosted_attribution.ps1
scripts/phase2d_upstream.py
scripts/phase2d_upstream_host.ps1
src/stellarator_robust/upstream_attribution.py
tests/test_upstream_attribution.py
```

The dependency script is an execution requirement missing from the original ten
staged additions. This remediation document is a publication/review requirement,
although it is not imported at runtime. Do not use broad `git add .` or include
temporary results, backup folders or logs simply because they are present.

### Durable evidence and provenance

| Evidence category | Records and required treatment |
|---|---|
| Historical preserved source evidence | The original 247 files under `results/ci/phase2d-hosted-investigation-41195815229/`, plus committed Phase 2B/2C failure archives and source Git objects. Preserve originals verbatim. A future durable bundle must bind original bytes, path inventory, sizes, hashes, original source commit and failed comparisons. No original file was copied, rewritten, deleted or regenerated here. |
| Local diagnostic evidence | `hosted-attribution-readonly-41195815229/` and `upstream-preflight-20261031-091816/` are explicitly cited by the two scientific reports, including the original inventories, binary64 references/block swaps/current vectors/field probes and launcher logs. These cited records require a durable manifest-bound bundle and source/version/command metadata before publication; keeping an ignored directory is insufficient. Preserve superseded preliminary Decimal-cast diagnostics with their qualification. |
| Authenticated hosted evidence | A durable bundle needs repository/run/attempt/job/artifact IDs, source/workflow commit, authenticated GitHub metadata and archive digests, original archives and complete extracted manifests, environment/dependency records, all seals and comparisons, including failures. No newly authenticated hosted evidence was obtained here. Existing locally saved metadata is not independently authenticated merely by hashing it. |
| Reproducible benchmark fixtures | Committed configs, original source Git objects, legacy ZIPs/inventories and frozen fixture inputs/contracts are validation inputs. Retain exact bytes/hash contracts in Git or an explicitly bound durable archive; regenerate only new experiments, never substitute new files for historical evidence. |
| Temporary execution logs | `final-validation-*`, backups, access checks and abandoned/incomplete attempts are local diagnostics. Retain failure logs locally; include in a durable bundle only when a published claim cites them. They are excluded from the code commit inventory. |

The two staged scientific reports cite evidence that is presently outside the
recommended code commit. Their durable evidence bundle and external provenance
are unresolved publication blockers. A separate bundle inventory/digest must be
reviewed before publication; this continuation neither creates nor claims one.

### Windows-host verification commands

Run from this checkout with the existing functioning Python 3.11 environment and
ordinary script policy. Stop on any failure; retain logs and choose fresh output
roots. Do not replace the environment or overwrite README/historical results.

```powershell
$py = '.\.venv\Scripts\python.exe'
& $py --version
if ($LASTEXITCODE) { throw 'Python unavailable' }
& $py -m pytest -q
if ($LASTEXITCODE) { throw 'Regression failure' }
& $py -m compileall -q src scripts tests
if ($LASTEXITCODE) { throw 'Compilation failure' }
& $py -m stellarator_robust.cli validate
if ($LASTEXITCODE) { throw 'Analytical validation failure' }
.\scripts\phase2d_upstream_host.ps1
```

The host script performs sealed producer/repeat/comparison and the complete fresh
production quick, output checks, independent audit, study, quick/study repeat,
training audit, fault audit and finalization sequence. Its guard requires the
247 historical files. Literal README helper scripts `test_and_record.py` and
`reproduce_check.py` write hardcoded historical paths; do not run them over the
preserved originals. The fresh-root production verifier performs corresponding
tests and full numerical repeats with hash-bound records. No README checkpoint
verification is claimed until all required gates have actually passed.

Verdict: **INCONCLUSIVE for implementation execution and hosted readiness;
not publication-ready; overall science PARTIAL; historical production FAIL;
upstream cause INCONCLUSIVE.** No tolerances, production field calculations,
refinement limits, current bounds, solver settings, physical constraints or
scientific objectives were changed. No stage/unstage, commit, push, PR operation,
merge, history rewrite or hosted dispatch occurred.

### Validation closure follow-up

See `PHASE2D_VALIDATION_CLOSURE.md` for the final fourteen-path publication
recommendation, additional controlled-error/environment/comparison validation
corrections and regression cases. `PHASE2D_EVIDENCE_BUNDLE_MANIFEST.json` now
specifies 295 available original paths and SHA256 values; it is a bundle plan,
not a published archive or authenticated hosted evidence. The historical source
Git object is unavailable locally (`git ls-tree`: not a tree object). All three
Python checks again exit 103 before startup. Publication remains blocked; the
historical scientific FAIL and upstream cause INCONCLUSIVE are unchanged.
