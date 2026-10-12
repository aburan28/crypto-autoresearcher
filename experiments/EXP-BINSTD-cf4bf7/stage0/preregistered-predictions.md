# Preregistered predictions — EXP-BINSTD-cf4bf7 (BEFORE Stage 2)

Frozen reference: `experiments/EXP-BINSTD-cf4bf7/specification.yaml`
`preregistered_prediction` and `H-BINSTD-4a2f99`.

## Measured / independently recomputed (Stage 0/1/4)

| Quantity | Prediction | Label |
|---|---|---|
| Corrected ladder error_pp | pair1 +4.5; pair2 −17.0; pair3 −11.1; pair4 +11.9; pair5 +0.2 | EXPECTED |
| `ord_n(2)` / `f` for n∈{17,29,31,37,41,53} | 8/3, 28/2, 5/7, 36/2, 20/3, 52/2 | EXPECTED |
| `ord_17(4)` lattice | ord=4, f=5, 32 subspaces, dims {0,1,4,5,8,9,12,13,16,17} | EXPECTED |
| Null arm n=37 | f=2; mid-dim stable V absent | EXPECTED |
| Contrast n=31 | f=7; **not a null arm** | EXPECTED |
| Stage 1 curve orders | Constructible; #E verified in Hasse interval | PROTOCOL |

## Modeled prior (Stage 2 only; NOT a measurement until run)

| Quantity | Modeled prior | Source |
|---|---|---|
| WDSat conflict ratio on richest stable F_4-subspace | within 1% of 1.0 (basis-blind) OR ≤0.5 with within-curve non-stable near 1 | IDEA-20260920-b9f0c5 / H-BINSTD-4a2f99 |

Missing Stage 2 is recorded as `instrument_unavailable`, **not** as ratio=1.0.

## Hard fails

- Any `f≠2` on n=37 after ruling out implementation bugs.
- Treating n=31 as null.
- Using n=41 as poor lattice control.
