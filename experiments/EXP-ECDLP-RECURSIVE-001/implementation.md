# Implementation

The generator imports the already-verified affine short-Weierstrass arithmetic from `EXP-ECDLP-ENERGY-001`, then selects deterministic nonsingular ordinary curves whose entire group has prime order. Field primes are constrained to `p mod 4 = 3` for deterministic square roots, and this restricted modulus policy is emitted with every curve. The generator rejects nonmonotone subgroup schedules across bit sizes.

For each `m`, the factor-base cardinality is the smallest even `B` satisfying the frozen unordered-occupancy sizing rule. This rule chooses a comparable test scale; it is not used as the finite support model. Exact support maps retain one functional index witness per reachable point.

The split compiler builds through `ceil(m/2)`. It stores the two required support maps, scans the smaller map online, computes target complements in the other map, and stops at the first witness. An independent full-depth support chain supplies exact coverage and is charged only to diagnostic expansion. Construction, compiler, diagnostic, online, and rho operations are reported separately.

Promotion uses functional witness-map deep bytes, average online group operations, exact success probability, and subgroup order in a matched-random normalized `S*T^2/(epsilon*q)` diagnostic. Advice-entry and online-operation ratios remain visible but cannot bypass that joint gate.

`random_x` traverses a seeded uniform permutation of field x-coordinates and uses the same square-root and subgroup-membership path as coordinate predicates. `random` remains the structural random-scalar control. The scalar progression remains a compression-positive and expansion-negative control and cannot be promoted.

The generator emits SHA-256 hashes for itself and the imported coordinate-arithmetic source. The verifier is a separate implementation that recomputes and enforces both hashes, rejects duplicate JSON keys and non-finite numbers, enforces exact integer types, reconstructs every curve, target, factor-base source, support map, first witness, operation count, ratio, rho trial, and promotion decision, and compares the full submitted document recursively. Canonical verification enforces the frozen configuration; a separately labelled CLI option permits reduced integration-test configurations without changing any replay check.

Python deep-size and estimated traffic fields are implementation diagnostics. They are not portable memory lower bounds.
