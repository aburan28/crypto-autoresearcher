# Red-Team Review: TYPED-TT-PREFIX-STREAMING-TRADEOFF-V1

## Verdict

Accept as a verified fixed-curve advice-memory tradeoff. Do not promote it to an asymptotic ECDLP result.

## Checks

1. The producer cross-checks every queried streaming value against the direct affine oracle.
2. The diagonal verifier reruns the producer and validates source hashes, relation bindings, supported descent, and sealed direct-operation counters.
3. The lexicographic receipt is valid as an expected negative control and preserves direct-reference exactness.
4. Prefix transitions are charged as online point additions; the suffix table remains separately charged as fixed-curve preprocessing.
5. Source input points are reported separately, so the retained-advice reduction is not presented as total algorithm memory.

## Remaining objections

- Python object sizes are implementation-specific and are not a hardware memory lower bound.
- The current-prefix cache assumes the existing grouped traversal; arbitrary target/query interleavings would cause more recomputation.
- Logical bandwidth omits cache-line, allocator, and hash-table effects.
- The relation matrix, sparse linear algebra, and individual-log descent remain inherited from the toy fixture.
- No size sweep yet supports an exponent claim.

## Required follow-up

Run larger `A,B` sweeps with explicit retained-memory and online-addition curves, then compare complete relation filtering, sparse linear algebra, and individual descent against matched Pollard-rho operation counts.
