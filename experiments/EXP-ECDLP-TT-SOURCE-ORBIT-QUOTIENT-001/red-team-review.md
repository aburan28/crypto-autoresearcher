# Red-team review: source-orbit quotient locator

## Handoff: quotient interpretation audit

### Claim or task

Try to invalidate the source-orbit quotient result or expose an omitted cost,
special-curve assumption, or verifier weakness.

### Status

`NEGATIVE RESULT` for the strict sub-full hypothesis; `OBSERVATION` for exact
full-budget quotient correctness.

### Assumptions

- Only the two fresh 14-bit generated curves are in scope.
- The class selector is source-only and target-independent.
- All class members are lifted with the original equality residual before
  witness acceptance.
- The comparison is a toy operation model and does not forecast a deployed
  curve.

### Evidence so far

- Full controls pass exact support, held-out support, valid witnesses, and
  matched rho on both curves and all four families.
- The independent verifier reconstructs the suffix partition with a separate
  affine addition implementation and checks the reported class digest,
  member count, full-entry counts, and every lifted class index.
- Clean committed verifier run `RUN-TT-SOURCE-ORBIT-QUOTIENT-005` passes with
  `dirty=false`.
- The source cache is target-independent but large enough to matter: about
  22.92-24.76 MB for this toy instance. Lift cache entries and lift queries
  are separately recorded.

### Failure modes

- A field-multiplication-only comparison would overstate the result because
  quotient evaluation performs two source additions and raises inversion/
  point-add counts.
- The class count is 55 rather than a small constant: the observed reduction
  is the ordinary sign-orbit compression of 100 source pairs, not a new
  low-dimensional factor base.
- Full exactness does not establish an online improvement; every full-class
  predicted zero still incurs a member-level lift, and sub-full budgets lose
  support or rank.
- The verifier shares the repository's point-witness representation and
  relation fixture format, so it is independent in fixture regeneration and
  class arithmetic but not a fully independent implementation of every
  upstream relation transcript producer.
- The experiment has no cryptographic-scale sweep, individual-log descent, or
  fixed-curve preprocessing crossover.

### Next concrete action

Use the negative result to constrain the next candidate: retain the x-orbit
identity only as a correctness control, and implement a genuine shared-sign
state operator whose charged addition/inversion count is below the original
full predicate before testing any smaller class budget. Add a permutation,
alternate-coordinate, and random ordinary-curve control in that successor.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001/analysis.md`
- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001/runs/RUN-TT-SOURCE-ORBIT-QUOTIENT-005/raw-result.json`
- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001/src/verify_orbit_quotient_replication_harness.py`
