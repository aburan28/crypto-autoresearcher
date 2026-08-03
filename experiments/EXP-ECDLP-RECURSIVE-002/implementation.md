# Implementation

Arithmetic protocol v2 preserves the audited affine arithmetic and factor-base
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

The v3 plan pins the complete local execution set:

| Boundary | SHA-256 |
|---|---|
| generator | `b3c9cd083af9e838c009bf76f83ac4fd6909c4c9160fcaada122d9f0a6de95bd` |
| independent verifier | `77b45770d29835166b6dc81a91b10fc44ae6c47f55d79535a6a3a85a4f60bc48` |
| prior arithmetic verifier | `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552` |
| recursive source | `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d` |
| coordinate-energy source | `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71` |
| package initializer | `fd91824b4834ee56ff9d6b37f0bf0a7e4212aba5e8cde2487eb661a0714702d4` |
| CLI | `02ee2cd8056a0d1603b784d10ca84568f678365a0bc5f68c229c6e96eba7a630` |
| strict records | `04feb8a0d9315e69fbefce915e03a68056ee6caba9aadd6c05f80820a11faaf3` |
| runner | `f259a243ee3a3286cc5ad2884834ec7afd9d4ce761b9323dbde076c14ec3ad94` |
| experiment schema | `f9587a024b6e10ba93febe0b27af02767fe7f88a9b180512950190691a1e4816` |
| manifest schema | `6eec48e58d8d64af8451370aa51649f94c34ef8af71956af8989bf26116fcfd1` |
| approval schema | `703661252453efe5cb7eb9295ba2675a30d79b76a4269627aa1311597e2e430a` |
| receipt schema | `2da55f4b48e03a9100d9330e49415f935010eec36bf341a07a11d20e064b67c0` |
| contract | `8c7b7baa52102d5885e86e091903691e3d269742700df5a85235dd66f581a3cf` |

Execution protocol v3 retains that mathematical payload and replaces the
mutable in-specification trust boundary. An external approval lock binds the
approved Git base, complete plan and specification digests, every local
harness and transitive arithmetic source, the exact Python runtime, and the
effective UID. Approved experiments cannot fall back to unplanned execution;
only explicit unapproved draft runs retain that development path.

Locked argv uses an absolute Python executable with `-I -S -B`. Under a
non-root effective UID, the child receives hard `RLIMIT_NPROC=0`, so the frozen
single-process programs cannot create descendants. Process-table sampling is
retained as defense in depth. A pre-repair fast-detach probe escaped sampling
in 12 of 12 trials and is preserved in
`pre-run-adversarial-probe-v3a.md`; the no-descendant regression now passes.

Before reserving a run directory, the runner verifies the external lock, exact
argv/metadata, complete protocol hashes and file identities, run count,
timeout, memory, cumulative CPU, clean tree, approved commit, and runtime
policy. After child quiescence it rechecks the commit, tree, lock,
specification, plan, and every protocol file. It emits a strict runner receipt
covering complete artifacts, measurements, and predecessor linkage. Verifier
launch requires the generator artifact set to be committed byte-for-byte, with
no path changes beyond that set.

Resource claims stop at the schema's named boundaries. Child wall/CPU/peak RSS
is enforced. Post-child parsing and core-artifact hashing is reported
separately. Process-monitor helper cost and receipt/manifest serialization and
publication are excluded, not silently attributed to the candidate algorithm.

A nine-curve development smoke with two plus two null rows, all 128 targets,
all four order seeds, and one rho trial completed valid in 19.83 seconds with
69,189,632 bytes maximum RSS. It had maximum order variation `1.04198` and
maximum sampled-to-exact error `0.02812`. This is runtime/correctness evidence
only and is not a registered hypothesis result.

Rank, relation independence, sparse linear algebra, factor-base logarithms,
individual descent, and exponent fitting remain absent by contract. Canonical
execution remains prohibited until a third independent pre-run audit and a
final external-lock/approval-commit check both return `GO`.
