## STEP 34 permanent Python/YAML verification repair (2026-10-31)

production_acceptance = **FAIL**; scientific_status = **PARTIAL**.
Local implementation only; no new verified research checkpoint is claimed.
The prior four uncommitted STEP 33 files were inspected and their trigger,
source-SHA, stage guard and discovery corrections preserved.

The supported command is now:

```powershell
python scripts/verify_phase2d_step33_workflow.py .github/workflows/phase2d-step33-causal.yml
```

The validator reads a normal path argument using pathlib.Path and
encoding="utf-8-sig", parses with yaml.safe_load, and handles both quoted `on`
and PyYAML YAML 1.1's boolean trigger key. It rejects duplicate mapping keys,
missing/malformed contract fields, incorrect trigger branches, absent synchronize
or manual dispatch, pull_request_target, incomplete capture/replay cohorts,
invalid compare dependencies and unsafe global or job permission grants.
This is a project contract validator, not a complete GitHub Actions schema validator.
PyYAML must be installed in the executing environment.

The host calls the standalone script with an argument array before tests and
publication. Its optional --host-preflight also replaces the two existing inline
Python interpreter/dependency snippets, so the host transfers no Python statements
through shell quoting. Existing publication file restrictions now include the two
new Python files. No commit, push, merge or workflow dispatch was performed.

New regression cases exercise invalid and missing YAML, required fields and jobs,
every missing cohort in capture and replay, permissions, dependencies, duplicate
keys, quoted/unquoted trigger keys, BOMs, paths with spaces, shell-independent
subprocess invocation, process exit status and Python 3.11 syntax parsing.

Validation attempts in this session:

- git diff --check: PASS.
- Available Windows PowerShell parser: zero host syntax errors.
- Existing .venv pytest, compileall and standalone validator: blocked before
  interpreter startup; the configured Python311 executable is missing.
- No new test count, Python 3.11 runtime pass or PowerShell 7 runtime pass is
  asserted. The earlier 311-test result supplied with this task does not validate
  these changes. The Windows host must execute the new and existing regressions.
- Analytical, quick, independent audit, output and full reproducibility gates
  remain unverified for this repair; no result-file SHA256-bound scientific pass
  is claimed. Production calculations, gates, historical results and failed
  evidence were not changed.

## STEP 33 trigger and verification repair (2026-10-31 session)

production_acceptance = **FAIL**; scientific_status = **PARTIAL**.
This repair is prepared locally, with no commit, push, merge or dispatch.
No new research checkpoint is claimed verified.

Authenticated connected API inspection confirmed draft PR #7 is open, with
head `codex/phase2d-upstream-attribution`, source
`cf77cf5466beadec7bd273e5c72ce9732cf253a7`, and base
`codex/phase2d-cross-platform-reproducibility`.
Contrary to the earlier empty CLI observation, the repository run API now exposes
[STEP 33 run 41256776296](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41256776296)
for that exact source, event `push`, workflow ID `403150023`. It progressed from
in_progress to completed/failure during inspection. All four capture jobs and all
four replay jobs succeeded; the compare job's Python comparison command failed.
Thus this is an observed failed hosted workflow, not an absent workflow. No
artifact download or independent hash-bound numerical revalidation was performed
here; the specific numerical cause remains unverified.

Registration and ability to execute are demonstrated for that existing run.
The connector rejected workflow-list and Actions-permissions endpoints as outside
its supported endpoint set. Repository policy settings were not inspected through
another route, and GitHub CLI configuration was not inspected or bypassed.
The original cause of the transient empty listing cannot be established from
these observations; no claim that default-branch absence prevented push runs is
supported. Existing CI workflows use PR base filters for earlier research branches;
STEP 33 previously had only push and manual dispatch events.

The repair preserves push and adds opened/synchronize/reopened PR events targeting
the actual base. Read-only contents permission, all four environments, numerical
commands and thresholds, artifact failure detection and digest verification remain.
All jobs explicitly check out the PR source SHA when applicable and use it for
expected-head comparison, avoiding accidental merged-source evidence. Compare
requires successful capture and replay jobs and successful preceding comparison
steps; artifact uploads retain always() for failure evidence.

