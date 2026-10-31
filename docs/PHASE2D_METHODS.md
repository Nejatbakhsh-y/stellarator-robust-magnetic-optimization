# Phase 2D methods — incomplete investigation

Scientific status: **PARTIAL**. No corrected scientific benchmark has been
established. The Phase 2C objective, constraints, configurations, numerical
code and historical results are unchanged.

For weighted residual RMS values B (before failure), L (frozen failure) and
P (recovered), the unchanged metric is R=(L-P)/(L-B). Phase 2C evaluates
energy differences using

    L²-P² = sum_i w_i delta_i (2 r_P,i + delta_i)
    R = [(L²-P²)/(L²-B²)] [(L+B)/(L+P)].

Factoring avoids subtracting nearly equal computed RMS values. It does not
remove sensitivity of the mathematical ratio to its matrix, disturbance,
weights and currents. With D=L-B, its differential is

    dR = [(1-R)dL - dP + R dB]/D.

Small D amplifies input perturbations. This is a sensitivity expression,
not an error bound or justification for changing acceptance thresholds.
The scientific comparison remains rtol=1e-11, atol=1e-13; refinement remains
1e-4; the denominator guard remains 1e-15 T.

`scripts/phase2d_reference.cs` prepares an independent direct-RMS evaluator
using BigInteger fixed-point arithmetic. It decomposes the actual binary64
bits, evaluates weighted squared residuals, takes integer square roots and
forms the original ratio at 60/90 fractional decimal places. Conversion,
products and square roots truncate at that resolution. Agreement is a
precision-convergence diagnostic, not an interval certificate.

`scripts/phase2d_investigate.ps1` prepares all-outage comparisons and model/
current swap experiments for rows 3 and 4. It requires a fresh output path,
checks all supplied hashes before calculations and never updates its inputs.
The complete runner has NOT executed: local PowerShell policy rejected it.
The C# evaluator compiled and passed only the exact scalar smoke example
B=1, L=2, P=1.5, R=0.5 at 60 fractional places.

The exhaustive raw-field inventory, independent geometry regeneration,
optimizer trajectory analysis and input-swap attribution remain incomplete.
No field has been excluded from the existing scientific comparator.

## Python continuation (unexecuted)

`scripts/phase2d_investigate.py` supersedes the PowerShell runner as the
intended investigation entry point. The original PowerShell and C# files are
preserved. This Python 3.11 implementation uses only the standard library;
it neither changes PowerShell policy nor calls production metric code.

It checks inventory coverage, duplicate entries, path containment, byte
lengths, hashes and worker manifests before evaluating anything. Output must
be fresh and disjoint from the original evidence tree. All six worker pairs
are traversed across all JSON files, retaining differing leaves, missing
fields/files, unequal array lengths, units when known, environments, absolute
and relative errors and unchanged thresholds. Metadata/timing classifications
are diagnostic labels, not comparison exclusions. Unknown units and unknown
scientific significance remain explicit.

The direct Decimal calculation converts recorded binary64 inputs exactly,
then independently forms residuals, weighted squared norms and the original
RMS-subtraction ratio at 60/90-digit precision. It prepares all-outage audits
and four combinations of Windows/other-worker model and current inputs for
each affected row. The command exits nonzero even on completed investigation,
because no corrected cross-platform benchmark has been established. Its
records distinguish investigation completion from numerical/scientific PASS.
This implementation and its new integrity/reference tests remain unexecuted.

## 2026-10-30 remediation continuation

Latest execution status: **PARTIAL / local execution blocked**. See
[the versioned remediation record](../results/phase2d/remediation-20261030-193501/STATUS.md)
for exact commands, historical hashes, I/O changes and outstanding phases. The
current attempt executed zero tests: the required .venv launcher exited 103 before
Python startup. All 247 preserved inputs match their hashes. Existing investigation
records contain 84 agreed/converged audits and 24 swaps, with zero manifest hash
mismatches; they were inspected, not recalculated here. Earlier statements that
swaps were merely prepared describe the earlier attempt and are superseded by
this inspection of the preserved investigation. No physical or numerical correction,
new hosted pass, verified checkpoint, commit or publication is claimed.
