## Handoff: SGCP V8 exact-commit theory review

### Claim or task

Determine whether exact commit
`a1719f7d910d3cc454911a55ceb8b30d833a0b2d` is ready only for design of a
separately reviewed, hash-complete launch plan.

### Status

`OBSERVATION` for plan-design readiness and `RESTRICTED THEOREM` for the fixed
finite graph/downward-ideal equivalence.

Decision: `GO` for launch-plan design only. This does not authorize a density
row, matrix, runner, execution, budget change, or coordinator state change.
`maximum_runs=0` remains binding. The research claim remains `HYPOTHESIS`,
`TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- Only exact committed scoped blobs were treated as evidence.
- The theorem is limited to the frozen compiler and downward-closed ideals.
- The standalone complete five-field oracle covers frozen B4 only.
- Structural receipts are not CPU, wall-time, parser, allocator, RSS, disk,
  I/O, cache-traffic, or memory-bandwidth measurements.
- Missing, unresolved, exhausted, or invalid evidence remains `INCONCLUSIVE`.

### Evidence so far

- For eligible maxima, independence in the pair-conflict graph is equivalent
  to injectivity of EC evaluation on the union of their downward ideals. An
  internal collision contradicts vertex eligibility; a cross-ideal collision
  creates an edge.
- Downward closure supplies the partial-operation associativity and monotonic
  constrained-label lemma. Injective evaluation supplies unique public formal
  sources, and degree-eight final edges are excluded by construction.
- The separate DFS independently proves only retained-support optimality.
  Secondary constrained-count, edge-count, retained-maxima, and lexical fields
  are correctly labeled replay-confirmed outside the frozen-B4 oracle.
- The gate remains a preregistered finite toy rule, not a significance or
  scaling result. Complete invalid evidence remains inconclusive.
- The nine hashes in the V8 test log match the exact commit blobs. Ledger state
  remains `review_required`, `runs=[]`, and zero budget.

No blocker, high, or medium theory finding was identified.

Two low findings remain:

1. The proposed 900-second and 4-GB role values in `hypothesis.json` are not
   approved limits. A future plan must give the authoritative zero budget
   precedence and derive external resource limits separately.
2. Three fail-closed producer diagnostics still say `version-7` despite the V8
   schema. This is stale provenance wording, not an execution escape.

### Failure modes

- B6/B8 lack a standalone complete five-field semantic oracle.
- B6/B8 search feasibility, output size, cache occupancy, CPU, wall time, RSS,
  allocator/parser memory, traffic, disk, and I/O are unmeasured.
- The theorem does not cover other compilers, non-downward operations,
  relation generation, rank, factor-base logarithms, descent, or an ECDLP
  complexity claim.
- No current artifact supports an exponent, preprocessing crossover, rho
  improvement, deployment, or prime-field ECDLP result.

### Next concrete action

Subject to unanimous review, design but do not execute a separate plan pinned
to `a1719f7d...`, with hash-complete commands, environment, immutable role
artifacts, and external resource limits. Any B6/B8 limit hit must be
`INCONCLUSIVE`, and execution would require another review and coordinator
approval.

### Artifact paths

- `git:a1719f7d910d3cc454911a55ceb8b30d833a0b2d`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v8.md`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v8.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`

