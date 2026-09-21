# Experiment Contract: D4 Membership Recovery Batch V1

## Hypothesis

The D4 membership plus deferred D2 recovery route may become competitive when
fixed-curve advice is amortized across many public targets. The experiment
measures this directly with shared advice, total online work, amortized work,
and success probability.

This is a fixed-curve batch experiment. It is not a generic-group theorem or
an ECDLP break.

## Parameters

- immutable input: `development/TYPED-FIVE-EC-V1/raw-result.json`;
- predecessor route: independently verified `D4-MEMBERSHIP-RECOVERY-V1`;
- three generated prime-order curves and four coordinate families;
- batch sizes `k in {1,4,16,64}`;
- `supported_batch`: public targets `A_i + D4_i`, guaranteeing a positive
  relation control without private scalar material;
- `translated_control`: public `planted + j*generator` targets;
- routes: recursive D2+D2, materialized D4, membership plus recovery;
- one retained advice charge per batch; every target query and support-hit
  recovery is charged.

## Metrics

- batch target digest and target count;
- successful target count and empirical success probability;
- total and amortized online work;
- advice words and offline build work;
- `S*(T/k)^2/(epsilon*q)` diagnostic, only as a finite toy frontier;
- predecessor route receipt hash and independent batch aggregation replay.

## Success criterion

The batch aggregation must exactly reproduce all per-target route metrics and
hit sets from the predecessor semantics. A useful fixed-curve improvement
requires the membership route to beat materialized D4 after shared advice,
offline construction, amortized work, and success probability are charged.

## Falsification criterion

Any target schedule mismatch, aggregate mismatch, predecessor hash mismatch,
or accepted mutation falsifies this batch record. A finite batch win is not an
ECDLP exponent result.

## Reproduction

```bash
python3 src/d4_membership_batch.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --batch-sizes 1 4 16 64

python3 src/verify_d4_membership_batch.py \
  /path/to/raw-result.json
```

## Handoff

### Claim or task

Measure whether many-target amortization rescues D4 membership with deferred
D2 recovery.

### Status

HYPOTHESIS, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- target batches share fixed-curve D2 and D4-support advice;
- supported targets are public positive controls, not deployment claims;
- the predecessor exact-route receipt remains immutable.

### Evidence so far

- membership advice is lower than materialized D4;
- support-hit recovery is the dominant online cost;
- a batch could only help if recovery work amortizes or is shared.

### Failure modes

- each supported target can trigger a fresh D2 scan;
- translated controls can dilute success probability;
- target schedule construction can be mistaken for attack work.

### Next concrete action

Run both target schedules, preserve the predecessor receipt linkage, and
red-team aggregate accounting.

### Artifact paths

- `src/d4_membership_batch.py`
- `src/verify_d4_membership_batch.py`
- `development/D4-MEMBERSHIP-BATCH-V1/RUN-001/`
