## Handoff: SGCP source-repair v4 re-review

### Claim or task

Determine whether v4 repairs the source-freeze findings preserved in
`source-red-team-v3.md`.

### Status

OBSERVATION, GO. Source-freeze readiness only. This is not approval, run
authorization, launch evidence, or ECDLP evidence.

### Assumptions

- Review was read-only; nothing was edited, approved, committed, or launched.
- The focused `22/22` pass was inspected as an existing receipt, not rerun by
  the reviewer.
- Review was limited to the prior v3 findings.

### Evidence so far

1. Frozen relative argv: PASS. The plan retains the relative builder token,
   runner mode preserves `sys.argv[0]`, and the verifier exact-compares emitted
   and receipt argv.
2. Specification-derived composition control: PASS. The test loads both
   commands from the plan, exact-compares emitted argv, and rejects an absolute
   builder-token receipt mutation.
3. Literal target-pair maps: PASS. The builder emits raw and retained maps, the
   coordinate verifier reconstructs them independently, and the scalar-index
   pairs are translated to canonical point order and exact-compared. Pair
   reversal is a rejecting regression.
4. Scoped scalar/covert wording: PASS. The public model distinguishes forbidden
   named fields from covert encoding, and the report states that covert encoding
   is not excluded.
5. In-range diagnostic channel: PASS. A recomputed in-range
   `wall_clock_ns=23` remains valid while `covert_scalar_encoding_excluded` is
   false; the oversized mutation remains rejecting.
6. Freeze integrity/state: PASS. All 16 protocol hashes match; builder hash is
   `0580aad43fc1cc0a9bce11b34cce5626edade57ff902b6ad53ab31db0216d1b1`,
   verifier hash is
   `931d7bd240dc6565d22ae85385d253a7b9ab20b123198ab133df43ef68bb4337`,
   status is `review_required`, `approved_by` is null, `runs/` is empty, and
   `preflight/` is absent.

### Failure modes

No blocking source-freeze failure remains within the reviewed scope.

Residual boundaries:

- Composition evidence is a synthetic runner-shaped development fixture, not
  canonical provenance.
- In-range diagnostic channels can carry information; the report now states
  this honestly.
- Literal pair maps are charged private audit material, not free attack advice.
- All evidence remains five-bit implementation evidence without scaling, rank,
  descent, or faster-than-rho significance.

### Next concrete action

Freeze the reviewed source in Git. Keep approval and any runner launch as
separate explicit actions.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v3.md`
- `experiments/EXP-SGCP-EMBED-001/source-review-response-v4.md`
- `experiments/EXP-SGCP-EMBED-001/development-test-log-v4.md`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
