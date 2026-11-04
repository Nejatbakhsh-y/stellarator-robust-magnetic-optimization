# STEP48 independent source provenance and numerical evidence audit

2026-11-02. Scientific comparison **FAIL**; production acceptance **FAIL**;
overall scientific status **INCOMPLETE**; unique numerical root cause
**INCONCLUSIVE**. No verified research checkpoint is claimed.

Reviewed AGENTS.md, STEP46 and STEP47 reports, execution status and the retained
refinement diagnosis. HEAD is `fc698446870114451fde5b88b9c5608d9a8539a7` on
feature branch `codex/phase2d-upstream-attribution`. Only the STEP48 script,
test and this report are added outside ignored results. No staging, commits,
pushes, dispatches, workflow changes, production changes or PR #7 actions occurred.

Evidence is `results/phase2d/step47-20261102-100432-7e05bcf1/`.
The controlling assessment is its
`python-independent-20261102-105332-aaa12f1c/assessment.json`, SHA256
`0591f377a6bb82cd7afc929fe87ba554b73a1cff2d7ca6ab3c543f2dd61d84a5`.
This matches its adjacent manifest. That seal establishes local consistency,
not independent origin authentication.

Fresh output is beneath the supplied, preexisting empty output directory:
`results/phase2d/step48-provenance-20261102-110626-d776f555/local-review-20261102/`.
Its `status.json`, `source-records.json`, `numerical-records.json`,
`cross-capture.json`, `historical-before.json` and `validation-attempts.json`
contain the executed PowerShell/.NET inventory. Its executor is explicitly
identified; this is not represented as execution of the new Python program.
All 1,135 supplied evidence files, including the later Python assessment,
retain their original bytes. Older STEP47's 1,114-file count covered an earlier
inventory. No original evidence was overwritten.

## Source provenance findings

All 32 source maps were independently inspected, retaining every recorded
commit and digest: 4,192 file references, not unique source files.
Twenty maps contain 2,620 references at `4177d52...`; all match exact Git blob
bytes. Twelve maps contain 1,572 references at `8d87244...`; that exact commit
object is unavailable. No hash of failed Git stdout is used as source evidence.

| Commit | Exact object availability | ci.yml Git blob | SHA256 of blob bytes |
|---|---|---|---|
| `4177d52f1ac68f869147c2e3e02e1f8b876546d0` | Available | `5b1e1438f8089aac35ddc421a57f151fb2ec5183` | `21703ab6edc3f69ac9108531d92fb467f2b05fbe96ca5bb713fe61be91eed7ff` |
| `8d87244eb07b7ff6e811596728441aee8b2fd618` | SOURCE_COMMIT_UNAVAILABLE | Unresolved | Unresolved |
| `fc698446870114451fde5b88b9c5608d9a8539a7` | Available | `5b1e1438f8089aac35ddc421a57f151fb2ec5183` | `21703ab6edc3f69ac9108531d92fb467f2b05fbe96ca5bb713fe61be91eed7ff` |

Every supplied workflow digest is the `21703...` value above, including the
twelve older-source maps. Available path history establishes that revision
at `a491572519d9c81159911fcc2a00fa5a55c62927`, dated October 31. The preceding
available revision at `ad96ee2ac9e6265ca0b97caa5d0b88f13454f6b2` has blob
`8f86b61bbcfb79b7dadaf895f3fe30dcc1ca079c`, SHA256
`1ad003697c5c722abc3ed72a982acad2fa1564f2bc35f93f2578d2236306c6f9`.
Thus the recorded digest matches a known revised workflow. It does not establish
which workflow existed in the unavailable commit, or when the older manifest
was generated relative to that revision. Commit timestamps alone cannot date
unavailable artifact generation. Staleness or reassociation remains a hypothesis.

The UTF-8 path `.github/workflows/ci.yml` resolves exactly at available commits.
The 647-byte blob has LF bytes. Its CRLF-transformed SHA256 is
`771ee590cecbc866fe546e5ace759e0c655f6d87fc95de052fe162d03e643751`, which
is not the recorded digest. There is no demonstrated path, encoding or newline
explanation for the unavailable historical object. The source producer
`source_fingerprints()` hashes filesystem bytes, not Git blob objects; those
identities must be tested, not presumed identical. No original source-file copy
or ZIP byte stream is available to authenticate the older record independently.

