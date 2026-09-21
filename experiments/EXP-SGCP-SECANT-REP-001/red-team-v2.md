# Red-Team Review V2

## Handoff: V2 exact-commit falsification

### Status

`HYPOTHESIS`: `REVISE` before implementation design. Execution remains
forbidden.

### Closed from v1

V2 adequately defined EC formulas, multiset witnesses, residue and hash
encodings, source permutations, common versus formal universes, multiple
factor-base draws, fixed charts, fresh optimizer state, joint support/conflict
gates, and separated costs.

### Remaining blockers

- Hash controls did not bind a complete factor-base digest.
- Conflict density was undefined for fewer than two eligible vertices.
- Formal-lex Hamming scope and the two-cap objective vector were underspecified.
- The synthetic positive control exercised only the optimizer, not candidate
  representative selection.
- Outcome predicates and replication quantifiers were ambiguous.
- Implementation defects were inconsistently treated as hypothesis
  falsification.
- The inherited optimizer and sampling reference was not hash-pinned.
- The literature gate remained open.

### Next concrete action

Publish a zero-run v3 repair and keep implementation blocked pending v3 review
and literature completion.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/contract.md`
- `experiments/EXP-SGCP-SECANT-REP-001/hypothesis.json`
- `experiments/EXP-SGCP-SECANT-REP-001/specification.json`
