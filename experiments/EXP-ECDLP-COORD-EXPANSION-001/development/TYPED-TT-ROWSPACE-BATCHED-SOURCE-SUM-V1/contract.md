# Experiment Contract: TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1

## Hypothesis

For a fixed curve and reused target-independent row-space locator, caching the
source points `A+R0+R1+R2+R3+R4` across a batch of targets reduces repeated
elliptic point additions without changing the row-space, witness, or predicate
semantics.

## Null hypothesis

Target batching does not reduce fully charged source work once the source-point
cache memory, target predicate evaluations, row-space construction, and
reconstruction costs are included.

## Parameters

- field/curve family: generated ordinary prime-order prime-field toy curve
- input: the committed 16-bit fixture from `TYPED-TT-ROWSPACE-SCALE-PROBE-V1`
- curve: `p=63311`, `q=63199`, `A=B=14`
- coordinate families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`
- target stream: the same deterministic 15-target stream as the scale probe
- row-space: adaptive cut-3 basis, bounded at 64 source prefixes
- suffix sample: four deterministic `B^2` columns
- validation prefixes: 256 deterministic prefixes from the full source order
- batch widths: `1, 2, 4, 8, 15`
- baseline: current per-target `SourceOracle` evaluation
- candidate: target-independent shared source-point cache followed by one
  target predicate evaluation per target
- negative control: same query schedule with target-separated source caches

## Metrics

- source point additions, field operations, and inversions;
- source-advice reads and unique source sums;
- target predicate field operations;
- row-space and reconstruction field operations;
- retained advice bytes and source-point-cache bytes;
- sampled entries, row-space rank, predicate mismatches, and independent
  reference mismatches;
- wall-clock time for orientation only.

## Positive control

The source sum for a fixed index tuple is target-independent. A shared cache
must compute each queried source sum once while evaluating all requested target
predicates exactly.

## Negative control

The target-separated cache uses the identical query indices and predicate
logic, but keys each source sum by `(target, indices)`. It should preserve
exactness while removing cross-target source-sum reuse.

## Success criterion

The shared candidate must preserve all sampled values and independent reference
checks, show monotonically increasing target-predicate work with batch width,
and reduce source point additions relative to the current per-target baseline
for at least one width. Any claim is restricted to fixed-curve batching.

## Falsification criterion

The candidate is a negative result if it introduces no source-operation saving,
if the cache is too large to be a viable fixed-curve tradeoff, or if any
sampled or independently checked value differs. A source-operation saving
alone does not pass the ECDLP promotion gate.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_batched_source_sum.py \
  development/TYPED-TT-ROWSPACE-SCALE-PROBE-V1/RUN-001/input-fixture.json \
  --families random_x source_prf_x x_interval rational_union \
  --max-prefixes 64 --validation-prefix-limit 256 \
  --sample-limit 4 --target-budget-factor 1
```
