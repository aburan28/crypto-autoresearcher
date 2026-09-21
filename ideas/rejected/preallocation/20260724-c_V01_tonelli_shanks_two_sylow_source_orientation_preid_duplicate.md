# Pre-ID duplicate draft — Tonelli–Shanks two-Sylow source orientation

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V01`; no canonical ID allocated.
- Disposition: `merged_rejected_finite_field_root_oracle_and_noncanonical_sign_lift`.
- Class/risk/lane: algorithm / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a correct modular root or valid elliptic relation is not an ECDLP break.

## Falsifiable hypothesis

For each public summation-polynomial endpoint, the two-Sylow descent used by
Tonelli–Shanks canonically orients every quadratic branch and returns exact signed
factor-base occurrences. The oriented roots would yield full-rank relations and 100
fresh blind descents with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

The native operation repeatedly lowers the order of a supplied quadratic residue in
the two-primary subgroup of `F_p^*` until it exposes a square root. It is ECDLP-new
only if endpoint equations alone supply all required residues and the root branch
canonically lifts to point labels, signs, repetitions, and exceptional strata.

## Assumptions

1. Every restricted endpoint fibre is encoded by boundedly many public quadratic residues.
2. The two-Sylow transcript distinguishes empty, singleton, and multiple signed source fibres.
3. Root signs lift canonically to elliptic point signs without scalar or source advice.
4. Residue construction, root extraction, replay, rank, factor logs, and descent meet both caps.
5. Frozen preprocessing is target-independent and contains neither source tables nor factor logs.

## Semantic fingerprint

`public_endpoint_residues | two_Sylow_order_descent | canonical_modular_roots | exact_signed_point_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/deferred/ECDLP-IDEA-049_bounded_root_decomposition_transducer_hypothesis.md` — root branches help only with a complete noncircular source transducer.
2. `ideas/rejected/ECDLP-IDEA-051_hash_restricted_frobenius_isolation_descent_hypothesis.md` — restricted root isolation does not supply occurrence labels.
3. `ideas/rejected/ECDLP-IDEA-020_cartier_differential_syndrome_descent_hypothesis.md` — Frobenius/order data preserve aggregates rather than sources.
4. `ideas/ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md` — x-only relations still require an exact all-sign lift.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — subset-stable exact source return remains the live gate.

## Closest primary literature

- Shanks, *Five number-theoretic algorithms* (1973), introduces the RESSOL order-descent method; Schlage-Puchta, [On Shanks' algorithm](https://arxiv.org/abs/1105.1456), analyzes the supplied-residue algorithm.
- Adleman, Manders, and Miller, [On taking roots in finite fields](https://doi.org/10.1109/SFCS.1977.18), treats root extraction from supplied field elements.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a canonical signed root-to-source lift.

No checked source constructs the required generic-prime endpoint-to-occurrence interface. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed factor decks, residue compiler, nonresidue policy, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))` without source tuples, dense resultants, target advice, or factor logs.
- Charge every residue construction, order query, root branch, exceptional fibre, signed occurrence replay, and failed restriction.
- Collect at least `max(d_FB+32,1000)` independently verified rows, require rank `d_FB`, and solve every factor-base logarithm.
- Reuse byte-identical state on 100 fresh `Q+[t]P` targets, return signed tuples, subtract masks, and verify `[x]P=Q`.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal relation and target
densities `N^delta,N^delta_t`; root/replay work and workspace `N^q,N^q_m`;
rank credit `N^r`; output `N^o`; ambiguity/failure `N^u`; and factor-log costs
`N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho and BSGS remain exponent `0.50`.

## Likely fatal obstruction

Tonelli–Shanks opens a supplied residue; it does not compile the residue from the
endpoint fibre. The two roots differ only by field sign, while x-only elliptic
representations already quotient point sign. Different exact source fibres can give
the same residue and order transcript, so canonical replay restores the missing
Query2P1/source oracle.

## Proof track

Prove an endpoint-only residue compiler, restriction-uniform empty-fibre semantics,
injective all-strata root-to-occurrence lifting, full rank/log recovery, blind
descent, and both complete cost caps.

## Disproof track

Exhibit equal residue/order transcripts with different signed fibres, one
source-derived residue, one unresolved point-sign branch, or complete exponent at
least `0.50`.

## Positive and negative controls

- Positive: supplied quadratic residues with planted roots and externally labelled source points.
- Negative: equal residues from different fibres, nonresidues, repeated roots, x-sign collisions, exceptional and fresh targets.
- Baselines: IDEAs 049/051/158, P1553 R4, rho, and BSGS.
- Correct roots and relations remain toy/model-bound controls.

## Quantitative promotion and falsification gates

- Promote only with proved compiler/lift theorems, zero source errors on all strata across four sizes, miss probability at most `2^-80`, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one supplied/source-bearing residue, equal-transcript source collision, missed/false occurrence, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v01_residue_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v01_equal_transcript_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Tonelli–Shanks. Root correctness, relation
validity, a validator pass, or a toy scalar remains `toy`, `heuristic`,
`model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct the smallest two endpoint fibres with the same quadratic residue and two-Sylow transcript but different exact signed point lifts.
