# STEP 33 validation record

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
