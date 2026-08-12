# Experiment Contract: Typed Two-Dimensional Target Lattice V1

## Hypothesis

For public target lattices `Q_{u,v}=Q0+uD+vE` and typed sources
`A_i=P0+iD`, the shared `u-i` diagonal can be retained while the second
direction `vE` supplies distinct quotient coefficients. A coordinate-specific
index might therefore preserve target-key compression and improve row yield.

## Null Hypotheses

1. The second direction merely multiplies target records by `V`, restoring the
   materialized `B^3` boundary.
2. Lattice hits still collapse to too few quotient rows or fail target
   coverage after witness replay.
3. Any rank increase is bought by target-side work or memory that exceeds the
   fixed-curve typed baseline.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: all three generated ordinary prime-field curves;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`, and
  `rational_union`;
- `U=ceil(B^alpha)` along `D`, with `alpha in {1,1.5}`;
- `V in {1,2,4,8,16}` along a second public direction `E`;
- `Q0`, `D`, and `E` are deterministic public test points; their test-only
  known multiples are used only to audit equations;
- fixed advice: one canonical `D2=R+R` table with all pair witnesses;
- query: one `D2+R` scan against lattice complement keys;
- relation field: `F_q`, with quotient width `|R|+2`.

## Metrics

- lattice target count `U*V`, target schedule additions;
- exact key records `(U+|A|-1)*V*|R|`, unique keys, bytes, and operations;
- `D2+R` lookups, hit records, witness replays, and coverage;
- distinct equations, quotient rank, full-rank flag, and rank per target;
- fixed plus online work, amortized work per target, peak retained advice,
  cumulative transient key bytes, and wall/RSS;
- matched unrelated-target control with the same `U*V` targets.

## Positive Controls

- all lattice witnesses replay to their named targets;
- all equation coefficients agree with the public test scalar expression;
- `V=1` reduces to the prior aligned diagonal construction;
- target records meet the exact diagonal bound before point collisions;
- no private scalar is used by the candidate route.

## Success Criterion

A scoped lattice signal requires exact semantics, full quotient rank for at
least one tested cell, and no restoration of the full `U*V*|A|*|R|` target
record count. Promotion toward a generic ECDLP route additionally requires
charged fixed/advice/workspace and target descent gates below the rho scale;
this experiment does not define that promotion by itself.

## Falsification Criteria

- any witness or equation mismatch falsifies the implementation;
- rank staying below `|R|+2` across the sweep preserves the row-collapse
  negative;
- key records or transient memory scaling as `U*V*|A|*|R|` preserves the
  materialization barrier;
- a finite rank win with online work at or above rho is a diagnostic, not a
  cryptanalytic improvement.

## Reproduction Command

```bash
python3 src/typed_two_dimensional_lattice.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --u-exponents 1 1.5 --v-sizes 1 2 4 8 16
```
