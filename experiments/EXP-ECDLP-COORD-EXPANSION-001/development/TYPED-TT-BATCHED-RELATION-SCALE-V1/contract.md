# Experiment Contract: TYPED-TT-BATCHED-RELATION-SCALE-V1

## Hypothesis

The fixed-curve shared-source-sum relation signal from the p947 fixture
survives on the next committed ordinary curve at `p=4027`, with source-work
savings and exact witness/support checks across public coordinate families.

## Null hypothesis

Scaling the same construction causes support, held-out coverage, quotient rank,
or diagnostic-solution agreement to fail for one or more families, or removes
the source saving after the same control is charged.

## Parameters

- curve: `recursive-toy-p4027-a2225-b334-q4129`;
- dimensions: `A=7`, `B=8`, six generated relation targets plus four supported
  held-out targets where available;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- row-space: adaptive cut-3 construction, full predicted suffix scan;
- baseline: materialized typed D4 support and independent post-hoc diagnostic
  solution digest;
- control: target-separated source sums discarded after each target.

## Metrics and gates

- require exact direct references, witnesses, support, and held-out expected
  witness coverage;
- compare row-space and quotient ranks between shared and separated modes;
- report diagnostic solution agreement per family, including failures;
- report source additions, cache bytes, logical payload, and matrix work;
- no promotion unless all family-specific boundaries are preserved.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_batched_relation_transcript.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --curve-id recursive-toy-p4027-a2225-b3340-q4129 \
  --families random_x source_prf_x x_interval rational_union
```