Host discovery uses authenticated repository REST run metadata and exact workflow
path, avoiding workflow-name/default-branch lookup. It supports push source SHA
and PR association #7 with exact head/base/source identity. Authenticated PR detail
confirms repository and current source identity. A synthetic run SHA additionally
requires authenticated commit metadata with exactly the associated base and source
as its ordered parents. Eligible runs rank by creation time then numeric run ID;
duplicate IDs, missing timestamps, malformed states/attempts and ambiguous PR
associations fail closed. Polls are bounded (maximum 420, at most 60 seconds each).
Discovery examines at most 100 branch runs per poll and explicitly rejects a
truncated inventory rather than selecting from incomplete results. A large branch
history requires a future bounded pagination extension; it is not classified as
an absent run. Artifacts bind the selected run attempt; missing/ambiguous required
captures or replays prevent comparison. Earlier hosted failure cannot yield a
scientific PASS from a successful downloaded comparison. Comparison exit 1 remains
scientific FAIL, and hosted failures preserve an established local PASS.

Validation in this session:

- Available Windows PowerShell parser: zero host syntax errors.
- Extracted real helper smoke checks: push discovery PASS, bounded absence PASS,
  PR source discovery PASS, synthetic merge/source binding PASS, complete artifact
  inventory PASS, scientific FAIL with preserved local PASS PASS.
- git diff --check: PASS.
- Existing .venv Python 3.11 pytest, compileall and analytical validation attempts:
  blocked before interpreter startup (missing configured Python311 executable).
- Full production verifier attempt (fresh output path): same launcher failure;
  quick, independent audit, output and reproducibility gates could not execute.
- PowerShell 7 runtime attempt: executable cannot be accessed by the system.
- YAML reviewed structurally against existing workflows; no local YAML/Actions
  schema validator was available through the working Python environment. Hosted
  validation of the edited workflow is pending publication by the Windows launcher.

Regression tests now cover push/PR discovery, merge SHA, source/branch identity,
absence, pending/failed/successful runs, deterministic ranking, malformed metadata,
complete/incomplete artifacts, scientific FAIL and local PASS preservation, and
workflow stage/security guards. They are prepared but pytest could not execute in
this environment. Full local and hosted verification remains required. No
production equations, objectives, bounds, solver tolerances, 1e-4 refinement limit
or historical numerical evidence were changed. Infrastructure execution does not
establish reproducibility, robust outperformance or confinement validation.

