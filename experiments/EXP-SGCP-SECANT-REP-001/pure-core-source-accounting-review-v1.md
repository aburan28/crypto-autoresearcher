# Handoff: Pure-core source V1 accounting review

## Claim or task

Audit exact success and failure-prefix accounting for source commit
`8fa78727eca4f98f0d1e4d7e7756de8609d829bf`.

## Status

`OPEN` - `REVISE`.

## Assumptions

- Reviewed tree: `a44c435e117436602ca2e744fb3ea9061c94d960`.
- Source SHA-256:
  `2a6eb4ca1bfcf9ab351da429d36dc308c9ba898d2fd73f2a5ab56f40b5a6edd4`.
- Reviewer principal: `019fac1a-3407-78f2-a253-bb9621b9a094`.
- Review was static only and authorized no runtime action.

## Evidence so far

- Independent derivation reproduces all successful V7 totals and all reachable
  failure-prefix charges.
- Fixed-size EC work is exactly 21 unordered pairs; trial division remains the
  only input-size-dependent portion.
- The source and decision provenance are closed and only the authorized path
  changed.

## Failure modes

- Counters are cumulative rather than phase-local, and pair enumeration plus EC
  addition are charged in one replacement instead of one replacement per
  operation.
- The unreachable empty-fiber invariant has an unauthorized empty error index.
- `dict[AffinePoint,...]` invokes object hashing despite the literal no-hashing
  exclusion. Hash-free linear grouping avoids the ambiguity at this fixed size.

## Next concrete action

Use local counter vectors with componentwise phase composition, split every
charged event into its own replacement, remove the unreachable failure, and
replace dictionary grouping with an equality-based list.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/src/sgcp_secant_math_core.py`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-v6.md`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-amendment-v7.md`
