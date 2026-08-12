## Handoff: SGCP V7 exact-commit theory review

### Claim or task

Determine whether exact commit
`fe093d3d80bba38e729fd8c98f78bed569e5087d` is ready for a separate
EXP-SGCP-EMBED-002 launch-plan design.

### Status

`NEGATIVE RESULT` for V7 protocol readiness and `RESTRICTED THEOREM` for
the fixed finite graph/downward-ideal equivalence.

Decision: `REVISE` for launch-plan design only. Execution remains `NO-GO`.
The underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`,
and `NOVELTY-UNVERIFIED`.

### Assumptions

- Only exact committed blobs at `fe093d3` were treated as evidence.
- Exactness is limited to the registered finite curves, predicates, compiler,
  downward ideals, graph, objective, and gate.
- Structural resource reservations are combinatorial ceilings, not wall-time,
  RSS, I/O, allocator, or CPU authorization.
- No generated density row, canonical matrix, runner, plan, or run was
  created by this review.

### Evidence so far

- The V7 development-log hashes match the exact committed artifacts.
- The fixed downward-ideal conflict-graph theorem, five-field objective,
  exact gate arithmetic, frozen B4 complete oracle, and fail-fast registered
  admission remain internally consistent.
- The frozen B4 oracle independently reconstructs complete candidate and
  eligible lists, including recursive parent pairs.
- The generated Mobius control is factor-base-only; the frozen p=19, B=4 row
  remains the only constructed density row.
- Ledger state remains `review_required`, with `runs=[]` and
  `maximum_runs=0`.

### Findings

1. `BLOCKER`: the successful actual-work receipt omits one density-primary
   `curve.points()` call per cap. The charge was added to an older sibling
   primary routine, while V7 `independent_density_primary_optimum` enumerates
   the curve without charging `primary_curve_point_enumerations`. A valid
   four-cap report can therefore claim zero primary point enumerations and
   `actual_work_complete=true`. The focused test asserts only actual less
   than or equal to reservation, so the zero count passes.
2. `MEDIUM`: canonical secondary-objective independence is overstated. A
   separate DFS independently proves the retained-support optimum, but the
   constrained count, public-edge count, retained maxima, and lexical
   tie-break are replay-confirmed by a structurally similar verifier. A
   structurally distinct complete five-field oracle exists only for frozen
   B4. Outside that fixture, the secondary objective must be labeled
   replay-confirmed unless a distinct proof implementation is added.

### Restricted theorem

For the fixed representative compiler and downward ideals, graph independence
is equivalent to injectivity of EC evaluation on the union of selected ideals.
Each eligible maximum has an injective individual ideal. An edge is exactly a
collision in the union of two ideals. Conversely, any collision in the global
union lies within one ideal, contradicting eligibility, or across two ideals,
producing an edge.

This theorem does not cover non-downward partial operations, a different
compiler or factor base, algebraic coordinate attacks, relation generation,
matrix rank, target descent, or an ECDLP exponent claim.

### Failure modes

- A completed receipt can undercount primary point enumeration.
- Tests establish only upper-bound compatibility, not exact successful counts.
- Canonical secondary fields are replay-confirmed rather than independently
  proved outside frozen B4.
- Canonical B6/B8 feasibility, wall time, RSS, rank, descent, and rho
  comparison remain open.

### Next concrete action

Prepare one no-run V8 repair that charges and positively tests every
density-primary and frozen point enumeration, narrows canonical secondary
exactness to replay-confirmed, preserves the frozen B4 complete oracle, and
requests fresh exact-commit review before launch-plan design.

### Artifact paths

- `fe093d3:experiments/EXP-SGCP-EMBED-002/contract.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/specification.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v7.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/development-test-log-v7.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/source-self-review-v7.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `fe093d3:tests/test_sgcp_embed_family.py`

