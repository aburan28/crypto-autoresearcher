---
id: KN-TECH-5c41e7
type: technique
title: "Ceiling of the distinct-residue coverage ratio: it cannot detect excess coverage at small cell sizes"
tags: [coverage-ratio, instrument-ceiling, reduction-mod-p, global-lift, czlift, null-calibration, pigeonhole, derivation, experiment-design, proves-too-much]
confidence: established
source:
  citation: "Internal derivation (pigeonhole plus the uniform occupancy expectation), recorded in experiments/EXP-CZLIFT-14f6d5/analysis.md (D1) and experiments/EXP-CZLIFT-a255fc/analysis.md (O-14); checked against planted controls in three experiments."
  url: null
internal_refs: [EV-CZLIFT-376eee, EV-CZLIFT-b6fe48, DEC-20261023-26a6de, DEC-20261023-6931ab, DEC-20261023-fdc4af, DEC-20261024-23d64d, EXP-CZLIFT-a255fc, EXP-CZLIFT-14f6d5, EXP-CZLIFT-8c50ea]
proof_status: derivation
proof_refs: [experiments/EXP-CZLIFT-14f6d5/analysis.md, experiments/EXP-CZLIFT-a255fc/analysis.md, experiments/EXP-CZLIFT-a255fc/reports/validation-20261022/ptm1_output.json, experiments/EXP-CZLIFT-8c50ea/reports/validation-20261022/validation_report.yaml]
added: 2026-10-24
superseded_by: null
---

## The instrument

A coverage cell reduces `n` points (for example, the global points of bounded
height on `E/Q`) into a finite group of `N` elements (for example `E(F_p)`,
`N = N_p`) and counts the distinct residues `m`. The coverage ratio compares
`m` with what `n` independent uniform draws would give:

```
ratio = m / ( N (1 - (1 - 1/N)^n) )   ~   m / ( N (1 - e^{-x}) ),   x = n/N.
```

A ratio above 1 is read as "covers better than uniform", below 1 as
"collides more than uniform".

## The ceiling (derivation)

No point set can have more distinct residues than points or than group
elements: `m <= min(n, N)`. Hence, for every possible point set,

```
ratio <= cap(n, N) = min(n, N) / ( N (1 - (1 - 1/N)^n) )  ~  min(x, 1) / (1 - e^{-x}).
```

- For `x <= 1` the cap is `x/(1 - e^{-x}) = 1 + x/2 + x^2/12 + ...`. It
  increases with `x` and tends to 1 as `x -> 0`, for example as `p` grows at a
  fixed point count.
- For `x >= 1` it is `1/(1 - e^{-x})`, which decreases.
- The maximum is `e/(e - 1) ~ 1.582`, at `x = 1`. The cap exceeds 1.5 only
  for `x` in `(0.875, ln 3 ~ 1.0986)`. It exceeds 1.2 only for `x > 0.376`.
- A median is monotone in each element, so a cell set's median ratio is at
  most the median of its per-cell caps. An all-injective point set (for
  example a discrete-log-known progression `kG`) attains it.

Therefore any criterion edge above the cap ("median <= 1.2", "fewer than 5
percent of cells above 1.5") is unreachable on that cell set and cannot fail.
"Criterion met" on that side then measures the instrument, not the point set.

## Where it was seen

- **EXP-CZLIFT-a255fc** (eight-curve rank ladder, `H <= 3e5`): the median `x`
  over frozen cells is 0.10. A maximally spread planted set passes the frozen
  criterion (median 1.0514 / 1.0548). The observed 1.0330 / 1.0333 is
  nonetheless above every seeded uniform null (upper edge <= 1.0041), which
  only calibrated nulls could show (EV-CZLIFT-376eee, DEC-20261023-26a6de).
- **EXP-CZLIFT-14f6d5** (record curves): only 6 of 131 and 7 of 156 cells
  have a cap above 1.5, so "frac above 1.5 < 0.05" cannot fail (at most 0.046 /
  0.045). The median cap is 1.071 / 1.082 < 1.2, so the upper edge cannot fail
  either (EV-CZLIFT-b6fe48, DEC-20261023-6931ab, analysis D1).
- **EXP-CZLIFT-8c50ea** (cubic field, inadmissible for other reasons): the cap
  is at most 1.3089 (main) and 1.2632 (replication). An all-injective median
  would be only 1.00820 / 1.00785, so only a heavy collision deficit could move
  the criterion (DEC-20261023-fdc4af D7).

## How to use it in a contract

1. Report the per-cell cap beside every ratio, and before the run declare
   every criterion edge above the cap uninformative.
2. Read excess only against a seeded same-shape uniform null (the same `n`
   and `N` per cell, at least 1000 replicates, exact per-cell tails, the
   median's position in the null band). Add a structured null where the map is
   a homomorphism with a kernel height floor (DEC-20261023-26a6de). Effects of
   +3 percent are visible this way and invisible to a fixed band.
3. Include the proves-too-much control: a planted maximally spread set must
   FAIL any criterion that claims power against excess. If it passes, the
   criterion has none.
4. The lower side stays informative. A collision deficit (subgroup
   confinement, a large image index) can push the ratio well below 1.
5. A cell-filter rule that depends only on `(n, N)` keeps the cap fixed before
   any reduction is examined. State the filter and the median convention.

## Limits

- The ceiling bounds distinct-residue counts. It says nothing about
  collision-count statistics, per-cell exact tails, or whether a given set of
  reductions is uniform.
- It is not evidence for or against any lifting attack. The CZLIFT global-lift
  obstruction is the separate counting bound "half coverage needs at least
  `N_p/2` distinct points" (EV-CZLIFT-376eee D7, conditional beyond toy scale
  on T1–T4).
- Not covered here: the model dependence of naive-height counts `N_E(H)`. It
  is deferred until the translation instance of EXP-CZLIFT-14f6d5 is packaged
  as a certificate.

## Falsification

A point set whose cell ratio exceeds `cap(n, N)` is impossible by pigeonhole.
Observing one means the uniform expectation or the distinct count was
miscomputed (for example, duplicate points counted twice, or the point at
infinity counted twice).

## Scope labels

`DERIVATION` (elementary), checked against planted controls in three CZLIFT
experiments at toy tier. A design rule for coverage instruments; not a
statement about any curve's reductions, any attack cost, or any deployed
curve.
