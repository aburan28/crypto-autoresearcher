# Red-Team Review: TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1

## Verdict

Accept as a verified witness-generation boundary result. Do not promote it to an index-calculus improvement or ECDLP result.

## Checks

1. Full-mode source predicates were independently checked against the typed curve for every emitted witness.
2. Full-mode support matched typed `D4` support across all 12 rows.
3. The full query fraction is exactly one, making the exhaustive cost explicit.
4. The truncated control retains valid arithmetic but loses support and rank, so witness validity is not being confused with relation sufficiency.
5. The verifier reruns both modes and binds producer, prerequisite, input, and result digests.

## Remaining objections

- The curves and dimensions are toy-scale and inherited from the public fixture.
- The target budget is a bounded deterministic stream, not a success-probability estimate for deployed parameters.
- Some full rows do not reach quotient rank within the target budget; this is a relation-yield limitation, not a solver failure proof.
- Python object size and logical payload bytes are accounting proxies, not hardware memory-bandwidth measurements.
- The full control explicitly scans `B^5`-scale source tuples and therefore cannot support a sub-exhaustive complexity claim.

## Required follow-up

Implement a compressed join or adaptive locator that is independently charged and tested on larger source dimensions. Require support, rank, held-out descent, and matched-baseline success before considering promotion.
