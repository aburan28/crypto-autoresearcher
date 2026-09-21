# ECDLP-IDEA-165 — Fixed rational pair-sum quotient unranking

## Status and claim labels

- Class: `algorithmic-representation`
- Risk band: `conservative-theorem-gated`
- Top lane: `none`
- State: `deferred_bounded_degree_pair_quotient_scoped_negative_target_router_open`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: any finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; quotient narrowing, a source pair, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

One target-independent bounded-degree rational map `pi` on oriented pair sums of a sparse elliptic factor base has `o(B^2)` quotient states and a constant-list canonical inverse from `(pi(S_i+S_j),R)` to exact oriented source pairs. Composing two such states with a fifth source yields complete five-source relations, factor logs, and masked descent below rho and BSGS.

## Mechanism-new operation

The operation is **fixed rational pair-sum quotienting with exact constant-list unranking**. It is not a factor-base shape, preprocessed 3SUM table, heuristic x-only bucket, or solver swap. The removal test is one map frozen before targets, a proved subquadratic state set, and a public source inverse whose advice is also subquadratic.

The theorem-only producer receipt now closes the fixed-map compression arm. Exact
state-only composition forces the quotient to be injective; more generally, pair
states times exact inverse-list size is `Omega(B^2)`. A bounded-degree rational map
has a quadratic image on a generic Sidon factor base, while small-doubling factor
bases move the same payload into growing source multiplicity. A genuinely new
target-local indexed collision router remains outside this scoped result.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, orientations, `pi`, masks, and verifier are frozen.
2. `pi` is target independent and bounded degree over every admitted curve.
3. Distinct pair-source fibers compress to `B^(2-epsilon)` states while every useful state has a constant-list exact inverse.
4. Composition covers repetitions, infinity, collisions, and all signs without a pair dictionary.
5. Map construction, state generation, inverse advice, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`oriented_factor_base_pairs | fixed_bounded_degree_rational_quotient | subquadratic_state_image | constant_list_exact_pair_unranking | five_source_blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H686`, the fixed-curve compiler/advice boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit source-view hypothesis.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source gate.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, the explicit stage-one pair/triple boundary.

## Closest primary literature

- Green and Ruzsa, [Freiman's theorem in an arbitrary abelian group](https://arxiv.org/abs/math/0505198), supplies structural controls for small sumsets, not an elliptic source inverse.
- Golovnev et al., [Data Structures Meet Cryptography: 3SUM with Preprocessing](https://arxiv.org/abs/1907.08355), supplies preprocessing/query controls that do not meet the claimed source-biconditional compression.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies neighboring pair-sum equations.

No checked primary source supplies `pi`, its inverse, and complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `pi`, orientations, pair-state representation, inverse rule, factor base, masks, and verifier.
2. Prove target-independent image-size and constant-list inverse theorems without enumerating `F^2` as advice.
3. Build the allowed compact state representation once and record every collision.
4. Query known `R_j=[r_j]P`, compose pair states plus a fifth source, unrank all pairs, and verify every full tuple.
5. Preserve misses, duplicates, ambiguity, repeats, infinity, and output; collect rank `B` and verify factor logs.
6. Apply the identical query/unranking path to fresh `Q+[t]P` masks.
7. Substitute logs, remove masks, keep all candidates, and verify `[x]P=Q`.
8. Charge map/state construction, advice, queries, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let quotient setup cost `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query plus unranking `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

All inverse advice and pair-state output count in `a,a_m,o`.

## Likely fatal obstruction

The producer theorem confirms the scoped obstruction. A bounded-degree map has `Theta(B^2)` image on generic pair sums; any subquadratic image forces growing exact source lists or quadratic total advice. Merely adding `R` to the inverse input relocates the work to the unsupplied target-local five-term collision router.

## Proof track

Exhibit `pi`, prove uniform subquadratic image and constant-list exact inverse bounds, then derive complete `lambda,mu<=0.45` descent.

## Disproof track

Prove generic image size `Theta(B^2)`, exhibit unbounded source fibers, show inverse advice is quadratic, or derive time/memory exponent at least `0.5`.

## Positive and negative controls

- Structured small-doubling sets with known quotient maps.
- Random and interval factor bases with matched sizes.
- Explicit pair tables, 3SUM indexing, x-only bucket, rho, and BSGS controls.
- Exhaustive toy pair/five-source fibers and blind-target verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires the fixed-map image and inverse theorems plus `lambda,mu<=0.45`. A later approved toy test needs 100% source recall, zero false tuples, constant charged lists, and no target-selected map. Quadratic state/advice, one lost source, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Existing theorem-only quotient/unranking gate: `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md`
- Map specification: `ideas/artifacts/ECDLP-IDEA-165/rational_map_spec.md`
- Fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-165/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-165/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-165/cost_analysis.md`

The theorem gate is non-run producer evidence. Every other path is prospective; no experiment is authorized.

## Interpretation boundary

This is deferred and novelty-unverified. Finite checks are toy and projections heuristic and model-bound. A narrowed bucket or valid relation is not a breakthrough.

## Exactly one next executable action

1. Independently review `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` and either recommend rejection of the fixed-map operation or freeze one explicit noncongruence target-local collision-router recurrence with setup at most `B^2.25`, query at most `B^1.25`, and exact all-strata source output; do not build a pair table or run a solver.
