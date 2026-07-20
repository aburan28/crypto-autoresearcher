# ECDLP-IDEA-275 — Arc-descent valuation-branch gluing

## Status and claim labels

- Class: `descent_topology`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_source_separating_arc_cover_materializes_branches_and_lacks_section`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; successful descent, compatible valuation branches, a valid relation, recovered factor, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The source fiber of an ECDLP relation admits a compact arc-cover by rank-at-most-one valuation rings on which branches split and become locally recoverable.  Gluing compatible local branches by arc descent would return exact finite-field factor points and complete target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **pull the source functor to an arc-cover of valuation rings, split or identify local branches there, and glue a unique global source point from compatible valuation data**.  This is a new descent topology rather than a parameter change or solver substitution.  Arc descent reconstructs a sheaf or object from an already supplied cover and compatibility data; it does not select a point in a many-point fiber.  A cover fine enough to separate factor tuples and the local sections on it materialize the branches, while a compressed unlabelled cover glues the entire source scheme and leaves target branch choice unchanged.  It therefore merges with valuation/tropical lifting, local-global transfer, and source-section negatives after cover and overlap costs are charged.

## Assumptions

1. Public source equations and endpoint determine a finite compact arc-cover without enumerating factor tuples.
2. Every relevant source branch becomes locally unique and computable over rank-at-most-one valuation rings.
3. Compatibility on overlaps selects one exact rational branch and returns finite-field factors with sub-rho ambiguity.
4. Cover construction, valuation precision, all overlaps, local sections, gluing, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | arc_cover_of_source_fiber | valuation_local_branch_split | overlap_gluing | exact_rational_source_section`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the local-to-global return-map hypothesis.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the lift and specialization compatibility boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H682`, the valuation/tropical branch hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and source-orientation barrier.
5. `inputs/ledger_inventory.json` — imported `ECFG-H633`, the local branch reconstruction control.

## Closest primary literature

- Bhatt and Mathew, [The arc-topology](https://arxiv.org/abs/1807.04725), defines arc-covers through rank-at-most-one valuation rings and proves descent results for suitable invariants.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations and factor-base setting.

No checked source turns arc descent into a canonical point-selection or sub-rho factorization operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the instance, source equations, arc-cover construction, valuation precision, overlap complex, factor base, masks, and verifier.
2. Construct the cover and local source schemes for known-log relation endpoints without enumerating global branches.
3. Recover every local section, solve all overlap compatibilities, glue exact rational branches, and map them to signed factor points.
4. Verify relations, collect independent rows, solve and verify every factor log.
5. Apply the identical frozen cover and gluing rule to fresh masked targets `Q+[t]P`.
6. Retain all compatible descent data, return a complete factor decomposition or scalar residue, remove the mask, and verify the endpoint.
7. Accept only exact `[x]P=Q`, charging every valuation ring, precision digit, cover member, overlap, branch, factor log, descent step, and live byte.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one cover/local-solve/glue/return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, local/global branch output be `N^o`, gluing ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every valuation ring, cover member, overlap cell, precision digit, local section, compatibility tuple, failed glue, source branch, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Descent is reconstruction from local data, not creation of a canonical section.  If the global source fiber has many factor tuples, pulling it to valuation rings preserves that multiplicity unless the cover is decorated with branch labels.  Supplying all local branches and overlap compatibilities materializes the source deck; choosing one branch requires target-correlated advice.  The arc topology can certify that objects glue while leaving exactly the hard point-selection problem intact.

## Proof track

Construct a target-uniform compact arc-cover on which branches become canonically unique, prove exact effective gluing and factor return, and certify both complete exponents at most `0.45`.

## Disproof track

Show branch multiplicity survives all unlabelled covers, prove source-separating cover/overlap state at least `N^0.50`, demonstrate target branch selection imports advice, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied finite cover of a scheme with one known global section and explicitly compatible local sections.
- Negative controls: two-point finite etale fibers, permuted local branch labels, incomplete overlaps, valuation lifts without a section, tropical cells, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a cover and local solver of exponent at most `0.45`, canonical all-strata branch gluing, exact factor return, blind descent, and complete `lambda,mu<=0.45`.  Persistent branch multiplicity, source-labelled cover data, cover/output/state at least `N^0.50`, missing section, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-275/arc_descent_source_gluing_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-275/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-275/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-275/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative descent-topology proposal.  Every valuation test would be toy and projections heuristic and model-bound.  Valid local sections or successful gluing do not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-275/arc_descent_source_gluing_theorem.md` proving canonical compact branch gluing or the persistent-multiplicity/source-state obstruction.
