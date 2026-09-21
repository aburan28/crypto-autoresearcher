## Handoff: SGCP V9 exact-commit theory review

### Claim or task

Determine whether exact commit
`224189ce2acc054c4e319597940f34bb0edee619` is ready only for design of a
separately reviewed, hash-complete launch plan.

### Status

`OBSERVATION` for plan-design readiness and `RESTRICTED THEOREM` for the fixed
finite graph/downward-ideal equivalence.

Decision: `GO` for launch-plan design only. This does not authorize a density
row, matrix, runner, plan, execution, budget change, or coordinator state
change. `maximum_runs=0` remains binding. The research claim remains
`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- Only exact committed blobs were treated as evidence.
- The graph theorem is limited to the fixed compiler and downward-closed ideals.
- The standalone complete five-field oracle covers frozen B4 only.
- B6/B8 have independent primary proof and deterministic, structurally similar
  replay confirmation for secondary fields.
- Structural receipts are not CPU, wall-time, parser, allocator, RSS, disk,
  I/O, cache-traffic, or memory-bandwidth measurements.
- Missing, unresolved, exhausted, or invalid evidence remains `INCONCLUSIVE`.

### Evidence so far

- All nine hashes in `development-test-log-v9.md` match the exact commit blobs.
- The fixed pair-conflict graph remains equivalent to injectivity on a union of
  individually eligible downward ideals: internal collisions contradict vertex
  eligibility, while every cross-ideal collision creates a graph edge.
- The separate DFS independently proves the primary retained-support optimum.
  Secondary constrained-count, public-edge, retained-maxima, and lexical fields
  remain replay-confirmed outside the standalone frozen-B4 oracle.
- V9 changes accounting, path handling, producer guards, and phase closure
  without changing the mathematical object, gate, or ECDLP claim boundary.
- Exact-snapshot probes validated all 11 records and passed all 58 focused tests.
- No generated density row, matrix, runner, launch plan, run, or budget was
  created or changed.

No blocker, high, or medium theory finding was identified.

One low wording finding remains: `specification.json` says "full primary and
secondary proof" in one stopping rule. The surrounding exactness contract
correctly limits B6/B8 secondary evidence to deterministic replay, but the
phrase should be narrowed so it cannot later be quoted as independent
five-field proof.

### Failure modes

- B6/B8 lack a standalone complete five-field semantic oracle.
- B6/B8 feasibility, output size, cache occupancy, CPU, wall time, RSS,
  allocator/parser memory, traffic, disk, and I/O are unmeasured.
- Proposed 900-second and 4-GB role values are not approved budgets; the
  authoritative budget remains zero.
- The theorem does not cover other compilers, non-downward operations, formal
  quotients, relation generation, rank, factor-base logarithms, or descent.
- No current artifact supports an exponent, preprocessing crossover, rho
  improvement, deployment, or prime-field ECDLP result.

### Next concrete action

Obtain fresh accounting and red-team decisions on the same exact commit while
retaining `maximum_runs=0`; only unanimous scoped `GO` decisions could permit a
separate coordinator decision about launch-plan design.

### Artifact paths

- `git:224189ce2acc054c4e319597940f34bb0edee619`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v9.md`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v9.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
