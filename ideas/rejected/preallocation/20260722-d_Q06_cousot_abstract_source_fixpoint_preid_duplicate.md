# Pre-ID duplicate draft — Cousot abstract source fixpoint

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q06`; no canonical ID allocated.
- Disposition: `merged_rejected_approximate_source_semantics`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a sound invariant or fixpoint is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, define an abstract domain for partial signed sums whose
least fixpoint is exact on empty versus nonempty restricted target fibres and carries enough
trace information to replay one occurrence. The target-independent abstract semantics
supports rank-complete relations and 100 fresh masked descents with complete exponents at
most `0.45`.

## Mechanism-new operation

The native operation maps concrete semantics into a lattice of abstract states and computes
sound fixpoints, possibly with widening/narrowing. It counts only if the abstraction is
endpoint-derived, exact for rare existence on every restriction, and has a charged
concretization to signed occurrences. A sound overapproximation followed by exact source
checking is a control.

## Assumptions

1. A finite public abstract domain has subcap height/width and target-uniform transformers.
2. Abstraction and transfer functions do not enumerate concrete factor-base tuples.
3. The abstract zero/nonzero predicate is biconditional, not merely sound, for all restrictions.
4. Widening loses no rare target fibre and retained traces concretize to signed occurrences.
5. Byte-identical abstract state serves relation targets and fresh masked targets.

## Semantic fingerprint

`public_endpoint_abstract_domain | cousot_fixpoint_transformers | exact_restricted_nonemptiness | trace_concretization_signed_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — abstraction needs the missing exact concrete checker.
2. `ideas/rejected/ECDLP-IDEA-146_weak_near_unanimity_bounded_width_descent_hypothesis.md` — bounded-width local consistency needs an exact global source theorem.
3. `ideas/rejected/ECDLP-IDEA-378_comprehensive_groebner_target_atlas_hypothesis.md` — a target atlas can materialize source-solving state.
4. `ideas/rejected/preallocation/20260721-b_J11_adaboost_endpoint_weak_oracle_preid_duplicate.md` — approximate amplification cannot certify exact rare support.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Cousot and Cousot, [Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints](https://doi.org/10.1145/512950.512973), computes sound abstract fixpoints that may deliberately lose concrete detail.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), provides concrete equations but not an exact small abstract domain.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic cost control.

Abstract interpretation is a distinct native framework, but sound overapproximation is not
the exact existence-and-replay operation required here. No exact elliptic abstract domain is
known from these sources; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, concrete semantics, abstract lattice, Galois connection, transformers, widening, restrictions, traces, strata, and verifier.
2. Build target-independent abstract state within `B^(9/4+o(1))`; forbid tuple enumeration, scalar residues, target fitting, and hidden decomposition calls.
3. For each known-log target, compute the restricted fixpoint, concretize one trace to signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging domain construction, iterations, widening/narrowing, traces, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge every abstract element/transformer application, failed/concrete check, fixpoint iteration, trace, restriction update, rank, log, bit operation, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, fixpoint query/workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; all refinement and concretization are
charged. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and
fresh work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

Useful abstract domains merge concrete states, so a rare nonempty fibre and an empty fibre
can share one abstract element. Restoring biconditional existence and occurrence replay
requires source-specific predicates or a concrete Query2P1 check. An exact domain can grow
to the concrete source state, eliminating the claimed compression.

## Proof track

Prove a finite endpoint-only domain with exact restricted nonemptiness, subcap fixpoint
convergence, trace concretization, and complete relation/log/descent costs.

## Disproof track

Exhibit empty/nonempty abstract collision, a widening loss, source-specific predicates,
concrete checking, source-sized height/width, lost replay, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy transition system whose chosen abstract domain is exact and trace-labelled.
- Negative: rare singleton fibres, empty fibres sharing intervals, widening/narrowing mutations, same abstract state/different sources, and blind targets.
- Baselines: CEGAR, bounded-width consistency, P1553 R4, rho, and BSGS.
- Soundness or convergence is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact abstraction at four sizes/all strata, proved domain/iteration caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one empty/nonempty collision, concrete/source-specific checker, replay loss, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q06_galois_connection_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q06_empty_nonempty_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q06_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not abstract interpretation. All evidence is toy, heuristic,
model-bound, and novelty-unverified; a sound fixpoint or valid trace is not a breakthrough.

## Exactly one next executable action

1. Construct the smallest proposed abstract domain on paper and preserve the first empty/nonempty collision or prove exact restricted concretization within both caps.
