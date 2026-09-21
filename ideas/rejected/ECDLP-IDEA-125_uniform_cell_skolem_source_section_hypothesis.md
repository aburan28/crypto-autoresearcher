# ECDLP-IDEA-125 — Uniform cell-Skolem source section

## Status and claim labels

- Class: `model-theoretic-representation`
- Risk band: `representation-changing`
- State: `merged_rejected_uniform_skolem_source_oracle`
- Evidence scale: primary-literature and structural preflight only; no experiment ran
- Scale labels: prospective checks are `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; quantifier elimination, a definable section, a valid relation, or a correct toy scalar is not an ECDLP break.

## Falsifiable hypothesis

After a uniform lift of the prime-field elliptic five-source relation to a Denef-Pas language, parameterized quantifier elimination yields a bounded number of cells and a public definable Skolem section selecting exact signed factor-base sources for every soluble target. If the cell count, formula size, residue data, or source ambiguity grows to rho, or if no scalar-blind definable section exists, the hypothesis is false.

## Mechanism-new operation

The proposed operation is **uniform bounded-cell decomposition with a factor-base source Skolem section**. It would transform the quantified relation formula into `N^h` target-uniform cells, each carrying an explicit definable function from target parameters to a complete signed source tuple, including residue-field and valuation side conditions. This changes representation only if formula construction and evaluation avoid enumerating factor-base elements or source fibers and the section remains exact after finite-field specialization.

This is not a generic symbolic solver, variable order, parameter change, dense elimination, or post-hoc selector. Quantifier elimination alone gives a definable description, not a compact source inverse; a choice function obtained by ordering or listing all residue points is an explicit source table. The supposed operation merges with IDEA-068's constructive source-section obligation, with IDEA-098's source-lifting shelling machinery and IDEA-111's canonical section orbit as adjacent formulations. Calling the missing symmetric-fiber choice a uniform Skolem function does not remove their obstruction, so the idea is rejected rather than deferred.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and a target-independent factor base `F` of size `B=N^beta`.
2. The curve, factor-base predicate, five signed addition constraints, infinity, repetitions, and target parameter admit a uniform bounded-complexity formula in a suitable valued-field/residue-field language.
3. Quantifier elimination and cell decomposition are effective uniformly in `p`, `E`, `F`, and `R`, with at most `N^h` cells and coefficient payload below rho.
4. Every nonempty target fiber has a scalar-blind definable Skolem section that outputs exact signed factor-base points, multiplicities, and all exceptional cases.
5. Cell and section evaluation do not enumerate residue-field domains, encode an explicit large-prime table, or hide a dense resultant/quotient computation.
6. Formula compilation, residue data, cells, source output, relation collection, factor logs, blind descent, verification, and peak memory are charged.

## Semantic fingerprint

`uniform_valued_field_lift | Denef_Pas_cell_decomposition | bounded_parameter_cells | definable_Skolem_source_section | finite_field_specialization`

The removal test is a uniform complexity theorem plus exact scalar-blind source functions. Generic quantifier elimination, CAD/Grobner/resultant substitution, lexicographic choice after enumeration, or applicability-only definability is a duplicate or control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which asks for a public algebraic source-fiber generator and target join; a bounded definable section is a precise representation-changing candidate for that missing source operation.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H640`, where explicit signs or a genuinely symbolic finite-field backend remain open; uniform cells must preserve the full signed source semantics.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H641`, which requires a true symbolic `S5` backend or different factor-base generator after tested decompositions fail; formula syntax alone is insufficient.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where materialized transition polynomials become dense; the cell representation must prove it never reconstructs those polynomials.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where the frozen bit-vector membership compilation times out; model-theoretic elimination is distinct only with a uniform sub-rho theorem, not a solver swap.

## Closest primary literature

- Denef, [p-adic semi-algebraic sets and cell decomposition](https://doi.org/10.1515/crll.1986.369.154), proves cell decomposition for p-adic semialgebraic sets; it does not give sub-rho complexity or source sections for growing elliptic finite-field fibers.
- Pas, [Cell Decomposition and Local Zeta Functions in a Tower of Unramified Extensions of a p-Adic Field](https://doi.org/10.1112/plms/s3-60.1.37), supplies a uniform valued-field framework; it does not bound the requested source-labelled finite-field specialization.
- Cluckers, [Analytic p-adic Cell Decomposition and Integrals](https://arxiv.org/abs/math/0206161), proves analytic cell decomposition and parameterized results, not a compact elliptic factor-base Skolem inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation equations but no uniform cell complexity or definable source choice.

The checked primary literature proves definability and decomposition theorems in related structures, not this effective bounded-cell/source-section claim. Novelty remains unverified, and no concrete identity separates it from the existing constructive-section lane.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, a uniform valued/residue-field language, the five-source formula, sign/order convention, exceptional strata, and specialization map.
2. Eliminate the source quantifiers symbolically and produce a target-uniform cell family without enumerating factor-base or residue-field elements.
3. Attach to every soluble cell explicit Skolem functions for all signed source coordinates and prove their completeness, disjointness, multiplicity handling, and finite-field validity.
4. Evaluate the cells and source functions on public targets, then independently verify every output by curve membership, factor-base membership, and elliptic addition.
5. Apply the identical formula to known multiples until `B+sigma` verified rows have rank `B`, charging empty cells, failures, and all outputs.
6. Solve and independently verify the factor-base logarithms.
7. Evaluate the same cells on blind `Q+[t]P`, recover complete source tuples, substitute factor logs, subtract `t`, and retain every candidate.
8. Accept only `[x]P=Q` and serialize formula, cell, source, rank, factor-log, descent, time, and memory receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; uniform formula and elimination time/memory be `N^a,N^a_m`; cell count, coefficients, residue payload, and serialized section be `N^h,N^h_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; cell evaluation, source output, and exact verification per query be `N^k`; source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time/memory be `N^ell,N^ell_m`. Then

