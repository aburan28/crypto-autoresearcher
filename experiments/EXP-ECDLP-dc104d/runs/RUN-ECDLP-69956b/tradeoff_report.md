# EXP-ECDLP-dc104d — the stability-signal tradeoff: proof note + toy verification

Run RUN-ECDLP-69956b, specification v1 (approved DEC-20260921-f718a2).
The proof note (proof_note.md) carries obligations O1-O6 with
binding verdict labels; this report carries the toy readings.

| row | lambda | SE | n | note |
|---|---|---|---|---|
| IVQ | 0.4948 | 0.0018 | 10 | IVQ |
| IVQI | 0.5028 | 0.0017 | 10 | IVQI |
| R01 | 0.0822 | 0.0027 | 10 | R01 |
| R01I | 0.4996 | 0.0002 | 10 | R01I |
| R08 | 0.5000 | 0.0000 | 10 | R08 |
| R08I | 0.5000 | 0.0000 | 10 | R08I |
| C02A | 0.5006 | 0.0004 | 10 | C02A |

## Controls

| control | result |
|---|---|
| C01_numerically_zero | PASS |
| C02A_parseval_band | PASS |
| R08I_equals_R08_exact | PASS |
| vhat0_equals_1_all_ok_cells | PASS |

Equality case worst relative difference (R08I vs R08): 0.00e+00

## Verdicts

- equality_case: **holds**
- R01_inversion_collapse: **inversion_collapse_confirmed**
- IVQ: **inversion_collapse_confirmed**

delta lambda(R01) - lambda(R01I) = -0.41738014736311446 (SE 0.0027482362463789847); delta lambda(IVQ) - lambda(IVQI) = -0.007987821958101604 (SE 0.0024829072327710137)

## Reading

The mechanism's measured instance stands: the structured
interval's inversion image collapses to the flat level, the
QR equality case holds exactly, and the both-structures
family shows no structure to collapse (or collapses like
the interval). Together with the proof note's fragment
(O4 derived, O2/O3 folklore-flagged, O5 open with the
extractions named), the stability-signal tradeoff is on
record as a theorem-SHAPED obstruction with a validated
mechanism instance -- NOT a theorem. The synthetic-
statistic lane is closed in all measured directions; the
extraction tasks (Freiman converse, partial inversion-sum
bound) and the Lean-lane revisit trigger are the named
successors, all non-executable curation work.

Per-cell values: tradeoff_registry.json; obligations: proof_note.md.

