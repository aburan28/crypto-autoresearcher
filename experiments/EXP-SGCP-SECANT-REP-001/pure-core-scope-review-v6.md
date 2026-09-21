# Handoff: EXP-SGCP-SECANT-REP-001 pure-core scope pivot

## Claim or task

Can V6 authorize writing only the fixed-chart least-slope mathematical core
while postponing every evidence-bearing campaign layer?

## Status

`HYPOTHESIS`, `MODEL-BOUND` - **GO for scope design; NOT GO to write yet**

## Assumptions

- The core is deterministic, referentially transparent, and file-free.
- Inputs and outputs are immutable mathematical values.
- The chart, affine-addition, fiber, and least-slope formulas match protocol v6.
- Local counters are abstract algorithmic counters, not process accounting.
- Core output is not experiment evidence.
- A future verifier independently reimplements the mathematics.

## Evidence so far

A singleton file can isolate curve validation, factor-base validation, chart
transformation, nonidentity pair-sum fibers, and least
`(slope,i,j)` selection without seeds, files, digests, serialization, controls,
formal universes, optimizer state, or campaign authority.

## Failure modes

The pivot fails if the core accepts campaign values, performs I/O, imports
project code, uses randomness/time/global state, builds evidence artifacts, is
shared by the future verifier, or is imported/compiled/tested before a later
exact-source review.

## Next concrete action

Freeze and independently review a singleton pure-core API and source-writing
transition.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/contract.md`
- `experiments/EXP-SGCP-SECANT-REP-001/implementation-contract-v5.md`
