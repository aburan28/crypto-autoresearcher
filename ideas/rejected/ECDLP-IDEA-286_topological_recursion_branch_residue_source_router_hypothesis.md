# ECDLP-IDEA-286 — Topological-recursion branch-residue source router

## Status and claim labels

- Class: `mechanism`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_recursion_residues_aggregate_branches_without_endpoint_section`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid recursion invariant, residue identity, relation, recovered branch label, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform spectral curve compiled from the ECDLP source equations has ramification branches corresponding to exact factor tuples, and Eynard–Orantin recursion produces endpoint-conditioned residues that isolate one branch.  Reading that residue would return relations and fresh-target decompositions with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the source fiber into a spectral curve, recursively propagate local ramification residues, and use an endpoint-conditioned residue signature to route to an exact source branch**.  This is a residue-recursion mechanism, not dense elimination or a solver swap.  Topological recursion constructs curve invariants from already supplied spectral data, ramification points, local conjugates, and a bidifferential.  Its residues sum local contributions and are not an inverse map from an external endpoint to a chosen preimage.  If ramification points are made source-tuple labels, the spectral curve or residue table materializes the source; if compressed, distinct branches share signatures.  The operation therefore merges with branch-table, symmetric-invariant, and missing-section negatives.

## Assumptions

1. Public source equations and endpoint canonically compile to compact spectral-curve data without enumerating solutions or factoring a dense eliminant.
2. Relevant source tuples correspond injectively to computable ramification branches or finite residue signatures.
3. An endpoint-conditioned recursion insertion canonically selects and exactly returns the signed factor points on every stratum.
4. Spectral compilation, normalization, ramification, recursion depth, residue arithmetic, output, ambiguity, factor logs, descent, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | source_spectral_curve_compilation | topological_recursion_residue_propagation | endpoint_branch_routing | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the materialized source-product control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the aggregate invariant without source output.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the shared symmetric row signature control.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact curve-pencil branch control.

## Closest primary literature

- Eynard and Orantin, [Invariants of algebraic curves and topological expansion](https://arxiv.org/abs/math-ph/0702045), defines recursively constructed invariants of a supplied algebraic curve from its local spectral data; it does not give an inverse selecting a hidden source branch.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations whose bounded solutions the residue router would have to return exactly.

No checked primary source supplies an endpoint-conditioned topological-recursion section for a summation-polynomial fiber; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source equations, spectral compiler, normalization, ramification convention, recursion kernel, masks, and verifier.
2. For random known-log endpoints, construct compact spectral data and endpoint insertion without enumerating source branches.
3. Evaluate the recursion, route every accepted residue signature to exact signed factor points, and verify each resulting relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen spectral compiler and recursion to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode all surviving residue branches to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging spectral construction, ramification data, recursion terms, residue output, branch ambiguity, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one spectral/recursion/router attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned residue/source output be `N^o`, unresolved branch ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every spectral coefficient, normalization branch, ramification point, local conjugate, recursion graph, kernel evaluation, residue, failed signature, source branch, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Topological recursion propagates symmetric invariants of a spectral curve by summing residues at known ramification points.  It neither discovers a hidden preimage nor canonically selects one source tuple from a many-to-one endpoint fiber.  Encoding each tuple as its own branch makes ramification data or recursion output source-sized; retaining only compact invariants creates collisions.  An endpoint insertion that already identifies the desired local branch imports the missing section.

## Proof track

Construct spectral data without source enumeration, prove compact residue signatures are injective on all source strata, prove endpoint-conditioned exact factor return, and certify complete `lambda,mu<=0.45` including all recursion graphs and branches.

## Disproof track

Exhibit two source branches with identical recursion signatures, prove ramification/recursion/output size at least `N^0.50`, show branch conditioning imports the witness or dense eliminant, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy spectral curve with simple ramification, labelled local conjugates, and independently checked low-order recursion residues.
- Negative controls: permuted branch labels, isospectral curves with shared low-order invariants, symmetric branch sums, explicit branch tables, dense resultants, post-hoc residue selectors, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires source-free spectral compilation, injective compact branch routing, exact all-strata factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  A residue collision, source-labelled ramification input, spectral/recursion/output exponent at least `0.50`, missing factor return, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-286/topological_recursion_router_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-286/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-286/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-286/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative mechanism proposal.  Every finite spectral-recursion check would be toy and projections heuristic and model-bound.  A valid residue, recursion identity, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-286/topological_recursion_router_theorem.md` proving compact endpoint-conditioned branch selection or the residue-collision/source-materialization obstruction.
