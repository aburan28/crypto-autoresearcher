# Pre-ID duplicate draft — Massey shift-register source syndrome

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U04`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_syndrome_sequence_and_recurrence_decoder`.
- Class/risk/lane: algorithm / high-risk / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a shortest LFSR or locator recurrence is not an ECDLP break.

## Falsifiable hypothesis

Endpoint evaluations produce a short exact syndrome sequence whose shortest feedback register has
roots labelling the signed factor-base occurrences of a relation. Berlekamp–Massey recovery would
open sources, support full rank/logs and blind descent, and keep both exponents at most `0.45`.

## Mechanism-new operation

The native operation synthesizes the shortest linear feedback shift register for a supplied finite
sequence. ECDLP mechanism credit requires an endpoint-only syndrome sampler and a recurrence-root
to exact occurrence inverse. Applying Berlekamp–Massey to an already materialized source moment
sequence repeats IDEA-006/053/078.

## Assumptions

1. Public endpoints yield exact source-sensitive syndromes without enumerating sources.
2. Linear complexity is uniformly small for relations and masked targets.
3. Register roots resolve signs, repetitions, ordering, and exceptional strata.
4. Sampling, synthesis, factoring, replay, rank, factor logs, and descent satisfy both caps.
5. No factor logs or target-specific training enter the syndrome rule.

## Semantic fingerprint

`public_endpoint_syndrome_samples | Berlekamp_Massey_shortest_register | locator_roots | exact_signed_occurrence_lift | full_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md` — short recurrence owner.
2. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — moments plus Prony-style source decoding.
3. `ideas/rejected/ECDLP-IDEA-078_sparse_source_enumerator_interpolation_hypothesis.md` — supplied black-box sequence/evaluator boundary.
4. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — endpoint syndrome construction is already the missing operation.
5. `ideas/rejected/ECDLP-IDEA-070_p_kernel_reverse_automaton_hypothesis.md` — finite-state recurrence does not orient the hidden scalar/source.

## Closest primary literature

- Massey, [Shift-register synthesis and BCH decoding](https://doi.org/10.1109/TIT.1969.1054260), synthesizes a shortest register from a supplied sequence.
- Wiedemann, [sparse finite-field equations](https://doi.org/10.1109/TIT.1986.1057137), similarly derives recurrences from supplied matvec sequences.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide a short source syndrome.

No checked source supplies endpoint-only syndromes or exact occurrence roots; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, syndrome sampler, sequence length, decks, restrictions, masks, and verifier.
- Build reusable state under `B^(9/4+o(1))` without source moments, factor logs, dense resultants, or target fitting.
- Charge every syndrome sample, register update, discrepancy, factor/root, ambiguity branch, and signed replay.
- Verify at least `max(d_FB+32,1000)` independent rows, rank `d_FB`, and all factor-base logs.
- Apply identical state/rule to 100 fresh `Q+[t]P` targets, subtract masks, and verify every scalar.
- Include density, failure, output, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, syndrome/synthesis/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and log solve `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`. Rho/BSGS are `0.50`.

## Likely fatal obstruction

Berlekamp–Massey begins after a source-sensitive sequence exists. Exact syndromes already aggregate
the hidden occurrences; constructing them costs source search, while aggregate sequences can remain
unchanged across distinct signed fibres. A recurrence describes the aggregate, not a canonical
elliptic source history.

## Proof track

Prove a public short-syndrome theorem, restriction-stable linear complexity, injective all-strata
root lift, full rank/log/descent, and complete sub-rho costs.

## Disproof track

Hold the sequence and register fixed while varying sources, expose source-enumerator work in one
sample, or show generic linear complexity/source replay or total exponent reaches `0.50`.

## Positive and negative controls

- Positive: planted BCH/linear-recurrence sequences with known locators.
- Negative: equal-syndrome different-source fibres, dense random sequences, repeated/tangent/infinity cases, shuffled labels, and fresh targets.
- Baselines: IDEAs 006/014/053/078, P1553 R4, rho, and BSGS.
- Correct register synthesis or one locator relation is not promotion.

## Quantitative promotion and falsification gates

- Promote only with exact sampler/lift theorems, zero errors, failure at most `2^-80`, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-derived sample, equal-sequence source collision, unbounded linear complexity, false/missed occurrence, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u04_syndrome_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u04_equal_sequence_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u04_linear_complexity_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Berlekamp–Massey. Correct recurrence recovery, a locator, or a
valid row remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Compute exact endpoint moment sequences for the smallest exhaustive toy fibres and search for equal sequences with different signed source supports.
