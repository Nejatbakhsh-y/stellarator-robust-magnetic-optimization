# Phase 2D root-cause investigation

Status: **PARTIAL**. Evidence reviewed here is archived evidence, not newly
executed high-precision scientific calculations.

The supplied cross-platform record reports four failed JSON paths:

| Path below `/quick/faults/` | Windows | Linux reference | Absolute error | Threshold |
|---|---:|---:|---:|---:|
| `3/fractional_recovery` | -0.414688997029067 | -0.4146889970636461 | 3.457911734727759e-11 | 4.246889970636461e-12 |
| `3/recovery_evidence/fractional_recovery` | same | same | same | same |
| `4/fractional_recovery` | 0.16726624849972482 | 0.16726624849716587 | 2.5589530494585233e-12 | 1.7726624849716587e-12 |
| `4/recovery_evidence/fractional_recovery` | same | same | same | same |

Values and thresholds are dimensionless. The gate uses the observed value
in its relative term. Row 3 is failed coil 3; row 4 is failed coil 6.
Relative errors against the Windows values are 8.338562211134874e-11
and 1.529866319686252e-11, respectively, for both repeated paths.
Linux NumPy sensitivity reproduces these reported failures and values.
The SciPy sensitivity comparison passes its unchanged tolerance.

The archived 90-digit direct evaluations differ across workers themselves:

| Failed coil | Windows 90-digit reference (leading digits) | Linux reference (leading digits) | RMS subtraction condition |
|---|---:|---:|---:|
| 3 | -0.4146889970290669773006 | -0.4146889970636458802374 | 948121.1885 |
| 6 | 0.1672662484997249804609 | 0.1672662484971658358737 | 99276.9267 |

For these two rows across all four workers, saved stable-metric errors
against each worker's own archived reference are at most 6.11e-16.
The failed cross-platform gaps therefore persist in high-precision evaluation
of the workers' recorded inputs. Merely increasing precision in the final
metric evaluator cannot reconcile these different inputs.

This supports input sensitivity as a remaining mechanism; it does NOT yet
identify which upstream calculation dominates. The archived projected free
gradients are about 1e-18 or smaller. Small gradients alone neither certify
identical optimizer solutions nor bound error in this evaluation ratio.

BLAS, summation order, optimizer outputs, response geometry and disturbance
arithmetic remain possible upstream contributors. Model/current swap experiments
are prepared but unexecuted. Peak-search decisions, conditioning of the fitted
system, and deterministic geometry require independent attribution before a
production correction is justified. No new correction is asserted.

## Continuation status

The Python replacement now prepares independent Decimal recalculation and
model/current swaps without PowerShell scripts. Its attempted execution
returned 103 before Python started. Consequently no new independent numerical
root-cause conclusion supersedes the archived-evidence analysis above. No
model, optimizer, geometry, physical constraint, tolerance or production
metric correction has been made on the basis of unexecuted hypotheses.

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
