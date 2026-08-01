## Handoff: v5 source-implementation authorization

### Claim or task

Close the sole v4 blocker and decide whether source implementation may begin.

### Status

`OBSERVATION` - `GO` for source implementation only; execution remains
`REVIEW_REQUIRED` until source hashes, focused tests, implementation accounting,
and implementation red-team review pass.

### Assumptions

- Pending status fields are outputs of this gate, not defects to repair before
  the gate can decide.
- The source process remains confined to the v5 source-visible files.

### Evidence so far

- The source subtotal is `(1022,1512,8176,9688)`.
- The withheld target delta is `(25,0,200,200)`.
- The campaign upper bound is `(1047,1512,8376,9888)`.
- All four componentwise equalities are explicit and exact.
- `source-execution-matrix-v2.json` contains no target-partition count block,
  target specialization count, target tuple/value/cell descriptor, target
  schedule, or target-bearing digest.
- Source counts live only under `source_partition_counts` with explicit source
  prefixes.
- Isolated staging, closed IR, filesystem/environment audit, two frozen source
  artifacts, bound runtime identity, and the 29-mutation schedule remain in
  force.
- The claim remains toy, restricted, model-bound, and not an ECDLP
  improvement.

### Failure modes

- Prose capability rules are not evidence until implemented and mutation
  tested.
- A shared producer/verifier helper can invalidate implementation independence.
- Exact toy completion does not establish asymptotic scaling.

### Next concrete action

Freeze the v5 protocol commit, implement disjoint producer and verifier
closures, and return for pre-run implementation review.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/red-team-v4.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v5.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v2.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v4.json`
