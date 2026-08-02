# Pre-implementation benchmark review v2

## Handoff: accounting-layer re-review

### Claim or task

Re-audit the shared accounting note and both experiment contracts and ledgers
for benchmark correctness only.

### Status

`REVISE`, with five narrow accounting repairs applied after review. This record
does not authorize implementation or make a mechanism verdict.

### Assumptions

- `n=B^5`.
- Advice limits are byte caps; a stronger comparator may use less advice when
  that minimizes total work.
- Independent-row yield may depend on current rank.
- Generic theorem quantities retain their original bit and oracle-query units.

### Evidence so far

- Tier A, Tier B, one-instance boundaries, exponent-loss formulas, and crossover
  requirements were correct.
- The stationary binomial confidence budget was not general enough for
  rank-dependent `eta_r`; the shared note now uses a geometric-sum quantile and
  retains the binomial formula only as a stationary or conservative special case.
- Equal-byte BSGS was incorrectly forced to consume the entire advice cap. It
  now minimizes total work over `1<=m<=M_B` and labels `m=M_B` as an online-only
  fixed-advice frontier.
- Constructive generic preprocessing now uses its own complete record size,
  valid parameter set, and total-work minimization over that set.
- The exact preprocessing theorem is reported in advice bits. The record-count
  ratio is labeled an exponent diagnostic, and the preprocessing-query
  diagnostic is restored.
- GENROOT support rows now use exact `N_2,N_3` bounds, with `Theta(B^j)` retained
  only as a measured collision-light specialization.

### Failure modes

- Reapplying a stationary rank-yield model to late-rank rows.
- Weakening a comparator by forcing excessive advice use.
- Reusing BSGS record size for a generic walk construction.
- Substituting field operations, traffic, relation probability, or batch sharing
  into a theorem stated in generic-group queries and advice bits.

### Next concrete action

Independently re-read the repaired formulas and issue a final accounting-only
`GO` or a precise remaining revision list before any implementation decision.

### Artifact paths

- `notes/ecdlp_relation_preprocessing_accounting_20260718.md`
- `contract.md`
- `object-dimension-ledger.md`
- `../EXP-ECDLP-SUBSET-NORM-TREE-001/contract.md`
- `../EXP-ECDLP-SUBSET-NORM-TREE-001/object-dimension-ledger.md`
