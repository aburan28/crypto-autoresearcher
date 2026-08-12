# Mixed Layer V1 Analysis

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

A homogeneous factor base formed by a random transverse core plus a short
progression layer did not achieve simultaneous `D2/D3` compression and
`D5_new` retention on any tested draw.

This narrows one layered construction in cyclic support geometry. It is not a
negative result for position-specific factor bases, compressed support
representations, elliptic-coordinate correspondences, or ECDLP.

## Parameters

- prime cyclic groups: 251, 503, 1009, 2003, 4001, and 8009
- formal occupancy target: 0.5
- sign-canonical factor-base sizes: 5, 6, 8, 9, 10, and 12
- random-core fractions: 0, 0.45, 0.55, 0.65, 0.8, and 1
- candidate draws per cell/fraction: 31
- matched uniform-random null draws per cell: 31
- joint effect gate: `D2,D3<=0.8x` and
  `D5_nonidentity,D5_new>=0.9x` random medians

The construction is scalar-defined and exists only as a cyclic
additive-combinatorial diagnostic. It is not an admissible ECDLP factor base.

## Result

No individual draw crossed the joint effect gate.

| q | B | core fraction | D2 ratio | D3 ratio | D5_new ratio |
|---:|---:|---:|---:|---:|---:|
| 251 | 5 | 0.45 | 0.933 | 0.857 | 0.774 |
| 503 | 6 | 0.45 | 0.952 | 0.891 | 0.846 |
| 1009 | 8 | 0.45 | 0.917 | 0.812 | 0.718 |
| 2003 | 9 | 0.45 | 0.867 | 0.728 | 0.592 |
| 4001 | 10 | 0.45 | 0.818 | 0.642 | 0.440 |
| 8009 | 12 | 0.45 | 0.808 | 0.621 | 0.410 |

At the largest group, increasing the random core to 0.65 restores `0.844x`
`D5_new` coverage, but `D2` rebounds to `0.962x` and `D3` to `0.911x`.
Increasing the core to 0.8 restores null-like coverage and also restores
null-like `D2/D3`.

The observed crossover therefore moves in the wrong direction:

- enough progression mass to compress early sums destroys five-term coverage;
- enough random mass to restore coverage destroys early-sum compression.

## Scaling signal

Exploratory six-point fitted exponents for median `D5_new` are:

- pure progression: 0.279;
- 45% random core: 0.805;
- 55% random core: 0.938;
- 65% random core: 0.971;
- 80% random core: 1.029;
- fully random: 1.018.

The 45% mixture's coverage ratio decays as the groups grow. These slopes are
diagnostic, not asymptotic estimates.

## Mechanistic interpretation

The homogeneous union does not enforce a useful relation shape. Five-term
words may draw any number of leaves from either layer. A compressed early
sumset comes from progression-heavy words, while near-random final expansion
requires most leaves to come from the transverse core. The two effects do not
compose at the tested factor-base size.

## Strongest valid conclusion

Random-core plus progression union is not a viable realization of the layered
escape under this schedule. The V2 finite witnesses do not scale by merely
adding random outliers to one homogeneous factor base.

## Next positive direction

Use position-specific layers rather than a union:

`A1 + A2 + R3 + R4 + R5`.

The first two sets should come from a low-complexity coordinate correspondence
with a succinct pair-sum image. The three transverse sets should be selected
independently to restore coverage. The relevant objective is then the full
asymmetric `(columns, pair-image representation, triple-image membership,
coverage, rank)` frontier, not homogeneous `D2` cardinality alone.

A second escape is to keep nearly maximal `D2` but represent or query it
through a compressed algebraic circuit. That directly targets the user's
recursive-addition and batch-decomposition lead.

## Next falsifier

Before EC implementation, optimize asymmetric cyclic layers under a fixed
total column budget. Compare:

- materialized `A1+A2` versus succinct progression/correspondence parameters;
- materialized `R3+R4+R5` versus recursive membership;
- total coverage and relation-column rank proxy;
- exact offline/online Pareto points against homogeneous MITM.
