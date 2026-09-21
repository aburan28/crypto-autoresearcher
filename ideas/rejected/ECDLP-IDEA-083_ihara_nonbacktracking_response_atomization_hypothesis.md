# ECDLP-IDEA-083 — Ihara nonbacktracking-response atomization

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `merged_rejected`
- Evidence scale: `toy` determinant identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an Ihara determinant or cycle coefficient is not an ECDLP break.

## Falsifiable hypothesis

Weight a partial-sum graph by factor-base atoms and a target twist. The Ihara/Bass nonbacktracking determinant or its logarithmic derivative isolates base-to-target nonbacktracking walks; sparse coefficient recovery and edge backtracking return exact source tuples, enabling full relation collection and blind descent below rho.

## Mechanism-new operation

The proposed operation is **nonbacktracking zeta response plus source-labelled coefficient atomization**. It is rejected/merged because the determinant is an aggregate cycle/walk invariant; extracting exact edges repeats spectral-incidence, Hecke-cycle, and Cauchy-reporter lanes while the partial-sum graph has `Omega(N)` states.

## Assumptions

1. The partial-sum graph is public and sub-rho to construct.
2. Target twists separate relevant walks without a scalar-labelled character.
3. The zeta coefficient support is sparse and source-resolving.
4. Nonbacktracking removes duplicate/cancelled relations without losing valid ones.
5. Coefficient extraction, edge output, rank, descent, and memory are charged.
6. No explicit large-prime or walk table is hidden in the graph.

## Semantic fingerprint

`elliptic_partial_sum_graph | target_twisted_nonbacktracking_operator | Ihara_Bass_determinant_response | sparse_edge_atomization | exact_relation_and_descent`

Collision fingerprint: `spectral_incidence | determinant_cycle | Cauchy_reporter | unchanged_walk_density`.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H663`, the deterministic character/kernel lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, where the exact transform is full rank.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where phase matrices remain full-state.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H670`, the nearest source-resolved incidence reporter.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H671`, the adjacent affine-pencil/source-recovery lane.

## Closest primary literature

- Bass, [The Ihara-Selberg zeta function of a tree lattice](https://doi.org/10.1142/S0129167X92000357), gives the determinant formula, not elliptic source recovery.
- Pollard, [Monte Carlo methods for index computation](https://doi.org/10.1090/S0025-5718-1978-0491431-9), supplies the generic walk baseline.
- Dörfler and Bullo, [Kron reduction of graphs](https://arxiv.org/abs/1102.2950), is the nearest boundary-response operation and likewise aggregates paths.

## Complete factor-base-to-target-descent path

1. Freeze graph, edge labels, target twist, determinant/coefficient convention, and factor base.
2. Compare every nonbacktracking walk and coefficient with exhaustive source tuples.
3. Recover edge atoms and verify exact elliptic relations.
4. Collect rank, solve and verify factor logs.
5. Apply to masked blind targets, recover source walks, unmask the scalar, and verify all candidates.

## Full rho/BSGS cost model

Rho time and BSGS time/memory exponents are `1/2`. Let graph exponent be `g`, determinant/coefficient computation `k`, support/output `o`, factor-base exponent `beta`, inverse relation/target densities `delta,delta_t`, linear algebra `ell`, and memory `mu`. Then `lambda=max(g,k,beta+delta+k+o,ell,delta_t+k+o)`. Materialized graph edges and coefficient lists count at full size.

## Likely fatal obstruction

Ihara zeta aggregates cycles, not labelled open source paths. Target twisting by a public character risks requiring the scalar orientation, while a faithful partial-sum graph contains all group states. Sparse zeta coefficients can coexist with exponentially many edge lifts; atomization reconstructs the explicit walk table.

## Proof track

Construct a sub-rho graph/twist and prove a coefficient/source biconditional with bounded lift and complete descent costs.

## Disproof track

Show graph size at least `N^(1/2)`, distinct source walks share coefficients, target twist needs DLP, or coefficient/source output repeats occupied reporter costs.

## Positive and negative controls

- Regular graphs with known Ihara determinants.
- Planted unique nonbacktracking paths.
- Many-path cospectral graphs.
- Additive-character and ordinary adjacency spectra.
- Exhaustive elliptic partial-sum graphs.
- Blind target twists and complete edge output.

## Quantitative promotion and falsification gates

The necessary gate is zero coefficient/source ambiguity and sub-sqrt graph size on a generic family. Promotion would require upper 95% `g,o,lambda,mu<=0.45`. The candidate is merged/rejected because the determinant changes the reporter but not the graph-state, density, or source-output obstruction.

## Artifact plan

- Collision/no-go: `ideas/artifacts/ECDLP-IDEA-083/ihara_atomization_boundary.md`
- Graph prototype: `ideas/artifacts/ECDLP-IDEA-083/nonbacktracking_graph.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-083/verify_walk_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-083/analysis.md`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. A correct determinant identity or sparse cycle count is not a source-resolved relation or performance result.

## Exactly one next executable action

1. Compute `ideas/artifacts/ECDLP-IDEA-083/ihara_atomization_boundary.md` on exhaustive tiny graphs, grouping every determinant coefficient by its complete source-walk fiber.

