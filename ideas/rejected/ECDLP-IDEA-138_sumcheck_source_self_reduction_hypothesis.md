# ECDLP-IDEA-138 — Sum-check source self-reduction

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `rejected_relation_certificate_dense_prover`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: prospective tests are `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a verified sum, accepted proof, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Arithmetize the five-source relation predicate and use recursive sum-check/GKR reductions not only to certify a nonzero relation count but to condition coordinates and extract one exact source tuple with sub-rho total prover, verifier, transcript, and self-reduction cost. Repeating the operation yields rank and blind descent.

## Mechanism-new operation

The proposed operation is **witness-extracting interactive sum-check with source conditioning**. A transcript would recursively fix source-index bits while maintaining a certified nonzero conditional sum, returning an exact tuple rather than only a count.

The semantic audit rejects it. Sum-check reduces verifier work but the prover normally evaluates the full multilinear sum/circuit; no prover shortcut or witness-generating identity is specified. A transcript certifying a supplied computation is a relation/count certificate, and bit-by-bit conditioning repeats the missing source oracle. Changing proof systems, commitments, or Fiat–Shamir does not remove source generation.

## Assumptions

1. Public `E,<P>,N,Q,F`, `B=N^beta`, exact projective relation predicate, and source-index bit encodings are frozen.
2. Prover work and memory, not only verifier time, are below rho and use no enumerated witness table.
3. Conditional sums are exact over a field large enough to prevent cancellation and decode signs/multiplicity.
4. Every transcript yields an independently verified source tuple and the same procedure handles blind targets.
5. Proof generation, repetitions, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`multilinear_relation_predicate | sumcheck_GKR_transcript | nonzero_conditional_sum | bitwise_source_self_reduction | exact_tuple_extraction | full_prover_cost`

Only a genuinely sub-rho prover that generates sources would be new. Succinct verification or a relation-only proof is the rejected control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H680`, which requires a source-resolving circuit, not a verifier for a supplied computation.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the complete source-query exponent boundary the prover must meet.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where compact transition evaluation does not give cheap composed sources.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, a solver-backend control that fails without a source-specific operation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`, where an exact output-sensitive zero tree still pays to construct all leaves.

## Closest primary literature

- Lund, Fortnow, Karloff, and Nisan, [Algebraic methods for interactive proof systems](https://doi.org/10.1145/146585.146605), introduce sum-check-style verification; they do not reduce honest prover enumeration for this relation.
- Goldwasser, Kalai, and Rothblum, [Delegating computation: interactive proofs for muggles](https://doi.org/10.1145/1374376.1374396), reduce verifier work for layered circuits while retaining prover work tied to circuit evaluation.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the relation polynomial but no witness-extracting prover shortcut.

No checked source gives the required source-generating prover. Novelty remains unverified, while the stated verification-only mechanism is occupied.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, arithmetization, random coins, transcript policy, complete source semantics, and independent verifier.
2. For known-log targets, generate a proof of a nonzero exact relation sum without enumerating the source domain.
3. Recursively condition source bits, prove each retained conditional sum, decode one or all signed tuples, and verify elliptic addition.
4. Repeat until `B+sigma` rank-`B` rows exist; solve and verify factor logs.
5. Apply identical conditioning to fresh masked targets, substitute logs, enumerate ambiguity, and accept only `[x]P=Q`.
6. Charge honest prover, transcript, verifier, source output, rank, linear algebra, descent, and peak memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let arithmetization/setup be `N^a`; honest prover time/memory `N^p,N^p_m`; conditional-round time and working memory `N^q,N^q_m`; source output `N^o`; inverse densities `N^delta,N^delta_t`; ambiguity `u`; and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+p+q+o,ell,delta_t+p+q+o+u,beta)`

`mu=max(p_m,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Verifier polylogarithmic cost cannot replace `p`. Every repeated proof and conditional branch is charged. Toy verifier timings are model-bound.

## Likely fatal obstruction

Interactive proofs certify work; they do not perform it. The honest prover must evaluate the relation sum or possess an equivalent witness-generating representation. Exact rare-event conditioning can multiply prover work by source bits/branches, and cancellations can certify a count without exposing ancestry. Thus the proposal shifts the dense computation to the prover and returns a certificate, one of the corpus's explicit duplicate classes.

## Proof track

Derive an elliptic-specific sum-check prover whose total work constructs conditional sums and exact sources with complete `lambda,mu<=0.45`, independent of a precomputed witness or dense table.

## Disproof track

Show the prover evaluates the full domain/circuit, consumes a witness table, or that transcript self-reduction is identical to source search. Any relation-only output or `lambda>=1/2`/`mu>=1/2` closes the stated mechanism.

## Positive and negative controls

- **Positive control:** low-degree sums with sparse supplied multilinear tables and planted witnesses.
- **Positive control:** exhaustive tiny elliptic relations with independent source enumeration.
- **Negative control:** standard sum-check/GKR with full honest-prover accounting, proof-only certificates, and random predicates matched for support.
- **Negative control:** bitwise conditioning with and without source tables.
- **End-to-end control:** rho/BSGS and blind targets under identical total-work accounting.

## Quantitative promotion and falsification gates

This record is rejected because no sub-rho source-generating prover is specified. A successor requires a new elliptic algebraic identity and independently proved complete `lambda,mu<=0.45`. Falsify on omitted prover work, witness advice, relation-only output, one missed source, or complete exponent at least `0.5`.

## Artifact plan

- Prover-cost reduction: `ideas/artifacts/ECDLP-IDEA-138/dense_prover_reduction.md`
- Prospective source-sum identity: `ideas/artifacts/ECDLP-IDEA-138/source_sumcheck_identity.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-138/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-138/cost_analysis.md`

No artifact or run exists.

## Interpretation boundary

This is preserved rejected evidence. All novelty claims are unverified, tests would be toy, and costs are heuristic/model-bound. Efficient verification is not efficient source generation and cannot establish an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-138/dense_prover_reduction.md` mapping every proposed sum-check message to the charged relation-domain evaluations or witness advice it requires.
