# ECDLP-IDEA-185 — Cartier–Foata heap Möbius source inversion

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_piece_identity_source_deck_scoped_negative`
- Cohort: `20260718-d`
- Evidence scale: primary-literature and semantic preflight only; no experiment ran
- Contract posture: no contract warranted after the labelled-piece reduction
- Scale labels: every prospective finite check is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a trace normal form, Möbius identity, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Signed factor-base additions admit a public dependence relation under which independent partial additions commute. The resulting Cartier–Foata trace monoid and heap poset have a canonical Möbius inverse that recovers every exact labelled source piece from the endpoint trace without enumerating words, enabling rank-complete relations and blind masked target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **elliptic partial-addition trace encoding, Cartier–Foata heap normalization, and heap-poset Möbius source inversion**. It is mechanism-new only if a public endpoint determines a compact heap whose pieces retain exact factor-base identities without a supplied source word. Normalizing an already labelled word, changing heap traversal, altering the declared commutations, or using an explicit large-prime/source alphabet is a control.

Semantic review found that a heap canonically represents the dependence order of a supplied trace; it does not invert an endpoint product to the missing trace. Commutation normal forms preserve causal order modulo independence but do not create point identities. Labelling pieces by factor-base points restores the required information only by materializing the original `B`-letter, arity-`m` source deck. This version is merged/rejected at that exact scoped boundary.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, signed-source arity, dependence relation, masks, and verifier are frozen.
2. A scalar-blind target-uniform compiler maps every endpoint to a finite trace/heap without knowing a source word.
3. Declared commutations preserve elliptic addition and every exceptional stratum, repetition, sign, and multiplicity.
4. Heap Möbius inversion returns every exact labelled factor-base piece and tuple with neither a word oracle nor a source table.
5. Alphabet construction, dependence tests, heap storage, Möbius evaluation, output, rank, descent, verification, time, and memory are charged.

## Semantic fingerprint

`endpoint_to_elliptic_trace_monoid | Cartier_Foata_heap_normal_form | heap_Mobius_exact_piece_inversion | no_labelled_source_word | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where lossless ancestry retains source-distinct edges.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the charged provenance-state control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge materialization boundary.
4. `inputs/ledger_inventory.json` — imported `P1477`, the nearest serial/canonical transition representation.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.

## Closest primary literature

- Cartier and Foata, [Problèmes combinatoires de commutation et réarrangements](https://doi.org/10.1007/BFb0079468), establish trace-monoid normal forms and Möbius methods for words modulo declared commutations.
- Viennot, [Heaps of pieces I: Basic definitions and combinatorial lemmas](https://doi.org/10.1111/j.1749-6632.1989.tb16436.x), develops the heap representation of partially commutative structures.

These sources begin with labelled pieces or a supplied trace. Neither gives an elliptic endpoint-to-labelled-heap inverse or a complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta`, the piece alphabet, dependence relation, heap convention, arity, signs, masks, and an independent verifier.
2. Compile every known-log endpoint `R_j=[r_j]P` into the same scalar-blind trace/heap representation without using `r_j` or a source word.
3. Apply Cartier–Foata normalization and heap Möbius inversion to emit all exact signed factor-base source tuples and multiplicities.
4. Verify point membership and elliptic sum; preserve commutation classes, repeated pieces, infinity, collisions, misses, false tuples, and all output heaps.
5. Collect at least `B+sigma` independently verified rows of rank `B`, solve factor-base logarithms, and verify each recovered logarithm by scalar multiplication.
6. Apply the identical endpoint compiler and heap inversion to fresh masked targets `Q+[t]P`.
7. Substitute verified factor logs, remove masks, retain all ambiguity candidates, and accept only `x` satisfying `[x]P=Q`.
8. Charge alphabet and dependence setup, normal forms, all heap nodes and source labels, Möbius work, failed trials, output, rank, linear algebra, descent, verification, time, and peak bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let alphabet, dependence, and heap-compiler setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one normal-form/Möbius query cost `N^q,N^q_m`; emitted heaps/tuples and target ambiguity be `N^o,N^u`; and factor-log linear algebra cost `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All alphabet labels, dependence edges, heap nodes, Möbius intervals, word branches, output tuples, failed endpoints, and target ambiguity are charged.

## Likely fatal obstruction

Cartier–Foata normalization selects a canonical representative only after the labelled trace is known. The dependence poset preserves which supplied pieces may commute, not which factor-base points produced a bare elliptic endpoint. Erasing labels merges different same-sum tuples; restoring exact labels gives a `B`-piece alphabet and potentially `B^m` heaps. Exact composable endpoint labels cannot be both source-separating and compact without assuming the missing source inversion.

## Proof track

Define a compact target-uniform endpoint heap, prove its Möbius inverse is source-biconditional for all signs and exceptional strata without a labelled-word oracle, and establish complete rank and blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Find two distinct source traces mapping to the same unlabelled heap, show exact piece labels require an explicit source word or `B^m` heap family, find one dependence-induced missed multiplicity, or prove either complete exponent at least `0.5`.

## Positive and negative controls

- Positive: finite trace monoids with a supplied labelled word and independently checked Cartier–Foata normal form.
- Positive: exhaustive toy elliptic source words deliberately provided to the heap builder.
- Negative: erase the point labels while preserving the dependence order; same-shape heaps must fail exact source recovery.
- Negative: explicit source-word dictionaries, alphabet refinements, post-hoc selectors, solver substitutions, rho, BSGS, known-log leakage, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected at compact endpoint-to-labelled-heap compilation. A successor under a new ID requires 100% source/multiplicity recall, zero false tuples, no supplied word or explicit/implicit `B^m` heap family, verified rank `B`, successful blind masked descent, and formal `lambda,mu<=0.45`. Values in `(0.45,0.50)` are inconclusive; one lost identity, hidden source alphabet/deck, or either exponent at least `0.50` falsifies the scoped successor. A canonical heap or valid relation alone has no promotion value.

## Artifact plan

- Endpoint trace and dependence specification: `ideas/artifacts/ECDLP-IDEA-185/elliptic_trace_spec.md`
- Label/source lower-bound audit: `ideas/artifacts/ECDLP-IDEA-185/heap_label_inversion_audit.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-185/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-185/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-185/cost_analysis.md`

All paths are prospective. No artifact directory, contract, or run exists.

## Interpretation boundary

This is a novelty-unverified conservative scoped negative. Any future finite evidence is toy, and all cost projections remain heuristic and model-bound. The result rejects only the unsupplied labelled-source inverse; it does not reject heap combinatorics and does not claim a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-185/heap_label_inversion_audit.md` proving or refuting that a public endpoint can determine a source-biconditional labelled Cartier–Foata heap without receiving or enumerating a factor-base word.
