# Result Accounting Review

## Handoff: Coordinate Stage-A accounting audit

### Claim or task

Audit compiler/audit separation, accounting, baselines, hashes, null
calibration, and V2/V3 reproducibility.

### Status

NEGATIVE RESULT

### Decision

`REVISE`. The scoped geometry result is reproducible and no false win
occurred. Accounting and run provenance are incomplete for canonical
acceptance.

### Assumptions

- Reviewed source is pinned to `fefe32f5`.
- V3 is bound to source SHA-256 `5af1bfcc...06e5c45b`.
- Stage A is support geometry, not a DLP solver or exponent result.
- Factor-base logs, relations, rank, linear algebra, and descent are absent.

### Evidence so far

- All 582 configurations reproduce their support, split, ratio, and gate
  arithmetic.
- V2/V3 arithmetic records match after reporting-only fields are removed.
- Raw, source, and stderr hashes match the V3 manifest.
- Factor bases and point-only D2/D3 tables were built and hashed before target
  generation and the subgroup census.
- Candidate `D2` ratios are `0.990-1.000`; missing charges cannot turn this
  effect-size miss into a pass.

### Benchmark context

| bits | q | compiler group ops | JSON advice | query ops/target | supported targets | measured rho |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 953 | 488-700 | 3,907-5,503 B | 8.46-26.29 | 53.1-92.2% | 159 |
| 12 | 3,919 | 860-1,152 | 6,879-9,128 B | 32.45-50.45 | 30.5-50.0% | 456 |
| 14 | 15,583 | 2,002-2,528 | 16,354-21,060 B | 58.27-74.75 | 39.1-54.7% | 444.5 |

These point-decomposition queries are not comparable to discrete-log recovery:
they assume neither factor-base logarithms nor relation rank and descent.

### Failure modes

- Factor-base build work is omitted from the summary compiler total.
- Query table traffic, witness verification, scalar audit work, and null-source
  hash/permutation work are not fully charged.
- Field additions, subtractions, exponentiation internals, hash costs, and
  memory traffic are unavailable.
- JSON bytes, Python deep-size proxies, and process RSS are different memory
  models and must not be combined.
- The six rho trials are unoptimized and omit some finalization costs.
- The original manifest lacks contemporaneous environment and dirty-state
  receipts.
- The original verifier does not cover every cost or every transient witness.

### Exact recoverable omissions

- Candidate factor-base construction: 3,168 group operations, 10,323 field
  multiplications, and 2,862 inversions.
- Candidate query traffic: 387,343 point negations and D3 lookups.
- Executed candidate witness checks: 23,880 group operations.
- Candidate scalar audit: 399,906 support transitions, 107,409 canonical
  classes, and 584,699 split pairs.
- Full-sweep source-null setup: 1,276,270 source-PRF hashes and 1,276,270
  random-x permutation entries.

### Next concrete action

If these frozen constructors are revisited, rerun from an isolated worktree at
the pinned source with phase-separated factor-base, compiler, resident advice,
query, witness, audit, and rho receipts. Do not spend that canonical-run budget
unless a successor first produces a geometry or representation signal.

### Artifact paths

- `development/DEV-COORD-EXPANSION-V3/run-manifest.json`
- `development/DEV-COORD-EXPANSION-V3/raw-result.json`
- `development/DEV-COORD-EXPANSION-V3/verifier-receipt.json`
- `development/DEV-COORD-EXPANSION-V3/analysis.md`