References: [GitHub event semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
explain PR base filtering and synthetic merge SHA; [workflow triggering](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
explains token-originated event restrictions. These mechanisms are possibilities,
not an established diagnosis of the earlier empty observation.

# STEP 33 validation record

## Permanent PowerShell 7 syntax verifier (2026-10-31)

Scientific status remains **PARTIAL** (`scientific_status = PARTIAL`);
`production_acceptance = FAIL`. No research checkpoint is claimed verified.

The reported `inputFormat` parameter failure came from the cross-process
`pwsh -Command { ... }` invocation and argument binding. It does not establish
a syntax error in the host script. Use this permanent invocation from the
research checkout (one command):

```powershell
pwsh -NoLogo -NoProfile -NonInteractive -File scripts/verify_phase2d_pwsh7.ps1 -TargetPath scripts/phase2d_step33_host.ps1
```

`scripts/verify_phase2d_pwsh7.ps1` requires PowerShell 7, resolves a literal
filesystem target to an absolute path, rejects missing files, and uses
`System.Management.Automation.Language.Parser.ParseFile` without executing or
modifying the target. All returned parser errors are printed with the absolute
filename, line, column, error ID and message. Exit 0 means parsing succeeded;
exit 1 means syntax errors; exit 2 means target resolution or verification failed.
PowerShell versions below 7 are rejected by the version requirement.
No parser scriptblock is passed between processes. Windows PowerShell parsing
does not substitute for this check.

`tests/test_phase2d_pwsh7.py` covers invocation arguments, valid and invalid
syntax, missing files, paths with spaces, nonexecution and byte preservation,
and parsing both the verifier and host. Subprocess calls use argument arrays,
without `shell=True`. Runtime tests skip only if `pwsh` cannot be found; a
discovered launcher that fails to start fails the test.

Checks attempted in this repair session:

- The exact permanent command above could not start: the discovered WindowsApps
  `pwsh.exe` reported that the file cannot be accessed by the system.
- `.\.venv\Scripts\python.exe -m pytest -q tests/test_phase2d_pwsh7.py tests/test_phase2d_step33_host.py`
  could not start: the environment's Python 3.11 base executable is missing.
  No pytest test executed in this session.

The user reports prior Windows-host results of 2 targeted tests, 24 host tests,
and 292 full regression tests passing. These are prior reported results, not
reruns here and not verification of the newly added verifier.

The existing host and host regression tests were inspected and preserved:
`--limit` uses string `'100'`, lookup is commit based, selection returns one
eligible run ordered by timestamp then numeric ID, missing runs do not pass,
and hosted orchestration failures retain an established local PASS. This repair
adds only the verifier, its regression module and this documentation section.
Historical evidence and numerical gates remain unchanged. No scientific gates
were rerun, and no scientific acceptance is claimed.

Remaining verification is to execute the command and regression module with
working PowerShell 7 and the existing Python 3.11 environment. All required
README, analytical, quick, independent audit, output and full reproducibility
checks with result-SHA256-bound passing records remain prerequisites for a new
research checkpoint claim. No staging, commit, push, merge, dispatch or GitHub
configuration access was performed.

## Targeted regression repair (2026-10-31)

Scientific status remains **PARTIAL**; production acceptance remains **FAIL**.
This section supersedes the discovery ordering description below; historical
validation records remain preserved.

The mocked CLI received integer `100` because PowerShell had not performed native
argument conversion. The invocation now supplies string `'100'`. Windows
PowerShell's JSON-array pipeline behavior allowed filtering/sorting to operate on
an array as one object, returning both runs. Explicit enumeration now filters
individual records by exact SHA, workflow name, push event and branch when present.
No branch is inferred when metadata is absent. Exactly one eligible run is chosen
by creation timestamp descending (missing timestamps sort last), then numeric run
ID descending. Without timestamps, numeric ID determines the selection. Invalid
timestamps/IDs, duplicate eligible IDs, invalid JSON and non-array responses fail
discovery rather than producing a scientific comparison. Commit-based discovery
continues without a workflow selector.

The existing assertions are unchanged. Added regression cases cover timestamp
priority, timestamp ties and malformed/ambiguous metadata. Initial report fields
now explicitly separate local validation, hosted execution, hosted discovery,
hosted scientific comparison, numerical attribution, production acceptance and
overall scientific status. Hosted failures preserve established local validation.

Checks actually executed in this repair session:

- Direct mocked extracted-helper checks under Windows PowerShell passed both
  reported regression scenarios, string argument typing, timestamp priority,
  numeric ID ties, exact identity rejection, malformed timestamp/ID rejection,
  duplicate-ID rejection and local PASS preservation. These are supplemental
  checks, not executions of the pytest tests.
- Windows PowerShell static parsing passed with zero syntax errors.
- `git diff --check` passed.
- Both named pytest regressions, the entire host pytest module, all pytest tests
  and `compileall -q src scripts tests` were attempted using the existing `.venv`.
  None started: its Python 3.11 base executable is missing.
- PowerShell 7 syntax verification was attempted, but its launcher could not be
  accessed by the system. The Windows PowerShell parser is not a substitute for
  this required check.

Only the host script, host regression tests and this report were edited for this
repair. Production physics, optimization, solver tolerances, numerical acceptance
criteria and original results were unchanged. Existing unrelated work was retained.
No commit, push, merge, workflow dispatch or GitHub access was performed.

Remaining verification: restore the ordinary Python 3.11 and PowerShell 7
executables, execute both named regressions, the host module, the full regression
suite, compilation and PowerShell 7 syntax verification. No research checkpoint is
claimed verified. Full README/analytical/quick/audit/output/reproducibility gates
with result-SHA256-bound records remain necessary before any new checkpoint claim;
hosted scientific comparison and numerical discrepancies remain unresolved.

## Workflow discovery repair (2026-10-31)

Scientific status remains **PARTIAL**; production acceptance remains **FAIL**.
This repair does not establish production reproducibility or numerical agreement.
The original implementation-stage record below is retained as historical evidence.

The later saved `step33-20261031-191651-e684d712/host-validation/execution.json`
records zero exits for every local Python stage through finalization, implementation
`LOCAL_GATES_PASSED`, published commit `b546975f1163e0de66a1153ceb505dca2677dcbc`,
and subsequent `Workflow listing failed`. Its local `FAIL` is an orchestration
classification defect, not evidence of a failed local calculation. The failing
path was the post-push `gh run list --workflow phase2d-step33-causal.yml`
lookup, which the host reported as HTTP 404 because this newly introduced workflow
was absent from default branch `main`. The stale recorded stage `finalization`
also obscured the actual failure location. Source history confirms that commit
introduced STEP 33's workflow and host script together. No historical record was
rewritten to correct its labels.

Discovery now uses repository/commit listing, limit 100, without `--workflow`.
It filters case-sensitively by source SHA, exact workflow name, `push` event, and
research branch when returned. The latest matching run ID is selected. At most
420 queries with 30-second intervals are made; query failures stop immediately.
Intermediate absence is `NOT_YET_VISIBLE`; exhaustion records
`NOT_FOUND_WITHIN_BOUND` and execution `NOT_EXECUTED`. This observation cannot
prove that a run will never be created. A visible unfinished run remains
`RUNNING`. API/discovery errors, missing artifacts, inconclusive comparison,
completed numerical failure and successful hosted validation remain separate.
Run conclusions `startup_failure` and `timed_out` explicitly record hosted
infrastructure failure; the separate `hosted_run_outcome` preserves that
observation if artifact checks subsequently fail.
An unsuccessful hosted conclusion alone never proves numerical failure; a
passing downloaded comparison with an unsuccessful hosted conclusion records
`HOSTED_INFRASTRUCTURE_OR_SOFTWARE_FAILURE`, requiring job inspection to determine
the cause. Comparison exit 1 records scientific `FAIL` and a nonzero host exit.
Only comparison exit 0 plus successful hosted conclusion yields hosted `PASS`.
Later orchestration failures preserve an established local `PASS`; actual local
gate failures retain their existing `FAIL` or launcher `INCONCLUSIVE` result.

Added `tests/test_phase2d_step33_host.py` (previously absent) exercises extracted
host helpers with a fake `gh`: branch-only discovery, exact name/SHA/event/branch
rejection, bounded missing and pending cases, comparison exits 0/1/2, unsuccessful
host conclusion, missing artifacts, and local PASS preservation. Static guards
cover publication gating, branch push trigger and absence of dispatch/merge/force.
The host publication allowlist includes this new regression file.

Repair validation actually performed: Windows PowerShell static parser passed;
mocked extracted helpers passed identity rejection, missing/pending run,
comparison exit 0/1/2, missing artifact, infrastructure/software status and local
PASS checks; `git diff --check` passed. An initial ad hoc smoke harness failed due
to array handling in that harness; the corrected harness passed. The `.venv`
Python launcher cannot find its Python 3.11 base executable, so the requested
pytest invocation could not start. The PowerShell 7 launcher also cannot start.
The pytest suite, PowerShell 7 host runtime, full numerical gates and live repaired
GitHub discovery are therefore **unverified in this repair session**. No checkpoint
is claimed verified. No commit, push, dispatch, merge or default-branch change was
performed; CLI configuration was not inspected or bypassed.

Read-only connected inspection of historical run `41231422708` confirmed worker
success and all six diagnostic/production comparison steps failing, consistent
with retained evidence. Those failures and the original STEP 32 evidence under
`step32-host-20261031-183500-a1965e0d` remain intact. Production equations,
objectives, bounds, tolerances (`rtol=1e-11`, `atol=1e-13`) and refinement limit
`1e-4` were unchanged. No inference of robust outperformance or confinement
validation follows from this orchestration repair.

Remaining: restore ordinary host executable availability; run the new regression
suite and all local scientific/software gates with fresh output; conditionally
publish from the Windows host using the existing push trigger; authenticate
required artifacts for the exact new commit; inspect hosted jobs and all four
cohorts and reciprocal comparisons. Independently validated, hash-bound production
reproducibility is still required before changing scientific acceptance.

## Original implementation-stage record

Software completion **INCONCLUSIVE**; scientific completion **INCONCLUSIVE**.
Production acceptance **FAIL**; overall scientific status **PARTIAL**.
Prepared code has not passed a runtime test in this implementation stage.

Evidence root: `results/phase2d/step33-20261031-191651-e684d712/`.

| Check | Status | Actual evidence |
|---|---|---|
| Existing STEP 32 software baseline | PASS | Original tests.log: 264 passed; host exit 0; recorded compilation and analytical validation pass. Not a STEP 33 rerun. |
| STEP 32 manifest bytes | PASS | 194 entries; zero hash mismatches; five complete inventories. |
| STEP 32 recorded sources | PASS | 96 recorded SHA256 paths match present files. |
| STEP 33 tests | INCONCLUSIVE | Attempted full pytest: launcher exit 103 before Python startup. |
| STEP 33 compilation | INCONCLUSIVE | Attempted compileall: same exit 103. |
| Analytical validation | INCONCLUSIVE | Attempted: same exit 103. |
| STEP 32 independent assessment | INCONCLUSIVE | Attempted: same exit 103. |
| Fresh capture/local controlled experiment | INCONCLUSIVE | Capture attempted: exit 103; dependent local replay cannot run. |
| Full production/repeat verification | INCONCLUSIVE | Verifier attempted: exit 103; no new hash-bound production checkpoint. |
| PowerShell 7 host execution | INCONCLUSIVE | Supplied executable could not launch: file cannot be accessed by system. No policy or installation change attempted. |
| Host static parse | PASS | Available Windows PowerShell parser: zero syntax errors. This does not validate PowerShell 7 runtime or publication. |
| Git integrity | PASS | git fsck exit 0, dangling objects reported and preserved; no cleanup performed. |
| Hosted metadata inspection | PASS | Read-only connector confirms draft PR #7 head and actual historical worker/compare outcomes; JSON retained. |
| New hosted numerical comparison | INCONCLUSIVE | No committed STEP 33 implementation; no dispatch/publication authorized in implementation stage. |
| Historical numerical comparison | FAIL | Run 41231422708 diagnostic and production comparisons failed for all three Linux cohorts. |

Runtime attempts and native exits are in `runtime-attempts.json`; PowerShell
launch failure is in `host-attempt.json`; static parser evidence is in
`powershell-syntax.json`. `step32-numerical-review.json` preserves the actual
saved conditioning, KKT and high-precision recovery records. These are records
read from the supplied successful host directory, not recomputed results.

New regression cases cover correct KKT signs at active bounds, infeasible and
nonstationary candidates, a coupled interior optimum, nonfinite rejection and
rejection of a relabeled Windows environment as Linux. They remain unexecuted.
The STEP 33 host reuses the inspected STEP 32 host stages, adds sealed historical
assessment, Git object integrity, explicit publication inventory and draft-PR
identity. Publication code remains unexecuted.

Remaining requirements: restore the existing host executables through ordinary
maintenance; run the nonpublishing STEP 33 host with all gates; inspect the new
Decimal KKT, bounded perturbation and component-field records; independently
authenticate original ZIPs/source provenance; then conditionally publish the
diagnostic implementation from the host and inspect all four completed cohorts
and reciprocal comparisons. Independently satisfy the original production gates
before any scientific acceptance change. No checkpoint verified claim is made.
