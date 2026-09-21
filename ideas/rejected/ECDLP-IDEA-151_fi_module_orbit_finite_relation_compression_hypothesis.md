# ECDLP-IDEA-151 — FI-module orbit-finite relation compression

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `merged_rejected_fixed_arity_orbit_compression`
- Cohort: `20260718-a`
- Evidence scale: representation-stability and semantic audit only; no experiment ran
- Contract posture: rejected archival record; no execution contract
- Scale labels: every prospective measurement is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; finite generation, an eventual character polynomial, a compressed orbit table, or a toy relation is not an ECDLP break.

## Falsifiable hypothesis

The source-labelled elliptic relation modules obtained while the factor base grows form a finitely generated FI-module whose bounded-degree orbit data can be computed from public curve equations and inverted to every exact signed source tuple. If the orbit basis and its target specialization remain sub-rho in dimension, construction, and output, relation collection and masked target descent could avoid materializing the full source hypergraph.

## Mechanism-new operation

The proposed operation is **FI-module finite-generation compression followed by exact orbit-to-source lifting**. Factor-base labels are treated as the finite-set variable, injections induce transition maps, and relation tensors are projected to an orbit-finite representation controlled by finitely many generators and character polynomials.

The semantic audit rejects the current form. Simultaneously relabelling abstract factor-base labels and their attached coordinates is equivariant, but permuting labels while holding one fixed numeric specialization's coordinates in place is not a symmetry. FI finite generation can control representation type across relabelled families; it does not compress the coordinate payload or labelled source output. For fixed arity five, source-slot symmetry is only the existing `S_5` quotient, while lifting an FI orbit back to every coordinate-bearing labelled relation recreates the source-output cost.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of order `N`, target `Q=[x]P`, and nested public factor bases `F_B` with `B=N^beta` are frozen.
2. Injection maps between factor bases induce a genuine FI-module structure compatible with elliptic relation equations, signs, targets, repeats, and infinity.
3. A bounded generation degree and finite orbit basis are constructible from public equations without enumerating relation rows.
4. Target specialization preserves enough information to lift each compressed element to exact factor-base identities.
5. Orbit lifting, multiplicity, coefficient growth, relation retries, linear algebra, blind descent, output, and memory are charged.
6. Source-slot permutation, unlabeled support shapes, character-polynomial statistics, and post-hoc label expansion are controls.

## Semantic fingerprint

`growing_factor_base_labels | FI_module_relation_sequence | bounded_generation_degree | orbit_finite_target_specialization | exact_labelled_source_lift`

The required novelty is an exact source-faithful FI functor. Fixed-`S_5` symmetrization, unlabeled orbit counts, a character polynomial, or explicit expansion of all orbit members is a duplicate or control.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator that an FI-module presentation cannot assume.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where retaining exact witness ancestry prevents lossless compression of source edges.
3. `inputs/ledger_inventory.json` — imported `P1477`, where source-faithful forward and backward state polynomials become dense.
4. `inputs/ledger_inventory.json` — imported `P1478`, where an exact local invariant becomes quadratic when source-complete transitions are composed.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source membership exponent boundary that orbit construction and lifting must meet.

## Closest primary literature

