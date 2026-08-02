# Red-Team Review: TYPED-TT-ADAPTIVE-FRESH-SEED-V1

## Verdict

Accept as fresh-seed toy evidence. Do not promote it to an ECDLP advance.

## Objections

1. The diagonal-first prefix schedule may be selecting a favorable representation order.
2. Full validation is still charged separately and dominates any claimed construction saving.
3. The adaptive constructor imports the prior source-aware oracle and has no independent circuit-native evaluator.
4. Exact tensor reconstruction does not produce a relation matrix solution or an individual discrete logarithm.
5. The field sizes are diagnostic and cannot support cryptographic-size extrapolation.

## Resolution

The adversarial order receipt records reproducible failure for lexicographic and reverse-lexicographic schedules. The relation/descent binding receipt separately replays every independent relation target and every held-out target supported by both existing descent paths. These controls narrow the claim to schedule-sensitive source-prefix structure and exact toy replay.

## Required follow-up

Test randomized factor-base permutations, build an independent arithmetic evaluator, retain the skeleton as explicit fixed-curve advice, and compare full relation and descent cost against rho.
