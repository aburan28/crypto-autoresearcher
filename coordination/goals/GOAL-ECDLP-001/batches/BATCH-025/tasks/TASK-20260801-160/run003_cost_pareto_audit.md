# RUN-SMTH-PILOT-003 cost and Pareto audit

Task: `TASK-20260801-160`
Status: design only; no execution authorized
Target: resource feasibility of the null-only `EXP-SMTH-002` instrument

## Exact workload and fresh-state boundary

RUN003 starts at deterministic index zero under the canonical frozen domain
`EXP-SMTH-002/v1`. It does not resume or ingest RUN002. The retired RUN002
domain was `EXP-SMTH-PILOT-001/v1`, so the canonical roster is independently
generated without adding the run ID to the seed preimage or changing the
experiment.

All output is isolated beneath:

- `experiments/EXP-SMTH-002/runs/RUN-SMTH-PILOT-003/`
- `experiments/EXP-SMTH-002/results/RUN-SMTH-PILOT-003/`

The roster is exactly 139 paths: two implementation records, six run records,
three run-specific result metadata files, and 128 closed certificate shards.
Any pre-existing target invalidates the attempt before construction begins.

## Fully charged cost table

RUN002 retained 1,700,608 of 4,186,112 records in 52 of 128 shards. Its
validated aggregate counters were 588.538158 CPU seconds, 392.02581237501 wall
seconds, 35,246,284 tracked bytes, 36,655,104 physical bytes at failure-receipt
time, and 5,610,411 primality checks. The ratio from retained to full records is
2.4615384615. These values are a planning prior only; RUN002 data are not
RUN003 observations.

| Charged quantity | Exact/linear planning value | Conservative planning envelope | Binding cap |
|---|---:|---:|---:|
| Factorizations | 4,186,112 exact | 4,186,112 | 4,186,112 |
| Reconstructions | 4,186,368 exact | 4,186,368 | 4,186,368 |
| Primality checks | 13,810,243 projected | 27,620,486 (2x) | 33,554,496 |
| Wall time | 964.99 s projected | 1,929.98 s (2x) | 7,200 s |
| CPU time | 1,448.71 s projected | 2,897.42 s (2x) | 28,800 s |
| Tracked disk | 86,760,084 B projected | 347,040,336 B (4x) | 34,359,738,368 B |
| Physical disk | 90,227,949 B projected | 360,911,796 B (4x) | 34,359,738,368 B |
| Concurrent RSS | no defensible point estimate | measured attempt maximum | 4,294,967,296 B |
| Workers | 4 | 4 | 4 |
| Open output files | at most 4 | 4 | 4 |

The enormous disk and CPU headroom is not evidence of feasibility; only a
completed run can establish it. No RSS point estimate is admitted. RUN002's
4,310,335,488-byte value was a retired-PID accumulator, while the 274,939,904-
byte RT146-C1 maximum was synthetic and not the scientific workload.

## What is charged

The wall, CPU, RSS, disk and descriptor ledgers begin before dependency import
and seed-roster generation. They include setup, deterministic object
generation, factorization, every prime check, every reconstruction, statistic
updates, JSON serialization, gzip compression, shard close/fsync/hash,
checkpoint construction and verification, terminal verification, and failure
cleanup. Setup and verification are not free side channels. RUN003 permits one
initial process launch and no resume or retry.

The run must report phase-level and total counters. The fully charged total,
not factorization-only throughput, controls feasibility. Reconstruction count
is 4,186,112 in-pipeline checks plus 256 independent closed-shard boundary
checks, for an exact cap of 4,186,368. Per-attempt cost is not multiplied by an
inverse success probability because exactly one launch is authorized and
feasibility has no retry policy.

## Controls before interpretation

Both null arms have identical record counts, shard layout, worker ceiling,
factorization/certificate function and resource monitor. Every certificate is
verified before shard acceptance. The first and last record of every shard are
independently reconstructed, giving 256 boundary records on completion. A
composite-as-prime injection and a one-byte shard mutation must be rejected by
pre-run self-tests.

Any descriptive IID-versus-additive difference is diagnostic only. With four
replicates, no threshold, p-value or belief update about `HEUR-DS-1`,
`H-SMTH-001`, or `H-SMTH-002` is permitted.

## Pareto audit

### ECDLP frontier

`dominated_by: generic Pollard rho`.

Pollard rho addresses the actual generic prime-order ECDLP target in expected
square-root group work. RUN003 has no source arm, performs zero elliptic-curve
group operations, and solves zero discrete logarithms. Thus it is not merely
slower on the same frontier; it does not supply an ECDLP algorithm at all.

Quantitative `sota_delta`:

- generic ECDLP time-exponent improvement: `0.0`
- generic ECDLP memory-exponent improvement: `0.0`
- ECDLP instances solved: `0`
- source/group queries: `0`
- Shoup-bound contradiction evidence: `0`
- additional null factorizations if complete: `4,186,112`

### Instrumentation frontier

RUN002 is not a completed comparator: it stopped after 52 shards and its RSS
quantity was contaminated. RUN003's planned advantages are fresh namespace,
canonical seed domain, active-epoch RSS accounting, and a complete charged
roster. These are integrity improvements, not demonstrated performance gains.
Before execution, the quantitative completion delta is still zero.

## Decision boundaries

- `completed_feasibility_only`: the instrument completed once inside all caps;
  this may support only a later resource-budget derivation and contract review.
- `failed_infrastructure_or_budget`: preserve the exact checkpoint; it says
  nothing about smoothness or ECDLP.
- `invalid_integrity`: repair or supersede the instrument; do not interpret its
  statistics.

No outcome of RUN003 can support an ECDLP breakthrough, beat Pollard rho, evade
the generic Shoup lower bound, or change a hypothesis or goal status.
