# Cross-isogeny symmetry discovery for index calculus

Status: proposed research and implementation roadmap, **not** a proven ECDLP speedup. Extends umbrella #2047 and individual fiber experiments #2048–#2056.

## Goal
Discover exploitable algebraic structure across isogenous elliptic curves and use it to reduce total cost per *new independent verified relation* and, ultimately, complete ECDLP instance cost. Distinguish algorithm-dependent improvements from intrinsic hardness claims.

## Research workstreams

| ID | Candidate | Core test | Failure mode |
|---|---|---|---|
| S01 | Isogeny-aware Frobenius orbit folding | Joint orbit keys for P and phi_i(P), preserving relative phases | Images add no independent orbit compression |
| S02 | Cross-isogeny symmetry breaking | Canonical orbit representative plus phase/path variables in SAT and F4 | Added equations raise degree |
| S03 | Cross-isogeny factor bases | Intersection/pullback of low-complexity factor bases along phi_i | Membership too sparse |
| S04 | Invariant-ring coordinates | Replace raw variables by generators of invariant ring | Degree explosion or reconstruction overhead |
| S05 | Equivariant Groebner/Macaulay | Identify group-stable ideal and invariant subspaces; decompose compatible linear maps | Semilinearity or lack of ideal invariance |
| S06 | Representation switching | Choose separate curve models for membership, relation solving, verification | Transfer dominates |
| S07 | Isogeny-path preprocessing cache | Share resultant/elimination templates and polynomial reductions across paths | Insufficient reusable structure |
| S08 | Torsion-coset slicing | Stratify relation varieties by torsion translations and characters | Empty/redundant strata |
| S09 | Trace/norm coordinates | Galois-invariant coordinate encoding with phase reconstruction | Relative phase lost |
| S10 | Isogeny-aware Weil restriction | Study induced maps and equations on Weil restrictions | Dimension blowup |
| S11 | Syzygy transfer | Pull back/push forward polynomial identities through rational maps with denominators handled | Degree explosion; invalid saturation |
| S12 | Fiber-product decomposition | Identify low-degree components/parametrizations of E1 x_E0 E2 | Repackaged known correspondence |
| S13 | Representation-aware solver portfolio | Jointly choose model, factor base, monomial order, SAT/F4/F5 | Overfitting and tuning artifacts |
| S14 | Conductor phase-transition detection | Test abrupt d_reg / relation-yield changes across certified strata | Noise or representation artifacts |

## Mathematical correctness conditions
- Work with ordinary isogeny classes with certified Frobenius trace, endomorphism conductor and subgroup order; a given class has one imaginary quadratic endomorphism *algebra*, even as orders vary.
- Isogenies defined over F_q commute with q-Frobenius; do not infer extra independent symmetry from redundant images.
- Frobenius on extension-field coordinates is semilinear: establish compatible F_p-linear or invariant formulation before claiming block diagonalization.
- Degree-ell separable fibers are geometric kernel cosets, not necessarily ell rational preimages. In characteristic 2, verify separability rather than assuming it for degree 2.
- If r is coprime to isogeny degree, r-torsion is mapped injectively and the scalar search space is not compressed.
- When transferring ideals, clear denominators, saturate exceptional loci, and verify both directions; preserve group relations and independent-rank accounting.

## Proposed symmetry-discovery engine
1. Input certified curves and edges from the existing curve catalog and isogeny sweeper.
2. Enumerate automorphisms, efficiently evaluable endomorphisms, Frobenius, dual isogenies, mixed-degree paths and correspondences.
3. Build a transformation registry with domain/codomain, degree, field of definition, kernel, rational map, evaluation cost, and certificates.
4. Test invariance of candidate factor bases, relation varieties and polynomial ideals. Record exact failure witnesses.
5. Generate canonical orbit keys with explicit phase payload, invariant generators, syzygy candidates, and compatible Macaulay block bases.
6. Compile candidate treatments into reproducible F4/F5/SAT experiment configurations.
7. Run paired benchmarks; update a hypothesis/evidence ledger; promote only independently reproduced improvements.

## Data contract (logical tables)
- curves(curve_id,field_id,model,trace,group_order,endo_conductor,proof_uri)
- isogenies(edge_id,src_id,dst_id,degree,separable,kernel_spec,map_spec,dual_edge_id,construction_seconds,eval_ns,proof_uri)
- actions(action_id,curve_id,action_kind,definition_field,semilinear,phase_encoding,cost_ns,certificate)
- factor_bases(fb_id,curve_id,defining_equations,density_estimate,membership_ns,orbit_policy)
- ideals(ideal_id,curve_id,fb_id,variables,equations,term_order,degree_profile,hash)
- invariants(invariant_id,action_id,ideal_id,preserved,proof_uri,generators,syzygies,block_dims)
- experiments(exp_id,baseline_id,treatment_id,seed,solver,hardware_id,timeout_s,config_hash)
- outcomes(exp_id,attempts,misses,timeouts,duplicates,verified,independent,rank,preprocess_s,solve_s,la_s,verify_s,peak_bytes,success)
- evidence(evidence_id,hypothesis_id,source_url,doi,claim,assumptions,replication_status)

Use immutable input manifests, exact large integers as decimal strings, field element canonical encodings, explicit NULL for unknown invariants, and provenance hashes. Distinguish features available before the experiment from observed labels to prevent leakage.

## Paired experimental protocol
- Toy exhaustive validation first; ordinary binary m=31,51,53,83 where suitable; ordinary prime and extension fields.
- Within-class same-trace/order pairs, same-level controls, isomorphic model controls, independent random targets, and held-out isogeny classes.
- Baselines: direct Semaev/F4/F5, SAT, existing Frobenius-only orbit method, phase-aware fixed-control, and Pollard rho control.
- Same factor-base cardinality targets, seeds, solver versions, timeouts, rank goals, CPU pinning, NUMA, hardware and memory limits.
- Count failed targets, duplicates, map generation/evaluation, fiber construction, cache preparation, solver, linear algebra and verification.
- Primary metric: total wall time per new independent verified relation; secondary: total time for a full verified DLP instance. Report confidence intervals and censored failures.
- First go/no-go threshold: >=2x reproducible improvement on larger valid cases, with no unaccounted preprocessing or relation-density collapse.

## Milestones / PR decomposition
M1. Literature and negative-results matrix, exact invariance tests, transformation registry schema.
M2. Sage reference generator and property tests for cross-isogeny Frobenius/dual/phase identities.
M3. S01/S02/S03 experiments and matched baselines.
M4. S04/S05/S09/S11 algebraic solver prototypes; explicit ideal preservation and saturation tests.
M5. S06/S07/S13 stage-selection portfolio and cache-cost accounting.
M6. S08/S10/S12/S14 exploratory sweeps; scale and publish positive/negative findings.

## Paper-quality claims checklist
Document closest prior work and exact novelty, mathematical hypotheses and proofs, implementation version, reproducible input artifacts, all failures, statistical uncertainty, cost accounting, and why any speedup is not simply an inexpensive transfer to an already-easier representation.

## Acceptance criteria for this research-tracking PR
A coherent, falsifiable set of workstreams and measurable gates. This PR is a planning artifact; it does not assert that implementations or experiments are completed.
