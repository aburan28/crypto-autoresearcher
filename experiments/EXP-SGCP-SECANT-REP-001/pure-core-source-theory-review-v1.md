# Handoff: Pure-core source V1 theory review

## Claim or task

Review the singleton source at commit
`8fa78727eca4f98f0d1e4d7e7756de8609d829bf`, tree
`a44c435e117436602ca2e744fb3ea9061c94d960`, and source SHA-256
`2a6eb4ca1bfcf9ab351da429d36dc308c9ba898d2fd73f2a5ab56f40b5a6edd4`.

## Status

`OPEN` - `REVISE`.

## Assumptions

- Reviewer principal: `019fac1a-3494-77d1-ba61-8cd98eb1915e`.
- Review was static text and Git-byte inspection only.
- No import, compilation, parsing through Python, test, execution, or source
  edit occurred.

## Evidence so far

- Public exports, immutable types, validation precedence, formulas, chart
  labels, fiber ordering, representative selection, purity boundary, successful
  counters, and result invariants otherwise match V6/V7.
- The source commit changed only the path authorized by the V9 Coordinator
  decision.

## Failure modes

- One unreachable empty-fiber failure returns `indices=()` although the contract
  permits only `(i,j)` for internal witness failures.
- The implementation threads one cumulative `CoreOps` through all phases rather
  than returning phase-local counters and combining them componentwise.

## Next concrete action

Remove the unreachable failure and refactor operation accounting into
phase-local immutable vectors before a fresh exact-source review.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/src/sgcp_secant_math_core.py`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-v6.md`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-amendment-v7.md`
