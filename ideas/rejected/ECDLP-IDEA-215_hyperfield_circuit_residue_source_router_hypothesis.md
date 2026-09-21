# ECDLP-IDEA-215 — Hyperfield-circuit residue source router

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_tropical_atlas_and_residue_source_deck`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and information-flow audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a hyperfield circuit, residue lift, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

A canonical nonarchimedean lift maps signed elliptic factor points to a tropical phase hyperfield whose bounded circuits are biconditional with five-source elliptic sums. Support-changing circuit elimination and exact residue/sign lift would return every source, enabling factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **hyperfield circuit elimination followed by exact residue-source lifting**. It merges/rejects because hyperfield matroid circuits encode linear-dependence supports, while elliptic addition is nonlinear; any linearizing feature module or valuation atlas that preserves exact residue/sign ancestry becomes the missing source deck.

## Assumptions

1. Public curve/group/factor base `B=N^beta` and target are frozen with a canonical target-independent valued lift.
2. The lift is addition-compatible, not merely a Teichmüller point lift, and uses no source-marked chart atlas.
3. Bounded circuits are biconditional with all signed five-source relations and lift uniquely to exact points on every stratum.
4. Lift/extension, feature dimension, circuit search, residue output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`nonarchimedean_elliptic_lift | tropical_phase_hyperfield | bounded_source_biconditional_circuits | support_changing_circuit_elimination | exact_residue_sign_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/source-ancestry barrier.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the tropical/valuation source-loss control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the residue-feature orientation boundary.
4. `inputs/ledger_inventory.json` — imported `P1478`, the structured source compiler frontier.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the failed residue transfer route.

## Closest primary literature

- Baker and Bowler, [Matroids over hyperfields](https://arxiv.org/abs/1601.01204), develops circuit axioms for linear dependence over hyperfields.
- Viro, [Hyperfields for tropical geometry I](https://arxiv.org/abs/1006.3034), supplies tropical hyperfield arithmetic and its information loss.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives nonlinear elliptic endpoint equations.

No checked source gives an addition-compatible elliptic lift, bounded circuit biconditional, and exact source return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the valued lift, feature module, circuit grammar, residue inverse, masks, and verifier.
2. Prove the circuit/source biconditional on generic and degenerate strata without a chart/source atlas.
3. For known endpoints, enumerate accepted circuits, return exact signed factor points, and verify every row.
4. Collect full rank, solve and verify factor-base logarithms.
5. Repeat unchanged on fresh `Q+[t]P`, substitute logs, subtract `t`, preserve ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`; BSGS also uses that memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, circuit query/lift `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Extension and feature dimension enter setup/memory; both exponents must be at most `0.45`.

## Likely fatal obstruction

`F_p` has only the trivial intrinsic valuation; nontrivial lifts are noncanonical. Hyperaddition intentionally merges residues and phases. Teichmüller point lifts are not addition-compatible, and linearizing nonlinear elliptic addition needs a feature/atlas whose dimension or source marks carry the occupied ancestry state.

## Proof track

Construct one canonical bounded lift/feature module, prove circuit iff signed five-sum and exact all-strata residue return, then derive complete `lambda,mu<=0.45`.

## Disproof track

Exhibit two source tuples with one circuit/residue image, prove lift noncanonicity or feature dimension at least `B^3`, lose one sign/source, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied linear configurations with known hyperfield circuits and residue lifts.
- Negative controls: Teichmüller lifts, shuffled residues, source-marked tropical atlases, ordinary matroid support, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires lift/feature state at most `B^2.25`, query at most `B^1.25`, 100% source/sign/multiplicity recall, zero false tuples, no source atlas, and `lambda,mu<=0.45`. One collision, noncanonical lift, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective identity: `ideas/artifacts/ECDLP-IDEA-215/hyperfield_circuit_identity.md`
- Prospective lift: `ideas/artifacts/ECDLP-IDEA-215/residue_lift_spec.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-215/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-215/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-215/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. A circuit, residue lift, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-215/hyperfield_circuit_identity.md` for the generic signed two-plus-three relation and certify either a canonical finite circuit atlas with exact lifts or a concrete residue/source collision.
