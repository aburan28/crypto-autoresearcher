# Certified complementary-point reference and degree-to-cost analysis

Read cost-bridge.md for assumptions, derivations and costs. This producer
package is scoped to a symbolic result and fixed software correctness tests;
its status file is immutable after snapshot, so later review decisions live
separately. It establishes no general ECDLP or measured solver advantage.

The implementation enumerates one coordinate domain and reconstructs the
complementary point. The independent checker reconstructs the complete
projected set via a quadratic/linear S3 identity and checks witnesses through
division-free group equations. It imports no producer code.

Example input (prime p is an explicit premise, not proved by the tools):

```json
{"p":13,"a":1,"b":1,"target":[0,1],
 "D1":{"kind":"interval","offset":11,"size":4},
 "D2":[0,1,2,3,4]}
```

Coefficients a,b are arbitrary integers reduced modulo p. All domain/target
coordinates and optional `nonresidue` are canonical integers, excluding
booleans. An explicit domain list must contain distinct coordinates and its
order is preserved for D1 traversal. Intervals have canonical offset and
0<=size<=p, with wraparound. R must lie on the nonsingular curve and have
nonzero ordinate. Infinity is not an affine-domain coordinate.

From the repository root, with an input JSON file saved separately:

```sh
python3 research/prime_sat_costbridge_20261029/reference.py --input instance.json --output result.json --mode all
python3 research/prime_sat_costbridge_20261029/check_reference.py --input instance.json --result result.json
```

Output creation is exclusive. The producer returns sorted distinct ordered
projected pairs, aligned point witnesses, complete lift-status coverage and
a shared-nonsquare certificate. The checker reports `valid` conditional on
p prime, `primality_verified:false`, and `execution_counts_verified:false`.
Setup probe metadata is descriptive, not independently authenticated work.
First mode always reports incomplete, including no-witness exhaustion.
It certifies a returned witness without requiring all-model output.

The fixed software integrity suite is:

```sh
python3 -m unittest discover -s research/prime_sat_costbridge_20261029 -p test_reference.py -v
```

The suite has four prospectively fixed tiny curve/target fixtures, boundary
domains, a complete tiny test-only oracle, and corruption controls. The
actual invocation, source hashes and captured output are in
unit-test-results.json. Its unittest elapsed line is ordinary diagnostic
output, not a performance comparison or scientific measurement. No undeclared
sweep or rerun of a prior experiment is part of this package.

No external dependency is required for these Python modules. They are not
constant-time cryptographic library routines and supply no primality
certificate. The p=3 mod4 shortcut and general Tonelli-Shanks paths are
supported conditionally for general prime input; the tests do not certify
performance at large field sizes. The deterministic nonsquare scan is fully
charged in setup; explicit domains use Python's expected hash-table model.

The next experiment needs a separately frozen source/protocol and identical
output semantics, including witness reconstruction, certificate production,
checking and domain setup. Lower presentation degree alone is not a runtime
result, and point decomposition alone is not scalar recovery.
