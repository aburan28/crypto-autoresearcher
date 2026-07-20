## Handoff: SGCP V3 independent preflight review

### Claim or task

Audit whether the committed no-run V3 snapshot closes the provenance, exact
matrix, family-gate, representative-compiler, source-interface, and accounting
holes that forced the V2 `REVISE` decision.

### Status

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`, and V3
`review_required`; development curve rows and canonical runs remain zero.

### Assumptions

- Prime-order ordinary short-Weierstrass toy curves only.
- The deterministic curve generator and predicates use coordinates but never
  scalar indices.
- The tested object is each predicate composed with the frozen
  lexicographically least nonidentity-2F representative compiler.
- Every canonical primary and secondary optimizer cell must be exact; one gap
  invalidates the whole matrix.
- The public label-to-formal source table is explicit charged advice.
- Structural-work fields are combinatorial cells, not operation totals.
- Relation generation, rank, descent, preprocessing crossover, rho comparison,
  and exponent claims are outside this experiment.

### Evidence so far

- V2's finite density objective and corrected energy definitions survived
  independent review, but V2 accepted provenance, schema, scalar, objective,
  exactness, and empty-document mutations.
- V3 independently derives curve and predicate transcripts, freezes the exact
  168-row/672-cell matrix and six-pair gate, closes schemas, and recursively
  rejects scalar-material keys.
- V3 emits and verifies the representative table and public source table.
- V3 removes operation-total and peak-memory claims, resets cap-local caches,
  and labels JSON bytes as nested and nonadditive.
- The focused V3 unit/frozen suite passes without creating a curve-family row.

### Failure modes

- Producer replay and verifier replay may still share a search-model error;
  the separate depth-first proof must be evaluated for independence.
- Exact closure of every B=8 cap may exceed future budgets.
- A complete family effect may be entirely compiler-specific.
- Observational wall time is not external cost evidence.
- The protocol still has no relation-generation, rank, descent, or attack path.

### Next concrete action

Run three fresh read-only reviews on one committed V3 snapshot and issue
separate `GO` or `REVISE` decisions for theory, accounting, and red-team scope.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/research-question.json`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/literature-review-v1.md`
- `experiments/EXP-SGCP-EMBED-002/decision-v2.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v3.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v3.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v3.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
