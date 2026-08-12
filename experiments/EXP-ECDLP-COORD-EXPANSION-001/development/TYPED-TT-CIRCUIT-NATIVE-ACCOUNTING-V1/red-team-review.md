# Red-Team Review: TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1

## Verdict

Accept as a verified fixed-curve constant-factor evaluator improvement. Do not promote it to an asymptotic ECDLP result.

## Checks

1. Every queried source-native value is compared with the direct affine oracle.
2. The diagonal receipt passes adaptive, relation, descent, counter, source-hash, and measured-rho checks.
3. The lexicographic receipt is valid as a negative control and records exactness failure rather than treating it as success.
4. Source advice construction, retained bytes, logical reads, online operations, and direct-reference operations are all present.
5. The measured rho trials recover their known toy scalars and are reported separately from the candidate workload.

## Remaining objections

- Python dictionary size is an implementation-specific retained-memory measure, not a hardware memory lower bound.
- Logical bandwidth counts source point payload reads but omits cache-line, hash-table, and allocator effects.
- The source advice stores all prefix fibers, so the online reduction does not alter the leading source-space exponent.
- The relation matrix and full individual-log attack are still inherited from the fixture.

## Required follow-up

Use a compact/circuit-native representation for the retained source states, add a matched sparse linear-algebra baseline, and require a complete relation-plus-descent cost below rho before treating the result as more than an implementation improvement.
