# Phase 2C numerical stability investigation

Benchmark: `phase2c-householder-v2-pattern-v2-energy-v3`. Base:
`74fddfe3a2a7cf95ee334f8bc1ec7757ef22c379`; isolated branch:
`codex/phase2c-stable-fault-metrics`. Existing branches and PRs are not rewritten
or merged. Phase 1, Phase 2 and Phase 2B evidence remain preserved, including
the negative holdout findings. Scientific status remains PARTIAL.

## Failure provenance and exhaustive inventory

Run 41044895641 has four completed, failed numerical jobs and one failed
cross-platform job. Each worker successfully generated and repeated its numerical
pipeline and passed its independent audits before committed-reference comparison
failed. All five original ZIP artifacts are preserved under
`results/phase2c/history/`; SHA-256 digests were verified against GitHub's API.
`github-run-41044895641.json` retains job steps, source SHA, package cohorts,
artifact IDs and published digests. No downloaded URL credentials are retained.

`phase2c_inventory.py` enumerates every differing leaf in quick results, complete
studies, geometry and investigation analyses, for all ten pairs among the
committed benchmark and four workers. It retains within-tolerance differences,
non-numerical differences, provenance, timings, legacy geometry, and adaptive
search diagnostics. It does not stop at the first mismatch. The compressed
inventory is lossless; the separate summary identifies primary output failures.
Historical diagnostic conventions remain explicit; their fields are not silently
reclassified as new scientific successes.

Before regenerating diagnostic output, the original 20,605,029-byte inventory
was copied to `history/inventory-initial.json`, verified, and marked read-only.
Both original and copy have SHA-256
`0af5f1618a7e0722a015bdd3388da69d52fe95e3c386e4f3eb95bdadbfee899a`.
Both remain present. Their hashes and the five ZIP digests are enforced by the
Phase 2C preservation contract and final raw-byte manifest. Read-only attributes
protect the local archive; Git content hashes preserve identity after checkout.

## Conditioning and algebra

Let B, L and P be pre-fault, frozen-fault and recovered weighted RMS values;
the published fractional recovery is R=(L-P)/(L-B). For fault row 3, L and B
are approximately 2.59145e-5 T and differ by only 5.46649e-11 T. Subtraction
conditioning (|L|+|B|)/|L-B| is about 9.48e5. With D=L-B,

* dR/dL=(1-R)/D;
* dR/dP=-1/D;
* dR/dB=R/D.

Thus already rounded RMS inputs amplify errors by factors proportional to 1/D.
Compensating their sum after subtraction cannot recover discarded information.
This is a floating-point evaluation problem in a sensitive derived metric;
it does not show a significant magnetic-field discrepancy by itself. Small
input-current/model differences can still be amplified and must be measured.
The original worker bundles did not retain the complete recovered-current or
fine-grid fault residual vectors. Their exact internal energy arithmetic cannot
be reconstructed from three already rounded RMS scalars. This limitation is
retained explicitly: the independent precision probe uses newly recomputed
inputs, and the new benchmark records those formerly missing vectors/currents.
The archived workers' complete reported outputs remain inventoried separately.

For residual r(x)=b+A x, E(x)=sum_i w_i r_i(x)^2 and delta=A(x-y), the identity

`E(x)-E(y) = sum_i w_i delta_i (2 r_i(y)+delta_i)`

avoids subtracting two nearly equal full energies. With pre/frozen/recovered
currents x_B,x_L,x_P,

`R = [(E(x_L)-E(x_P))/(E(x_L)-E(x_B))] * [(L+B)/(L+P)]`.

This is algebraically the same real-valued metric, obtained by rationalizing
both RMS differences. Current increments are formed first, and the matrix is
applied to these increments; nearly equal full field vectors are not subtracted.
`math.fsum` accumulates row dot products and signed weighted energy terms.
Products and current differences remain binary64; no exact-arithmetic claim is
made. This improves cancellation behavior rather than altering recovery meaning.
The rationalized expression assumes nonzero RMS sums, as holds for every
production outage in this nonzero-disturbance benchmark; no universal degenerate
zero-field arithmetic guarantee is claimed.
Negative recovery and values above one remain possible and are retained.
The recovered currents minimize the original bounded ridge objective on the
training grid; this ratio is evaluated using fine-grid RMS. Neither ridge nor
grid changes imply monotone fine-grid recovery. These values are not clipped
or treated as evidence of a new optimization defect.

The original `abs(L-B)>1e-15 T` denominator guard is retained, evaluated through
the factored energy identity in the new version. Zero/guarded denominators still
produce `None`. Finite numeric arrays, dimensions and nonnegative nonzero weights
are checked; nonfinite inputs/results fail. No rounding or clipping is applied.
Original separately reported pre/frozen/recovered RMS fields are unchanged.

## Implementation and independent checks

`fault_metrics.py` implements the opt-in `residual-energy-v3` evaluator.
`experiments.py` uses it only when the explicit configuration version requests
it. Historical defaults retain their original operations. New fault evidence
includes full recovered currents, all three residual vectors, signed energy
differences and absolute summand sums, stable RMS values, and solver success.
All these new scientific quantities remain strictly compared.

`phase2c_fault_audit.py` independently recomputes the response and disturbance,
then evaluates exact binary64 matrix, field, weight and current inputs in Decimal
at 60 and 90 decimal digits. It compares the two precisions, each corrected ratio,
and residual vectors, and retains full precision reference strings. It also
records projected free-coordinate training gradients, ridge objectives, current
bounds, fixed failed currents, naive evaluation and one-ULP RMS sensitivity.
These references certify evaluation of the recorded inputs, not exact geometry,
an exact optimizer, or a global field maximum. The response inputs have raw hashes.
The preliminary 70-digit probe also examines all 24 coil removals, including
three coils below the original active threshold. The production experiment
continues to report only its original 21 active-coil outages; the probe does not
alter that selection policy. Fault-array indices and physical failed-coil IDs
are distinguished: row 13 is coil 15, for example.

`phase2c_legacy_compare.py` grades all unchanged quick/study scientific groups
against Phase 2B, explicitly enumerating only the intentional version/config/input
hash links and recovery-evaluation changes. Source/runtime metadata and solver
timing/iteration treatment follow the prior documented contract. The complete
new first/repeat comparison includes all new fault evidence. A collector uses
the original scalar comparator at every leaf and accumulates failures instead of
stopping at the first numeric discrepancy. Any failure leaves the report FAIL
and the command nonzero; no tolerance is changed.

Phase 2B comparison APIs gained optional version/comparator parameters; their
defaults retain the previous behavior. `optimize.py`, the Biot-Savart model,
geometry, peak search, uncertainty generator, objectives, bounds, ridge weights,
solver settings and experimental cohort sizes remain unchanged.

## Validation scope

The Phase 2C workflow runs full independent/repeated calculations on Windows
NumPy 2.4.6/SciPy 1.17.1, Linux with the same packages, Linux NumPy 2.3.5 alone,
and Linux SciPy 1.16.3 alone. Workers compare against the new committed benchmark;
the final job independently compares all three Linux cohorts to the actual
Windows worker. Missing, incomplete, invalid, hash-mismatched or scientifically
different bundles fail closed. Failed outputs are always uploaded. There is no
CI commit, push, secret access, permission escalation, or automatic merge.

Local results and actual hosted outcomes are reported separately in
PHASE2C_RESULTS.md. No Linux result is inferred from local Windows execution.
Finite peak observations, small synthetic holdout samples, numerical rather
than interval dual checks, and absent device/confinement validation remain
limitations. All previously documented negative robustness findings stand.
