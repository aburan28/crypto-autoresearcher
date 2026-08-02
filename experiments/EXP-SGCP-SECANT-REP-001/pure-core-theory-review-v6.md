# Handoff: Pure-core V6 theory review

## Claim or task

Review exact commit `9c90744904fcbd340d387b9ad3da55f1c59c0851`
for uniquely authorable mathematical behavior.

## Status

`OPEN` - **REVISE**

## Evidence so far

Formula fidelity, validation order, chart transformation, pair branching,
intercept identity, fibers, least-slope selection, diagnostics, immutable
types, singleton scope, and locked authority passed.

## Failure modes

1. `ChartFixture.u` does not say whether it stores raw `u` or `u mod p`.
2. Literal constants `4,27,3,2 mod p` do not say whether they charge
   `field_reductions`.

## Next concrete action

Freeze the stored chart scalar and literal-reduction accounting, then obtain a
fresh exact-commit review.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-v6.md`
