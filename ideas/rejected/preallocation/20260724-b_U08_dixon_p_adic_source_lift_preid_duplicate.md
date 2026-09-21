# Pre-ID duplicate draft — Dixon p-adic source lift

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U08`; no canonical ID allocated.
- Disposition: `merged_rejected_p_adic_lifting_of_supplied_source_linear_system`.
- Class/risk/lane: representation / representation-changing / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; exact rational reconstruction or modular solving is not an ECDLP break.

## Falsifiable hypothesis

Endpoint equations admit a low-precision modular source sketch whose unique p-adic lift reconstructs
exact signed factor-base occurrences without materializing the high-precision system. Dixon lifting
would give a compact representation and full blind descent with `lambda,mu<=0.45`.

## Mechanism-new operation

The native operation solves a supplied exact linear system by modular inversion and successive
p-adic refinement followed by rational reconstruction. It is ECDLP-new only if low-precision
endpoint residues are point-faithful and their unique lift returns occurrences. Lifting a
source-labelled or dense resultant system is a representation/backend change.

## Assumptions

1. Public endpoints yield a compact modular system without source enumeration.
2. A good public prime and nonsingular modular inverse exist uniformly.
3. p-adic digits preserve signs, repetitions, charts, and occurrence identity.
4. Precision, reconstruction, replay, rank, factor logs, and descent satisfy both caps.
5. No target-specific advice or hidden scalar chooses the modulus or reconstruction bound.

## Semantic fingerprint

`public_modular_endpoint_system | Dixon_p_adic_refinement | rational_reconstruction | exact_signed_source_lift | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-275_arc_descent_valuation_branch_gluing_hypothesis.md` — local/valuation lifts need a global exact source section.
2. `ideas/ECDLP-IDEA-160_nonlogarithmic_ramification_break_scalar_digits_hypothesis.md` — digit extraction is useful only with a nonlogarithmic scalar/source channel.
3. `ideas/rejected/ECDLP-IDEA-115_source_labelled_ulrich_chow_complex_hypothesis.md` — a supplied source matrix is already the missing representation.
4. `ideas/rejected/ECDLP-IDEA-378_comprehensive_groebner_target_atlas_hypothesis.md` — dense target systems and reconstruction state are charged.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — local residues must still support exact restricted replay.

## Closest primary literature

- Dixon, [Exact solution of linear equations using p-adic expansions](https://doi.org/10.1007/BF01459082), starts from a supplied integer/rational linear system.
- Kannan and Bachem, [Smith and Hermite normal forms](https://doi.org/10.1137/0208040), provide neighboring exact canonical-form algorithms for supplied matrices.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide a low-precision point-faithful system.

No checked source supplies the endpoint modular compiler or exact occurrence lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, modulus rule, precision schedule, system compiler, reconstruction bound, restrictions, masks, and verifier.
- Build reusable state under `B^(9/4+o(1))` without source tables, dense resultants, factor logs, or target fitting.
- Charge modular system construction, inverse, every p-adic digit/refinement, precision failure, reconstruction branch, and signed replay.
- Verify `max(d_FB+32,1000)` independent rows, rank `d_FB`, and every factor-base log.
- Reuse byte-identical eligible state on 100 fresh masked targets, subtract masks, and verify scalars.
- Charge bit precision, bad-prime retries, output, failure, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, setup/state are `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, lifting/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, and logs `N^ell,N^ell_m`.
Use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require both `<=0.45`,
state `<=B^(9/4+o(1))`, online work/workspace `<=B^(5/4+o(1))`; rho/BSGS are `0.50`.

## Likely fatal obstruction

p-adic lifting preserves information already present in a supplied system. Low-precision endpoint
aggregates can collide across source fibres; making them point-faithful restores the dense/source
system. Rational reconstruction recovers coefficients or a solution vector, not a canonical map
from basis coordinates to factor points.

## Proof track

Prove an endpoint-only modular compiler, uniform good-prime/precision bounds, injective all-strata
lift to occurrences, full rank/log/descent, and complete bit costs below both caps.

## Disproof track

Find equal modular transcripts with different source fibres, expose source-labelled coefficients
or modulus selection, or show required precision/replay/complete exponent reaches `0.50`.

## Positive and negative controls

- Positive: supplied exact systems with small rational solutions and known p-adic reconstruction bounds.
- Negative: equal residues with different lifts/sources, bad primes, singular reductions, precision overflow, exceptional strata, and fresh targets.
- Baselines: direct exact solving, arc descent, IDEA-160, P1553 R4, rho, and BSGS.
- Correct rational reconstruction or a relation remains a control.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/lift theorems, zero source collisions, bounded precision/retries, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one supplied source coefficient, residue collision, ambiguous reconstruction, cap breach, false/missed occurrence, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u08_modular_system_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u08_equal_residue_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u08_precision_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Dixon lifting. Correct p-adic refinement, rational
reconstruction, or a valid row remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Enumerate the smallest endpoint modular systems and test whether identical residue/refinement transcripts can correspond to different exact signed source fibres.
