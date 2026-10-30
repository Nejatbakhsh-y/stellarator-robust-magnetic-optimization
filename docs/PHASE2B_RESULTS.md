# Phase 2B local numerical results

Scientific status: **PARTIAL**. Hosted cross-platform status must be observed separately.

Benchmark: `phase2b-householder-v2-pattern-v2`.
Study SHA256: `c8f1cf9df1cdc6fb8eb5ab8595ede2015aee4647671d98142205ec1ec8f2a960`.
Quick SHA256: `716ebb2a81585c3240a261902910a5f7d75a35e90c7e298c6bf71701bf871263`.

Final local suite: 94 passed. All nine numerical pipeline commands returned 0.
Two complete quick and Phase 2 studies matched at rtol=1e-11, atol=1e-13.
The independent quick audit, independent training replay/dual audit and candidate smooth-circle checks pass.

| Method | observed finite peak [T] | smooth field at candidate [T] | configured relative polygon error |
|---|---:|---:|---:|
| dense | 0.0002993326578347548 | 0.0002993378597371157 | 1.7378030181251516e-05 |
| matched_nominal | 0.00029931014888016379 | 0.00029931535021920095 | 1.7377455026433551e-05 |
| robust | 0.00029926566704432923 | 0.00029927086749073346 | 1.7377055267158142e-05 |

These are observed lower bounds and candidate evaluations, not continuum supremum certificates.

| Seed / count | robust minus nominal mean RMS [T] | fraction improved |
|---|---:|---:|
| 20261111 / 4 | 8.2193419059802946e-09 | 0 |
| 20261111 / 8 | 7.9980561009721585e-09 | 0 |
| 20261112 / 4 | 7.0391762275347723e-09 | 0 |
| 20261112 / 8 | 4.4178495851162401e-10 | 0 |

Every tested minimax fit still worsens this synthetic holdout; no robustness superiority is inferred.

## Preserved trace and convergence analysis

All 145 archived peak discrepancies are retained as legacy failures.
They comprise 97 coordinate fields, 46 algorithmic trace fields, and two dimensionless refinement-error fields.
Maximum common-geometry field difference from the old coordinate changes: 4.3368086899420177e-19 T.

| Method | finite / Nelder–Mead best-field gap [T] | 20 / 28 level field change [T] |
|---|---:|---:|
| dense | 6.8812143483309995e-15 | 0 |
| matched_nominal | 2.5747091091099517e-15 | 0 |
| robust | 1.1704287712632766e-14 | 0 |

Largest numerical dual gap: 3.8392440268597561e-11.
This is a numerical finite-scenario check, not an interval certificate or population guarantee.

All 38 original Phase 1/2 evidence files, including their command and fingerprint records, are byte-preserved.
The retained original study SHA256 is 395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258.
Current raw data, repeated data, failed audit diagnostic, historical Linux data, command logs and manifests are under results/phase2b/.
No global peak, equilibrium, confinement, engineering or device validation is established.
