# Final research-demonstration release readiness

Observed 4 November 2026. Reviewed research source: `f1c3309b9c8887a29c6be22f2de4caa575f4c732`. This publication audit does not establish a new verified numerical checkpoint.

Research demonstration: COMPLETE WITH DOCUMENTED LIMITATIONS

Full scientific acceptance: NOT ESTABLISHED

Production acceptance: FAIL

## Environment diagnosis and regression

The existing `.venv/pyvenv.cfg` records Python 3.11.9 at `C:\Users\nejat\AppData\Local\Programs\Python\Python311`. Inside this session's filesystem sandbox, the launcher exits 103 with “No Python at …”; a direct path probe also reports Access denied. An authorized execution outside that sandbox starts **Python 3.11.9** using the same `.venv\Scripts\python.exe`. The previous publication drafts' claim that the base interpreter was missing was therefore not established: the observed blocker was sandbox access. No Python installation, dependency change, replacement environment, launcher edit or environment deletion was necessary. The existing environment remains preserved and ignored. The PATH Python is Anaconda Python 3.13.9 and was not used for validation.

| Executed check | Actual result |
|---|---|
| Existing Python outside filesystem sandbox | PASS; Python 3.11.9, exit 0 |
| `python -m pip check` using that environment | PASS; “No broken requirements found”, exit 0 |
| `python -m pytest -q --junitxml=results/ci/publication-audit-20261104/pytest.xml` | PASS; **961 passed, 2 warnings**, exit 0, 509.01 seconds |
| `python -m stellarator_robust.cli validate` | PASS; exit 0; 256-segment analytical-loop maximum relative error `5.0202428052203985e-05` |
| New standalone quick experiment, independent quick audit, output check and full reproducibility sequence | NOT RUN; no new result-SHA256-bound research checkpoint is claimed |

The suite was run in full, rather than only selecting a lightweight subset. Warnings concern pytest's `record_property`/xunit2 compatibility and an intentionally duplicated ZIP member fixture. The test log, JUnit XML and exit record are retained in the fresh ignored directory `results/ci/publication-audit-20261104/`. Their SHA256 values are:

- `pytest.log`: `afae29dba87e5cdcc16829d911c20e10ff20d3067011c01a64aeb12507d1d623`
- `pytest.xml`: `4b7477691245a507ec144ac5e9e61a58b09032886503303980971ebc4a6ac86b`

These are regression records, not fresh experiment or reproduction records. The original quick result still hashes to `83162de245bfa5f64fad773f0c8212ccb04d2ae8af8287c03589fd8ee8374889`, matching its historical audit and reproduction bindings. Byte identity and passing tests do not supersede adverse scientific findings. Historical statements that Python failed before startup describe earlier execution attempts; they are retained without changing numerical evidence.

## Hosted failures: infrastructure and science are separate

Read-only GitHub access observed all three PR-triggered workflows for the reviewed head completed with failure. This endpoint returns the first page of PR-triggered runs; it is not an inventory of every push/manual run. Full job logs were inspected, including every failed job in these three runs. The observations below concern the old research head, not checks on a later documentation commit.

| Hosted run / failing stage | Classification and precise finding |
|---|---|
| [scientific-validation 41633435324](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41633435324), validate / pytest | Evidence-provisioning failure: `test_all_71_original_archives` cannot read `results/phase2d/step49-original-archives-20261102-120255-a1314650/manifest.json`. **1 failed, 903 passed, 26 skipped, 1 warning**. Analytical/quick/output/audit steps skipped. |
| [STEP 33 41633435372](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41633435372), four capture jobs / pytest | Same missing manifest in all four logs. Linux: **1 failed, 903 passed, 26 skipped** per cohort; Windows: **1 failed, 947 passed, 6 skipped**. Subsequent capture uploads fail because capture never ran. Replay and compare skipped. |
| [Upstream attribution 41633435313](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/actions/runs/41633435313), four workers / pytest and production stages | Same evidence-provisioning failure. `phase2c_verify.py` subsequently raises `RuntimeError: tests failed`; downstream fault/legacy/investigation steps lack `upstream-production/quick/results.json`; finalization reports incomplete required stages. These cascades are not new numerical tolerance failures. |
| Upstream attribution, upstream compare job | Evidence failures: frozen upstream worker execution was skipped after pytest; three upstream comparisons exit 2. Production comparisons raise “Worker did not complete all required stages”. |
| Upstream attribution, four STEP 42 reciprocal replay jobs | Execution completed with no recorded errors; each replayed four captures and recorded four diagnostic passes. Exit 1 is deliberately retained by the script for scientific FAIL; it is not an interpreter/infrastructure crash. History evidence remains `MISSING_EVIDENCE`. |
| Upstream attribution, STEP 42 comparison | **Executed numerical FAIL**: 48/48 current-vector comparison records pass, but **24/32 recovery-ratio comparison records fail** the unchanged tolerance. Status is EXECUTED with no recorded errors; `fresh_comparison=FAIL`, root cause INCONCLUSIVE, production acceptance FAIL. These records include reference/self comparisons and shared inputs; they are not 80 independent trials. |

