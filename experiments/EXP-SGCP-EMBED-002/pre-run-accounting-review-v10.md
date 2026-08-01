# EXP-SGCP-EMBED-002 pre-run accounting review v10

## Handoff: V10 exact-commit accounting review

### Claim or task

Assess exact commit `3af44e847392c4c7e258ef60d0bf3e5dc01daa43`
for accounting readiness to design, but not execute, a launch plan.

### Status

`OBSERVATION`; no accounting finding was raised against the V10 repair.

### Assumptions

- Structural reservations are source ceilings, not runtime or memory forecasts.
- Producer and verifier must remain separate resource roles.
- External CPU, wall time, RSS, parser/allocator behavior, disk, I/O, cache
  occupancy/traffic, and memory bandwidth remain unmeasured.

### Evidence so far

- All nine V10 test-log SHA-256 values match exact committed Git blobs.
- Public generated and legacy row construction remains fail-before-work, and
  non-frozen public density construction remains gated.
- Completed graph/expansion work is checked by row-local equality rather than
  reservation dominance alone.
- Interrupted paths preserve charged partial work, the trusted reservation,
  failed-unit state, and `actual_work_complete=false`.
- The focused and repository-suite results are reported without converting
  structural counts or transient wall time into cryptanalytic costs.

### Failure modes

- Canonical B6/B8 output size, cache occupancy, and role feasibility are still
  unknown.
- A future plan must bind commit, command, environment, and immutable paths and
  add hard external resource limits.
- No current receipt supports a preprocessing crossover or end-to-end attack
  cost claim.

### Next concrete action

Permit launch-plan design only if theory and red-team reviews also issue scoped
GO and the coordinator separately approves design.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/development-test-log-v10.md`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `git:3af44e847392c4c7e258ef60d0bf3e5dc01daa43`

## Verdict

`GO` for launch-plan design only. Execution remains unauthorized.
