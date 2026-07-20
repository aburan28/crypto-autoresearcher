# ECDLP-IDEA-181 — Factorization-homology configuration scanning inverse

## Status and claim labels

- Class: `representation`
- Risk band: `high_risk`
- Top lane: `none`
- State: `merged_rejected_scanning_provenance_backend`
- Cohort: `20260718-c`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: merged/rejected; no contract or run is authorized
- Scale labels: any future finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a scanning equivalence, section, configuration, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Before stabilization, a public endpoint determines an exact compactly represented section in a factorization-homology scanning target, and an unstable inverse returns every finite labeled factor-base configuration mapping to that endpoint. These two maps enable complete relations, factor logs, and masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **exact unstable endpoint-to-section construction followed by section-to-labeled-configuration inversion before stabilization**. It differs from a stable scanning equivalence or group-completed recognition theorem: the inverse must preserve finite point identities, signs, multiplicities, and provenance. Supplying the source configuration or stabilizing away its degree is a control.

Independent review found that demanding the exact unstable inverse simply reinstates the
source fiber and overlaps IDEA-012/114/120/169. The cited factorization-homology result
has nonabelian Poincare-duality hypotheses that must be distinguished from classical
group-completed scanning; neither supplies the required finite-provenance inverse.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, manifold, labels, scanning target, masks, and verifier are frozen.
2. Endpoint data alone constructs a compact unstable section without enumerating source configurations.
3. The inverse returns all exact finite signed labeled sources before stabilization or group completion.
4. Degree, collisions, multiplicities, infinity, component data, ambiguity, and output remain sub-rho.
5. Section construction, scanning inversion, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_to_unstable_section | pre_stable_scanning_inverse | exact_labeled_configuration_sources | finite_provenance_preservation | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-ancestry barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the finite divisor-fiber no-promotion result.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the source-recoverable product boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transcript boundary.

## Closest primary literature

- Segal, [Configuration-spaces and iterated loop-spaces](https://doi.org/10.1007/BF01390197), gives the classical configuration-to-loop-space scanning/recognition setting.
- Ayala and Francis, [Factorization homology of topological manifolds](https://arxiv.org/abs/1206.5522), characterizes factorization homology and proves nonabelian Poincare duality with configuration-space calculations.

The checked primary sources provide classical group-completed scanning or nonabelian Poincare duality under explicit connectivity/coefficient hypotheses, not the required finite-provenance endpoint/source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the manifold, label algebra, section model, unstable scanning map, factor base, masks, and verifier.
2. Construct a compact section from each known `R_j=[r_j]P` without `r_j` or a source configuration.
3. Apply the exact unstable inverse to emit every finite signed labeled factor-base configuration.
4. Verify all configurations; preserve order quotients, collisions, repeats, infinity, misses, degree, and output.
5. Collect rank `B`, solve factor-base logs, and independently verify every recovered log.
6. Apply the identical endpoint-to-section map and inverse to fresh `Q+[t]P` masks.
7. Substitute verified logs, remove masks, retain every ambiguity candidate, and verify `[x]P=Q`.
8. Charge section construction, inverse branches, labels, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let scanning setup cost `N^a,N^a_m`, reciprocal relation and target densities be `N^delta,N^delta_t`, unstable inverse cost `N^q,N^q_m`, output and target ambiguity be `N^o,N^u`, and factor-log algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents; every component, stabilization stage, label, configuration, and emitted source is charged.

## Likely fatal obstruction

Classical scanning becomes an equivalence only after stabilization, connectivity hypotheses, or group completion. Those operations identify configurations through creation, motion, and cancellation and therefore forget the finite labeled provenance needed for factor-base descent. Before stabilization, a section generally has many configurations or no canonical inverse, so exact inversion restores the original source-fiber search.

## Proof track

Give explicit finite endpoint/section maps, prove a source-biconditional unstable inverse preserving labels and multiplicities on every stratum, and derive complete blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Show scanning is injective only after stabilization, construct distinct finite sources with the same section, expose group-completion cancellation, lose one source stratum, or derive either exponent at least `0.5`.

## Positive and negative controls

- Supplied finite labeled configurations with forward scanning.
- Stable and group-completed scanning equivalences from the cited theory.
- Colliding configurations, opposite labels, and equal stabilized sections.
- Exhaustive toy fibers, rho, BSGS, known-log, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening under a new ID requires an operation distinct from the IDEA-012/114/120/169 configuration/provenance lanes, exact endpoint-to-section and pre-stable inverse theorems, 100% source and multiplicity recall, zero false configurations, finite provenance preservation, no source advice, and formal `lambda,mu<=0.45`. Stable-only equivalence, one collision/lost source, or either exponent at least `0.5` falsifies this version.

## Artifact plan

- Prospective unstable inverse theorem: `ideas/artifacts/ECDLP-IDEA-181/unstable_scanning_inverse_theorem.md`
- Prospective section/configuration specification: `ideas/artifacts/ECDLP-IDEA-181/scanning_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-181/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-181/cost_analysis.md`

All paths are prospective; no artifact, contract, or experiment was created.

## Interpretation boundary

This is merged/rejected and novelty-unverified. Finite checks are toy and projections heuristic and model-bound. A scanning equivalence or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-181/unstable_scanning_inverse_theorem.md` specifying exact endpoint-to-section and section-to-labeled-source maps before stabilization and proving whether finite provenance survives.
