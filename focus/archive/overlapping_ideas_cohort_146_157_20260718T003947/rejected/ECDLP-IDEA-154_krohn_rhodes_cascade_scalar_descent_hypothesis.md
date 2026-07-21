# ECDLP-IDEA-154 — Krohn–Rhodes cascade scalar descent

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_faithful_state_orientation`
- Cohort: `20260718-a`
- Evidence scale: semantic and literature audit only; no experiment ran
- Contract posture: no contract; unapproved; zero runs authorized
- Scale labels: every prospective finite test is `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct cascade, compact toy automaton, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a generic ordinary prime-field curve and target-independent factor base `F` of size `B=N^beta`, the labelled partial-sum transition system for `m`-term decompositions admits a public Krohn–Rhodes prime/reset cascade of retained size `N^(c+o(1))`, `c<1/2`, whose endpoint state can be inverted to exact signed factor-base source tuples in complete query exponent `q<1/2`. The identical cascade supports relation collection and blind descent of `Q+[t]P`, with complete time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **prime/reset cascade decomposition with exact source-word inversion**. Public factor atoms act on a bounded observable state of elliptic partial sums; Krohn–Rhodes decomposition replaces the full transition semigroup by a wreath-product cascade, and endpoint component states are recursively inverted to a source word.

This is not ordinary automaton minimization, a solver substitution, an explicit scalar-orbit table, a parameter change, or an ECFG selector. It is distinct only if the cascade is constructed before materializing all partial sums, remains sub-rho, and has an exact endpoint-to-source inverse.

The record is rejected because Krohn–Rhodes decomposition factors a supplied transformation semigroup but does not shrink the faithful state set. For a prime cyclic translation action, retaining enough orientation to distinguish all endpoint continuations restores `N` states or an equivalent order-`N` dictionary. Dropping that orientation gives only membership or orbit aggregation, merging with IDEA-011/070/084/120 and the ledger’s explicit-source boundary.

## Assumptions

1. `E/F_p` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, with `Q=[x]P`.
2. `F` is target-independent, signed, and has size `B=N^beta`.
3. Cascade construction uses only public point encodings and complete elliptic addition; scalar indices and discrete-log labels are forbidden.
4. The state quotient is continuation-faithful: accepting states invert to all exact ordered or canonically unordered source tuples, including signs, repetitions, infinity, and exceptional charts.
5. Setup, transition evaluation, failed endpoints, source output, rank, factor-log linear algebra, blind descent, verification, and peak bit memory are charged.
6. No claim extrapolated from a toy cascade is treated as cryptographic-scale evidence.

## Semantic fingerprint

`elliptic_partial_sum_transition_semigroup | Krohn_Rhodes_prime_reset_cascade | subrho_continuation_faithful_state | exact_source_word_inverse | blind_masked_descent`

The load-bearing operation is a sub-rho continuation-faithful cascade with source inversion. A compact aggregate semigroup, ordinary DFA minimization, explicit orbit directory, or membership-only endpoint state is a duplicate or control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-001`, where direct functional-graph inversion fails to provide a graph-specific single-target shortcut.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1474`, where a known-scalar orbit does not compress a noninvariant sparse deck or its source labels.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, where recursive addition transcripts do not compress exact source edges.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized serial-`S3` forward/backward state polynomials fail the complete five-term source boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the open requirement for a public source-fiber generator and transposed target join.

## Closest primary literature

- Krohn and Rhodes, [Algebraic theory of machines. I. Prime decomposition theorem for finite semigroups and machines](https://doi.org/10.1090/S0002-9947-1965-0188316-1), establishes prime/reset cascade decomposition, not sublinear faithful inversion of elliptic partial-sum states.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring point-decomposition equations but no cascade or source inverse.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/BFb0052236), supplies the generic-group comparison boundary.

These sources do not supply the claimed continuation-faithful quotient or source-word decoder. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta,m`, complete addition charts, source ordering, and deterministic observables.
2. Define the source-labelled partial-sum transformation semigroup without enumerating its full state graph.
3. Construct the prime/reset cascade and prove continuation faithfulness against exhaustive tiny instances.
4. For known-log targets `R=[r]P`, evaluate the endpoint cascade and invert every accepting state to exact signed factor-base tuples.
5. Verify every tuple by direct elliptic addition; retain `B+sigma` independent relation rows of rank `B`.
6. Solve factor-base logarithms and verify every point logarithm independently.
7. Apply the frozen cascade to fresh `Q+[t]P`, invert all ambiguity, substitute factor logs, remove `t`, and accept only `x` satisfying `[x]P=Q`.
8. Charge construction, retained state, transition work, failed endpoints, output, rank, linear algebra, descent, and verification against rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let advice/setup exponents be `a,a_m`; retained cascade construction and size exponent be `c`; complete target-query and working-memory exponents be `q,q_m`; inverse useful-row and target densities be `delta,delta_t`; source-output exponent be `o`; factor-log linear-algebra exponents be `ell,ell_m`; and ambiguity/final inversion exponent be `u`. Then the standardized complete exponents are

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

All state labels, wreath-product tables, inverse dictionaries, failed paths, and serialized output are included. Toy slopes remain heuristic and model-bound.

## Likely fatal obstruction

A cascade can reduce algebraic description without reducing faithful action degree. If two partial sums are merged, a continuation can distinguish them whenever one completes to the target and the other does not. For a generic prime-order translation action, this continuation congruence is expected to separate all `N` group states. Exact source inversion therefore restores an `N`-state action, an order-`N` orientation dictionary, or equivalent query work.

## Proof track

Construct the observables and semigroup; prove a sub-rho continuation-faithful congruence; give an implicit cascade algorithm and exact inverse; and prove `c,q,q_m,lambda,mu<=0.45` through full relation rank and blind descent.

## Disproof track

Prove that continuation equivalence separates every group state, that any faithful transformation representation has retained size `N^(1-o(1))`, or that source inversion requires an order-`N` dictionary; alternatively exhibit a merged-state false positive or false negative.

## Positive and negative controls

- Positive cascade control: a planted reset/prime automaton with a known logarithmic-depth cascade and exact word inverse.
- Positive correctness control: exhaustive partial-sum automata on tiny curves.
- Negative state control: the explicit `N`-state cyclic translation action.
- Mechanism control: ordinary DFA minimization and explicit ECFG/orbit directories.
- Leakage control: forbid scalar labels, target-trained quotients, discarded branches, and hidden transition tables.
- End-to-end control: matched rho and BSGS with the same targets and accounting.

## Quantitative promotion and falsification gates

A fresh successor requires zero continuation or source errors on every exhaustive fixture through 16-bit subgroup order, at least 1,000 verified relations and 100 blind descents at each of two largest toy sizes, upper 95% bounds `c,q,q_m<=0.20`, and complete `lambda,mu<=0.45`. Falsify the declared mechanism on one continuation collision, one missed or false source, retained state or inverse dictionary exponent at least `0.50`, or complete `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Prospective state theorem: `ideas/artifacts/ECDLP-IDEA-154/krohn_rhodes_state_lower_bound.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-154/fixtures.json`
- Prospective cascade builder: `ideas/artifacts/ECDLP-IDEA-154/cascade_builder.py`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-154/verify_sources.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-154/cost_analysis.md`

No contract, experiment, run, or prospective artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified mechanism evidence. All finite tests would be toy; every scaling claim is heuristic and model-bound. Cascade correctness or a valid relation would not establish a better-than-rho algorithm or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-154/krohn_rhodes_state_lower_bound.md` proving or refuting that continuation equivalence separates all generic prime-order partial-sum states, without implementing a scaling experiment.
