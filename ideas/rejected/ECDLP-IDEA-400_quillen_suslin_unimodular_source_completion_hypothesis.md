# ECDLP-IDEA-400 — Quillen–Suslin unimodular source completion

## Status and claim labels

- Class: `projective_module_unimodular_completion`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_module_generators_encode_relations_and_unimodular_basis_has_no_factor_atom_inverse`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid projective-module trivialization is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-derived local source-syzygy frames form a compact projective module over a polynomial ring, and constructive Quillen–Suslin completion patches them into one global unimodular basis whose coefficients canonically decode exact factor occurrences under all restrictions.

## Mechanism-new operation

The screened operation is **prove projectivity of locally defined relation frames, complete a unimodular row, trivialize the module globally, and back-substitute the global basis to occurrence-labelled factor points**. The claimed new step is global algebraic patching, not a different Gröbner order or linear solver.

## Assumptions

1. Endpoint data construct compact module generators without first enumerating relations or source tuples.
2. The module is finitely generated projective uniformly across every signed and exceptional stratum.
3. Constructive completion has subgate degree, coefficient, time, and memory growth.
4. One global basis retains exact occurrence labels and supports arbitrary deck restrictions without recompletion.
5. Generator construction, projectivity proof, completion, back-substitution, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_local_source_syzygies | projective_polynomial_module | Quillen_Suslin_unimodular_completion | global_basis_to_factor_occurrence_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; a module presentation must implement exact source return, not only relation validity.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; source-bearing generators are charged as advice.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; an invertible full-rank basis change is not compression.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; expanded polynomial state cannot hide the source deck.
5. `inputs/ledger_inventory.json` — imported `P1478`; factor occurrences and restriction replay must be explicit in the complete path.

## Closest primary literature

- Quillen, [Projective modules over polynomial rings](https://doi.org/10.1007/BF01390008), proves freeness over polynomial rings but begins with the module.
- Suslin, [Projective modules over polynomial rings are free](https://doi.org/10.1070/IM1976v010n04ABEH001813), establishes the complementary freeness theorem without constructing elliptic source generators.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies nonlinear endpoint equations but not a compact projective source module.

No checked source gives the proposed endpoint-only module and factor-atom inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, polynomial ring, module presentation, local frames, completion rule, restrictions, and verifier.
2. Construct and trivialize the target-independent projective module within `B^(9/4+o(1))`, charging degrees and coefficients without relation enumeration.
3. For known-log targets, specialize the global basis, decide exact restricted existence, back-substitute one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging failed specializations, ambiguity, output, and dependent rows; solve and verify factor logs.
5. Reuse the unchanged module and basis on fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute factor logs, remove `t`, retain all basis/specialization branches, and verify `[x]P=Q`.
7. Charge generator construction, completion, specialization, inverse, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Quillen–Suslin starts after module generators are supplied. Generators exact enough to describe elliptic source syzygies already encode the relation incidence, while a free basis represents module combinations rather than primitive factor points. Back-substitution needs the missing atom dictionary, and constructive degrees can reflect the full source deck. This meets IDEAs 052, 065, 115, 142, 152, and 372 without being a mere backend substitution.

## Proof track

Construct endpoint-only compact generators, prove projectivity and bounded constructive completion, prove a restriction-stable basis-to-factor inverse, and certify `lambda,mu<=0.45`.

## Disproof track

Show one generator contains source incidence, exhibit equal global module coordinates with different factor tuples, or prove completion degree/state/output above the caps.

## Positive and negative controls

- Positive: supplied small projective modules with planted unimodular completions and labelled basis atoms must replay exactly.
- Negative: free modules whose bases mix atoms, relabelled generators with identical spans, nonprojective specializations, all signed strata, restrictions, and blind targets.
- Baselines: IDEAs 052/065/115/142/152/372, generic module solvers, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only module construction, bounded completion, exact atom inverse, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing generator, atom collision, nonprojective stratum, cap violation, or either exponent at least `0.50`.
- A correct toy unimodular completion is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-400/module_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-400/unimodular_completion_bounds.md`
- `ideas/artifacts/ECDLP-IDEA-400/basis_atom_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-400/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic module-completion route, not Quillen–Suslin. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; module freeness or completion correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-400/module_source_obligations.md` and classify every proposed generator and basis-to-atom map by endpoint versus source dependence.
