## Handoff: source-tag join v1 pre-run review

### Claim or task

Determine whether v1 could validly test and promote source-tagged D2+D2 routing.

### Status

NEGATIVE RESULT for v1 readiness; REVISE. No repository development or
canonical experiment was launched under v1.

### Assumptions

- The review concerns the bucket-scanning source-tag model, not index calculus
  or source-aware decomposition generally.
- Source provenance is syntactic advice and must be charged.
- Candidate and baselines use the same outer factor ordering and exact support.

### Evidence so far

- With the same outer scan, materialized D4 performs the same `Q-f` operations
  and no inner EC verification; the v1 strict online-dominance gate was
  unattainable.
- V1 omitted exact D2-complement MITM even though its D2 point dictionary was
  already available.
- Its completed-tag shuffle did not preserve compositional source structure.
- One selected witness per D2 point can create policy-specific source tags.
- Fixed tag counts can saturate all `r^3` routes and manufacture a zero route-
  storage slope without improving online work.

### Failure modes

- Null mismatch manufactures an ordinal or pair-sum signal.
- A source tag secretly depends on constructor scalars or factor logs.
- D2-squared incidence is moved into route advice or build workspace.
- Candidate witnesses preserve support but lose rank when relation collection
  is restored.
- Reused toy schedules or fixed-r saturation are overinterpreted as scaling.

### Next concrete action

Review v2 before launch. V2 must split structural and compiler gates, add source-
record and exact-margin nulls, exact D2 and partial-D4 baselines, fresh schedules,
streaming route compilation, all-witness diagnostics, and ineligible toy slopes.

### Artifact paths

- `experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/contract-v1.md`
- `experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/contract.md`
- `experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/theory.md`
- `experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/src/source_tag_join.py`
