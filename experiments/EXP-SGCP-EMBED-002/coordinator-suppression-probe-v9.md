# EXP-SGCP-EMBED-002 coordinator suppression probe v9

## Handoff: V9 completed-work counter suppression

### Claim or task

Test whether a completed frozen path independently enforces each new
graph/expansion actual-work count rather than relying only on its charge site.

### Status

`NEGATIVE RESULT` for V9 accounting fail-closed behavior. This is an
instrumentation fault-injection result, not a mathematical result.

### Assumptions

- The probe used exact commit `224189ce2acc054c4e319597940f34bb0edee619`.
- Only the authorized frozen p=19, B=4 control row was constructed.
- Replacing `charge_actual_work` in memory models an omitted or misplaced future
  instrumentation call; it is not presented as an input-driven attacker bypass.
- A hash-bound future runner mitigates runtime source substitution but does not
  independently validate an instrumented count.

### Evidence so far

For each target counter, the probe forwarded every other charge and suppressed
only that target while leaving all mathematical reconstruction unchanged:

```text
graph_candidate_evaluations valid=True actual=0 errors=[]
graph_eligible_conflict_checks valid=True actual=0 errors=[]
graph_eligible_pair_output_cells valid=True actual=0 errors=[]
expansion_cells valid=True actual=0 errors=[]
```

The source-owned reservation enforces only an upper bound for these four
counters. Unlike exact point-enumeration counts, successful graph and expansion
counts are not reconciled against independently reconstructed row dimensions.
The phase ledger also passes because the mathematical phase completes.

The independently derivable successful values are:

- candidate evaluations: `candidate_count`;
- eligible conflict checks: `C(eligible_candidate_count,2)`;
- eligible pair-output cells: `eligible_candidate_count^2`;
- expansion cells: `sum(C(B+d-1,d) for d in {1,2,4,8})`.

### Failure modes

- A future missing charge can produce a false-valid undercount while remaining
  below the reservation.
- This probe does not show that the exact V9 source currently skips a loop
  charge; it shows that the claimed successful count lacks a second validity
  invariant.
- Other dominance-only counters may still rely on exact source binding rather
  than independent equality checks.

### Next concrete action

On each successfully reconstructed row, compare the four observed counter
deltas with the independently derived exact dimensions and invalidate any
mismatch; add suppression controls for all four counters.

### Artifact paths

- `git:224189ce2acc054c4e319597940f34bb0edee619`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
