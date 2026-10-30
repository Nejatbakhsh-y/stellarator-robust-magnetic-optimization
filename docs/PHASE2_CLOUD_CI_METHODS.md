# Phase 2 cloud CI methods

The PR trigger targets `codex/phase2-peak-robustness-uq`. The existing Phase 1
workflow is preserved. Linux and Windows smoke jobs run pytest, verify the entire
saved manifest and published numerical references, and execute the saved gate.
The full Linux job has a 180-minute ceiling; its compute step has 160 minutes to
leave time for failure artifact upload. Smoke jobs have 20 minutes. Redundant
PR updates cancel older runs. No larger research preset is requested.

Checkout credentials are disabled; permissions are contents:read. Full validation
uses a detached disposable worktree of the checked-out commit, with source loaded
from that worktree. It validates committed reference fingerprints before executing
fresh calculations. No runner commit or push occurs. A local-only overlay option
allows testing uncommitted implementation and explicitly records that distinction.

The full job runs a fresh complete Phase 2 quick study, compares it with the
published checkpoint, then runs phase2_verify: pytest, analytical validation,
fresh Phase 1 quick experiment, output checks, independent audit, second Phase 1
experiment, historical comparison, and second complete Phase 2 study. Independent
training replay/dual audit, intentional invalid-evidence rejection, manifest
refresh, final gate, and six reports follow. Reports derive the passing test count
from executed commands, instead of freezing the original 17-test checkpoint count. Every subprocess failure propagates.

Scientific arrays retain rtol=1e-11, atol=1e-13. Scenario random inputs and configuration,
integer values, statuses, keys and dimensions match exactly. The derived
sampled_clearance_m leaf in validated holdout/training records alone uses these
same numerical tolerances; its nonzero errors remain recorded. Missing fields,
invalid types and nonfinite values fail. See PHASE2_CLEARANCE_REPAIR.md for the
additional archived Linux disagreement that this narrow exception still rejects. Only top-level
source_commit, source_dirty and python are excluded after validation against Git
and platform at runtime. Each trial's nonnegative finite solver timing is also
excluded. Every excluded reference/current value is recorded. Scientific numeric
differences are recorded with absolute and relative error; failures include their
path and magnitude in execution.json/logs. No optimizer tolerance is relaxed.

Phase 2 evidence uses raw-byte hashes and -text attributes; source/config hashes
normalize CRLF/LF. Historical Phase 1 results.json is a text blob: checkout bytes
are compared with Git's filtered base blob. Its raw blob hash is recorded separately
from its checkout hash. The saved Phase 2 input is CRLF and hash linked. In the
disposable worktree only, after parsed equality and frozen hash verification, its
exact bytes are supplied as the Phase 1 input. This prevents line endings from
masquerading as a changed scientific input on Linux. Published files are preserved.

Artifacts retain structured step timing/return codes, package/Python/platform and
commit metadata, fresh results/figures, repeated results, gate and audit records,
comparison details, and reports for 14 days, including failures. Study JSON contains
peak candidate metrics and paired holdout statistics; training_audit.json contains
numerical primal-dual gaps. execution.json records stage failures. Cancellation or
runner termination can interrupt finalization; workflow artifact upload is always
attempted for files already written. The full upload explicitly includes the
worktree result/repeat/report directories, so it does not depend on final copying. No credentials/configuration are uploaded.
