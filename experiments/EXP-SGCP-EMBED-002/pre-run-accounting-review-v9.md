## Handoff: SGCP V9 exact-commit accounting review

### Claim or task

Audit exact commit `224189ce2acc054c4e319597940f34bb0edee619` for
accounting integrity and readiness for launch-plan design only.

### Status

`OBSERVATION`; decision `GO` for launch-plan design only. This is one review,
not authorization to create a plan, change `maximum_runs=0`, construct a
generated row, or execute anything.

### Assumptions

- Only exact committed blobs and bounded temporary probes were inspected.
- Frozen B4 remains the only standalone complete five-field oracle.
- B6/B8 secondary fields remain deterministic replay confirmations.
- Structural counters are not field/group operations, CPU, RSS, parser,
  allocator, disk, I/O, cache-traffic, or bandwidth models.

### Evidence so far

- All nine V9 test-log hashes match the exact commit blobs. The focused suite
  passes 58/58, all 11 records validate, and a regenerated ledger matches.
- Every stored counter has either a direct reservation mapping or the aggregate
  cache reservation. Completed cache lookup/miss and frozen, semantic, and
  primary enumeration counts have equality checks.
- Frozen graph/expansion actual values are 31 candidate evaluations, 66
  eligible conflict checks, 144 eligible pair-output cells, and 214 expansion
  cells. Their source reservations are 35, 595, 1,225, and 214.
- Charges occur inside the corresponding loops. Injected second-charge failures
  preserve value 2, the trusted reservation, a failed one-of-one unit, and
  `actual_work_complete=false`.
- The remaining frozen vector is 1/1/4 point enumerations, 218 replay nodes,
  250 primary nodes, replay caches 268/268, primary caches 56/129, 401
  retained-model calls, and 41,404 retained-model cells.
- Across the canonical 168-row source reservation, candidate, conflict,
  pair-output, and expansion ceilings total 27,496, 3,514,280, 7,056,056, and
  473,928. At the five-million primary-node ceiling, cumulative cache, call,
  and retained-cell bounds are enormous and are not feasibility forecasts.

No blocking accounting issue was assigned by this reviewer.

Two low findings remain:

1. `actual_work_complete` means completeness of the instrumented receipt, not
   universally that no exception occurred. A factor-base exception yields an
   invalid report and failed phase but can retain `actual_work_complete=true`.
2. Most successful graph, expansion, hash, retained-model, and aggregate-cache
   counters are dominance-checked rather than equality-checked. Their accuracy
   relies on the hash-bound instrumentation and frozen regression vector.

### Failure modes

- Canonical B6/B8 runtime, output size, cache occupancy, CPU, wall time, RSS,
  parser/allocator behavior, disk/I/O, and memory traffic remain unknown.
- Structural ceilings are too loose to establish 900-second or 4-GB feasibility.
- No standalone B6/B8 complete five-field oracle exists.
- No attack-level result or improvement over rho, BSGS, VOW, index calculus,
  linear algebra, or target descent is supported.
- `maximum_runs=0`, zero execution budgets, `review_required`, and `runs=[]`
  remain intact.

### Next concrete action

Route this accounting `GO` through the remaining exact-commit review gate; only
unanimous scoped `GO` decisions could permit a separate coordinator decision
about launch-plan design.

### Artifact paths

- `git:224189ce2acc054c4e319597940f34bb0edee619`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v9.md`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v9.json`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
