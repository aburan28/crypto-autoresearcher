# ECDLP-IDEA-397 — Parikh semilinear source projection

## Status and claim labels

- Class: `formal_language_projection`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_grammar_requires_source_transitions_and_parikh_projection_erases_occurrence_provenance`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct toy Parikh image or semilinear membership result is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible context-free grammar generates exactly the words encoding signed five-deck relations, while a compact Parikh semilinear representation of its language supports restriction membership and a canonical inverse from one count vector to occurrence-labelled factor points, enabling complete blind descent below the frozen gates.

## Mechanism-new operation

The screened operation is **compile elliptic endpoint constraints into a grammar, project derivations to Parikh count vectors, represent the image as a finite union of linear sets, query restricted membership, and invert one vector to a factor word and point occurrences**. It differs from word rewriting or semigroup transfer only if grammar productions and inverse provenance are source-free and subgate.

## Assumptions

1. A target-uniform grammar of subgate size generates all and only exact signed five-deck relations.
2. Its Parikh image has a compact effective semilinear representation for every restriction.
3. Count vectors retain enough information for a canonical derivation and occurrence-labelled point inverse.
4. Grammar restriction and semilinear intersection do not require enumeration of terminals, productions, periods, or source tuples above the caps.
5. Grammar construction, semilinear conversion, membership, inverse derivation, output, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_context_free_relation_grammar | Parikh_count_projection | compact_effective_semilinear_image | restricted_count_membership | canonical_count_to_factor_word_and_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H643`; a fixed-curve grammar is charged as compiler/advice unless constructed uniformly.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`; group-law reparameterization preserves the inversion burden.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`; exact serial source-state languages densify beyond the gate.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless derivation ancestry retains source-distinct transitions.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled productions are explicit source edges.

## Closest primary literature

- Parikh, [On Context-Free Languages](https://doi.org/10.1145/321356.321364), proves semilinearity of the commutative image of a supplied context-free language; it does not provide a compact effective inverse to labelled derivations.
- Chomsky and Schützenberger, [The algebraic theory of context-free languages](https://doi.org/10.1016/S0019-9958(63)91069-1), develops algebraic structure for supplied grammars without compiling elliptic relation fibres.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives commutative endpoint equations but no context-free grammar or count-to-point section.

No checked source supplies the proposed source-free grammar, compact semilinear image, and canonical occurrence inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, terminal alphabet, grammar schema, Parikh coordinates, semilinear normal form, inverse-derivation rule, restrictions, masks, and independent verifier.
2. Build target-independent grammar and semilinear state within `B^(9/4+o(1))`, without one terminal, production, or period per source tuple.
3. For known-log targets, intersect with deck restrictions, find a feasible count vector, reconstruct one derivation and occurrence-labelled five-point tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging empty/spurious vectors, inverse ambiguity, and dependent rows; solve and verify factor logs.
5. Apply the unchanged grammar, semilinear query, and inverse to fresh scalar-blind `Q+[t]P`, charging target updates, restrictions, and rebuilds.
6. Substitute factor logs, remove `t`, retain every ambiguity branch, and verify `[x]P=Q`.
7. Charge grammar/semilinear construction, membership, integer arithmetic, inverse derivation, source lift, output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Parikh's theorem begins with a grammar and deliberately forgets terminal order and derivation history. Constructing productions that accept exactly elliptic relation words requires the source-transition predicate already charged by the ledger, while a count vector cannot distinguish occurrences or recover which factor points produced it. Effective semilinear descriptions may also expand sharply and are existence summaries, not witness sections. This merges with IDEAs 084, 120, 166, 185, and 371 unless a new endpoint-only grammar and provenance-preserving inverse theorem are proved.

## Proof track

Construct a subgate exact grammar for every stratum, prove a polynomial-size semilinear representation, prove count membership iff exact source plus a canonical occurrence lift, and derive complete `lambda,mu<=0.45` bounds.

## Disproof track

Show that one production encodes source incidence, construct distinct relation words with the same Parikh vector but incompatible point labels, or prove grammar/semilinear expansion above the frozen caps.

## Positive and negative controls

- Positive: supplied context-free grammars with known semilinear images and planted derivations must reproduce exact count membership and labelled inverse derivations.
- Negative: anagrams with equal Parikh vectors but different source validity, ambiguous grammars, relabelled terminals, all signed strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 084/120/166/185/371, explicit source grammars, word-rewriting/semigroup controls, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only exact grammar, polynomial-size effective semilinear image, source-biconditional canonical inverse, `1,000` independent rows, `100` blind descents, frozen caps, and `lambda,mu<=0.45`.
- Falsify on one source-labelled production, one same-vector/different-source collision, one missing/spurious inverse, semilinear expansion above cap, or either exponent at least `0.50`.
- A correct toy Parikh image or membership answer is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-397/grammar_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-397/parikh_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-397/count_to_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-397/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic Parikh projection, not Parikh's theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; semilinear correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-397/grammar_source_obligations.md` and classify every terminal and production in the smallest proposed grammar as endpoint-derived or source-labelled advice.
