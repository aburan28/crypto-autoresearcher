# Analysis: TYPED-TT-DOWNSTREAM-COST-ACCOUNTING-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The producer independently rebuilt the public D3/D4 source advice, relation collection, incremental quotient basis, full quotient solve, and held-out D4/R+D3 descent for all 12 fresh rows. Every compiler digest, relation transcript, independent-equation set, quotient solution and rank, and held-out descent transcript matched the frozen fixture. The independent verifier returned `valid: true`.

The receipt charges, aggregated over 12 rows:

- `23,506` relation-collection group operations;
- `71,950` relation-collection field multiplications;
- `1,061` matrix row additions;
- `8,508` matrix field multiplications and `208` matrix inversions;
- `150` verified held-out targets;
- `2,622` coefficient-recovery field multiplications and `2,322` field additions.

The materialized D4 builder ranges from `65` to `710` entries and `35,315` to `284,959` measured Python builder bytes across the rows. The diagonal streaming full batch is exact and direct-reference exact; the linked lexicographic full batch preserves direct arithmetic while reproducing the adaptive failure.

## Interpretation

This closes an evidence gap in the experiment: relation and target-descent costs are now independently regenerated and explicitly recorded. It does not make the streaming evaluator a complete attack. The source-native and typed-five operation counters are deliberately not merged into a promotion metric because they use different instrumentation models, and the relation architecture remains a toy fixture with inherited target generation and public factor-base records.

## Next action

Build a single field-operation model for both evaluators, generate larger source dimensions, and make the candidate relation collector produce fresh witness-bearing rows rather than binding to the fixture transcript. Only then compare complete offline advice, relation filtering, matrix solve, target descent, and rho under one promotion gate.
