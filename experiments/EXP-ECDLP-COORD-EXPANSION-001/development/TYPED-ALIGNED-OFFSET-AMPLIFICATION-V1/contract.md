# Experiment Contract: Typed Aligned Offset Amplification V1

## Hypothesis

For aligned target cohorts `Q_t=Q0+tD`, a small deterministic set of common
offsets `Q0` can amplify target coverage toward an unrelated-target control
without changing the exact diagonal key identity. This is a many-target
decomposition hypothesis only.

## Null Hypotheses

1. Additional offsets do not materially improve covered-target fraction.
2. Any coverage improvement is erased by the charged target construction,
   target-key advice, query scans, or transient memory footprint.
3. Offset cohorts do not preserve enough per-offset quotient rank to support
   a one-instance relation collector.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: all three generated ordinary prime-field curves;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`, and
  `rational_union`;
- target schedules: `T=ceil(B^alpha)` for `alpha in {1,1.5,2}`;
- offset counts: `K in {1,2,4,8}`;
- aligned targets: `Q_{s,t}=Q0_s+tD`, with deterministic public test
  multiples for each `Q0_s`;
- matched control: `K*T` deterministic unrelated known-log targets;
- fixed advice: one canonical `D2=R+R` table, with all pair witnesses;
- query: one aligned target-key build and one `D2+R` scan per offset;
- relation field: `F_q`.

## Metrics

- target construction additions and scalar multiplications;
- target-key records, unique keys, collisions, serialized and deep bytes;
- `D2+R` attempts, lookups, hit records, witness replays;
- covered target count and fraction, per offset and aggregate;
- distinct quotient equations, rank, and full-rank offset count;
- total online work and amortized work per target;
- peak retained advice and cumulative transient advice bytes;
- peak RSS, wall time, and exact replay digests.

## Positive Controls

- every reported witness replays to its named public target;
- every aligned offset has the exact `(T+|A|-1)|R|` key-record bound;
- `K=1` matches the first offset of the prior aligned-batch protocol;
- the unrelated control uses the same fixed `D2` and scan implementation;
- no private scalar is used by the candidate route.

## Success Criterion

This experiment records a scoped many-target signal only if, for a tested
cohort, aggregate aligned coverage is at least 80% of the matched unrelated
control, the per-target charged work is reported, and all witness replays
pass. A stronger signal requires the same condition for at least three
coordinate families and two nontrivial offset counts.

No ECDLP promotion gate is defined here. Per-offset rank is reported only as
an obstruction diagnostic; independent offsets carry separate unknown target
logs unless an additional relation between offsets is supplied.

## Falsification Criteria

- any witness or equation mismatch falsifies the implementation;
- coverage below the control after charged work is a scoped negative for the
  offset-amplification hypothesis;
- peak or cumulative advice growing linearly in `K` without a coverage gain
  preserves the prior diagonal storage/rank boundary;
- full rank in one offset is not sufficient for promotion.

## Cost Boundary

With fixed `D2`, the idealized aligned cost for `K` offsets is approximately
`K*B*(T+B)` target-key work plus `K*B^3` scan work. The experiment reports
actual operation counters and transient memory rather than treating the
symbolic bound as a breakthrough.

## Reproduction Command

```bash
python3 src/typed_aligned_offset_amplification.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --target-exponents 1 1.5 2 \
  --offset-counts 1 2 4 8
```
