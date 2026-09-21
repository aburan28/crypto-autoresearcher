# ECDLP-IDEA-287 — Motivic Donaldson–Thomas wall-crossing source factorization

## Status and claim labels

- Class: `mechanism`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_wall_crossing_counts_classes_without_object_level_factor_return`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid stability structure, DT invariant, wall-crossing identity, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform 3-Calabi–Yau category or quiver-with-potential compiled from the ECDLP source equations has semistable objects corresponding to factor tuples, and a controlled stability-wall crossing canonically factorizes the endpoint class into those stable constituents.  Reading the factors would yield relations and fresh-target descent with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode source tuples as semistable objects with endpoint charge, cross a frozen stability wall, factor the motivic Donaldson–Thomas automorphism in the quantum torus, and decode stable factors as exact source points**.  This categorical factorization is not a solver substitution.  Kontsevich–Soibelman invariants count semistable objects of a fixed K-theory class and wall-crossing constrains ordered products of aggregate invariants.  It does not recover an individual object or Jordan–Hölder representative from its charge.  A quiver whose stable objects are labelled source tuples or an expanded quantum-torus product materializes the source alphabet; a compact invariant identifies many objects.  The operation merges with counting-invariant, product-materialization, and missing-section negatives.

## Assumptions

1. Public source equations and endpoint canonically determine a compact 3-Calabi–Yau category or quiver with potential without enumerating factor tuples.
2. Exact source tuples correspond injectively to stable factors, not merely to objects sharing one charge or S-equivalence class.
3. A target-independent stability path and wall-crossing product admit efficient exact factorization that returns signed factor-base points on every stratum.
4. Category/quiver construction, potential, stability data, invariant computation, quantum-torus products, output, ambiguity, factor logs, descent, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | calabi_yau_quiver_source_encoding | motivic_dt_wall_crossing | stable_object_factor_decode | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the expanded source-product control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate class invariant without object output.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the compact invariant versus source-preimage boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the auxiliary-category construction-cost boundary.

## Closest primary literature

- Kontsevich and Soibelman, [Stability structures, motivic Donaldson-Thomas invariants and cluster transformations](https://arxiv.org/abs/0811.2435), defines motivic invariants counting semistable objects by K-theory class and develops wall-crossing products; it does not decode an individual object from its charge.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations whose exact bounded solutions would have to become and return from stable factors.

No checked primary source constructs a compact ECDLP source category with an object-level inverse through motivic wall crossing; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source equations, category/quiver compiler, potential, stability path, wall-crossing order, masks, and verifier.
2. For random known-log endpoints, construct the compact categorical instance and endpoint charge without enumerating semistable source objects.
3. Compute and factor the wall-crossing product, decode every accepted stable factor to exact signed factor points, and verify each relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen category, stability path, and factorization to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode all surviving stable-object branches to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging quiver/category construction, invariant computation, quantum-torus expansion, object ambiguity, source output, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one category/DT/factorization attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned stable-object/source output be `N^o`, unresolved charge-to-object ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every quiver vertex/arrow, potential term, class, stability ray, semistable stack, motive coefficient, quantum-torus monomial, wall factor, object branch, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Motivic DT invariants and wall-crossing formulas aggregate objects by charge and stability; they do not select one object or decomposition inside a moduli stack.  Distinct factor tuples can be S-equivalent or contribute to the same invariant.  Refining the category, charge lattice, or quantum-torus monomials until every tuple is distinct creates source-indexed state or output, while constructing the desired stable object from the endpoint imports the witness.  Wall crossing rearranges aggregate counts rather than creating exact factor return.

## Proof track

Construct the category without source witnesses, prove tuple-injective stable-object encoding and canonical object-level factorization across every wall, prove exact factor return, and certify complete `lambda,mu<=0.45` including moduli and product expansion.

## Disproof track

Exhibit distinct source tuples with the same charge, S-equivalence class, or wall-crossing contribution, prove category/product/output size at least `N^0.50`, show the selected stability path imports a source object, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy finite quiver with known stable objects, explicit DT data, and independently checked wall-crossing factorization.
- Negative controls: objects sharing a charge, strictly semistable S-equivalent objects, permuted source labels, source-indexed quivers, expanded quantum-torus products, relation-only certificates, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires witness-free categorical compilation, object-level injectivity, exact all-strata factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  A charge/S-equivalence collision, source-labelled category, category/product/output exponent at least `0.50`, missing factor return, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-287/motivic_wall_crossing_factor_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-287/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-287/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-287/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk mechanism proposal.  Every finite quiver/DT check would be toy and projections heuristic and model-bound.  A correct invariant, wall-crossing identity, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-287/motivic_wall_crossing_factor_theorem.md` proving object-level exact factorization or the charge-collision/source-materialization obstruction.
