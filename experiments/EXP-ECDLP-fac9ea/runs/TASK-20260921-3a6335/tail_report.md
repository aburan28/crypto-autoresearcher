# EXP-ECDLP-fac9ea v5 tail re-measure — RUN-ECDLP-0c5f65

Amendment DEC-20260921-e7edc5 (the chunked/low-precision continuation
of the RUN-ECDLP-8e13c2 resource_exhaustion cells). Same transform
algorithm, constructions, seeds, and normalisation; complex64
execution, projected and measured within the 8 GiB cap.

## Controls

| control | result |
|---|---|
| dual_precision_crosscheck_le_1e-4 | PASS |
| vhat0_equals_1_within_1e-4_all_ok_cells | PASS |
| C01_tail_numerically_zero_1e-2 | PASS |

Dual-precision cross-check (R03 @ 4818013): relative L1 difference 6.26e-08 (bound 1e-4).

## Refits with the tail point (p = 67108879) included

| row | census lambda | with-tail lambda | moved > 2SE? | n |
|---|---|---|---|---|
| R01 | 0.0806 | 0.0783 +- 0.0020 | no | 17 |
| R02 | 0.0806 | 0.0783 +- 0.0020 | no | 17 |
| R03 | 0.4191 | 0.4149 +- 0.0056 | no | 17 |
| R04 | 0.4088 | 0.4089 +- 0.0035 | no | 17 |
| R05 | 0.3806 | 0.3763 +- 0.0044 | no | 17 |
| R06 | 0.5013 | 0.4990 +- 0.0029 | no | 11 |
| R08 | 0.5000 | 0.5000 +- 0.0000 | no | 17 |
| R09 | 0.1133 | 0.1088 +- 0.0046 | no | 17 |
| C02A | 0.4996 | 0.4996 +- 0.0006 | no | 17 |
| C02B | 0.5001 | 0.5001 +- 0.0002 | no | 17 |
| R03B | 0.4191 | 0.4149 +- 0.0056 | no | 17 |
| R01M | - | 0.5010 | - | 17 |
| R02M | - | 0.5005 | - | 17 |
| R03M | - | 0.5225 | - | 17 |
| R04M | - | 0.5234 | - | 17 |
| R05M | - | 0.5209 | - | 17 |
| R06M | - | 0.4971 | - | 11 |
| R08M | - | 0.4999 | - | 17 |
| R09M | - | 0.5012 | - | 17 |

## Outcome

NO VERDICT CHANGE: every affected row's fitted lambda moves
within its census standard error when the 2^26-class tail point
is included. The census fits, the PGL_2 stability deltas, and
the coset-at-random-level readings stand with the tail point
on record; the jackknife tail check of HEUR-1 is now complete
at the ladder's full span. The normalisation-invariant findings
of EV-ECDLP-81f4d4 are unaffected either way (they do not
depend on absolute levels).

The breach-measured values preserved in the original registry
agree with these in-cap re-measurements within the complex64
precision bound (per-cell comparison in tail_fits.json
breach_vs_incap_comparison) -- the breach did not corrupt the
measurements, it only violated machine protection.

Per-cell values, wall times, RSS high-water: tail_registry.json.

