# Typed Five-Term Elliptic-Curve V1 Analysis

## Status

`POSITIVE SIGNAL`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

The public point construction

`Q = P0 + iD + R_j1 + R_j2 + R_j3 + R_j4`

works end to end on the tested generated prime-order curves. Four
coordinate-defined `R` families preserve constant exact support, their typed
relation systems reach the full predicted quotient rank, and their
attack-visible quotient solutions recover held-out target logarithms.

This is the first functional validation of the typed `A+4R` relation
architecture in this campaign. It is not a compressed `4R` compiler, a
faster-than-rho algorithm, or deployment evidence.

## Scope

- curves: generated ordinary nonspecial prime-order curves;
- group orders: `953`, `3919`, and `15583`;
- `A` sizes: `7`, `6`, and `11`;
- `R` sizes: `5`, `8`, and `10`;
- coordinate families: random-x, source-PRF-x, x-interval, rational-union;
- model control: scalar progression, attack-ineligible;
- one seed and 10/12/14-bit toy sizes;
- exact materialized point-keyed `3R` and `4R` witnesses.

All public construction, relation collection, solving, and descent occurred
before the diagnostic subgroup census. The verifier independently reconstructs
the census only after replaying the attack-visible path.

## Exact Results

### Coordinate rows

| q | family | exact support | `|3R|` | `|4R|` | relation targets | candidate rows | quotient rank | verified held-out |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 953 | random-x | 0.392 | 35 | 70 | 16 | 7 | 6/6 | 26 |
| 953 | source-PRF-x | 0.340 | 30 | 55 | 13 | 8 | 6/6 | 21 |
| 953 | x-interval | 0.455 | 35 | 69 | 11 | 6 | 6/6 | 26 |
| 953 | rational-union | 0.416 | 35 | 69 | 10 | 6 | 6/6 | 23 |
| 3919 | random-x | 0.421 | 120 | 326 | 19 | 10 | 9/9 | 29 |
| 3919 | source-PRF-x | 0.391 | 118 | 313 | 25 | 12 | 9/9 | 24 |
| 3919 | x-interval | 0.419 | 120 | 328 | 37 | 15 | 9/9 | 31 |
| 3919 | rational-union | 0.392 | 120 | 329 | 22 | 13 | 9/9 | 23 |
| 15583 | random-x | 0.371 | 218 | 693 | 29 | 17 | 11/11 | 28 |
| 15583 | source-PRF-x | 0.382 | 220 | 710 | 16 | 12 | 11/11 | 26 |
| 15583 | x-interval | 0.379 | 220 | 711 | 29 | 12 | 11/11 | 28 |
| 15583 | rational-union | 0.420 | 218 | 691 | 33 | 15 | 11/11 | 32 |

Across the 12 attack-eligible rows:

- exact support ranges from `0.3403` to `0.4548`;
- all quotient systems reach their predicted rank;
- 133 candidate relation rows from 260 targets were independently replayed;
- all 317 supported held-out descents were independently replayed;
- materialized `4R` and `R`-scan-plus-`3R` agree on every held-out target.

The independent verifier also replayed the three controls, for 178 candidate
relations and 338 successful descents across all 15 rows.

### Control

The scalar-progression `R` control has exact support:

- `0.2132` at `q=953`;
- `0.0370` at `q=3919`;
- `0.0529` at `q=15583`.

Its additive collapse sharply separates it from all coordinate families at
the larger sizes. This confirms that the experiment can detect support loss;
it does not prove random-like coordinate support asymptotically.

## Exact Gauge And Rank

Every full row has coefficient one on `log(P0)` and total coefficient four on
the `R` columns. Therefore

`(-4, 0, 1, ..., 1)`

is an exact right-kernel vector. Full unquotiented rank is impossible and is
not the success criterion.

The quotient variables are

`p0' = log(P0)+4log(R0)`,

`d = log(D)`,

and `rj' = log(Rj)-log(R0)` for `j>0`.

The quotient width is `|R|+1`. Every attack-eligible row reaches that width,
and the independently solved quotient agrees exactly with the post hoc scalar
census. Same-type target rows are gauge invariant, so unique individual
factor-base logs are unnecessary for the tested descent.

## First-Witness Negative

The first pinned attempt retained only the first `A` split per successful
target. It stopped at quotient rank `7/9` on a 12-bit cell.

