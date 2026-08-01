# ECDLP-IDEA-214 — Freudenthal–Jordan Peirce source atomizer

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_orbit_invariants_aggregate_without_elliptic_atom_inverse`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and representation audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an orbit invariant, rank decomposition, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Signed elliptic factor points embed as rank-one elements of a bounded cubic Jordan/Freudenthal system such that its cubic/quartic composition maps five sources to a low-rank endpoint element. A canonical Peirce frame would invert that element to exact sources, enabling factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **Freudenthal invariant composition followed by canonical Peirce atomization**. It merges/rejects because bounded-rank orbit invariants aggregate sources and generic Peirce frames are tied to algebra rank, not five arbitrary factor labels; a faithful growing algebra stores the source deck.

## Assumptions

1. Public curve/group/factor base `B=N^beta` and target are frozen with a target-independent bounded-dimensional Jordan algebra.
2. A public embedding and endpoint composition are biconditional with all signed five-source relations.
3. The Peirce decomposition is canonical, unique, and exactly invertible to factor points across degenerate strata.
4. Embedding dimension, invariant arithmetic, decomposition, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`elliptic_factor_atoms_to_rank_one_Jordan_elements | Freudenthal_cubic_quartic_composition | endpoint_low_rank_orbit | canonical_Peirce_idempotents | exact_point_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H396`, the invariant-theory representation route.
2. `inputs/ledger_inventory.json` — imported `ECFG-H397`, the bounded-rank atomization hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H465`, the exceptional-algebra transfer boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear invariant/source gap.
5. `inputs/ledger_inventory.json` — imported `P1479`, the compact orbit-invariant frontier.

## Closest primary literature

- Krutelevich, [Jordan algebras, exceptional groups, and higher composition laws](https://arxiv.org/abs/math/0411104), develops cubic/Freudenthal rank and orbit invariants.
- Krutelevich, [Jordan algebras, exceptional groups, and Bhargava composition](https://doi.org/10.1016/j.jalgebra.2007.02.060), gives composition laws without an elliptic factor-source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), is the endpoint relation baseline.

No checked source gives the claimed elliptic embedding and canonical atom inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze algebra, point embedding, composition law, Peirce inverse, masks, and verifier.
2. Prove the endpoint-orbit/source biconditional and bounded representation size before finite tests.
3. For known endpoints, decompose to every exact signed factor atom and verify each elliptic row.
4. Collect full rank, solve and verify factor-base logs.
5. Repeat unchanged on fresh `Q+[t]P`, substitute logs, subtract `t`, retain ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`; BSGS also uses that memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, composition/decomposition `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Algebra dimension enters setup/memory; both exponents must be at most `0.45`.

## Likely fatal obstruction

A generic semisimple Jordan element has a bounded spectral frame fixed by algebra rank, not five arbitrary source-labelled atoms. Low-rank decompositions can be nonunique; invariant orbits retain aggregate rank/norm data. Growing the algebra to distinguish factor atoms charges the missing state.

## Proof track

Construct a bounded cubic-Jordan embedding, prove a unique all-strata Peirce/source inverse and source biconditional, and derive complete `lambda,mu<=0.45`.

## Disproof track

Exhibit two source tuples with one orbit invariant, nonunique Peirce decompositions, rank bounded below five, dimension/state growth at least `B^3`, or exponent at least `0.50`.

## Positive and negative controls

- Positive control: planted rank-one elements in a supplied Jordan algebra with known spectral frame.
- Negative controls: conjugate/nonunique decompositions, invariant-only orbit classifiers, tensor/apolar decompositions, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires algebra state at most `B^2.25`, query at most `B^1.25`, 100% source/multiplicity recall, zero false atoms, a unique public frame, no factor-labelled basis, and `lambda,mu<=0.45`. One orbit collision, nonunique frame, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective identity: `ideas/artifacts/ECDLP-IDEA-214/jordan_embedding_identity.md`
- Prospective inverse: `ideas/artifacts/ECDLP-IDEA-214/peirce_inverse_spec.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-214/symbolic_orbit_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-214/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-214/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. An invariant identity, rank decomposition, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-214/jordan_embedding_identity.md` and solve the bounded-dimensional cubic-Jordan coefficient identity, certifying either a source-biconditional inverse or a concrete nonuniqueness/rank obstruction.
