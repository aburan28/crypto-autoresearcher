# Pre-ID duplicate draft — Massalin superoptimized endpoint inverse

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q12`; no canonical ID allocated.
- Disposition: `merged_rejected_posthoc_program_synthesis`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a short synthesized program or passing test set is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, exhaustively synthesize a shortest public straight-line
program that maps an endpoint and restrictions to an exact signed five-source occurrence or
empty result. The target-independent program supports rank-complete factor logs and 100
fresh scalar-blind descents with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

The native operation enumerates instruction sequences, filters them on test vectors, and
checks semantic equivalence to a supplied reference function. It counts only if the reference
specification and equivalence checker are endpoint-only and cheaper than source search, the
program generalizes to all targets/strata, and its outputs replay occurrences. Synthesis
against labelled decompositions or a Query2P1 oracle is a control.

## Assumptions

1. A fixed public instruction set contains a subcap exact endpoint-to-source inverse.
2. Candidate enumeration, filtering, and complete equivalence checking fit the setup cap.
3. Tests and counterexamples are not derived from hidden scalar/source labels.
4. The selected program handles empty fibres, restrictions, signs, multiplicities, and exceptional strata.
5. One byte-identical program serves relations and 100 fresh masked targets without retraining.

## Semantic fingerprint

`public_endpoint_instruction_set | massalin_exhaustive_superoptimization | exact_source_inverse_program | signed_occurrence_output | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-c_C08_equality_saturation_source_egraph_preid_duplicate.md` — cost-based extraction is post-hoc unless source generation is charged.
2. `ideas/rejected/preallocation/20260722-c_P08_selinger_join_order_source_optimizer_preid_duplicate.md` — plan selection chooses among supplied source-bearing implementations.
3. `ideas/rejected/preallocation/20260721-e_M12_bfprt_pivot_source_selector_preid_duplicate.md` — selection cannot manufacture the endpoint/source predicate.
4. `ideas/deferred/ECDLP-IDEA-049_bounded_root_decomposition_transducer_hypothesis.md` — an exact source transducer needs a theorem-level public compiler.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Massalin, [Superoptimizer: A Look at the Smallest Program](https://doi.org/10.1145/36177.36194), enumerates short machine programs and uses probabilistic test filtering against a supplied function.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not a short endpoint-to-source reference implementation.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

Superoptimization is a distinct native synthesis operation, but it assumes a reference
semantics and equivalence tests. Supplying exact decompositions or post-hoc selection
reinstates the recorded obstruction; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, instruction set, length order, reference semantics, tests, equivalence checker, restrictions, strata, and verifier.
2. Enumerate and verify candidates within `B^(9/4+o(1))`; forbid source-labelled training tables, scalar residues, target fitting, and hidden decomposition calls.
3. For each known-log target, execute the frozen program, replay its signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging synthesis, rejected candidates, tests, equivalence proofs, outputs, and sparse linear algebra.
5. Reuse the identical program for 100 fresh `R=Q+[t]P`, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge instruction enumeration, program execution, all reference/equivalence queries, counterexamples, replay, rank, logs, bit complexity, code size, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, execution/query workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; synthesis and equivalence costs are
charged. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and
fresh work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

Superoptimization searches implementations of a supplied reference function; it does not
discover semantics without an oracle. Exact reference/equivalence checking is Query2P1 plus
signed source return, while finite tests permit overfitting and hidden scalar/source
selection. Exhaustive program enumeration also grows exponentially with length.

## Proof track

Prove endpoint-only reference/equivalence semantics, bounded complete synthesis, all-strata
generalization, signed output, and the full relation/log/descent path inside both caps.

## Disproof track

Expose labelled source tests, a Query2P1-equivalent reference/checker, an overfitting
counterexample, synthesis blowup, target retraining, lost replay, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied small reference function with a known four-instruction exact implementation.
- Negative: held-out endpoints, empty fibres, adversarial equivalent-on-tests programs, same output aggregate/different sources, and blind targets.
- Baselines: equality saturation, plan selection, BFPRT selection, IDEA-049, P1553 R4, rho, and BSGS.
- Short code or test agreement is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with a complete equivalence proof, zero errors at four sizes/all strata, bounded synthesis, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on a source-bearing reference/test, one held-out or replay error, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q12_reference_semantics_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q12_overfitting_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not superoptimization. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; a short program, equivalence pass, or relation is not a
breakthrough.

## Exactly one next executable action

1. Specify the reference semantics and complete equivalence checker and preserve the first Query2P1, signed-source, or labelled-training dependency.