The five STEP 42 replay/comparison ZIPs were downloaded without executing archived code. All ZIP SHA256 values match the GitHub artifact metadata; all internal manifest entries match. They are retained only in the fresh ignored audit directory. The concise local `hosted-replay-summary.json` has SHA256 `5bc865b59b9afd29e81c633d1fe8154f56efa09f247dd020fe9c1bfc1336ce03`.

| Artifact ID / name | GitHub ZIP SHA256 |
|---|---|
| 13229468441 / step42-windows-reference | `e9ba5d8aa02dbfcee0699fc0f667333e0d84be943c3375acc6b43c3777bb06f4` |
| 13229323048 / step42-linux-scipy-sensitivity | `4842f739d14a1ea77b53c420b02b112e4dbdc31175c0ee32d70a790b3c2543c5` |
| 13229083044 / step42-linux-numpy-sensitivity | `603c9edb5a4baf28ec13b820d70d88c62b2698726bb80bd6041616d767974948` |
| 13229073032 / step42-linux-reference | `b11a8f7f9a78c96b6aad74c73719b7932fd81db3615442c79299723f3182293a` |
| 13228919277 / step42-comparison | `37069ba05137ecb50de33e63de9a5d278fa9cb0d85e50b659e269052180901ff` |

The missing archive path is ignored by Git and required unconditionally by its test. A clean hosted checkout therefore needs authenticated evidence provisioning. The local test passes with the local archive collection. Do not skip that test, fabricate/substitute fixtures, upload unreviewed evidence, reinterpret missing evidence as numerical success, or loosen thresholds. Resolving provisioning would not resolve the independently observed recovery-ratio failures.

## PR #7 diff and review requirements

