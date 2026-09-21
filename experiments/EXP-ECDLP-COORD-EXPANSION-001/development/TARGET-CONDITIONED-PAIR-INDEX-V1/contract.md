# Experiment Contract: Target-Conditioned Pair Index V1

## Hypothesis

For a fixed curve and factor base `R`, a pair-sum index over exact `D2+D2`
witnesses can replace the recursive scan over all `D2` states. A nonlinear
coordinate fingerprint of the pair sum may reduce retained key material while
keeping target-conditioned lookup and exact witness lift.

This is a fixed-curve preprocessing experiment. It is not an ECDLP attack or
a generic-group claim.

## Null hypotheses

1. Pair-index records and full `D4` witnesses do not agree exactly.
2. Coordinate buckets save only key fields; the four-source witness payload
   dominates advice.
3. Candidate replay and pair-index construction erase any online or
   fixed-curve tradeoff.

## Parameters

- immutable input: `development/TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves;
- four coordinate families: `random_x`, `source_prf_x`, `x_interval`,
  `rational_union`;
- target batch: planted, held-out, shifted-control;
- exact nondecreasing source tuples at levels D2 and D4;
- pair index: unordered pairs of D2 states, retaining every witness product;
- fingerprints: `(x mod 2^w, y mod 2^w)` for `w in {1,2,4,8}`, with a separate
  identity bucket;
- exact replay: recompute the four-source point and accept only if it equals
  the target complement.

## Metrics

- D2 and D4 supports, witness records, and state digests;
- pair-index record count, bucket count, collision distribution;
- offline point additions, inversions, multiplications;
- per-target bucket lookups, candidate records, replay additions, online work;
- logical advice words: bucket/key fields plus four source indices per record;
- `S*T^2/q` diagnostic, reported only as a finite toy frontier;
- exact hit-set equality against recursive D2+D2 and materialized D4;
- independent replay and deterministic mutation rejection.

## Positive and negative controls

- materialized exact D4 is the positive exactness control;
- recursive D2+D2 is the scan-cost control;
- width `1` is the deliberately collision-heavy fingerprint control;
- width `8` is the near-exact coordinate control;
- all returned witnesses are independently replayed against the curve.

## Success criterion

The experiment is a valid observation only if every route preserves the exact
four-source hit set. A fixed-curve improvement would additionally require a
strictly better charged advice/query frontier after pair construction, all
witness records, offline work, target count, and success probability are
included.

## Falsification criterion

Any exactness mismatch, omitted witness, uncharged pair record, or verifier
mutation that is accepted falsifies the implementation. If exactness holds but
the witness payload or replay cost dominates, record a scoped negative for this
pair-index representation only.

## Reproduction

```bash
python3 src/target_conditioned_pair_index.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --widths 1 2 4 8

python3 src/verify_target_conditioned_pair_index.py \
  /path/to/raw-result.json
```

## Handoff

### Claim or task

Measure whether nonlinear coordinate buckets can replace the recursive D2
scan while preserving exact four-source witness lift.

### Status

HYPOTHESIS, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- fixed-curve advice is reusable across the target batch;
- point additions and field operations use the disclosed affine proxy;
- bucket records are fully charged, including all source-index payloads.

### Evidence so far

- recursive D2+D2 is exact but scans every D2 state per progression point;
- materialized D4 is exact and has much larger retained state advice;
- prior unary and symmetry quotients did not change the scan exponent.

### Failure modes

- pair records may multiply witness payload beyond D4;
- coordinate collisions may make replay cost approach the full pair index;
- a key-field saving is only a representation constant if record count is fixed.

### Next concrete action

Implement producer and independent verifier, run all registered curves and
families, then preserve the exact frontier and red-team interpretation.

### Artifact paths

- `src/target_conditioned_pair_index.py`
- `src/verify_target_conditioned_pair_index.py`
- `development/TARGET-CONDITIONED-PAIR-INDEX-V1/RUN-001/`