`lambda=max(a,h,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

`mu=max(a_m,h_m,beta+o,ell_m,u)`.

All quantifier-elimination branches, residue representatives, valuation bounds, coefficients and bit lengths, cells, empty targets, source tuples, relation rows, factor logs, and blind candidates are charged. Logical decidability without an effective uniform complexity bound supplies no ECDLP exponent.

## Likely fatal obstruction

Cell decomposition can replace a formula by many simple pieces without reducing their number or coefficient complexity. Uniformity in a fixed formula does not automatically cover factor-base predicates and parameters whose size grows with `p`. Definable Skolem functions can fail in relevant p-adic settings, and finite residue fibers with symmetric sources may have no canonical scalar-blind choice. Encoding a choice by a residue-field order or representatives can cost `Theta(B)` per variable or hide enumeration; listing all source branches restores the relation fiber. Specialization from characteristic zero or a valued lift may also merge, lose, or ramify finite-field sources. Most importantly, the proposal assumes the same complete source section already isolated by IDEA-068 rather than deriving a new algebraic identity that constructs it.

## Proof track

Historic survival would have required a uniform effective quantifier-elimination theorem for the frozen growing family, a complete finite-field source biconditional, and `lambda,mu<=0.45` through blind descent. It would also have required a concrete algebraic identity showing that the section is not the constructive-section oracle of IDEA-068 or the adjacent IDEA-098/111 source lifts. No such non-merge identity is supplied, so this proof track is closed under this ID.

## Disproof track

Exhibit a target family whose number of necessary cells or source branches is `N^(1/2)`; prove no definable Skolem section exists uniformly; show the factor-base predicate needs formula or residue payload at least `N^(1/2)`; find two specialized fibers indistinguishable by the cells but with different sources; or derive `lambda>=1/2` or `mu>=1/2`.

## Positive and negative controls

- Fixed p-adic semialgebraic families with published cell decompositions and explicit definable sections.
- Symmetric finite fibers with no canonical chosen point, and matched fibers where a unique section is planted.
- Factor bases defined by bounded-degree residue predicates versus arbitrary listed or hashed subsets of the same size.
- Exhaustive toy elliptic fibers across good, bad, ramified, repeated, signed, and infinity strata.
- Dense resultant, bit-vector `P1480`, and direct enumeration controls with identical output and coefficient accounting.
- Blind known-log targets with independent source/scalar verification and matched rho/BSGS baselines.

## Quantitative promotion and falsification gates

This record is merged-rejected. Historic promotion required a concrete non-merge identity constructing the source section, uniform effective cells, exact specialization, `100%` source recall with zero false tuples, no residue table, and `lambda,mu<=0.45`. Falsify on merger into IDEA-068/098/111, nonuniform constants above the gate, any missing symmetric-fiber choice, dense elimination, post-hoc choice, blind-descent failure, or a time/memory exponent at least `0.5`. Reopening requires a new idea ID whose mechanism names and proves the obstruction-removing identity rather than restating the section oracle.

## Artifact plan

- Uniformity and Skolem theorem gate: `ideas/artifacts/ECDLP-IDEA-125/cell_skolem_theorem.md`
- Prospective language/fixture specification: `ideas/artifacts/ECDLP-IDEA-125/language_fixtures.json`
- Prospective eliminator prototype: `ideas/artifacts/ECDLP-IDEA-125/uniform_cells.sage`
- Independent specialization/source verifier: `ideas/artifacts/ECDLP-IDEA-125/verify_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-125/cost_analysis.md`

These are prospective paths only; no artifact or experiment exists.

## Interpretation boundary

This merged-rejected representation proposal is novelty-unverified, heuristic, model-bound, and limited to prospective toy controls. Logical definability, quantifier elimination, a correct cell decomposition, or a toy source section is not a complete ECDLP algorithm. The rejection preserves the existing constructive-section lane and does not claim a generic hardness result or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-125/cell_skolem_theorem.md` as a merge-closure note mapping the proposed oracle to IDEA-068/098/111 and requiring any future successor to receive a new ID and exhibit a concrete source-section identity not implied by those records before any eliminator or toy run.
