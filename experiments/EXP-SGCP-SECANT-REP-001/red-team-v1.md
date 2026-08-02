# Red-Team Review V1

## Handoff: Exact-commit falsification

### Claim or task

Attack preregistration commit
`cc5e93d356ca114b09e6eff4d8c2a89cd3b384ae` for hidden confounds and
overclaim.

### Status

`HYPOTHESIS`: `REVISE`. Execution remains forbidden.

### Exact blockers

- Canonical residue ordering changes under `y -> -y` and admissible
  short-Weierstrass rescaling.
- Changing degree-two representatives changes the formal degree-four universe;
  V1 incorrectly called it identical.
- Singleton fibers and duplicate controls could make the matrix vacuous.
- The 31-control percentile and tie semantics were undefined.
- One cap, one factor base per curve, and reusable optimizer state could leak
  fixture or process effects into the score.
- The positive control did not demonstrate a known representative advantage.
- Conflict reduction was not a required mechanism gate.
- Comparison, sorting, deduplication, graph, cache, I/O, storage, failed
  attempts, and separated role costs were underspecified.

### Required controls

- Fixed sign-flip and nonzero coordinate rescalings with no best-chart choice.
- Source-label permutations and canonical line normalization.
- Exact nonvacuity thresholds and finite-rank ties.
- Multiple factor-base draws and the inherited cap schedule.
- Fresh optimizer state per compiler/cap cell.
- Synthetic positive, invariant negative, and exhaustive tiny controls.
- Separate shared, producer, optimizer, verifier, storage, and failure ledgers.

### Next concrete action

Bind these controls and accounting boundaries in a zero-run v2 revision, then
obtain fresh review.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/contract.md`
- `experiments/EXP-SGCP-SECANT-REP-001/specification.json`
- `research_ledger.md`
