# Implementation

The generator imports the already-verified affine short-Weierstrass arithmetic from `EXP-ECDLP-ENERGY-001`, then selects deterministic nonsingular ordinary curves whose entire group has prime order. It rejects nonmonotone subgroup schedules across bit sizes.

For each `m`, the factor-base cardinality is the smallest even `B` satisfying the frozen unordered-occupancy sizing rule. This rule chooses a comparable test scale; it is not used as the finite support model. Exact support maps retain one functional index witness per reachable point.

The split compiler builds through `ceil(m/2)`. It stores the two required support maps, scans the smaller map online, computes target complements in the other map, and stops at the first witness. An independent full-depth support chain supplies exact coverage and is charged only to diagnostic expansion. Construction, compiler, diagnostic, online, and rho operations are reported separately.

`random_x` traverses a seeded uniform permutation of field x-coordinates and uses the same square-root and subgroup-membership path as coordinate predicates. `random` remains the structural random-scalar control. The scalar progression remains a compression-positive and expansion-negative control and cannot be promoted.

The verifier is a separate implementation. It pins the generator source SHA-256, rejects duplicate JSON keys and non-finite numbers, enforces exact integer types, reconstructs every curve, target, factor-base source, support map, first witness, operation count, ratio, rho trial, and promotion decision, and compares the full submitted document recursively. Canonical verification enforces the frozen configuration; a separately labelled CLI option permits reduced integration-test configurations without changing any replay check.

Python deep-size and estimated traffic fields are implementation diagnostics. They are not portable memory lower bounds.
