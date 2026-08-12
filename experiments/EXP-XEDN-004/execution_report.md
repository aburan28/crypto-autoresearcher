# EXP-XEDN-004 execution report

- experiment: `EXP-XEDN-004`
- hypothesis: `H-XEDN-003`
- task: `TASK-20260725-003`
- frozen predicate sha256: `76f0cfe2f32362ff1110fc7c7b42db40d293099ae7718927c46223a42450b34f`
- runs: `RUN-XEDN-004-MAIN`, `RUN-XEDN-004-CTRL`
- sage: Homebrew SageMath 10.9 (`SAGE` env / Caskroom path)
- gate_supported: **true**
- gate_falsified: **false**
- validity: `valid` — coeffs ≤3, slope CI includes 0, μ₃ absent

## Method notes

- Family: `y² = x³ + a(t)x + b(t)`, `a ≠ 0`, `deg a ≤ 2`, `deg b = 6`, `j` non-constant.
- Surfaces discovered by two-section Weierstrass solve
  `a = ((y1²−x1³)−(y2²−x2³))/(x1−x2)`, then frozen free-x enumeration.
- **Primary** `max_|coeff|` comes from group-law small-support search among
  observed free-x sections (support ≤3 with `|c|≤3`, plus support-4 `±1`),
  verified by identity over `F_p(t)` and by specialisation (≥20 smooth fibres).
- Height-Gram LLL is retained as a diagnostic only. On one `p=13` surface it
  reported inf-norm 15 for a true but non-shortest kernel vector; the group-law
  search found a verified relation with inf-norm 1 (same VAL-XEDN-003-01 class
  of Gram over-report).
- Isotrivial `a=0` surfaces are excluded from the trend; μ₃-orbit fraction on
  eligible surfaces is 0 (control that the isotrivial automorphism was removed).

## Per-p max_|coeff| (eligible surfaces with a verified relation)

| p | eligible | max_|coeff| | μ₃-absent fraction |
|---|---------:|-------------:|-------------------:|
| 7 | 10 | 1 | 1.0 |
| 13 | 10 | 1 | 1.0 |
| 19 | 8 | 1 | 1.0 |
| 31 | 2 | 1 | 1.0 |

Slope vs `log p`: `0.0` with jackknife CI `[0,0]` (includes 0).

## Controls

- Planted two-section surface at `p=7`: pass (`n_slots≥2`).
- Isotrivial exclusion (`a=0`): pass.

## Scope reminder

Toy sizes only. Boundedness here does not close candidate B2, number-field
xedni, or crypto-scale ECDLP. It only tests whether the coefficient-bound
reading of DEC-20260724-009 can transfer past the μ₃ / isotrivial window for
this degree class.
