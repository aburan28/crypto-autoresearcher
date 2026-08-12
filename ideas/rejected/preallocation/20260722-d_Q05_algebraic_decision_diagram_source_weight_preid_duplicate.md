# Pre-ID duplicate draft — algebraic-decision-diagram source weight

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q05`; no canonical ID allocated.
- Disposition: `merged_rejected_weighted_decision_diagram_aggregate`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an exact weighted aggregate or compact diagram is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, compile an algebraic decision diagram whose terminals encode
exact signed occurrence counts or provenance weights for restricted five-source relations.
Diagram operations decide nonzero fibres and unrank actual occurrences for rank-complete
relations and 100 fresh masked targets with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation extends ordered decision diagrams with values in a finite algebra and
combines them by Shannon-style apply operations. It counts only if endpoint data construct
the weighted terminal function without source enumeration and if nonzero weights retain an
exact inverse to individual signed occurrences. Aggregating a supplied source table is a
control.

## Assumptions

1. The weighted relation function has a public target-independent variable order and subcap ADD.
2. Terminal weights are constructed without Query2P1 probes or enumerated source tuples.
3. Cancellation cannot map a nonempty fibre to zero or merge distinct signed occurrences irreversibly.
4. Restrictions and fresh targets update the same diagram inside the online cap.
5. A nonzero terminal supports charged exact occurrence replay on every exceptional stratum.

## Semantic fingerprint

`public_endpoint_weight_function | algebraic_decision_diagram_apply | exact_restricted_nonzero | terminal_to_signed_occurrence_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-b_B06_robdd_shannon_source_compiler_preid_duplicate.md` — Boolean terminals require the supplied exact predicate.
2. `ideas/rejected/preallocation/20260719-a_A04_zero_suppressed_decision_source_compiler_preid_duplicate.md` — a decision diagram compiles an already defined source family.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — aggregate circuits need source-faithful leaves and inverse provenance.
4. `ideas/rejected/preallocation/20260721-c_K09_ams_moment_source_sketch_preid_duplicate.md` — weighted moments lose rare support and occurrence identity.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Bahar et al., [Algebraic Decision Diagrams and Their Applications](https://doi.org/10.1109/ICCAD.1993.580054), represents supplied finite-valued functions with decision diagrams.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies relation equations but not a compact weighted terminal compiler.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The finite-valued diagram is native-scope distinct, but the ECDLP transplant is an
ROBDD/aggregate-circuit merge unless it constructs and inverts exact weights from endpoints.
Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, variables/order, terminal algebra, apply rules, restrictions, cancellation convention, strata, replay, and verifier.
2. Build the endpoint-only ADD within `B^(9/4+o(1))`; forbid truth tables, source tuples, scalar residues, target fitting, and hidden decomposition calls.
3. For each known-log target, restrict and evaluate the diagram, invert one nonzero terminal to signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging compilation, apply, terminals, cancellation handling, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge function construction, all nodes/edges/terminal values, restrictions, misses, inverse output, rank, logs, bit complexity, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, ADD query/workspace `N^q,N^q_m`, rank credit `N^r`, output
`N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; terminal arithmetic and cancelled
occurrences remain charged. Promotion requires `lambda,mu<=0.45`, setup/state
`<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain
exponent-`0.50` controls.

## Likely fatal obstruction

An ADD compresses a supplied finite-valued function. Computing exact occurrence counts or
provenance weights is already relation enumeration/Query2P1, while smaller aggregate
weights admit cancellation and same-weight/different-source ambiguity. Generic target
functions can have exponential diagrams and fresh targets can require rebuilding.

## Proof track

Prove endpoint-only terminal construction, target-uniform diagram size, cancellation-free
nonzero semantics, restriction-stable signed inversion, and complete relation/log/descent
costs inside both caps.

## Disproof track

Expose source enumeration or exact membership in terminal construction, one cancellation or
same-weight ambiguity, diagram blowup/rebuild, lost replay, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy weighted function with one planted uniquely labelled terminal.
- Negative: equal aggregate/different sources, cancelling signed pairs, empty restrictions, hard variable orders, and blind targets.
- Baselines: ROBDD, ZDD, AMS, source-faithful circuits, P1553 R4, rho, and BSGS.
- An exact aggregate is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact cancellation-safe semantics at four sizes/all strata, a proved node cap, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on a supplied weight table, one ambiguity/cancellation/replay error, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q05_terminal_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q05_cancellation_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q05_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not ADDs. All evidence remains toy, heuristic, model-bound,
and novelty-unverified; an exact weight or valid relation is not a breakthrough.

## Exactly one next executable action

1. Specify one terminal-weight constructor from public endpoints and either prove a cancellation-free signed inverse inside both caps or preserve its first source-enumeration dependency.
