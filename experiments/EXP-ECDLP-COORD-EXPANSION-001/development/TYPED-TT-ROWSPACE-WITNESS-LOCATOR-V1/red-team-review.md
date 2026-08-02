# Red-Team Review: TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1

## Verdict

Accept as a verified fixed-curve target-reuse observation. Do not promote it to a cryptanalytic improvement.

## Checks

1. The reuse basis is built from the first target only; later targets are not allowed to rebuild it.
2. Every predicted candidate witness is independently replayed on the typed curve.
3. Candidate support is compared against independently rebuilt typed-D4 support for every target.
4. Source queries, field reconstruction, target generation, relation basis, witness replay, and D4 work are kept in separate ledgers.
5. The verifier reruns both modes and requires strict reuse query savings plus the explicit `100%` suffix-reconstruction boundary.

## Remaining objections

- The target pool is a deterministic toy scalar stream and is not a success-probability estimate at cryptographic sizes.
- Only three generated curves and four coordinate families are tested.
- Support equality is a zero-support check; it does not prove that the row-space representation has a compact algebraic zero locator.
- Suffix reconstruction remains exhaustive, and its field-operation cost dominates the candidate.
- The materialized D4 baseline is already much cheaper in group operations; no matched Pollard-rho comparison is needed to reject promotion at this stage.
- Relation rank is bounded by the small target stream and is not a complete individual-log solve.

## Required follow-up

Construct a non-enumerative suffix zero locator or transposed target operator. Require held-out target support, relation rank, target descent, memory traffic, and matched materialized-D4/rho accounting on larger dimensions before treating the target-independent row space as more than a representation lead.
