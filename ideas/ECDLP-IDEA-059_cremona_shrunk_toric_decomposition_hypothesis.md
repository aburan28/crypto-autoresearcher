# ECDLP-IDEA-059 — Cremona-shrunk toric decomposition

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` birational preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; smaller mixed volume or a valid toric solution is not a break.

## Falsifiable hypothesis

A public, target-independent Cremona transformation of the symmetric elliptic
point-decomposition variety maps the generic factor-base-to-target system to a toric
chart whose saturated Newton polytopes have mixed volume `N^(v+o(1))` with `v<1/2`,
while a rational inverse recovers all source points. A source-resolving sparse solver on
this transformed system yields complete relation and descent costs below rho/BSGS.

## Mechanism-new operation

The operation is **birational cancellation of the dominant Newton faces before
elimination**. An explicit Cremona map uses the elliptic addition-law syzygies to shrink
the saturated mixed volume; sparse resultants are only the downstream verifier/solver.
Changing coordinates without a proved volume drop, tuning a factor base, using a dense
resultant, or reporting relation validity does not qualify.

## Assumptions

1. `E(F_p)` contains a prime-order subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. A deterministic factor base `F` has `B=N^beta` and target-independent defining equations.
3. Saturation removes all exceptional and denominator components without losing valid decompositions.
4. The Cremona map and inverse have sub-rho degree, coefficient height, evaluation, and storage.
5. The sparse solver outputs every source point and charges mixed cells, multiplicities, and failures.
6. All extrapolations are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`symmetric_point_decomposition | elliptic_syzygy_Cremona_map | dominant_Newton_face_cancellation | saturated_mixed_volume_drop | rational_source_inverse`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — demands a complexity-changing representation, not a rewrite.
2. `ledger/EV-REP-001.yaml` — supplies the matched coordinate controls.
3. `ledger/EV-REP-002.yaml` — records representation scaling evidence.
4. `ledger/FINDING-PF-IC-001.md` — fixes the measured prime-field baseline.
5. `ledger/SYNTHESIS-20260716.md` — requires full relation-to-target accounting.

## Closest primary literature

- Canny and Emiris, [A subdivision-based algorithm for the sparse resultant](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1993/CSD-93-776.pdf), gives the primary sparse-resultant and mixed-subdivision framework.
- Bernstein, [The number of roots of a system of equations](https://doi.org/10.1007/BF01085851), gives the mixed-volume root bound underlying the claimed reduction.
- Borger, Kahle, Kretschmer, Sager, and Schulze, [Liftings of polynomial systems decreasing the mixed volume](https://arxiv.org/abs/2105.10714), gives an equivalent-system reduction that can serve as a valid positive control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), gives the nearby decomposition equations.
- Petit, Kosters, and Messeng, [Algebraic approaches for the ECDLP over prime fields](https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf), provides the prime-field algebraic baseline.

The literature does not prove a target-independent elliptic Cremona map that lowers
saturated mixed volume with a cheap source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,m,beta,F`, exact symmetric decomposition equations, and saturation ideals.
2. Construct one target-independent Cremona map from explicit elliptic syzygies.
3. Compute original and transformed Newton polytopes, saturated mixed cells, exceptional components, and inverse-map costs.
4. Solve transformed systems for known `R=[a]P` and invert every toric solution to points in `F`.
5. Independently verify membership and `sum_i P_i=R`; retain all misses, multiplicities, and exceptional fibers.
6. Collect independent rows and solve factor-base logarithms.
7. Apply the identical map to `Q+[t]P`, recover a verified decomposition, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let map construction exponent be `a`, transformed
mixed-volume exponent `v`, solver overhead over output size `u`, inverse/verification
exponent `i`, reciprocal relation and descent densities `delta,delta_t`, factor-base
exponent `beta`, and storage exponent `s`. A query costs
`q=max(v+u,i)`, so
`lambda=max(a,beta+delta+q,2beta,delta_t+q)` and
`mu=max(s,beta,v)`. All saturation, coefficient growth, failed cells, and inverse branches
are included. Mixed volume alone is not the time bound.

## Likely fatal obstruction

Birational degree conservation may move the original degree into exceptional divisors,
coefficient heights, or many inverse branches instead of removing it. Saturation can
restore the full mixed volume, and a source-resolving sparse solve may cost at least its
`N^(1/2)` output/branch count.

## Proof track

Give the map and inverse, prove generic completeness after saturation, bound transformed
mixed volume, coefficient height, construction, solver, inverse, density, linear algebra,
descent, and memory, and derive `lambda,mu<1/2`.

## Disproof track

Show the saturated mixed volume is invariant or moves to exceptional components, prove
inverse degree/output `N^(1/2-o(1))`, find a lost valid component, or establish
`lambda>=1/2` for every complete-cost parameter arm.

## Positive and negative controls

- Positive control: a documented equivalent-system lifting with a certified strict mixed-volume decrease and invertible solution correspondence.
- Positive correctness control: exhaustive factor-base decompositions on tiny curves.
- Negative control: random sparse systems with matched support and degree.
- Representation control: original Semaev system and random birational maps of matched degree.
- Search control: use a frozen degree-bounded Cremona grammar, canonical coefficient order, and lexicographic tie-break; report every enumerated map.
- Leakage control: forbid target-selected maps, post-hoc discarded components, explicit tuple tables, and uncharged coefficient growth.

## Quantitative promotion and falsification gates

Across at least 20 curves per size from 11 through 23 bits and `m in {3,4}`, promotion
requires zero lost or false exhaustive solutions through 16 bits, at least 1,000 verified
relations and 100 descents at each of the two largest sizes, upper 95%
`v<=0.20`, `q<=0.20`, `a<=0.45`, `lambda<=0.45`, and `mu<=0.45`, with every
exceptional branch charged and stable fit sensitivity. Falsify on a generic saturation
counterexample, any independently reproduced lost/false witness, lower 95%
`v>=0.50` or `q>=0.50`, or full-cost lower 95% `lambda>=0.50` in every arm.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-059_cremona_toric_preflight.yaml`
- Map derivation: `ideas/artifacts/ECDLP-IDEA-059/cremona_map.sage`
- Polytope data: `ideas/artifacts/ECDLP-IDEA-059/polytopes/`
- Runs: `ideas/artifacts/ECDLP-IDEA-059/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-059/analysis.md`
- Retain maps, inverses, ideals, supports, mixed cells, witnesses, misses, seeds, commands, environment, commit, resource traces, stdout, and stderr.

## Interpretation boundary

All claims are toy, heuristic, model-bound, and novelty-unverified. A smaller unsaturated
polytope, successful sparse solve, or valid relation does not establish a generic
better-than-rho result.

## Exactly one next executable action

1. After coordinator approval, execute the frozen saturation-and-mixed-volume preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-059_cremona_toric_preflight.yaml`.
