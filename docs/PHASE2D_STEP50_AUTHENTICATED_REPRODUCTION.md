# STEP 50 authenticated original-artifact assessment

## Reinspection of the repeated Windows failure (2026-11-02)

The complete protected test and actual production entry loop were reinspected.
No production edit was made in this attempt: the mandatory original-string
guard already executes for every central-directory entry before any path
normalization. Repeating it cannot recover a backslash discarded during Windows
fixture serialization. The CPython 3.11.9 source linked below was rechecked.
Making this Windows fixture pass requires an authorized change that preserves
its intended unsafe bytes when writing the ZIP; that test change is currently
prohibited. No standard-library patch or rejection of legitimate `a/x` was added.

Targeted pytest, full pytest, compileall and pip check were attempted again with
the existing `.venv`; all returned exit 1 before execution because the base
Python executable is missing. None passed. `git diff --check` returned zero,
with the existing untracked-file coverage limitation. Production SHA256 remains
`3ccb57abb80d24e162d643227efad9f3718ecd52a9a9905f74daae20dcdf8d3a`;
the protected test SHA256 remains
`d3930940e56025347fc6270278793aef6d0576c4db2cf5505a9b63cabe6ce505`.
Only this report changed in this attempt. Archives and scientific records remain
untouched. Repair completion is not claimed: scientific comparison FAIL,
production acceptance FAIL, overall INCOMPLETE.

## Current repair and validation attempt (2026-11-02)

The protected test was read completely and its SHA256 remains
`d3930940e56025347fc6270278793aef6d0576c4db2cf5505a9b63cabe6ce505`.
The existing feature branch was retained. The production validator now retains
validated `(entry, name)` pairs in a complete name-validation pass before
opening any member content. The separate mandatory `chr(92)` preflight still
checks every `entry.orig_filename` before any path normalization, including
nested files and directories. All other protections remain in place.
Current production SHA256:
`3ccb57abb80d24e162d643227efad9f3718ecd52a9a9905f74daae20dcdf8d3a`.

The supplied Windows failure cannot be resolved by recovering information
already discarded by fixture serialization. CPython 3.11.9 source was checked
again: `ZipInfo.__init__` normalizes the host separator, and serialization uses
`filename`. The detailed diagnosis below still applies. No standard-library
monkeypatch, valid-name blacklist or test alteration was made. Accordingly this
is production validation hardening, **not a completed passing regression repair**.

Targeted pytest was attempted before editing. After editing, targeted pytest,
full pytest, compileall and pip check were each attempted through the existing
`.venv/Scripts/python.exe`; every command returned exit 1 at interpreter startup
with the missing-base-executable diagnostic retained below. Final attempts have
the same outcome. No Python test or compilation result is claimed. `git diff
--check` returned zero; the files remain untracked and outside its coverage.
Only the authorized production script and this report were edited. Original
archives, all 71 recorded SHA256 values, provenance and scientific evidence were
untouched. Scientific comparison **FAIL**, production acceptance **FAIL**, overall
**INCOMPLETE**. No commit, push, merge or workflow dispatch occurred.

## Latest investigation: Windows fixture loses the backslash (2026-11-02)

This section supersedes earlier uncertainty about the supplied Windows failure;
earlier failed attempts and evidence below are retained. The complete protected
test was inspected. `make()` constructs `zipfile.ZipInfo(name)` and writes it
using `writestr()`, then `test_unsafe_paths` calls production `archive()`.
The pre-edit production code already contained the exact required `chr(92)`
guard in both `archive()` and `safe()`. Repeating that guard is not a solution
to the Windows fixture failure.

