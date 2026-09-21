# EXP-XEDN-005 execution report

- experiment: `EXP-XEDN-005`
- hypothesis: `H-XEDN-004`
- task: `TASK-20260725-010`
- frozen predicate sha256: `76f0cfe2f32362ff1110fc7c7b42db40d293099ae7718927c46223a42450b34f`
- runs: `RUN-XEDN-005-MAIN`, `RUN-XEDN-005-CTRL`
- gate_supported: **true**
- gate_falsified: **false**
- validity: `valid`

## Protocol note

RT-XEDN-004 named raising free-x degree or deg-a. Raising free-x to
`deg x≤3` on `deg b=6` is empty (deg of `x³+ax+b` is 9, odd ⇒ not a
polynomial square). This experiment executes the **deg a≤4** raise with
free-x still `deg x≤2` / `deg y≤3`, and thickens p=31 to 10 eligible surfaces.

## Per-p max_|coeff|

| p | eligible | max_|coeff| | μ₃-absent | deg-a mix (eligible) |
|---|---------:|-------------:|----------:|---|
| 7 | 5 | 1 | 1.0 | mostly 4 |
| 13 | 5 | 1 | 1.0 | all 4 |
| 19 | 5 | 1 | 1.0 | all 4 |
| 31 | 10 | 1 | 1.0 | all 4 |

Slope vs `log p`: `0.0` (CI `[0,0]`).

## Scope

Toy sizes only. Supports coefficient-bound transfer to raised deg-a≤4 window
only; not B2 / crypto-scale.
