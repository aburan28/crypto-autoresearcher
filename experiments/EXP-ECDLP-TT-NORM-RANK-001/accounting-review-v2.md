# Accounting review of v2

## Handoff: exact schedule audit

### Claim or task

Recompute the v2 cross-product, cache lifetime, workload, comparators, cohort
semantics, and deterministic success boundary.

### Status

`GO` for the v2 schedule and comparator layer, before the later red-team
traffic repair.

### Assumptions

- Rank traffic needed the separate red-team access-model audit.

### Evidence so far

- Independently recomputed counts matched 24 source tables, 60 semantic cells,
  615868 source tuples, 2463472 RCB calls, 1539670 norm cells, 461901 power
  squarings, 288 rank jobs, 12 cohort spans, and 18 `D2+D3` jobs.
- The three target-family, deterministic-probability, and comparator blockers
  from v1 were repaired.
- Control ranks `(1,2,3,4)`, `(4,16,16,4)`, and `(2,1,1,1)` replayed.

### Failure modes

- This review accepted the aggregate traffic arithmetic supplied by v2; the
  subsequent red-team review correctly required a complete access model.

### Next concrete action

Use the v3 access model as authoritative for traffic.

### Artifact paths

- `execution-matrix-v2.json`
- `rank-traffic-model-v3.md`

