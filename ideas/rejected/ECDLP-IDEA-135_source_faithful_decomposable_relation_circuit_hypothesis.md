# ECDLP-IDEA-135 — Source-faithful decomposable relation circuit

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_knowledge_compilation_state_quotient`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: retired `review_required` draft; unapproved; zero runs permitted
- Scale labels: all prospective measurements are `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a compact circuit, exact model count, valid source tuple, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The exact Boolean relation over five source-index blocks and a public target has a deterministic decomposable negation-normal-form representation whose target-independent compiler and target-conditioned circuit both have time, size, and peak-memory exponent below rho. The circuit supports polynomial-delay enumeration of every signed factor-base tuple and conditioning for blind descent, without first materializing source leaves, serial-`S3` states, or a dense quotient.

## Mechanism-new operation

The proposed operation is **pre-leaf source-faithful knowledge compilation**. Encode each factor index in binary, compile curve membership and complete elliptic addition directly into a structured d-DNNF/SDD whose decomposable conjunctions split source blocks and whose deterministic disjunctions preserve exact provenance. Unlike P1510 product circuits, the compiled object must be built before `Theta(B^3)` leaf emission; unlike a count/certificate, it must enumerate every accepted tuple and survive target conditioning.

An OBDD ordering change, distributed generic compiler, SAT backend, approximate d-DNNF, post-hoc witness annotation, or a circuit built from enumerated satisfying assignments is a duplicate/control.

Rejected IDEA-117 starts from an explicit P1510 provenance grammar with `Theta(B^3)` leaves, whereas this hypothesis requires a structured circuit compiled directly from the compact elliptic equations before any source leaf exists. IDEA-120 quotients serial states by endpoint language and loses provenance; this circuit must instead remain biconditional with every source assignment. Any compiler that consumes IDEA-117 leaves or collapses to IDEA-120 membership is a merge, not a survivor.

Independent review rejects even that distinction: IDEA-120 already defines completion-and-provenance equivalence, requires exact source backtracking, forbids construction from dense states, and explicitly lists off-the-shelf knowledge compilation and BDD changes as controls. Replacing its canonical quotient by structured d-DNNF/SDD terminology changes the representation/backend, not the missing pre-leaf algebraic congruence.

## Assumptions

1. `E/F_p`, `<P>`, `N`, `Q`, and target-independent signed `F` of size `B=N^beta` are public; the primary relation arity is five.
2. One frozen vtree/decomposition is scalar-blind and uniform over the declared curve family.
3. Compilation starts from compact complete projective addition and factor-membership circuits, not from satisfying tuples, source tables, P1510 leaves, or quotient bases.
4. The target-conditioned circuit is biconditional with every ordered/signed source tuple, including repeats, infinity, denominators, and multiplicity.
5. Circuit construction, serialization, conditioning, enumeration, verification, rank, factor logs, blind descent, ambiguity, and bit memory are charged.

## Semantic fingerprint

`binary_factor_indices | pre_leaf_structured_dDNNF | deterministic_decomposable_source_blocks | exact_model_to_tuple_biconditional | target_conditioning | polynomial_delay_blind_descent`

