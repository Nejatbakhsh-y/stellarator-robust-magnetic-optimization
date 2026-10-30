# Phase 2C numerical validation report

Local Windows validation: PASS. Scientific status: PARTIAL. Hosted Phase 2C
Windows/Linux and package-sensitivity outcomes are PENDING until observed.
See PHASE2C_PUBLICATION.md for the authenticated stacked-PR handoff.

## Reproducible evidence

Quick SHA-256: `ba6f27db86176606a82e360220e2e96f250976bfc2774be167ab746ccc1914e5`.
Study SHA-256: `20f28ceb4a195c15c04d5ec3b36bc95ae65399cc540d8782eb593fc1fce63eca`.
Preservation contract: 104 hash-verified files (38 original Phase 1/2,
59 Phase 2B, five original failure ZIPs, and both initial-inventory copies).
Every retained new file is covered by the raw-byte manifest. Original SHA-256:
`395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258`
(Phase 2 study); Phase 2B study:
`c8f1cf9df1cdc6fb8eb5ab8595ede2015aee4647671d98142205ec1ec8f2a960`.

## Complete local checks

| Executed stage | Return code | Measured wall seconds |
|---|---:|---:|
| tests | 0 | 2.704 |
| analytical | 0 | 1.375 |
| quick | 0 | 200.734 |
| outputs | 0 | 0.422 |
| independent-audit | 0 | 221.453 |
| study | 0 | 1319.500 |
| repeat-quick | 0 | 284.422 |
| repeat-study | 0 | 749.500 |
| training-audit | 0 | 53.750 |

The first/repeat comparisons use rtol=1e-11 and atol=1e-13, exact
random draws/configuration, and the unchanged 1e-4 refinement gates.
All 21 active-coil outages received independent 60/90-digit arithmetic
checks. The legacy-scientific comparison passed for every unchanged
scientific quantity; all intentional metric changes are enumerated.
Final regression output:

```text
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 2.38s
```

Python compilation passed; see compilation.log. The initial numerical
pipeline used its recorded test snapshot; added evidence-contract tests
were rerun separately and by finalization. Calculation fingerprints must
remain identical to the at-run record. No production numerical code was
changed after these quick/study calculations.

## All original scientific failures

The lossless inventory retains all raw differences for all ten dataset
pairs, including provenance, timing, legacy geometry and NM diagnostics.
These are retained rather than hidden behind the first failing scalar.

| Original worker versus committed Phase 2B | Failed primary paths |
|---|---|
| phase2b-linux-numpy-sensitivity | `/quick/faults/3/fractional_recovery`, `/quick/faults/13/fractional_recovery` |
| phase2b-linux-reference | `/quick/faults/3/fractional_recovery`, `/quick/faults/13/fractional_recovery` |
| phase2b-linux-scipy-sensitivity | `/quick/faults/3/fractional_recovery`, `/quick/faults/4/fractional_recovery`, `/quick/faults/10/fractional_recovery`, `/quick/faults/13/fractional_recovery` |
| phase2b-windows-reference | `/quick/faults/3/fractional_recovery`, `/quick/faults/4/fractional_recovery`, `/quick/faults/13/fractional_recovery` |

The primary study scientific quantities have no additional out-of-tolerance
differences in these four archived workers. Complete investigation
diagnostics and already documented adaptive-coordinate/legacy-geometry
differences remain in the inventory, including within-tolerance values.

## Original and corrected recovery values

Row index differs from physical failed-coil ID because the original
active-current threshold excludes coils 4, 5 and 23. That policy is unchanged.

| Row | Failed coil | Original ratio | Corrected ratio | Corrected error vs 90 digits | RMS subtraction condition |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0.15153220300197251 | 0.15153220300197257 | 0 | 20.5121 |
| 1 | 1 | 0.26598420168711334 | 0.26598420168710341 | 1.11e-16 | 284.9777 |
| 2 | 2 | 0.14160824941257846 | 0.14160824941240704 | 8.327e-17 | 5693.348 |
| 3 | 3 | -0.41468899713385832 | -0.41468899702906697 | 0 | 948121.2 |
| 4 | 6 | 0.16726624850524488 | 0.16726624849972482 | 1.665e-16 | 99276.93 |
| 5 | 7 | 0.36964021709021083 | 0.36964021709013439 | 0 | 1592.282 |
| 6 | 8 | 0.50999153862068614 | 0.5099915386206606 | 0 | 211.4876 |
| 7 | 9 | 0.18615874855210651 | 0.18615874855210834 | 0 | 368.8151 |
| 8 | 10 | 0.68456405012647625 | 0.68456405012548571 | 3.331e-16 | 37684.78 |
| 9 | 11 | 0.35184075279572885 | 0.35184075279539123 | 1.11e-16 | 26725.59 |
| 10 | 12 | 0.30465694567812862 | 0.30465694568062768 | 0 | 38845.08 |
| 11 | 13 | 0.33176522375612938 | 0.33176522375469059 | 5.551e-17 | 34706.42 |
| 12 | 14 | 0.42310677304406963 | 0.42310677304387262 | 0 | 25957.09 |
| 13 | 15 | 1.0317963589982326 | 1.0317963589574775 | 4.441e-16 | 451320.6 |
| 14 | 16 | 0.35164017837605238 | 0.35164017837605094 | 5.551e-17 | 54.14407 |
| 15 | 17 | 0.18708838937929526 | 0.18708838937929237 | 0 | 211.9112 |
| 16 | 18 | 0.49346571408277251 | 0.49346571408145784 | 1.11e-16 | 13911.78 |
| 17 | 19 | 0.30448424187725792 | 0.30448424187639034 | 5.551e-17 | 16152.73 |
| 18 | 20 | 0.26186218857930454 | 0.26186218857872534 | 0 | 19039.04 |
| 19 | 21 | 0.28222265612681308 | 0.28222265612710157 | 5.551e-17 | 17784.26 |
| 20 | 22 | 0.37433556186479966 | 0.37433556186421985 | 1.11e-16 | 18329.31 |

Maximum corrected absolute error vs the 90-digit reference: 4.4408920985006262e-16.
Maximum recovered free-coordinate projected training gradient: 1.3010426069826053e-18 (dimensionless).

The reference evaluates exact recorded binary64 inputs. It does not
certify an exact-geometry response or exact optimizer. Full residual
vectors, current outputs, energy summands, reference strings and
one-ULP naive sensitivity ranges are retained in hash-linked evidence.

## Negative robustness findings and limitations

| Training seed | Count | Mean robust-minus-nominal RMS (T) | Fraction improved |
|---:|---:|---:|---:|
| 20261111 | 4 | 8.2193419059802946e-09 | 0 |
| 20261111 | 8 | 7.9980561009721585e-09 | 0 |
| 20261112 | 4 | 7.0391762275347723e-09 | 0 |
| 20261112 | 8 | 4.4178495851162401e-10 | 0 |

All four tested fits retain their negative synthetic holdout findings.
There is no global peak certificate, device/confinement validation,
interval arithmetic proof, or guarantee across untested libraries/hardware.
Observed agreement of finite calculations is separate from scientific
validation of robustness. No numerical tolerance, solver setting or
physical feasibility constraint was changed. See PHASE2C_METHODS.md and
the preserved Phase 2B limitations for the mathematical scope.

## Hosted status

Original run 41044895641: all four numerical jobs and cross-platform job
FAILED at comparison; their preceding pipelines/audits completed.
Phase 2C hosted results: PENDING. A local Windows pass is not a hosted
Linux or cross-platform pass. Final publication status is recorded
separately after the commit/push/PR attempt. No PR is merged.
