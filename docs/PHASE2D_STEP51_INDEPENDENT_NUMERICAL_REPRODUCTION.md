# STEP 51 independent numerical reproduction

2026-11-02. **BLOCKED before Python startup; not a verified research checkpoint.**
Scientific comparison **FAIL**; production acceptance **FAIL**; overall scientific
status **INCOMPLETE**; unique numerical root cause **INCONCLUSIVE**.

Work remained in the requested checkout at HEAD
`2ab944b2a38335feefbe082498db64321f120fc5`, on existing feature branch
`codex/phase2d-upstream-attribution`. AGENTS.md, the STEP 38–50 reports present
in this checkout, README, execution status and refinement diagnosis informed
this assessment. No separate STEP 43 or STEP 49 report was found in that report
series; the supplied original STEP 49 manifest is the archive trust anchor.
The supplied 62 STEP 50 / 905 full test passes are controller baseline claims,
not new executions by STEP 51.

## Executed original archive verification

PowerShell `Get-FileHash -Algorithm SHA256` independently read all **71 original
ZIP files**, with **71 matches and zero mismatches** against both
`verified_sha256` and `github_sha256` in the supplied manifest. Originals were
not extracted into or modified in their source directory. This establishes
consistency with supplied STEP 49 metadata, not a fresh GitHub API attestation.
Fresh internal source-manifest, semantic input-fingerprint and execution-identity
verification remains INCOMPLETE because Python did not start. Run/artifact
associations are retained from the original manifest, not newly attested.

Evidence is in
`results/phase2d/step51-independent-numerical-20261102-143359-7fa90e12/`.
Exactly the six requested JSON names are present. They were produced by an
explicitly labelled PowerShell fallback after the Python launch failed;
they are **not output from a completed Python assessment**. `status.json`
contains SHA256 seals for the other five records. `solver-reproduction.json`
contains each original ZIP digest, run/artifact ID and manifest digest.
No scientific assessment exit 2 is asserted for this attempted run: the actual
launcher process exit was **103**, before the program's exit contract could run.

## Implemented numerical investigation, execution still pending

`scripts/phase2d_step51_numerical.py` accepts `--archive-root`, `--manifest` and
`--output`, requires a new disjoint output directory and does not execute archived
code. It reuses STEP 50 bounded ZIP authentication/source checks, STEP 38 binary64
transport and semantic seals, STEP 40 schema/problem reconstruction and STEP 46
Decimal Householder QR, KKT and sensitivity arithmetic. These dependencies are
explicit reuse, not newly independent implementations.

For supported, sealed production captures it is designed to solve the exact
saved M/y with TRF/exact, normalized bounds [-1,1], tol=1e-12 and max_iter=1000.
Reconstruction differences are recorded separately instead of replacing original
serialized inputs. It records supports, row3/row4 fault identities (coil 3/6),
physical current scaling, singular values, condition numbers, saved/fresh objective,
feasibility and KKT diagnostics, and 60/90-digit interior QR references. An
out-of-box QR solution is not represented as a bounded reference.

Recovery calculations use exact decoded binary64 inputs, Decimal products and
sums, and saved/fresh/high-precision reference currents. They record numerator
and denominator changes, first-order terms, nonlinear remainder, maximum current
and projected field changes. Historical comparison/status JSON is retained by
run, artifact, member path and SHA256. Historical 21-failure and 11-failure STEP 33
cohorts and the earlier scalar-path failures must remain separate; repeated paths
are not independent experiments. The current implementation retains historical
records but does not yet independently enumerate and bind every historical failed
comparison to its worker-result currents. That requested investigation remains
unfinished, rather than presumed resolved by single-capture solves.