Retaining every supported `A` split found during the same complete `A` scan
raises every tested cell to full quotient rank. Thus:

`NEGATIVE RESULT`: deterministic first-witness selection can bias relation
rank even when exact support is constant and the full typed row universe
spans the quotient.

Relation collectors must charge and test witness-selection diversity, not
infer rank from support probability.

## Cost Boundary

The functional path uses explicit materialization:

- `|R| = q^(1/5+o(1))`;
- materialized `3R = q^(3/5+o(1))`;
- materialized `4R = q^(4/5+o(1))`;
- `4R` lookup plus `A` scan costs `q^(1/5+o(1))` per target;
- relation collection and ordinary sparse linear algebra target
  `q^(2/5+o(1))` after a suitable compiler exists.

At the tested sizes, `|4R|/sqrt(q)` is:

- `1.78–2.27` at `q=953`;
- `5.00–5.26` at `q=3919`;
- `5.54–5.70` at `q=15583`.

The finite fitted `4R` exponents are `0.822–0.917` across coordinate
families, consistent with an explicit-table cost far above rho. The fitted
`3R` exponents are `0.655–0.714`; `R`-scan-plus-`3R` trades lower advice for
larger query work and does not produce a charged exponent win.

`RESTRICTED NEGATIVE RESULT`: materialized `4R`, and the executed
`R`-scan-plus-materialized-`3R` alternative, do not yield a faster-than-rho
one-target algorithm in this cost model.

## Why The Typed Architecture Still Matters

Unlike the earlier `2A+3R` architecture, typed `A+4R` has strict room below
rho after the compiler:

- effective columns `c=1/5`;
- exact `A`-scan query `t=1/5`;
- relation collection `c+t=2/5`;
- ordinary sparse linear algebra `2c=2/5`.

The remaining classical breakthrough target is therefore concentrated in
one object:

> Given a fixed ordinary prime-order curve and a public coordinate-defined
> set `R` of size about `q^(1/5)`, compile exact witness-bearing membership in
> `4R` with complete fixed-curve build work below `q^(1/2-epsilon)`, retained
> advice and peak memory below `q^(1/2)`, and total target specialization and
> exact witness lift no worse than `q^(1/5+o(1))`.

This compiler condition is necessary but not sufficient. With quotient-column
exponent `c=1/5`, target-specialization exponent `t`, witness exponent `w`,
support loss `u`, and rank-yield penalty `r`, relation collection must satisfy
`c+u+r+max(t,w)<1/2`. At the intended `t=w=1/5`, this requires `u+r<1/10`.
Sparse linear algebra and randomized arbitrary-target descent must each also
remain strictly below exponent `1/2`.

For online exponent `1/5`, generic fixed-generator preprocessing requires
advice near `q^(3/5)` in its restricted model, with construction near
`q^(4/5)`. This is a model-bound comparator, not a validation or exclusion of
named elliptic-coordinate structure.

## Required Next Gates

1. Prove or disprove compressed exact `4R` membership for concrete
   coordinate predicates, not scalar sets.
2. Charge build field operations, retained bits, peak memory, bandwidth,
   witness lift, and supported-target count separately.
3. Require complete build exponent `<0.5`, relation exponent `<0.5`,
   linear-algebra exponent `<0.5`, and individual descent `<0.5`.
4. Compare against same-advice generic fixed-base preprocessing, optimized
   rho, materialized `4R`, `R+3R`, and `2R+2R` joins.
5. Replicate coordinate support and quotient rank on multiple seeds and larger
   generated curves before fitting an empirical exponent.
6. Test whether compressed witness selection preserves quotient rank or
   reintroduces the first-witness defect.

## Strongest Valid Conclusion

`OBSERVATION`: four public coordinate-defined factor bases support functional
typed `A+4R` relation collection, exact quotient rank, and held-out descent on
three generated toy prime-order curves.

`RESTRICTED THEOREM`: fixed `A+4R` weight guarantees the displayed gauge
direction. Conditional on quotient rank `|R|+1`, it is the complete kernel,
and every gauge-compatible target row is exactly evaluable. Complete kernel,
support, and rank are empirical claims for these 15 toy transcripts.

`NEGATIVE RESULT`: the explicit `4R` and `R+3R` compilers remain above the
required charged boundary, and first-witness-only row selection can lose rank.

The next experiment should attack compressed recursive `S4` membership, not
retune the materialized table.
