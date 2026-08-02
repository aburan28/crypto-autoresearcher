# Experiment Contract: Typed Aligned Batch MITM V1

## Hypothesis

For typed sources `A_i=P0+iD` and aligned target cohorts
`Q_t=Q0+tD`, the identity `k=t-i` reduces target-side MITM records from
`T|A||R|` to at most `(T+|A|-1)|R|`, while one `D2+R` scan recovers exact
five-term witnesses for the cohort.

This may improve amortized many-target decomposition. A separate gate tests
whether the same diagonal collapse preserves enough distinct quotient rows
for one-instance relation collection.

## Null Hypotheses

1. The aligned construction does not preserve exact target coverage after
   deduplication and witness replay.
2. The reduction in target records is erased by collisions, backpointers,
   memory traffic, or rank-yield loss.
3. One aligned hit covers many targets but contributes only one quotient row,
   preventing a one-instance sub-rho relation collector.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: prime orders `q=953,3919,15583`;
- coordinate `R` families: random-x, source-PRF-x, x-interval,
  rational-union;
- `B=|R|`, with the recorded `|A|`;
- target schedules:
  `T=ceil(B^alpha)` for `alpha in {0.5,1,1.5,2}`;
- aligned cohort: `Q_t=Q0+tD`, where `Q0` is a deterministic known multiple
  of the subgroup generator;
- matched control: `T` deterministic random known-log targets;
- fixed advice: unique `D2=R+R` points with all canonical pair witnesses;
- query: enumerate unique `D2` points plus one `R` point;
- relation field: `F_q`;
- witness policy: retain all target-key records and all canonical `D2`
  witnesses, then deduplicate exact quotient equations.

## Metrics

- `D2` attempted transitions, unique points, all witness records, bytes;
- target records, unique target keys, collisions, bytes, writes;
- `D2+R` attempts, point additions, lookups, hit records;
- covered target count and fraction;
- ordered and canonical witnesses;
- distinct quotient rows, quotient rank, and rank per hit;
- point-replay mismatches and equation consistency;
- group/field operations, memory traffic proxy, peak RSS, serialized bytes,
  wall time;
- aligned/random target-record ratio;
- work and bytes per covered target;
- analytical rho and BSGS scales, reported separately from measurements.

## Positive Controls

- every reported witness replays to its named target;
- every equation agrees with the known target scalar expression without using
  hidden logs of `P0`, `D`, or `R`;
- unique `D2` support and all canonical pair witnesses match direct
  enumeration;
- random target cohorts use the same `D2+R` scan and witness policy;
- scalar progression `R` is excluded from attack promotion.

## Many-Target Success Criterion

A provisional aligned-batch signal requires, for all three curves and at
least three of four coordinate families at some `0.5<alpha<1.5`:

- exact target-record count at most `(T+|A|-1)|R|`;
- aligned/random target-record ratio at most
  `2/min(|A|,|R|)`;
- aligned covered-target fraction at least 80 percent of the matched random
  cohort fraction;
- zero replay or equation mismatch;
- fitted advice-plus-workspace exponent below `q^(1/2)` across the tested
  schedule, with finite record and byte counts reported separately.

This is an amortized aligned-target result only.

## One-Instance Relation Success Criterion

Promotion toward a one-instance ECDLP route additionally requires:

- full quotient rank `|R|+1`;
- total charged batch work below the measured or analytical rho scale;
- independent-row yield sufficient to preserve
  `c+u+r+max(t,w)<1/2`.

Failure of this gate does not erase a many-target decomposition result.

## Falsification Criteria

- Any witness or equation mismatch falsifies the implementation.
- If one diagonal hit covers many targets but produces one equation, preserve
  that as a rank-yield negative.
- If full rank requires `T` or workspace exponent at least `B^2` or `B^2.5`,
  the one-instance route is narrowed.
- A finite constant-factor miss does not by itself disprove the exact batch
  identity.

## Cost Boundary

For `T=B^alpha`, the ideal aligned batch uses:

- fixed `D2`: `Theta(B^2)`;
- target records: `Theta(B(T+B))`;
- one scan: at most `Theta(B^3)`;
- amortized work:
  `B^(3-alpha)+B+B^(2-alpha)`.

This is below `B^2.5` per aligned target when `alpha>1/2`; memory remains
below `B^2.5` when `alpha<3/2`. These are symbolic bounds, not a single-target
ECDLP claim.

## Reproduction Command

```bash
python3 src/typed_aligned_batch_mitm.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --target-exponents 0.5 1 1.5 2
```
