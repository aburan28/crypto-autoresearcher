# Experiment Contract: D4 Membership With Deferred Recovery V1

## Hypothesis

A fixed curve can retain the exact `D4` support as a membership-only index,
retain the smaller `D2` witness table, and recover four-source witnesses only
for target complements that pass the `D4` membership test. This may lower
advice for many-target fixed-curve use while preserving exact relation rows.

This is a fixed-curve preprocessing experiment, not a generic-group or
deployed-key claim.

## Null hypotheses

1. Membership hits do not recover exactly the same witnesses as materialized
   `D4`.
2. The retained D2 recovery table plus D4 support keys costs as much as or
   more than materialized D4.
3. Recursive recovery on support hits erases the online benefit.

## Parameters

- immutable input: `development/TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves and four coordinate families;
- target batch: planted, held-out, shifted-control;
- D4 membership: exact point-keyed support only, no D4 witness payload;
- recovery: for each support hit, scan D2 states, compute the exact
  complement state, expand all D2 witness products, and replay each witness;
- controls: recursive D2+D2, materialized D4, and exact state-ID pair index;
- all D2 witness records and all recovery operations are charged.

## Metrics

- D2/D4 support, witness records, and state digests;
- retained D2 advice and D4 support key fields;
- membership lookups, support hits, recovery D2 scans, candidate witness
  products, replay additions, and online work;
- advice words and `S*T^2/q` diagnostic;
- exact hit-set equality against recursive D2+D2 and materialized D4;
- independent replay and mutation rejection.

## Success criterion

The route is valid only if every recovered witness set equals materialized D4.
A fixed-curve improvement requires the membership/recovery route to beat
materialized D4 after D2 advice, support keys, offline construction, target
count, support-hit rate, and recovery work are charged.

## Falsification criterion

Any support mismatch, omitted witness, undercharged recovery scan, or accepted
verifier mutation falsifies the implementation. A finite advice/query win is a
fixed-curve observation only; it is not an ECDLP exponent result.

## Reproduction

```bash
python3 src/d4_membership_recovery.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union

python3 src/verify_d4_membership_recovery.py \
  /path/to/raw-result.json
```

## Handoff

### Claim or task

Measure whether exact D4 support membership plus deferred D2 witness recovery
improves the fixed-curve advice/query frontier.

### Status

HYPOTHESIS, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- D4 support advice is reusable across the target batch;
- D2 state and witness advice is retained for recovery;
- every support-hit recovery scan and witness replay is charged.

### Evidence so far

- materialized D4 is the fastest exact query route but retains witness payload;
- recursive D2+D2 has low advice but scans on every complement;
- explicit and state-ID pair tables remain dominated by their pair record count.

### Failure modes

- support hit rate can make recovery effectively a full D2 scan;
- D2 recovery advice can erase the D4 payload saving;
- membership support can be too small to yield relation coverage.

### Next concrete action

Implement and independently replay the support-only route on all registered
curves, families, and target controls.

### Artifact paths

- `src/d4_membership_recovery.py`
- `src/verify_d4_membership_recovery.py`
- `development/D4-MEMBERSHIP-RECOVERY-V1/RUN-001/`
