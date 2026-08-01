# Pre-ID duplicate draft — Adleman–Manders–Miller r-th-root source branching

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V04`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_rth_power_residue_and_branch_oracle`.
- Class/risk/lane: algorithm / high-risk / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; extracting every finite-field root is not an ECDLP break.

## Falsifiable hypothesis

For a fixed small prime `r`, endpoint fibres compile to `r`-th-power residues whose
Adleman–Manders–Miller root branches coincide with the colored source strata.
Enumerating roots would return exact signed tuples, full factor-base rank, and 100
blind descents with complete time and memory exponents `<=0.45`.

## Mechanism-new operation

The native method decomposes `p-1=r^s t`, uses a supplied `r`-th-power residue and
an `r`-th nonresidue, and descends the `r`-primary order to extract roots. It is new
for ECDLP only if the residue and branch colors arise from endpoints without source
enumeration and lift injectively to occurrence labels.

## Assumptions

1. One bounded-degree residue encodes each restricted source fibre.
2. All `r` root branches preserve occurrence identity and empty-fibre semantics.
3. Nonresidue choice and branch ordering are public and target-independent.
4. Residue compilation, branch enumeration, replay, rank, logs, and descent meet both caps.
5. The method never uses source-labelled roots as advice.

## Semantic fingerprint

`public_endpoint_rth_residue | AMM_r_primary_order_descent | colored_root_branches | exact_signed_source_lift | full_descent`

## Five closest ledger entries

1. `ideas/deferred/ECDLP-IDEA-049_bounded_root_decomposition_transducer_hypothesis.md` — the canonical bounded-root owner.
2. `ideas/rejected/ECDLP-IDEA-244_balanced_type2_collision_residue_router_hypothesis.md` — residue routing collides without faithful source labels.
3. `ideas/rejected/ECDLP-IDEA-017_tropical_component_group_crt_descent_hypothesis.md` — component residues do not remove orientation/descent.
4. `ideas/ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md` — exact sign-stratum lifting remains required.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — root existence is weaker than exact subset-stable replay.

## Closest primary literature

- Adleman, Manders, and Miller, [On taking roots in finite fields](https://doi.org/10.1109/SFCS.1977.18), starts from supplied residues/nonresidues and extracts finite-field roots.
- Harasawa, Sueyoshi, and Kudo, [Root computation in finite fields](https://doi.org/10.1587/transfun.E96.A.1081), studies the native AMM/Cipolla–Lehmer root-computation scope.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not a source-faithful `r`-th-power residue.

No checked source constructs the ECDLP compiler or occurrence inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, colored factor decks, residue compiler, `r`, nonresidue search, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))` without source roots, dense resultants, target fitting, or logs.
- Charge every power test, order descent, root branch, color, exceptional fibre, occurrence replay, and failure.
- Verify `max(d_FB+32,1000)` independent rows, require rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical state on 100 fresh masked targets, subtract masks, and verify scalars.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, root/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and logs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`.
Rho/BSGS remain `0.50`.

## Likely fatal obstruction

AMM opens a supplied power residue and returns algebraic roots; it neither constructs
the residue nor attaches elliptic source labels. Aggregate residues can coincide for
different colored occurrence fibres, while a branch ordering derived from desired
sources is post-hoc advice. Exact replay recreates the original restricted predicate.

## Proof track

Prove endpoint-only residue construction, restriction-uniform root/source
bijections including degeneracies, target-independent branch orientation, full
rank/logs/descent, and complete sub-rho costs.

## Disproof track

Freeze the residue/root set while changing exact fibres, expose a source-derived
nonresidue/branch order, find a missed stratum, or show complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied `r`-th-power residues with planted labeled roots.
- Negative: equal root sets/different fibres, multiple roots, nonresidues, color permutations, exceptional and fresh targets.
- Baselines: IDEAs 017/049/158/244, P1553 R4, rho, and BSGS.
- Root correctness or relation validity is only a toy/model-bound control.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/bijection, zero source errors over all strata/four sizes, failure `<=2^-80`, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on one source-bearing residue, equal-root-set collision, branch advice, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v04_rth_residue_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v04_equal_rootset_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v04_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not AMM root extraction. Correct roots, relations, or
validator passes remain `toy`, `heuristic`, `model-bound`, `novelty-unverified`,
and not a breakthrough.

## Exactly one next executable action

1. Enumerate the smallest `r=3` aggregate residue whose complete root set is shared by two different colored signed source fibres.
