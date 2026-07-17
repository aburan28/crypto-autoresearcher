# Implementation

The generator reuses the audited affine arithmetic and factor-base constructors from the prior experiment while changing the experiment protocol. It deterministically rejects trace `0`, anomalous trace `1`, composite order, and `j in {0,1728}`. Every accepted curve has prime order, cofactor one, disclosed `p mod 4 = 3`, and a monotone subgroup schedule per seed.

Each curve receives 31 distinct random-scalar and 31 distinct random-x factor-base seeds. Seed collisions across nulls, candidates, and the scalar-progression control are fatal. The generator stores compact summaries and SHA-256 factor-base digests instead of duplicating every point/source record in the final document; the independent verifier must reconstruct each digest exactly.

For every base, separate support chains measure four-term compiler work and exact eight-term diagnostic support. The functional artifact includes the factor-base point list and witness-bearing four-term map. Four canonical point-sorted permutations, shuffled by preregistered order seeds, measure first-witness work over all shared targets. The primary frontier statistic uses the median order cost and exact success probability.

Empirical percentiles use midranks with a finite-null correction. Higher exact support/coverage efficiency and lower frontier cost are favorable. A candidate must beat both null families; one favorable random draw cannot pass it.

The first development smoke used one seed, all three sizes, four null replicates, 32 targets, two order seeds, and one rho trial. It completed valid in 4.14 seconds with 58,523,648 bytes maximum RSS. This is runtime evidence only and is not a registered experiment result.

Python deep-size and estimated lookup-traffic fields remain implementation-specific. Rank, sparse linear algebra, factor-base logarithms, descent, and exponent fitting are absent by contract.

The frozen generator is `src/null_calibrated_coverage.py`, SHA-256
`f2c0a9456758931c3c46651e2482330e05b76b6efb7253995c3b712572a3dc4f`.
The independent verifier is `src/verify_null_calibrated_coverage.py`, SHA-256
`0900818b0c4609d15d22b0ccb10645b77f804b520e0676eb0e37c016a4ba3197`.
The verifier does not import the new generator. It independently reconstructs
the curve search, targets, factor bases, exact supports, shuffled scans,
witnesses, empirical percentiles, family gate, operation counters, memory
fields, and rho controls. It binds the generator and three prior arithmetic
sources by SHA-256.

Three repository tests cover deterministic generation, a 14-check adversarial
verifier self-test, and an external generator-to-verifier round trip. The full
frozen schedule has not run. A canonical run remains prohibited until a fresh
independent pre-run audit returns `GO` and the specification is explicitly
approved.
