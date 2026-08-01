# ECDLP-IDEA-076 — Cluster-scattering broken-line coordinate

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `deferred_theorem_required`
- Evidence scale: `toy` chart identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Laurent expansion or broken-line charge is not an ECDLP break.

## Falsifiable hypothesis

A target-independent cluster/scattering atlas for a marked elliptic addition space admits canonical broken-line charges `c(R)` such that `c([a]P+[b]Q)` obeys a bounded-complexity piecewise-additive law and separates the hidden scalar after sub-rho refinement. Factor-base charges calibrate every wall transition, and blind target recovery, branch output, and memory remain below exponent `1/2`.

## Mechanism-new operation

The operation is **canonical scattering-diagram continuation of a point through cluster charts, using broken-line tropical charges as a source-preserving scalar refinement**. A coordinate mutation, Newton polytope, toric degeneration, or post-hoc chamber label alone is a duplicate/control. The atlas must be canonical, scalar-sensitive, and cheaper than enumerating its chambers.

## Assumptions

1. The relevant marked elliptic addition space has a finite-description cluster or log-Calabi-Yau chart over the tested finite fields.
2. Broken-line continuation and wall functions are public and target-independent.
3. Charge composition respects elliptic addition on complete charts.
4. The charge fibers shrink to fewer than `N^(1/2)` scalars without an order-`N` chamber dictionary.
5. Factor-base relation collection, independent rank, factor-log solving, calibration, wall crossings, coefficient growth, exceptional loci, candidate output, and peak memory are charged.
6. Blind targets use the frozen scattering diagram.

## Semantic fingerprint

`elliptic_cluster_atlas | canonical_scattering_diagram | broken_line_tropical_charge | piecewise_additive_scalar_refinement | calibrated_blind_recovery`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H465`, the nearest request for a genuine quotient/rational identity.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier any chart must remove.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H649`, where rational-map image factor bases are already an occupied control.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, which closes tested public phase bases.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H680`, the nearest bounded-coordinate/recursive-source lane.

## Closest primary literature

- Gross, Hacking, Keel, and Kontsevich, [Canonical bases for cluster algebras](https://arxiv.org/abs/1411.1394), constructs theta functions from broken lines but no generic elliptic scalar coordinate.
- Fock and Goncharov, [Cluster ensembles, quantization and the dilogarithm](https://www.numdam.org/item/ASENS_2009_4_42_6_865_0/), develops cluster atlases and mutations without ECDLP descent.
- Gross, Hacking, and Siebert, [Theta functions on varieties with effective anti-canonical class](https://arxiv.org/abs/1601.07081), supplies degeneration/scattering machinery but not the assumed marked finite-field atlas.

## Complete factor-base-to-target-descent path

1. Freeze the cluster seeds, wall functions, reduction rules, factor base, and exceptional-chart policy.
2. Map each factor-base point and verified relation to canonical tropical/cluster data.
3. Calibrate wall-crossing charges and prove their addition law without scalar labels.
4. Collect `B+sigma` independently verified source-labelled relations, solve the factor-base logarithm system, and verify every factor log.
5. Calibrate any residual charge offsets without scalar labels, then evaluate masked targets `Q+[t]P`, traverse the canonical refinement tree, and emit the full scalar candidate list.
6. Combine calibrated factor logs with each descent, unmask, and independently verify candidates, retaining only `[x]P=Q`.

## Full rho/BSGS cost model

Rho time and BSGS time/memory have exponent `1/2`. Let atlas construction exponent be `s`, number of visited chambers `N^chi`, coefficient/precision exponent `h`, factor-base exponent `beta`, inverse relation/target densities `delta,delta_t`, per-relation continuation cost `k`, source/candidate output exponent `o`, factor-log linear algebra exponent `ell>=2beta` absent proved structure, residual-list exponent `r`, and memory exponent `mu`. The full exponent is `lambda=max(s,chi,h,beta+delta+k+o,ell,delta_t+k+o,r)`. An `N`-chamber scattering diagram or order-`N` theta basis sets `chi` or `mu` to `1`.

## Likely fatal obstruction

Generic elliptic curves are proper rather than cluster tori, so any chart may cover only a punctured auxiliary space and forget the Picard-zero orientation. Broken-line charges usually label functions/monomials, not group elements; separating all `N` scalar multiples can require `Omega(N)` chambers or a theta basis whose index is already the DLP dictionary.

## Proof track

Construct the finite-field marked atlas and prove canonical continuation, addition compatibility, source recovery, bounded chamber count, scalar-fiber shrinkage, and full cost below rho.

## Disproof track

Show the charge is Picard-zero blind, depends on a noncanonical seed/path, needs `N^(1/2)` chambers/candidates, or reduces to the occupied toric/phase coordinate controls.

## Positive and negative controls

- Published finite-type cluster mutations and broken-line products.
- Planted piecewise-linear group actions with known charge paths.
- Two mutation-equivalent seeds and all wall-order permutations.
- Random toric coordinates matched for dimension.
- Ordinary curves with no claimed cluster model.
- Blind masked scalars and complete candidate output.

## Quantitative promotion and falsification gates

The theorem gate requires complete chart coverage, path independence, and an exact scalar-fiber bound. A later promotion gate requires zero chart/addition errors, 100 blind targets per largest size, upper 95% `chi,r,lambda,mu<=0.45`, and stable cross-seed results. Falsify as written if every valid charge factors through curve-level invariants, path dependence survives normalization, or lower 95% complete exponent is at least `0.50`.

## Artifact plan

- Atlas theorem: `ideas/artifacts/ECDLP-IDEA-076/cluster_atlas.md`
- Scattering data: `ideas/artifacts/ECDLP-IDEA-076/scattering_diagram.yaml`
- Prototype: `ideas/artifacts/ECDLP-IDEA-076/broken_line_coordinate.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-076/verify_charges.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-076/analysis.md`

## Interpretation boundary

This deferred idea is toy, heuristic, model-bound, and novelty-unverified. A canonical basis, valid mutation, or compact diagram is not evidence of a cryptanalytic improvement.

## Exactly one next executable action

1. Produce `ideas/artifacts/ECDLP-IDEA-076/cluster_atlas.md` containing one explicit marked elliptic addition atlas or a proof that the required cluster structure cannot cover the generic target space.