The unique gate is source-complete compilation from compact equations before leaf expansion. Knowledge compilation after enumeration, membership-only circuits, generic SAT, or provenance decoration is not new.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the public source-fiber/transposed-join question that a pre-leaf circuit would answer if source complete.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`, where a compact pair-membership polynomial with all translations retains the ordinary translated-circuit cost boundary.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized serial-`S3` forward/backward states fail the `B^(3/2)` gate; a pre-leaf compiler must remove rather than serialize them.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose compact one-transition norm densifies on composition; the circuit must preserve composition without that dense object.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where a frozen bit-vector serial-`S3` solver times out at the first cell; changing only the SAT/SMT/knowledge-compilation backend is a control.

## Closest primary literature

- Darwiche, [Decomposable negation normal form](https://doi.org/10.1145/502090.502091), establishes tractable operations on DNNF but no compact elliptic relation compiler.
- Pipatsrisawat and Darwiche, [A Lower Bound on the Size of Decomposable Negation Normal Form](https://doi.org/10.1609/aaai.v24i1.7600), relate structured decompositions to width/rectangle obstructions.
- de Colnet and Mengel, [Lower Bounds for Approximate Knowledge Compilation](https://arxiv.org/abs/2011.13721), show that allowing approximation does not generally evade representation blowups; approximation is invalid for exact ECDLP sources here.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring compact relation equations, not the required compilation theorem.

No checked source constructs or lower-bounds this exact source-complete family. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, subgroup, factor base, bit encodings, complete exceptional-case semantics, vtree, compiler, and independent enumerator/verifier.
2. Compile the target-independent portion from public equations and serialize it without enumerated source tuples or target fibers.
3. Condition on each known-log target `R_j`, enumerate every model with polynomial delay, decode it to signed factor points, and verify direct elliptic addition.
4. Retain `B+sigma` independently verified rows of rank `B`, solve factor logs, and verify each point logarithm.
5. Condition the same frozen representation on fresh `Q+[t]P`, enumerate complete sources and ambiguity, subtract `t`, and accept only `[x]P=Q`.
6. Charge compiler setup, target specialization, circuit bytes, enumeration delay/output, rank, linear algebra, descent, and peak memory against rho and BSGS.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time with constant state; BSGS is `N^(1/2+o(1))` time and memory. Let compiler time/memory be `N^a,N^a_m`; serialized target-independent size `N^c`; target specialization/query time and working memory be `N^q,N^q_m`; inverse row/target density `N^delta,N^delta_t`; per-row source-output exponent `o`; ambiguity `u`; and factor-log linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

The circuit node count, edge count, compile work, target copies, models, and decoding are all charged. A tiny stored circuit with exponential compile work fails. Toy node-count slopes are model-bound.

## Likely fatal obstruction

Deterministic decomposable circuits are unions of source-block rectangles. For generic fixed-target addition, many partial assignments have different continuation sets; exact provenance may therefore force a large rectangle cover or vtree width, echoing P1477 and Myhill–Nerode source-state growth. Compiling from the compact equation can cost as much as enumerating models even when the final circuit is small. No current theorem gives a sub-rho circuit or proves the necessary lower bound for this exact family.

## Proof track

Construct one explicit uniform vtree and compiler; prove circuit/model biconditionality, polynomial-delay exact decoding, and `a,a_m,c,q,ell,ell_m` bounds giving `lambda,mu<=0.45`. The proof must explain why the relation communication matrix has a small deterministic rectangle decomposition without scalar indices.

## Disproof track

Prove a structured d-DNNF/SDD size or compilation lower bound at least `N^(1/2-o(1))`; show that target conditioning creates source-distinct continuation classes requiring P1477-scale state; or exhibit any missed tuple, leaf-materialization dependency, hidden source advice, or complete exponent at least `1/2`.

## Positive and negative controls

- **Positive control:** bounded-treewidth CSPs and planted decomposable source families with independently enumerated model sets.
- **Positive control:** exhaustive tiny elliptic fibers, including signs, repeats, infinity, and denominator strata.
- **Negative control:** shuffled random group tables matched for model count and source-block sizes.
- **Negative control:** OBDD order sweeps, P1480 bit-vector solving, P1477 explicit states, P1510 leaf circuits, and post-hoc tuple annotation.
- **End-to-end control:** matched rho/BSGS, known-log relations, and blind targets with independent scalar verification.

## Quantitative promotion and falsification gates

The present lane is rejected as IDEA-120's knowledge-compilation representation. A fresh ID requires a mathematical operation outside the canonical completion/provenance quotient and complete `lambda,mu<=0.45` with exact source enumeration. Falsify on one source mismatch, pre-enumerated leaf input, nondeterministic overlap without multiplicity handling, hidden scalar coordinate, or a complete time or memory exponent at least `0.5`.

## Artifact plan

- Knowledge-compilation/IDEA-120 merge audit: `ideas/artifacts/ECDLP-IDEA-135/source_faithful_dDNNF_theorem.md`
- Frozen formula fixtures: `ideas/artifacts/ECDLP-IDEA-135/fixtures.json`
- Prospective compiler: `ideas/artifacts/ECDLP-IDEA-135/compile_relation.py`
- Independent model/source verifier: `ideas/artifacts/ECDLP-IDEA-135/verify_models.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-135/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-135_source_faithful_decomposable_relation_circuit_preflight.yaml`

No successor artifact or run exists; only the retired `review_required` contract exists.

## Interpretation boundary

This is rejected, novelty-unverified representation evidence. All finite results would be toy; extrapolations remain heuristic and model-bound. Compactness or correct model enumeration alone is not evidence of a below-rho ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-135/source_faithful_dDNNF_theorem.md` mapping every claimed d-DNNF operation to IDEA-120's completion/provenance quotient and recording the merge without compiling a circuit.
