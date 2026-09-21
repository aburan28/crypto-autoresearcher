# D4 Membership Recovery Batch V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The predecessor D4-membership route was evaluated on 96 batches: 12
curve/family cells, two public target schedules, and batch sizes
`1,4,16,64`. The independent batch verifier reproduced all aggregate metrics,
validated the target digests, checked the predecessor receipt hash, and
rejected all five mutations.

## Charged batch frontier

Mean values across the 12 cells are shown below. Advice is charged once per
batch; online work is total work divided by batch size; epsilon is the
empirical successful-target fraction.

### Supported positive-control schedule

| Batch size | Route | Amortized work | Epsilon | `S*(T/k)^2/(epsilon*q)` |
|---:|---|---:|---:|---:|
| 1 | materialized D4 | 81.2 | 1.000 | 2,546 |
| 1 | membership recovery | 542.0 | 1.000 | 51,610 |
| 4 | materialized D4 | 81.6 | 1.000 | 2,558 |
| 4 | membership recovery | 551.8 | 1.000 | 50,378 |
| 16 | materialized D4 | 76.0 | 1.000 | 2,189 |
| 16 | membership recovery | 474.0 | 1.000 | 36,118 |
| 64 | materialized D4 | 76.0 | 1.000 | 2,190 |
| 64 | membership recovery | 462.0 | 1.000 | 34,008 |

### Translated control schedule, `k=64`

| Route | Amortized work | Epsilon | `S*(T/k)^2/(epsilon*q)` |
|---|---:|---:|---:|
| materialized D4 | 58.3 | 0.422 | 3,089 |
| membership recovery | 196.7 | 0.422 | 14,473 |

The supported schedule guarantees a public relation witness by constructing
`A_i + D4_i`; it is a positive control, not a deployed-target claim. The
translated schedule uses public `planted + j*generator` targets and measures
ordinary target dilution.

## Accounting

- immutable input SHA-256: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`;
- cells: 12; batches: 96;
- D2 build additions: 848;
- D4 build additions: 17,840;
- public target-schedule additions: 9,211;
- producer wall time: approximately 0.79 seconds;
- producer peak RSS: 42,254,336 bytes;
- verifier wall time: approximately 0.54 seconds;
- verifier peak RSS: 87,539,712 bytes.

The batch verifier is independent for aggregation and target-digest semantics;
the exact route semantics are linked to the independently verified
`D4-MEMBERSHIP-RECOVERY-V1` receipt by hash. No batch result hides a recovery
scan: the predecessor route emits per-target work, and the verifier sums those
records before computing amortized metrics.

## Interpretation

Many-target advice amortization does not rescue membership-only D4 recovery in
these cells. Each supported target causes a fresh D2 recovery scan, so larger
batches reduce neither the recovery work per target nor the charged frontier
enough to compete with materialized D4. This is a negative result for this
batching strategy, not for all batched algebraic recovery operators.

## Next positive question

Any successor must share the recovery computation itself, not merely reuse its
advice. The credible next direction is an algebraically grouped recovery
certificate or multipoint operator whose construction is smaller than
materialized D4 and whose application cost is sublinear in the number of
target complements.