STEP47 `source_check` emits the same "Git source blob mismatch" for a failed
Git retrieval and a successful retrieval with a different digest. Its numerical
entry point also defaults to the requested commit rather than the recorded
older identity. These are demonstrated diagnostic classification limitations,
not demonstrated corruption of `ci.yml`. STEP48 resolves this by separating
object availability, byte equality and source identity without modifying STEP47.

The four STEP42 captures preserve `8d87244...`; their parent run says
`4177d52...`. All twelve older source maps have this association conflict.
They are **SOURCE_IDENTITY_INCONSISTENT** relative to that parent run and
**SOURCE_COMMIT_UNAVAILABLE** for exact byte verification. The 27 older upstream
environment identities documented in STEP47 remain historical records.
No current blob is substituted for them. There are no newly established
**VERIFIED_MISMATCH** source-byte records; unavailable objects cannot prove one.

The checkout is not shallow. `git fsck --full` and connectivity checking succeed,
with dangling blobs reported; no missing reachable-object corruption is reported.
That does not recover an absent unrelated commit. No remote retrieval or GitHub
configuration inspection was attempted. Original ZIP count remains zero;
artifact metadata and extracted seals cannot authenticate absent ZIP bytes.

## Classification of all ten numerical records

The latest supplied Python assessment supersedes the earlier report's statement
that no numerical calculation executed. Ten records contain completed TRF solves,
exact-reconstruction checks, saved/fresh KKT certificates, 60/90-digit interior QR
references, Decimal recovery interventions and geometry probes. These are
completed **recorded calculations**, not ten passing scientific experiments.
Their ten adjacent input seals and recorded input SHA256 values independently
match actual bytes. All ten associated source maps match the requested Git
commit. None of these ten failed source or input authentication; the four
older STEP42 captures were rejected before numerical calculation and are not
part of the ten. Their failure messages remain in the original assessment.

| Run / capture cohort | Calculation and reconstruction | Source / input | Row3 recovery | Row4 recovery | Sampled geometry |
|---|---|---|---|---|---|
| STEP32 Linux NumPy sensitivity | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP32 Linux reference | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP32 Linux SciPy sensitivity | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP32 Windows reference | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP33 Linux NumPy sensitivity | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP33 Linux reference | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP33 Linux SciPy sensitivity | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP33 Windows reference | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP45 Linux reference | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |
| STEP45 Linux SciPy sensitivity | COMPLETE_RECORDED | MATCH / MATCH | FAIL | FAIL | 100/100 pass |

Per-record input hashes, matrix/RHS hashes, KKT values and unrounded recovery
deltas are in `numerical-records.json`. All 30 solver cases report success and
interior QR references. No solver-reconstruction failure appears among these
completed records. All 1,000 geometry probes agree, but two points per grid
over 25 polygons are not full-grid geometry verification. Original saved-result
ratio binding remains incomplete for every record. Archive origin, missing
STEP45 coverage and full acceptance requirements remain incomplete.

## Scientific attribution

Each saved/fresh intervention holds its own A/b/w fixed. Its recorded row3 delta
ranges approximately from -6.55e-11 to +5.48e-11; row4 from -4.30e-12 to
+1.86e-12. All twenty fail the unchanged ratio tolerance. These local replay
interventions support a current-to-field-to-ratio sensitivity pathway for their
own sealed input. They do not uniquely identify the platform/library mechanism
that produced the current differences. Negative row3 recovery is not a benefit.

All six Windows/Linux cross-capture comparisons report nonidentical M and y
for every case. Their current tolerance checks pass; their row3 interventions
fail and row4 interventions pass. These are distinct comparisons from the ten
local saved/fresh replays. Different generated solver inputs prevent attributing
their output differences solely to the solver. Fixed-current field/matrix and
fixed-matrix current interventions separate contributions locally; they do not
turn unequal upstream inputs into a controlled identical-input experiment.

