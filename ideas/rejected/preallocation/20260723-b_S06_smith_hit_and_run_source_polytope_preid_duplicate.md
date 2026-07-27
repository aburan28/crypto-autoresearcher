# Pre-ID duplicate draft — Smith hit-and-run source polytope

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S06`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_convex_body_membership_and_rounding`.
- Class/risk/lane: representation / representation-changing / secondary pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; uniform convex-body samples, mixing, or a valid relation are not an ECDLP break.

## Falsifiable hypothesis

Signed elliptic source fibres have an endpoint-derived convex lift whose integer relation points
occupy inverse-polynomial volume. Hit-and-run with a source-free membership oracle and certified
integer rounding would yield full-rank relations and 100 masked-target descents with complete time
and memory exponents at most `0.45`.

## Mechanism-new operation

Hit-and-run chooses a random direction from a point in a supplied bounded region and samples along
the feasible chord. It counts only if endpoints construct a well-rounded convex body, membership
and chord endpoints without source incidence, and a sampled real point has an exact signed integer
source lift. Sampling a polytope whose inequalities enumerate source compatibility is a control.

## Assumptions

1. A compact endpoint-only convex body is nonempty exactly when the signed source fibre is nonempty.
2. Valid integral relation points have inverse-polynomial volume after a public rounding transform.
3. Membership, chord intersection, mixing, warm start, precision, and rejection satisfy both caps.
4. Integer rounding preserves signs, multiplicities, and exceptional elliptic strata.
5. The frozen body/rounding works unchanged for fresh scalar-blind masks.

## Semantic fingerprint

`public_endpoint_convex_source_lift | hit_and_run_random_chord_sampling | relation_lattice_neighbourhood_hit | certified_integer_signed_source_rounding | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260723-a_R07_karmarkar_projective_source_optimizer_preid_duplicate.md` — a compact integral source polytope is already the missing formulation.
2. `ideas/rejected/preallocation/20260723-a_R08_groetschel_lovasz_schrijver_source_ellipsoid_preid_duplicate.md` — exact separation or membership for restricted sources is Query2P1 in another interface.
3. `ideas/rejected/preallocation/20260723-a_R09_beck_teboulle_mirror_source_descent_preid_duplicate.md` — continuous geometry and gradients do not supply exact integral occurrence replay.
4. `ideas/rejected/preallocation/20260722-a_N12_schoning_hamming_source_walk_preid_duplicate.md` — a walk on a relaxation lacks a source-free exact acceptance boundary.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable source existence remains the live owner.

## Closest primary literature

- Smith, [Efficient Monte Carlo Procedures for Generating Points Uniformly Distributed over Bounded Regions](https://doi.org/10.1287/opre.32.6.1296), samples within a supplied bounded measurable region using Markovian random-direction methods.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides endpoint equations but no small convex lift, membership oracle, or exact integer inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source supplies the ECDLP body, membership/chord oracle, volume bound, rounding theorem,
or full descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, convex lift, membership/chord oracle, rounding transform, warm start, restrictions, strata, masks, precision, seeds, and verifier.
2. Compile target-independent body/oracle state within `B^(9/4+o(1))`, forbidding source inequalities, tuple tables, target fitting, log labels, dense resultants, and Query2P1.
3. For known-log targets, charge every membership/chord call, mixing step, rejection, precision repair, and integer lift; verify signed point sums before admitting rows.
4. Retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse byte-identical eligible state for 100 fresh `Q+[t]P`, round sampled points to signed occurrences, subtract masks, and verify all scalars.
6. Charge construction, rounding/isotropization, body dimension, condition number, bit precision, mixing, volume density, lift, rank, logs, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal verified volume/hit
densities `N^delta,N^delta_t`; membership/chord/mixing/rounding work and workspace
`N^q,N^q_m`; rank credit `N^r`; output `N^o`; ambiguity/failure `N^u`; and
factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Hit-and-run assumes region membership and returns continuous points. A convex body whose feasible
integer points are exactly signed elliptic sources needs the missing source constraints, while
the convex hull fills with fractional points unrelated to any source. Giving integral points
enough volume or exact rounding either destroys selectivity or materializes the source lattice.

## Proof track

Prove an endpoint-only compact convex lift, exact restriction membership, inverse-polynomial
relation volume, subcap mixing, all-strata integer replay, full rank/logs, blind descent, and
sub-rho costs.

## Disproof track

Exhibit an empty-versus-nonempty source pair with the same relaxation, a source-bearing inequality,
fractional-volume domination, rounding ambiguity, ill-conditioning, or complete exponent at least
`0.50`.

## Positive and negative controls

- Positive: a supplied well-rounded integral toy polytope with labelled lattice points.
- Negative: same relaxation/different integer support, thin lattice slices, fractional vertices, empty fibres, repeated strata, shuffled labels, and blind targets.
- Baselines: ellipsoid/separation, Karmarkar, Schöning, P1553 R4, rho, and BSGS.
- Uniformity or fast mixing on a supplied body is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact public body/membership/rounding theorems, zero errors at four sizes/all strata, relation-volume and mixing bounds, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one relaxation collision, source inequality, fractional false lift, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s06_body_membership_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s06_fractional_relaxation_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s06_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP convex lift, not hit-and-run. Correct body sampling, fast toy
mixing, or a valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`,
and not a breakthrough.

## Exactly one next executable action

1. Construct the smallest pair of signed elliptic source instances with the same public convex relaxation but different integer feasibility, and freeze the membership-oracle provenance.
