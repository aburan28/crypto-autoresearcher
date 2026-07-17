# Implementation

Protocol v2 preserves the audited affine arithmetic and factor-base
constructors while repairing the v1 pre-run blockers. It deterministically
rejects trace `0`, anomalous trace `1`, composite order, and special j. The
frozen seeds select nine prime-order curves over nine distinct field primes,
with a monotone subgroup schedule per seed.

Each curve receives 31 random-scalar and 31 random-x bases. Every base seed is
globally unique across the schedule. Both null constructors sample the same
sign-complete point-set distribution; random-x additionally follows the
coordinate construction path.

For each factor base, the generator computes exact four- and eight-term
supports. For every target it counts the number `k` of successful four-support
partials among `S=|4A|` and uses the exact uniform-permutation first-hit
expectation `(S+1)/(k+1)`, with cost `S` when `k=0`. Four deterministic shuffles
retain every target's actual lookup vector and must agree with the exact
aggregate expectation and with each other within 25 percent. The exact
expectation, not a favorable shuffle, drives the frontier statistic.

Construction accounting augments the inherited curve-operation counters with
a disclosed binary-square-and-multiply proxy for Legendre/root exponentiation,
three coordinate-RHS field multiplications per square-root test, square-map
multiplications, and rational-map multiplications/inversions. The gate requires
all three offline ratios to stay within `4x` random-x. Lookup traffic remains a
labeled 64-byte assumption; lookup count is the measured quantity.

Factor-base and advice maps are not duplicated into every result row. The
result retains frozen source hashes, deterministic seeds, factor-base digests,
support sizes, and witnesses from which the functional artifact is exactly
reconstructible. Python deep-size fields remain implementation-specific.

The frozen v2 generator is `src/null_calibrated_coverage.py`, SHA-256
`b3c9cd083af9e838c009bf76f83ac4fd6909c4c9160fcaada122d9f0a6de95bd`.
The independently reconstructed v2 verifier is
`src/verify_null_calibrated_coverage.py`, SHA-256
`77b45770d29835166b6dc81a91b10fc44ae6c47f55d79535a6a3a85a4f60bc48`.
It imports no v2 generator code and passed 51 mutation cases plus an external
reduced generator-to-verifier round trip.

The execution plan additionally pins:

- runner: `4da90cea377c1554b1fabbd4c314e37176d1bd3ad9d41a98b1f64276015f6b77`
- experiment schema: `f9587a024b6e10ba93febe0b27af02767fe7f88a9b180512950190691a1e4816`
- contract: `b629f5821dc13a60165511e07b6899fbe37f84256d75120422ceb6c73546629d`

Before reserving a run directory, the runner verifies those hashes and the two
source hashes, exact argv/metadata, run count, timeout, memory, cumulative CPU,
clean-tree policy, predecessor status/artifact, and verifier-reported input
SHA-256.

A nine-curve development smoke with two plus two null rows, all 128 targets,
all four order seeds, and one rho trial completed valid in 19.83 seconds with
69,189,632 bytes maximum RSS. It had maximum order variation `1.04198` and
maximum sampled-to-exact error `0.02812`. This is runtime/correctness evidence
only and is not a registered hypothesis result.

Rank, relation independence, sparse linear algebra, factor-base logarithms,
individual descent, and exponent fitting remain absent by contract. Canonical
execution remains prohibited until the v2 verifier, execution-plan enforcement,
semantic tests, and second independent pre-run audit all pass.