Saved/fresh KKT maxima span approximately 2.66e-19 to 1.45e-18 for these
fixed-support box problems. Small stationarity residuals and interior high
precision QR references support local optimization quality, not reproducible
binary64 vectors or bounded recovery error. Quantitative solver condition numbers,
cross-environment identical-input runs and a controlled driver/kernel experiment
remain absent from this new audit. QR precision agreement is empirical, not an
interval certificate or a validation of the entire minimax optimization.

For R=(L-P)/(L-B), the gradient in B,L,P order remains
`[(L-P)/(L-B)^2, (P-B)/(L-B)^2, -1/(L-B)]`.
Recorded row3/row4 denominator scales remain about 5.47e-11 T and 5.22e-10 T,
above the guard but cancellation-sensitive. Failures persist in recorded
high-precision arithmetic; binary64 quotient formatting alone is insufficient
to explain them. Saved-current field products are independently calculated from
captured matrices; sampled polygon integrals are additional limited geometry
evidence. Full-grid independent fields remain incomplete. Aggregate binary64
field/reduction/root/quotient effects are not an isolated serialization test.
The historical STEP44 one-ULP serialization issue remains preserved; no new
unique serialization, NumPy, SciPy, BLAS, LAPACK or OS cause is demonstrated.

## Implementation, regression attempts and final status

`scripts/phase2d_step48_provenance.py` accepts `--evidence`, `--assessment`,
`--output`, requires a fresh results directory outside original evidence, hashes
binary Git object output and writes `status.json`. It separates recorded source
identity from parent-run identity, tests alternate workflow revisions and newline
variants, checks adjacent input seals, fingerprints historical files and retains
all recorded hashes. Exit 2 denotes unresolved scientific requirements with a
complete report; unexpected audit errors produce exit 1 and an error report.
This project evidence cannot justify exit 0. Tests cover exact bytes, different
commits, stale maps, absent objects/paths, unsafe paths, metadata without ZIPs,
conflicting identities, incomplete calculations, false PASS prevention and
historical preservation. Synthetic fixtures are confined to tests.

The existing `.venv/Scripts/python.exe` still exits **103 before startup**,
reporting its configured Python311 base executable unavailable. Targeted pytest,
complete pytest, compileall, pip check, STEP48 execution, analytical validation,
fresh quick experiment, output checks, independent audit and full reproducibility
were attempted; all ten commands fail before execution. Exact commands and
messages are preserved in `validation-attempts.json`. Tests, compilation and
dependency integrity are **unverified**, not passing. No replacement environment
was used. The inline PowerShell review completed; direct `.ps1` execution was
blocked by the host execution policy. Git whitespace and integrity checks succeed;
these do not establish Python correctness. `.venv/` and new results remain ignored.

| Required final field | Status |
|---|---|
| Source provenance | INCOMPLETE: 2,620 matches; 1,572 unavailable-object references and upstream identity conflict |
| Artifact authentication | MISSING_EVIDENCE: no original ZIP/source artifact bytes |
| Independent numerical execution | Ten COMPLETE_RECORDED calculations; fresh local Python execution unavailable |
| Recovery-ratio validation | FAIL: both rows fail all ten local replays; original-result binding incomplete |
| Solver reproducibility | INCOMPLETE: unequal cross-platform inputs; controlled mechanism unresolved |
| Unique numerical root cause | INCONCLUSIVE |
| Scientific comparison | FAIL |
| Production acceptance | FAIL |
| Overall scientific status | INCOMPLETE |

Unresolved blockers are the unavailable older commit and original artifact bytes;
run/capture identity association; missing STEP45 artifacts; original saved-result
binding; failed recovery comparisons; full-grid geometry and quantitative solver
conditioning; authenticated identical-input cross-environment controls; working
required Python runtime and passing regression/dependency/README/full-repeat gates.

All criteria remain unchanged: rtol=1e-11, atol=1e-13, refinement=1e-4,
denominator guard=1e-15 T, original Biot-Savart equations, +/-3000 A bounds,
TRF/exact solver with tol=1e-12 and max_iter=1000, and 512 quick segments.
Original historical failures remain preserved. Finite-scenario minimax and small
holdout samples establish neither general robust outperformance nor confinement.