The new field routine directly integrates dl cross r / |r|^3 using Gauss-Legendre
quadrature on saved oriented polygon segments; it does not call production field
code or use production matrices to generate fields. It compares 16/32-order
quadrature, Bxyz fingerprints and component magnitudes, normal projections,
saved/fresh/frozen current reconstructions on training and fine grids. Production
matrices are comparison targets only. This checks quadrature on saved polygons,
not independently regenerated smooth geometry or the original 1e-4 segment
refinement requirement. No field PASS is claimed. Full Bxyz saved-result binding,
geometry-generation verification, segment refinement and independent field-based
recovery-ratio sensitivity remain incomplete.

Local Python/NumPy/SciPy, BLAS/LAPACK, loaded pools, thread environment and solver
settings are recorded when the program executes. Original Windows reference,
Linux reference, Linux NumPy sensitivity and Linux SciPy sensitivity are each
INCOMPLETE for fresh controlled execution. A local solve cannot substitute for
any of them. No unique OS/library/BLAS attribution is supported. Different input
hashes are not identical-input controls; reconstructed array differences are not
by themselves evidence of JSON serialization loss.

The program conservatively returns 2 for a completed unresolved assessment,
1 for unexpected execution failure, and has no PASS path while these mandatory
requirements remain incomplete. Software tests alone cannot yield scientific
acceptance. Additional implementation and execution are required to satisfy the
entire STEP 51 mission, including a demonstrable all-requirements exit-0 path.

## Attempted verification

All commands used the existing `.venv/Scripts/python.exe`; every invocation
returned **103** with:

```text
No Python at '"C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe'
```

Targeted STEP 51 pytest, full pytest, compileall on the two new Python files,
`pip check`, analytical CLI validation, a quick experiment targeting a fresh
STEP 51 location, output checks, independent quick audit, `test_and_record.py`
and `reproduce_check.py` were attempted. The STEP 51 CLI itself also failed
before startup. No tests were collected; no compilation, dependency or science
gate passed. No interpreter substitution, environment replacement or dependency
installation was performed. The README fixed-path helpers did not execute or
write any historical result. They should run in an isolated diagnostic copy
under this checkout when a working controller invokes them.

`tests/test_phase2d_step51_numerical.py` supplies deterministic archive/hash,
identical-input, binary64 perturbation, current bound/KKT, fault row 3/4 recovery,
high-precision QR/ratio, denominator guard, sensitivity, oriented field convergence,
missing seal/evidence, original capture reconstruction, attribution-incomplete
and false-acceptance checks. Tests and implementation are **unverified** here.
`git diff --check` passed but excludes these untracked files; it is not syntax
or numerical validation. `.venv/` remains ignored.

The controller can run the program with the supplied archive/manifest and a
**different fresh output directory**, since this attempt's evidence now exists.
Do not overwrite that evidence. All original acceptance criteria remain:
rtol=1e-11, atol=1e-13, refinement=1e-4, denominator guard=1e-15 T.
Production equations, objectives, bounds, constraints, fault definitions,
solver settings and workflows were untouched. Only the three requested source,
test and report files were added; no staging, commit, push, merge, workflow
dispatch or GitHub CLI configuration access occurred. PR #7 remains unmerged.

## Evidence-supported result

| Requirement | Result |
|---|---|
| Original ZIP-byte verification | 71/71 MATCH supplied STEP 49 metadata |
| Internal source / semantic input authentication | INCOMPLETE for fresh STEP 51 verification |
| Independent solver reproduction | INCOMPLETE; not executed |
| Independent magnetic-field verification | INCOMPLETE; not executed |
| Recovery-ratio validation | INCOMPLETE; historical FAIL retained |
| Numerical root-cause attribution | INCONCLUSIVE; A/B/C/D fresh controls unavailable |
| Scientific comparison | FAIL |
| Production acceptance | FAIL |
| Overall scientific status | INCOMPLETE |

Remaining blockers are the unavailable existing Python base, unexecuted final
implementation/tests and README gates, incomplete original-result binding and
all-failure analysis, full geometry/refinement verification, fresh controlled
four-environment measurements and unresolved historical scientific failures.
Finite-scenario minimax and small holdouts do not establish general robust
outperformance, confinement or device validation.
