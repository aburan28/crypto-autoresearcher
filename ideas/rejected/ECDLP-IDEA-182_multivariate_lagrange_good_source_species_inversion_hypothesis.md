# ECDLP-IDEA-182 — Multivariate Lagrange–Good source-species inversion

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_marked_coefficient_deck_reconstruction_scoped_negative`
- Cohort: `20260718-d`
- Evidence scale: primary-literature and semantic preflight only; no experiment ran
- Contract posture: retired `review_required` conservative preflight; unapproved and zero-run
- Scale labels: every prospective finite check is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct inversion identity, coefficient, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform recursive species encodes all signed factor-base assemblies summing to an elliptic endpoint, while a bounded set of source marks retains atom identities. Multivariate Lagrange–Good inversion of the implicit species equations then returns every exact source tuple from the public endpoint without enumerating the source fiber, enabling rank-complete factor-base relations and blind masked target descent with time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **source-marked recursive-species construction followed by multivariate Lagrange–Good coefficient inversion**. It is mechanism-new only if a public endpoint compiles to a finite implicit system whose inverse coefficients expose exact signed point atoms with neither one variable per atom nor one coefficient per source tuple. Applying Good inversion to a supplied source-marked series, replacing the coefficient engine, changing truncation, or explicitly tabulating large-prime/source coefficients is a control.

Operation-level review found the inversion transform new in vocabulary but not at the occupied source-fiber gate. An unmarked series counts or aggregates endpoint fibers, while exact point recovery requires marks that distinguish the `B` factor-base atoms and their arity-`m` assemblies. The marked coefficient oracle therefore reconstructs the same `B^m` deck or assumes it as input. This version is merged/rejected only at that scoped interface; the formal inversion theorem itself is not disputed.

## Assumptions

1. Public `E/F_p`, prime-order `P` of order `N`, target `Q`, signed factor base `F` of size `B=N^beta`, arity, masks, and verifier are frozen.
2. A scalar-blind endpoint compiler produces a finite target-uniform recursive system for every known-log and unknown-log endpoint.
3. Its source marks distinguish every exact signed atom, repetition, infinity case, and multiplicity without a source table.
4. Lagrange–Good inversion is exact on all relevant branches and emits every source tuple with no false tuple.
5. Series construction, coefficient queries, truncation, marks, output, failed trials, rank, linear algebra, descent, verification, time, and bit memory are charged.

## Semantic fingerprint

`endpoint_to_recursive_source_species | multivariate_Lagrange_Good_inversion | exact_marked_atom_coefficients | no_Bm_source_deck | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where lossless ancestry materializes source-distinct edges.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge output boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the source-faithful serial-state materialization boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete source, rank, and blind-descent gate.

## Closest primary literature

- Good, [Generalizations to several variables of Lagrange's expansion, with applications to stochastic processes](https://doi.org/10.1017/S0305004100034666), proves the multivariate inversion formula but assumes access to the defining series and its coefficients.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations for elliptic sums but not a compact exact source-marked coefficient oracle.

Neither checked primary source gives the proposed endpoint-to-marked-species compiler, exact atom extractor, or complete sub-rho descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta`, signed-source conventions, arity, implicit species equations, coefficient order, truncation, masks, and an independent verifier.
2. Compile each known-log endpoint `R_j=[r_j]P` into the same scalar-blind recursive system without using `r_j`, source tuples, or endpoint-specific advice.
3. Apply multivariate Lagrange–Good inversion and emit every exact signed factor-base tuple represented by the relevant endpoint coefficient.
4. Independently verify membership, elliptic sum, multiplicity, sign, repeats, infinity, misses, false tuples, and the complete emitted coefficient support.
5. Collect at least `B+sigma` verified independent rows of rank `B`, solve factor-base logarithms, and verify every recovered logarithm by scalar multiplication.
6. Apply the identical compiler and inversion to fresh masked targets `R_t=Q+[t]P` with independently sampled public masks `t`.
7. Substitute verified factor-base logs, remove each mask, retain all ambiguity candidates, and accept only `x` satisfying `[x]P=Q`.
8. Charge recursive setup, marks, coefficient support, all failed queries, output, rank, linear algebra, descent, verification, wall time, and peak bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let implicit-system and mark construction cost `N^a` time and `N^a_m` memory; reciprocal relation and target densities be `N^delta,N^delta_t`; one complete inversion/coefficient query cost `N^q,N^q_m`; emitted support and target ambiguity be `N^o,N^u`; and factor-log linear algebra cost `N^ell,N^ell_m`. Then the complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every mark, coefficient, truncation level, source-support word, failed endpoint, output tuple, and descent branch is included; treating the inversion identity as a unit-cost oracle is forbidden.

## Likely fatal obstruction

An endpoint-only unmarked series can retain fiber cardinalities or symmetric aggregates but not distinguish different exact point tuples with the same sum. Making Good's coefficient source-biconditional requires independent atom marks or equivalent source coordinates. Those marks have at least `B` identities and, at fixed arity, expose the `B^m` coefficient/source deck; an oracle returning the selected marked coefficient has already solved the missing endpoint-to-source problem. Thus inversion reorganizes supplied source information instead of creating it.

## Proof track

Give a scalar-blind endpoint compiler with bounded description, prove a source-biconditional between inverse coefficients and all exact signed tuples on every stratum, prove the coefficient support is neither stored nor enumerated, and derive measured and formal `lambda,mu<=0.45` through rank and blind descent.

## Disproof track

Exhibit two fibers with identical compiled systems but different sources, reduce exact marked coefficient access to a `B^m` dictionary, prove the number of necessary marks/support words exceeds budget, find one missed or false multiplicity, or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Positive: classical one- and multivariate recursive species with supplied atom marks and independently known coefficients.
- Positive: exhaustive toy elliptic fibers where all sources are deliberately supplied to the series builder.
- Negative: the same fibers with atom marks erased, which must preserve aggregate counts while losing point identities.
- Negative: explicit `B`-variable and `B^m` coefficient tables, post-hoc endpoint selectors, dense resultants, rho, BSGS, known-log leakage, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected at the compact marked-coefficient-oracle gate. A successor under a new ID requires 100% exact source and multiplicity recall, zero false tuples, no scalar/source advice, no explicit or implicit `B^m` support, verified rank `B`, successful blind masked descent, and formal `lambda,mu<=0.45`. Values strictly above `0.45` and below `0.50` are inconclusive; one source-biconditional failure, hidden source deck, or either exponent at least `0.50` falsifies the scoped successor. Correct inversion, relation validity, or a toy scalar never promotes it.

## Artifact plan

- Coefficient-oracle theorem: `ideas/artifacts/ECDLP-IDEA-182/lagrange_good_coefficient_oracle_theorem.md`
- Frozen recursive-species specification: `ideas/artifacts/ECDLP-IDEA-182/source_species_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-182/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-182/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-182/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-182_lagrange_good_preflight.yaml`

All research-artifact paths are prospective. No artifact directory or run exists; the contract remains review-required, unapproved, retired from dispatch, and zero-run. No correctness result would by itself support an ECDLP improvement.

## Interpretation boundary

This is a novelty-unverified conservative scoped negative: the marked coefficient interface merges with the recorded source-deck obstruction. Any future finite evidence is toy, and all complexity estimates remain heuristic and model-bound. The conclusion does not refute Lagrange–Good inversion and does not claim a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-182/lagrange_good_coefficient_oracle_theorem.md` proving or refuting that one bounded endpoint-compiled implicit system can expose exact point-atom coefficients without a `B`-marked or `B^m` source-support representation.
