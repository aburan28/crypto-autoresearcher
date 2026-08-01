# Handoff: EXP-SGCP-SECANT-REP-001 V4 source review

## Claim or task

Determine whether exact commit
`c05dabbf4cddae8e196448de174e6daab7eba0d7` unambiguously authorizes
source implementation only.

## Status

`OPEN` - **REVISE**

Source implementation is not authorized. `maximum_runs=0`, registered seeds,
canonical execution, and D01-D13 remain locked.

## Assumptions

- Review is limited to source and focused static-test design.
- Protocol v6 and the combined V3+V4 source contract are normative.
- Closed means independent implementations cannot choose unstated encodings.

## Evidence so far

- Exact commit and clean worktree were verified.
- All fourteen V4-bound file hashes and the four protocol-v6 hashes matched.
- All JSON parsed; the six control IDs and M01-M52 were complete and unique.
- V4 repaired intended 4,608-cell coverage, verification-field placement,
  mutation bindings, control order, exhaustion placement, and run/child budget
  separation.

## Failure modes

1. The source-writing exception conflicts with `specification.json`, which
   prohibits implementation while `maximum_runs=0` or `approved_by=null`.
2. Canonical records omit types, stream IDs, compiler mapping, decision schema,
   reference semantics, and complete ordering rules.
3. Conflict density, histograms, maxima, and digest input encodings are open.
4. The fourteen verification fields need literal-true and receipt bindings.
5. Controls need expected-digest equality and fail-closed terminal semantics.
6. Exhausted factor streams and missing-cell references remain ambiguous.
7. Verifier independence can be self-reported and bypassed by renamed helpers.
8. Qualified counter serialization and per-field failure charges remain open.

## Next concrete action

Publish a hash-bound V5 typed relational closure and obtain fresh exact-commit
review.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/implementation-contract-v4.md`
- `experiments/EXP-SGCP-SECANT-REP-001/source-schema-v4.json`
- `experiments/EXP-SGCP-SECANT-REP-001/implementation-design-consistency-v4.json`