[PR #7](https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization/pull/7) is open, draft, unmerged and reported mergeable. Source: `codex/phase2d-upstream-attribution`; actual target: `codex/phase2d-cross-platform-reproducibility` at `ecad1a2db55e91dfab9fdc63114b4cc4c3af9fb7`. That target is the local merge base. Default branch is `main`, observed remotely at `d711580800820b3b38bcd7006994c58b4665226c`. PR #7 alone does not integrate the work into main.

The complete original 137-file diff was inventoried against that actual target: 64,177 additions and one deletion. Every changed file was read by the structural audit, with all 52 Python files parsed, all 16 JSON files decoded, and all nine PowerShell files parsed without syntax errors. Changes comprise five YAML files, 37 Markdown files, 16 JSON evidence files, 15 text evidence files, nine PowerShell files, 52 Python files, one C# reference, pyproject metadata and .gitignore. The local inventory records every path and SHA256; it hashes to `3ec6bd5e7d668f4b9e4779703ece348d69b3a64e39ca7b25421073bce3356bd0`.

Scope and implementation review covered existing-file changes, diagnostic orchestration, serialization/manifest checks, numerical gate definitions, output-path protections, workflow dependencies and regression coverage. Findings:

- Existing-file changes are CI checkout provenance options, ignored local Phase 2D evidence, the README final section and added development dependencies. The sole deletion replaces the dependency list while retaining pytest.
- Existing production model/optimizer files, configurations, reference results and original audit are unchanged. The only new package module is investigation-only `upstream_attribution.py`; capture restores the temporarily instrumented solver in a `finally` block.
- No unintended deletion, historical numerical replacement or relaxed existing acceptance criterion was identified in this scope. New diagnostics and tests do not establish scientific acceptance.
- Confirmed integration defect: hosted workflows do not provision the local-only archive manifest required by the unconditional regression test.
- Confirmed reporting hazards: an empty legacy commit-status list is not a passing Actions result; deliberate nonzero scientific exits and missing-artifact cascades require different interpretations.
- The historical PowerShell helpers contain optional publication and expensive validation paths. They were reviewed without running them; no additional execution script was created.
- This is a full file-inventory/structural and targeted implementation review supported by executed regressions, not a claim of independent line-by-line mathematical certification of every diagnostic or numerical evidence row. Independent scientific review remains required.

Reviews and inline review threads returned empty lists. No submitted approval is established. Branch listing reports the target and main `protected=false`, and the ruleset collection returned `[]`; the branch-protection detail request returned HTTP 403, so precise mandatory review/check settings are not independently available. User-required validation and review gates remain binding regardless of that protection flag. No merge, retarget, default-branch change or protection bypass is permitted by this audit.

## Documentation and portfolio integrity

All five deliverables are present in `f1c3309`: [README](../README.md), [report](FINAL_RESEARCH_DEMONSTRATION_REPORT.md), [ten-slide presentation](FINAL_RESEARCH_PRESENTATION.md), [portfolio summary](FINAL_RESEARCH_PORTFOLIO_SUMMARY.md), and [completion record](FINAL_DEMONSTRATION_COMPLETION.md). Their **98 relative Markdown destinations exist and are tracked**. The report has 16 numbered sections; the presentation has 10 Markdown slides. No rendered PDF/deck is certified.

A wider scan of 86 Markdown files included inline and reference-style links outside code fences. No local destination was missing. However, **52 historical link occurrences resolve to 48 local-only paths** under ignored Phase 2D evidence. They occur in PHASE2D_METHODS, PUBLICATION, RESULTS, ROOT_CAUSE, VALIDATION, STEP40 and STEP41 documents. These links are not portable to a clean GitHub clone. They were not rewritten or deleted; future publication needs an authenticated, reviewed archival distribution strategy. The existing PHASE2B_RESULTS.md requires legacy cp1252 decoding; its historical bytes were preserved. External bibliography reachability and renderer-specific anchors are not certified.

The portfolio documents motivation, applied mathematical contributions, computational methods, reproduction procedures, historical findings and limitations, and links to the report/presentation. It preserves the negative robustness result, finite-scenario minimax scope, small/shared holdout limits and absent confinement/equilibrium/hardware validation. No license has been selected; public availability alone is not an open-source license. No Thea Energy affiliation, endorsement or device validation is implied.

## Publication handoff

The three previously untracked publication documents are retained and corrected: this audit, [replacement PR body](FINAL_PUBLICATION_PR_BODY.md), and [release-note draft](FINAL_RESEARCH_RELEASE_NOTES.md). Only these three documents are intended for the current documentation commit. Numerical source/configuration/results, historical reports and .venv are excluded. No environment-repair files are needed because the existing environment works with authorized access.

The earlier connected-tool attempt to update the PR returned HTTP 403, “Resource not accessible by integration”. Its remote description remains historical. GitHub CLI configuration access is separately denied and must not be inspected or bypassed. No remote metadata mutation is attempted in this continuation. Ordinary authorized PowerShell can later apply the prepared body:

```powershell
gh pr edit 7 --repo Nejatbakhsh-y/stellarator-robust-magnetic-optimization --title 'Research demonstration complete with documented limitations; scientific acceptance not established' --body-file docs/FINAL_PUBLICATION_PR_BODY.md
```

Release notes use the requested title and intended tag `research-demonstration-v1.0`, with the exact disclaimer. They are unpublished. No merge, release, tag creation/movement, default-branch change or history rewrite was performed. Any future publication must freshly check existing tags/releases and satisfy all specified validation/review requirements.

Remaining blockers: hosted archive provisioning; executed recovery-ratio comparison failures; incomplete full independent scientific validation and causal attribution; no current complete README result-SHA256-bound checkpoint; independent PR review; clean-clone historical evidence navigation; integration into the default branch; and restricted GitHub metadata-write access. Commit and push results must be reported from actual command outcomes, not inferred from this handoff.