- Church, Ellenberg, and Farb, [FI-modules and stability for representations of symmetric groups](https://arxiv.org/abs/1204.4533), establish finite generation and eventual representation stability; they do not give source-labelled inversion for coordinate-dependent elliptic relations.
- Sam and Snowden, [Gröbner methods for representations of combinatorial categories](https://arxiv.org/abs/1409.1670), prove noetherian and algorithmic structure for combinatorial representation categories; they do not remove orbit expansion or target-dependent source output.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), provides the neighboring fixed-arity relation equations but no FI-module compression with an exact source lift.

No checked primary source supplies the required coordinate-compatible FI functor or sub-rho labelled inverse. Novelty remains unverified outside the rejected fingerprint.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q`, a nested factor-base family, arity five, signs, ordering, targets, masks, and exceptional-fiber conventions.
2. Construct FI transition maps and a finite generating presentation directly from public elliptic equations.
3. Specialize the orbit-finite presentation at known-log targets `R_j=[r_j]P`, compute compressed relation classes, and lift them to all exact signed factor-base tuples.
4. Verify every lifted tuple by direct elliptic addition; preserve missed labels, duplicate orbits, false lifts, repeats, and infinity cases.
5. Collect `B+sigma` rank-`B` rows, solve and independently verify factor-base logarithms.
6. Apply the identical presentation to masks `R_t=Q+[t]P`, lift complete target decompositions, substitute factor logs, and subtract `t`.
7. Accept only candidates satisfying `[x]P=Q`, charging orbit construction, lifting, output, retries, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; FI-presentation derivation cost time/memory be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; specialization, orbit manipulation, exact lift, and verification per query be `N^q,N^q_m`; relation output and target ambiguity exponents be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Generation degree, character-polynomial evaluation, all orbit representatives, label lifting, coefficient bits, retries, and output are charged. Eventual polynomial dimension of degree five can still cost `B^5`, and a finite number of unlabeled orbit types does not bound labelled output. All prospective slopes are heuristic and model-bound.

## Likely fatal obstruction

Simultaneous relabelling of labels and attached coordinates is equivariant, but it changes the presentation rather than compressing one fixed coordinate instance. The only automatic within-instance symmetry is permutation of five source slots, already a constant-size quotient. Treating the fixed instance as an unlabeled `S_B` orbit collapses distinct coordinate-bearing relations to identical shapes; restoring identities requires the source table or expands an orbit to as many labelled tuples as the original relation fiber. FI finite generation therefore compresses representation type, not the coordinate payload and source output needed for factor logs.

## Proof track

Prove coordinate-compatible FI transition maps, bounded generation degree, sub-rho construction of every target specialization, and an exact labelled-source inverse whose cost includes all orbit members. Then prove `lambda,mu<=0.45` through rank calibration and masked descent.

## Disproof track

Show an injection of factor-base labels fails to preserve relation equations; exhibit coordinate-distinct fibers with identical FI orbit data; prove source lifting requires `Omega(B^3)` or larger expansion; show the construction reduces to fixed-`S_5` symmetrization; or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Genuine FI-modules with known finite generation and supplied label-compatible transition maps.
- Fixed-`S_5` source-slot symmetrization as the direct existing control.
- Random relabellings of the same factor base to test coordinate compatibility.
- Two factor bases with identical orbit shapes but different elliptic relation incidence.
- Exhaustive toy relation fibers compared with every lifted labelled source.
- Direct enumeration, rho, BSGS, and independent source/scalar verification.

## Quantitative promotion and falsification gates

The current formulation is rejected. Reopening requires a proved coordinate-compatible FI functor, exact source lifting, and formal `lambda,mu<=0.45`. Any future toy preflight must recover `100%` of labelled sources with `0` false lifts across all frozen exceptional strata. Costs strictly above `0.45` and below `0.50` are inconclusive and non-promoting. Falsify on one coordinate-incompatible injection, one source collision hidden by orbit data, fixed-slot symmetrization only, or either complete exponent at least `0.5`.

## Artifact plan

- Archival semantic no-go: `ideas/artifacts/ECDLP-IDEA-151/fi_orbit_source_no_go.md`
- Prospective FI presentation: `ideas/artifacts/ECDLP-IDEA-151/fi_relation_module.sage`
- Frozen relabelling fixtures: `ideas/artifacts/ECDLP-IDEA-151/fixtures.json`
- Prospective source verifier: `ideas/artifacts/ECDLP-IDEA-151/verify_sources.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-151/cost_analysis.md`

All paths are prospective. No contract or experiment is authorized.

## Interpretation boundary

This is preserved rejected, novelty-unverified evidence. Any future finite example is toy, and all cost projections are heuristic and model-bound. FI finite generation, an eventual character polynomial, or a correct toy lift would establish only a scoped representation fact, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Archive the fixed-arity and label-erasure proof in `ideas/artifacts/ECDLP-IDEA-151/fi_orbit_source_no_go.md` without opening an experiment contract.
