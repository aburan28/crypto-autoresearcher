# ECDLP-IDEA-171 — Target-Sperner directed source path

## Status and claim labels

- Class: `algorithm`
- Risk band: `high_risk`
- Top lane: `none`
- State: `merged_rejected_ppad_parity_path_without_source_oracle`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: every prospective finite check is `toy`; all projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a panchromatic simplex, directed path, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Each public endpoint admits a target-uniform Sperner triangulation and local labeling whose panchromatic simplices are biconditional with exact signed factor-base source tuples. A canonical boundary simplex starts a PPAD directed path with endpoint-only predecessor and successor rules, reaching all sources in sub-rho work for relation collection and masked target descent.

## Mechanism-new operation

The operation is **endpoint-uniform Sperner labeling followed by directed panchromatic path extraction**. Removal requires an explicit compact triangulation, local label and successor formulas, a panchromatic-simplex/source inverse, and a sub-rho path theorem. Labels computed by testing source extendibility, supplied source simplices, explicit graphs, generic path search, or post-hoc orientations are controls.

Independent review found that this is IDEA-157's parity-path representation with Sperner
terminology: no new local oracle or short-path theorem is supplied, and one PPAD path does
not enumerate all panchromatic/source terminals. The record is retained as a semantic
merge plus scoped missing-oracle boundary.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, triangulation family, labels, masks, orientation, and verifier are frozen.
2. Each label and both directed neighbors are computed from endpoint and local simplex data without source completion or scalar advice.
3. Panchromatic terminal simplices correspond exactly to every signed source tuple on all multiplicity and exceptional strata.
4. The canonical boundary start exists for known and blindly masked endpoints, and every required path is sub-rho.
5. Triangulation state, labels, paths, retries, output, rank, logs, descent, and peak memory are charged.

## Semantic fingerprint

`endpoint_uniform_Sperner_triangulation | local_public_labels | canonical_boundary_start | PPAD_directed_path | panchromatic_exact_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where exact source ancestry persists in graph edges.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge cost boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source query, rank, and descent gate.
5. `inputs/ledger_inventory.json` — imported `P1480`, the backend substitution control.

## Closest primary literature

- Papadimitriou, [On the complexity of the parity argument and other inefficient proofs of existence](https://doi.org/10.1016/S0022-0000(05)80063-7), supplies the directed parity-path framework but no elliptic labels or short-path guarantee.
- Friedl, Ivanyos, Santha, and Verhoeven, [On the black-box complexity of Sperner's Lemma](https://arxiv.org/abs/quant-ph/0505185), gives black-box query bounds relevant to local labeling, not a source decoder.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relation equations but no Sperner triangulation.

No checked primary source supplies the proposed local source-biconditional path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, triangulation, boundary convention, label oracle, path orientation, factor base, masks, and verifier.
2. Prove labels satisfy Sperner boundary conditions and panchromatic simplices invert exactly to all signed sources.
3. For known `R_j=[r_j]P`, construct the canonical boundary start and follow only locally computed directed neighbors.
4. Decode terminal simplices; preserve cycles, long paths, duplicate terminals, misses, multiplicities, and all output.
5. Verify source sums, collect `B+sigma` independent rows of rank `B`, solve factor logs, and verify each log.
6. Apply the unchanged triangulation, labels, and path rule to fresh masks `Q+[t]P`.
7. Substitute logs, remove masks, retain every path ambiguity, and accept only candidates satisfying `[x]P=Q`.
8. Charge triangulation construction, label queries, successor calls, path length, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one complete directed path plus source inversion cost `N^q,N^q_m`; output and ambiguity exponents be `o,u`; and factor-log algebra cost `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All simplices, label queries, successor computations, revisits, long paths, and terminal outputs are charged.

## Likely fatal obstruction

A label or successor that distinguishes whether a local face extends to an exact endpoint decomposition is the original constrained source oracle. Even if labels are cheap and Sperner guarantees a panchromatic simplex, PPAD totality does not bound the directed path below rho; black-box paths can force exhaustive-scale label queries.

## Proof track

An outside-scope successor must give compact endpoint-uniform triangulation and local formulas, prove the simplex/source biconditional, and derive path, output, `lambda`, and `mu` exponents at most `0.45`.

## Disproof track

Reduce one label or successor query to source completion, find a false or missing panchromatic source, exhibit a path exponent at least `0.5`, expose an explicit simplex deck, or show blind starts require scalar advice.

## Positive and negative controls

- Standard low-dimensional Sperner instances with local labels and known panchromatic simplices.
- Planted short directed paths with supplied terminal source labels.
- Long black-box Sperner paths, explicit source graphs, source-completion labels, rho, and BSGS.
- Exhaustive known-log and blind-target toy fixtures including repeats, signs, infinity, and empty fibers.

## Quantitative promotion and falsification gates

This version is rejected. Reopening requires a new endpoint-only label/successor theorem and uniform path bound with `lambda,mu<=0.45`. One source-completion query, missing source, false terminal, lower 95% path exponent at least `0.50`, or explicit state/output exponent at least `0.5` is falsifying.

## Artifact plan

- Prospective scoped no-go: `ideas/artifacts/ECDLP-IDEA-171/sperner_oracle_path_no_go.md`
- Prospective triangulation and label specification: `ideas/artifacts/ECDLP-IDEA-171/triangulation_label_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-171/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-171/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-171/cost_analysis.md`

All paths are prospective; no artifact, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is scoped rejected, novelty-unverified evidence. Finite checks would be toy and cost projections remain heuristic and model-bound. Sperner totality, a correct path, or relation validity is not an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-171/sperner_oracle_path_no_go.md` formalizing the natural endpoint label and successor predicates and reducing them to constrained decomposition or an explicit source-state traversal.
