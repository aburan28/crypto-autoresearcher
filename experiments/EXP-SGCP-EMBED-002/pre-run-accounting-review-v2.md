# EXP-SGCP-EMBED-002 independent accounting review v2

## Handoff: version-2 accounting boundary

### Claim or task

Determine whether version 2 completely charges the matched-density experiment
and can support a fixed-curve preprocessing conclusion.

### Status

`NEGATIVE RESULT`; recommendation `STOP` for fixed-curve preprocessing claims
and `REVISE` before canonical execution.

### Assumptions

- The review was read-only at commit
  `9b9253a664884c0faa5b89160c63b114a48deac3` plus the uncommitted V2 snapshot.
- No curve-family sweep was run.
- Dynamic checks used only the frozen `p=19,q=23,B=4` fixture and unit tests.
- This rejects the current evidence boundary, not the coordinate predicate
  hypothesis.

Reviewed snapshot SHA-256 values:

- producer: `43b37f60269a4cfb54544aef406013c320c2548c2b2e74ce154b49c1fa4a9965`
- verifier: `0f1f8164553a0b904afaedf9a8a7abc7be9947dd120cac47ccaa306004930a2a`
- tests: `e6874a974b13de2c27db7088593130b920fb460db44b5c721d5bab99a9f66310`

### Evidence so far

- All twelve V2 unit/frozen tests passed, but they do not establish complete
  document accounting or a complete matched-null grid.
- On frozen B=4, reversing cap order moved most model-cache work between cap
  receipts. The cap counts therefore measure search-order allocation rather
  than an intrinsic cap-local cost.
- Per-cap serialized byte counts are nested inside the public/private totals.
  Summing both levels double counts them, while public plus private omits the
  row envelope.
- The protocol itself excludes preprocessing crossover, rank, target descent,
  rho improvement, and deployment claims. Version 2 is not an ECDLP solver.
- With up to order `B^4` degree-four candidates, explicit pair outputs and
  degree-eight expansion can already require order `B^8` work before the
  exponential branch-and-bound search. Fixed `B in {4,6,8}` cannot estimate an
  attack exponent.

### Failure modes

1. The verifier accepts incomplete and empty documents because it does not
   bind the experiment ID, parameter grid, row uniqueness, four-null blocks,
   summary, or document operation totals.
2. A mutable model cache spans all four caps, making cap-local operation
   receipts depend on cap execution order.
3. The counters omit heap, bitset, sorting, serialization, hashing, and some
   field work. They are not a complete CPU-cost measure.
4. Verifier field/group work, peak memory, serialized output, and wall time are
   not charged.
5. `deep_size` measures retained objects, not peak working memory.
6. The node cap bounds popped search nodes, not greedy initialization,
   certificate serialization, or complete cell wall time.
7. Nested byte measures are not an additive storage decomposition.

### Next concrete action

Create a version-3 frozen repair with a complete document-grid verifier and
disjoint row-shared/cap-local receipts; narrow every counter and memory label to
what it actually measures before requesting another accounting decision.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