CPython 3.11.9's `ZipInfo.__init__` preserves its input in `orig_filename` but
replaces the host separator with `/` in `filename`. ZIP header serialization
uses `filename`, not `orig_filename`. On Windows, the fixture therefore writes
`a/x` for the input `a\\x`; reopening the ZIP cannot recover the lost spelling.
The actual executed path is `make()` -> `ZipInfo` normalization -> `writestr()`
-> `archive()` -> original-name guard -> `safe()`. The failure is consistent
with valid `a/x` reaching the validator, rather than a literal backslash being
accepted by `PurePosixPath`. Source inspected:
[CPython v3.11.9 zipfile.py](https://github.com/python/cpython/blob/v3.11.9/Lib/zipfile.py),
`ZipInfo.__init__`, `_encodeFilenameFlags`, `FileHeader`, and `_write_end_record`.
This is a source-based diagnosis, not a locally executed Python reproduction.

The production change preflights **all** central-directory `orig_filename`
strings before normalizing **any** member path. The exact mandatory guard
executes for files, nested names and directories. All existing additional
checks remain unchanged. This strengthens ordering but cannot distinguish a
Windows-normalized fixture from a legitimately written slash-separated name.
No monkeypatch of the standard library, test-specific rejection, sanitization,
test change or pytest configuration change was introduced. Under the protected
fixture constraint, passing the supplied Windows case cannot honestly be
promised by an archive-reader correction. A future authorized fixture correction
would need to serialize an actual backslash, for example by restoring
`ZipInfo.filename` before writing. No such change was made here.

Post-edit production SHA256:
`254b4bb1ee1d3817ea8ad0465dd2eba8a1ba3d6b8973506a6b474a9192816d10`.
Protected test SHA256 before and after:
`d3930940e56025347fc6270278793aef6d0576c4db2cf5505a9b63cabe6ce505`.

All four required Python commands were attempted using the existing
`.venv/Scripts/python.exe`: targeted pytest, full pytest, compileall and pip
check. Each failed at interpreter startup because the configured Python 3.11
base executable is missing (diagnostic retained below). They are **UNEXECUTED**,
not PASS. `git diff --check` returned zero; these files remain untracked, so
that command does not cover their contents. Only the two authorized files were
edited. The existing feature branch was retained. No commit, push, merge or
workflow dispatch occurred. All original archives, 71 recorded digests,
provenance and historical scientific failures were left untouched. Scientific
comparison **FAIL**, production acceptance **FAIL**, overall **INCOMPLETE**.
This repair is not a verified research checkpoint.

## Follow-up: enforce rejection at the archive entry boundary (2026-11-02)

The controller's latest supplied failure remains evidence: the unsafe-path
subset reported **1 failed, 26 passed, 31 deselected**, specifically literal
backslash `a\\x` not raising. Before editing, the complete protected regression
file and production implementation were inspected. The test imports this exact
script by absolute file location; `make()` writes `ZipInfo(name)` using
`writestr()`, then calls `archive()` with the resulting ZIP SHA256. The entry
loop reads `entry.orig_filename` and calls `safe()` before normalization.
The pre-edit source already contained the previous standalone guard in `safe()`;
that earlier change is not presented as a new repair or an explanation of the
controller failure. Execution of different source bytes cannot be established
from the supplied traceback alone.

This follow-up adds the mandatory guard directly to the executed `archive()`
entry loop, immediately after `original_name = entry.orig_filename` and before
`safe()` or `entry.is_dir()` is called:

```python
if chr(92) in original_name:
    raise ValueError("Unsafe ZIP member path")
```

There is no file-only or directory-only branch around this check: it covers
every entry reached, including nested names and directory entries, without
replacement or sanitization. The existing `safe()` guard and all other archive
protections remain intact. Only the authorized script and this report were
modified. No archive, provenance record, historical result, numerical setting,
test, or pytest configuration was changed.

Production script SHA256 after this change:
`691d0618a9f9b14734e6d8658494d8f916f7d69530864a5eeaafc3a2347976f0`.
Protected test SHA256 before and after:
`d3930940e56025347fc6270278793aef6d0576c4db2cf5505a9b63cabe6ce505`.

Both the pre-edit targeted attempt and all four required post-edit Python
commands failed at `.venv/Scripts/python.exe` startup because its configured
base executable is missing. Targeted pytest, full pytest, compileall and pip
check each returned exit 1; none executed and none is PASS. The exact launcher
diagnostic is retained below. Post-edit `git diff --check` returned exit 0,
but the STEP 50 files are untracked and therefore outside that check's coverage.
The controller must repeat runtime validation against these script bytes.
No research checkpoint is verified. Scientific comparison remains **FAIL**,
production acceptance **FAIL**, and overall scientific status **INCOMPLETE**.
No commit, push, merge or workflow dispatch was performed.

## Permanent ZIP path repair (2026-11-02)

The supplied latest regression record is **57 passed, 1 failed**, specifically
`test_unsafe_paths[a\\x]` failing to raise `ValueError`. A literal backslash is
a POSIX filename character but a Windows separator. The inspected pre-edit
checkout contained a combined backslash rejection; the supplied failure has
not been reproduced here and its exact executed source bytes are unconfirmed.
The earlier unsuccessful repair and supplied failure remain evidence, not PASS.

The complete existing regression file was read without modification. Its
`make()` passes the literal name into `ZipInfo(name)` and `writestr`; the test
then calls `archive()` with the ZIP's SHA256. Inside `archive()`, every entry
passes `entry.orig_filename` to `safe()`, including nested files and directories.
The correction makes the original-string rejection a standalone guard before
component splitting, terminal-slash removal or path parsing:

```python
original_name = name
if chr(92) in original_name:
    raise ValueError("Unsafe ZIP member path")
```

No backslashes are replaced or sanitized. All other validation checks remain.
The test SHA256 before and after this repair is
`d3930940e56025347fc6270278793aef6d0576c4db2cf5505a9b63cabe6ce505`.
Only this report and the production script were edited during this repair;
the three STEP 50 files were already untracked when work began.

`safe` is now the single strict original-name validator. It checks POSIX and
Windows path grammars and every component before constructing a normalized
identity. It rejects backslashes, roots/drives/UNC, traversal, empty and dot-only
components, ADS/Windows-invalid punctuation, NUL/C0/C1 controls, trailing spaces
or dots, and reserved devices (including superscript device digits). Exactly
one terminal slash is allowed for a legitimate directory. No unsafe spelling
is repaired. ZIP validation uses `orig_filename`, avoiding Python's NUL-truncated
`filename`, and rejects discrepancies. Casefold identities include directories
and implicit parent spellings. Duplicate identities, file/directory conflicts,
links, special files and inconsistent directory metadata are rejected.

SHA256 authentication now feeds the same immutable bytes into `ZipFile` through
`BytesIO`. Every member, including directories, is read for CRC verification.
Archive/member/total-size, expansion, encryption and entry-count controls remain.
Extraction uses exclusive writes and resolved destination-boundary checks before
directory creation and before file creation. The output is required to be fresh;
this is not a guarantee against a concurrent hostile process changing filesystem
links between checks and writes.

Deterministic temporary ZIP fixtures retain the backslash regression and add
original-name/NUL, control, drive/UNC/ADS, reserved device, component, casefold,
normalized duplicate, nested directory, malformed directory, boundary escape,
invalid ZIP and original-byte/SHA preservation checks. Existing CRC, SHA,
missing evidence, manifest and no-false-scientific-acceptance tests remain.

Validation attempted with the existing `.venv/Scripts/python.exe`:

| Command | Result |
|---|---|
| `-m pytest -q tests/test_phase2d_step50_reproduction.py` | Cannot start interpreter; no test result |
| `-m pytest -q` | Cannot start interpreter; no test result |
| `-m compileall -q src scripts tests` | Cannot start interpreter |
| `-m pip check` | Cannot start interpreter |
| `git diff --check` | Exit 0; STEP 50 files are untracked, so this does not check their contents |

The launcher reports the missing base executable at
`C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe`.
No replacement interpreter was used. Targeted and complete regressions are
**UNEXECUTED**, not PASS. Original ZIPs and historical evidence were not modified;
the earlier integrity records below are preserved, not newly recertified by this
repair. The controlling host must execute all requested checks. Scientific
comparison **FAIL**, production acceptance **FAIL**, overall **INCOMPLETE**;
all original numerical gates and failed evidence remain unchanged. No research
checkpoint is claimed verified. No commit, push, merge or workflow dispatch.

2026-11-02. **Scientific comparison FAIL; production acceptance FAIL; overall
INCOMPLETE.** Original archive evidence has now been directly examined. Missing
original ZIPs and the five missing STEP 45 categories are no longer blockers.
Fresh independent numerical reproduction remains unexecuted because the required
existing Python 3.11 environment cannot start. This is not a verified checkpoint.

HEAD remains `fd08178d4912a5716456d8644bdfd2d0310b0e9a`, on feature branch
`codex/phase2d-upstream-attribution`. Applicable root AGENTS.md was read. No
previous research file, workflow, production equation, tolerance or original
evidence was modified. No commit, staging, push, dispatch, merge or PR operation
was performed. `.venv/` and results remain ignored. Only this report and the
requested STEP 50 Python program and regression file are added outside results.

## Executed evidence and trust boundary

Input root: `results/phase2d/step49-original-archives-20261102-120255-a1314650/`.
The supplied `manifest.json` is the STEP 49 authentication trust anchor. Matching
its GitHub metadata digests establishes original-byte consistency with that
supplied authority; this investigation could not obtain a fresh API attestation.

Output: `results/phase2d/step50-independent-reproduction-20261102-122643-76951ad7/`.
The five requested JSON files exist. They explicitly identify the executed
PowerShell/.NET fallback, rather than falsely claiming the new Python program
ran. `controller-fallback.ps1` retains that fallback's source. Its commands were
executed inline after direct script invocation was denied by execution policy;
no execution-policy setting was changed. Early attempts failed before producing
assessment JSON; their terminal errors are not scientific calculations.
Existing output records were never overwritten.

`status.json` records assessment exit classification 2 and hashes of the four
other required JSON records. The fallback itself returned 2. The Python launch
failed before program entry; no Python return code 2 is claimed.

| Output record | SHA256 |
|---|---|
| archive-authentication.json | `eac131e8b28e346a28adf3688b6ae26e4d7ae9676be2c30675487d90c59f2707` |
| source-provenance.json | `33571977d23188e882aa57032c7643208d7d5d8d5b3a0f67c7f266badb118a5f` |
| numerical-comparisons.json | `8f615ea8b096d81c027df18b81865463c4b0da1d6d6a21acbc7a52f490e1fd35` |
| remaining-blockers.json | `c4c886efcb065681ad385c92394de2f528cef9296343dd6be2620521f6b711aa` |
| supplemental-authentication.json | `b668a6537744f703e95e58cdcd7b8a838f4a55847be20e1834b2ba428f2d3b9c` |
| step45-inventory.json | `a7484e1423029d5821ffe38b349fb8e2f3a0cfc5f627a6fe9fe685a449eb9b83` |

## Original archive and internal integrity

All **71/71** original ZIP SHA256 values independently match both supplied
`github_sha256` and `verified_sha256`. Artifact IDs are unique; the resulting
inventory also has no repeated ZIP digests. All members were decompressed and
their CRC32 values recomputed against ZIP central-directory records. All 71
archives passed. The scan rejected traversal, absolute/drive paths, backslashes,
case-insensitive repeated file names and symlinks; none was observed. Parsing
used a 256 MiB ZIP bound, 128 MiB member bound, 512 MiB total per ZIP, 4,096-entry
bound and 1,000:1 expansion bound. No original archive was extracted to disk by
the executed fallback: member bytes were hashed in memory. Consequently,
**on-disk extracted-file integrity was not measured** and is not called PASS.
The Python implementation additionally rejects Windows reserved names, special
files and file/directory collisions and uses exclusive writes for new extraction.
Those additional regression checks have not executed here.

All archives contain applicable manifest records. **1,079 direct internal hash
references match, with zero mismatches.** This includes original inputs,
outputs and all five STEP 45 diagnostic/comparison output manifests. Forty-eight
references lack targets at the literal archive-relative location. The
supplemental scan finds exact matching content digests for **48/48** in other
authenticated archives from the same run. This recovers content, not proof of the
original absolute directory or an unambiguous archive association where identical
bytes occur more than once. Nested STEP 45 input manifests were checked separately.

The numerical record preserves original comparison/status/causal/historical JSON
as exact original JSON text with its member digest. Forty-nine `inputs.json`
members were inventoried; these are repeated and differently scoped records,
**not 49 independent numerical experiments**. Byte authenticity, internal seals,
run identity, workflow identity, source identity and scientific reproducibility
are separate claims.

## Exact source provenance

The locally available branch commit is
`4177d52f1ac68f869147c2e3e02e1f8b876546d0`. Recomputed Git object SHA1 values
match that commit, its root tree `bf827d94f8a1828b79019aed2679c2d720461ef6`,
and workflow blob `5b1e1438f8089aac35ddc421a57f151fb2ec5183`. The workflow's
raw-byte SHA256 is
`21703ab6edc3f69ac9108531d92fb467f2b05fbe96ca5bb713fe61be91eed7ff`.
All **2,882/2,882** file references in 22 source maps recording that branch
commit match exact local Git blob bytes.

The distinct merge identity
`8d87244eb07b7ff6e811596728441aee8b2fd618` occurs in 12 original source maps,
whose associated run metadata records the branch commit. STEP 49 records the
same root tree and workflow blob for both commits and records the merge's two
parents. Those supplied records are preserved. All **1,572/1,572** file
fingerprints in these merge-labelled maps independently match the available
branch's file bytes. There is therefore **no demonstrated different source
file among the recorded fingerprints**. The older claim of a demonstrated
source-file conflict is not supported by these recovered bytes.

This does not authenticate the missing merge object locally, make the two
commits identical, prove every unrecorded tree member identical, or establish
the exact checkout reference used by every job. A merge checkout is consistent
with the recovered records and supplied merge metadata; it is not independently
established as the sole association mechanism. No source identity is rewritten.

Retrieval was attempted through Git and the GitHub API. The first Git attempt
could not write `.git/FETCH_HEAD`. A second attempt used a new bare object store
under this output directory, leaving checkout metadata alone; GitHub port 443
was unreachable. The API likewise could not connect. No GitHub CLI configuration
was inspected. Exact merge-object and tree retrieval remains **UNAVAILABLE**, not
cryptographically disproved. The new Python program can attempt isolated Git
object recovery when run in an available environment.

## STEP 45 completeness

All **17/17** listed original archives were inspected: four captures, four
capture-dependency bundles, four worker/replay bundles, four diagnostic bundles,
and one comparison bundle. The five previously absent categories now present are
Windows capture, NumPy-sensitivity capture, Linux-reference diagnostics,
Linux-reference capture dependencies and SciPy-sensitivity capture dependencies.
Each archive has its exact original ZIP digest and internal member records in
the inventory. **179 direct STEP 45 internal references match**, including all
35 output-manifest references. The separate nested-input scan finds matching
authenticated bytes for **252/252** recorded references within STEP 45's run.
Counts describe references, not unique files. Completeness is established against
the supplied 17-entry inventory and expected cohort structure; no fresh remote
artifact listing was available. Inventory completeness does not imply valid
solver results or scientific acceptance.

## Numerical and scientific assessment

| Required assessment | Evidence-supported status |
|---|---|
| Original archive authentication | 71/71 match supplied STEP 49 GitHub digests; all CRC checks pass |
| Internal manifest authentication | 1,079 direct matches; 48 external content digests recovered; original path association limited |
| Historical source provenance | Branch objects verified; recorded merge fingerprints match branch bytes; exact merge object unavailable |
| STEP 45 artifact completeness | 17/17; all five missing categories recovered; 252 nested input digests present |
| Independent solver reconstruction | Fresh execution unavailable; implementation supplied but unverified |
| Independent field calculations | Fresh execution unavailable; no new geometry or field PASS |
| Independent recovery-ratio calculations | Fresh execution unavailable; no new row 3/4 numerical measurement |
| Cross-platform reproducibility | Historical comparison failures retained; no fresh controlled reproduction |
| Unique numerical root-cause attribution | INCONCLUSIVE |
| Scientific comparison | FAIL |
| Production acceptance | FAIL |
| Overall scientific status | INCOMPLETE |

The recovered STEP 32 and STEP 33 comparison statuses preserve diagnostic FAIL,
PARTIAL and production FAIL. STEP 45 preserves diagnostic COMPLETE with scientific
FAIL and production FAIL. STEP 42's comparison preserves execution EXECUTED,
scientific FAIL, production FAIL and inconclusive cause. Dependency installation
PASS or a completed diagnostic is not scientific PASS. Their original missing-ZIP
statements remain historical records; this assessment supersedes that particular
availability classification without replacing their numerical failures.

No fresh matrices, RHS vectors, bounds/support certificates, fault solves, KKT,
feasibility or objective residuals, fields, high-precision row 3/4 ratios,
perturbation responses, quotient conditions or singular-value condition numbers
were calculated in the required environment. Historical calculations embedded in
authenticated archives are original evidence, not fresh independent measurements.
The supplied Python path reconstructs captured problems using STEP 40 transport,
fresh SciPy TRF solves and separately implemented STEP 46 scalar Decimal
certificates, Householder references and full-grid matrix/current field products.
It explicitly does not certify independently regenerated Biot-Savart geometry.
It is incomplete for the full requested controlled environment/perturbation study.
No difference is uniquely attributed to NumPy, SciPy, BLAS, LAPACK or an OS.

## Execution and regression limits

The existing `.venv/Scripts/python.exe` reports:
`No Python at '"C:\Users\nejat\AppData\Local\Programs\Python\Python311\python.exe'`.
Its recorded base is Python 3.11.9. No replacement interpreter or environment was
used. The STEP 50 command, targeted pytest, full pytest, compileall and pip check
were attempted; each failed at launcher startup. README analytical validation,
quick experiment in a new output location, output checks, independent audit and
full reproducibility commands were likewise attempted and could not start.
These are environment failures, not failed scientific calculations or passing
regressions. `git diff --check` passed; it does not validate untracked Python
syntax or substitute for pytest. The new tests have not been executed.

The test file covers the 71 real archives and synthetic missing/hash/CRC/truncated
ZIP cases, duplicate IDs/paths, unsafe paths, symlinks, missing/inconsistent
manifests, wrong/merge source identities, missing numerical inputs, an incorrect
solver certificate, failed ratio and preserved FAIL/no false acceptance. Passing
results are not asserted without execution. The controller must repair the
existing authorized runtime and rerun these tests and the documented README gates.
Because the supplied output now contains evidence, rerunning the Python assessor
requires a **different fresh output directory**.

Acceptance remains `rtol=1e-11`, `atol=1e-13`, refinement limit `1e-4`, denominator
guard `1e-15 T`, original equations/objective/constraints/production solver/fault
definitions. The original 256-segment failed audit remains preserved; production
quick geometry remains 512 segments. Finite-scenario minimax and small holdouts
do not establish robust outperformance, confinement or physical-device validation.

Remaining blockers are the working existing Python environment and executed
regressions/README gates, exact merge-object recovery and checkout association,
fresh complete solver/geometry/field/ratio/conditioning and perturbation studies,
controlled identical-input measurements across environments, and the original
scientific comparison failures. Original ZIP availability and STEP 45 inventory
coverage are now resolved to the extent described above.
## Windows ZIP fixture normalization correction (2026-11-02)

This correction supersedes the earlier fixture diagnosis below while preserving
the previous failed-repair evidence. Windows `ZipInfo` construction normalizes
backslashes in `filename`; writing that value loses the unsafe original spelling.
The prior direct `ZipInfo(name)` fixture therefore did not reliably test the
literal backslash archive member on Windows.

The single-entry backslash fixture now writes a forward-slash spelling, requires
equal UTF-8 byte lengths, and requires exactly two occurrences before replacing
the serialized names in the local header and central directory. It asserts two
literal-name occurrences afterward, reopens the archive, checks `orig_filename`
against the original test parameter, checks CRC with `testzip()`, and reads the
original payload. Every original unsafe-path parameter and expected exception
remains unchanged. An added parameterized regression exercises a deliberately
normalizing writer for file, nested, directory and UNC spellings on either OS.
These are portable regression checks, not evidence of executed cross-OS runs.

The inspected production `archive()` already preflights every entry's
`orig_filename`, rejecting a literal backslash with exactly
`ValueError("Unsafe ZIP member path")` before normalization or content access.
That behavior and all existing security checks are retained; only explanatory
comments changed in the production script.

Final Python source SHA256 values for this correction:

- Script: `2aa1d9494abf8711476fd48e3c931c735f8fc7349b6b58cc18c96e02a8fac7bb`.
- Tests: `c4f9dee644f1dfa5c5efab170c4fb1b0d3bf70ab7e4bd03a55db954d84582d7a`.

Required targeted pytest, full pytest, compileall and pip check were attempted
using the existing `.venv/Scripts/python.exe`. Each returned exit 1 at launcher
startup because the configured Python311 base executable is missing. No Python
test or compilation result is PASS. Windows and Linux execution remain
unverified. `git diff --check` returned exit 0; all three authorized files were
already untracked, so ordinary Git diff does not cover their contents.

Only the three authorized files were edited. All 71 original authenticated ZIPs,
scientific evidence, equations, solver settings, thresholds and failed recovery
results remain untouched. Scientific comparison **FAIL**, production acceptance
**FAIL**, overall scientific status **INCOMPLETE**. No research checkpoint is
claimed verified. No commit, push or merge was performed.
