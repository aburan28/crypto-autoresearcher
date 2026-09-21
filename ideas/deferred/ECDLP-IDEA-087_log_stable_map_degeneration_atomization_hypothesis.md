# ECDLP-IDEA-087 — Log-stable-map degeneration atomization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `deferred_theorem_required`
- Top lane: `high-risk`
- Evidence scale: no run; any future degeneration preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid logarithmic degeneration, tropical type, cycle identity, or correct toy relation is not an ECDLP break.

## Falsifiable hypothesis

The universal `m`-source elliptic-addition correspondence admits a public target-independent logarithmic degeneration whose basic stable-log-map special fiber is stratified by tropical gluing types. For every output `R`, the relevant evaluation fiber product has components in exact bijection with signed factor-base source tuples, and a constructive component/source inverse recovers them without materializing `F^m`. The complete degeneration, `B+sigma` relation collection, factor-log solve, masked target descent, output, and memory all have exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **degenerate the full addition correspondence to a basic stable-log-map problem and atomize its evaluation fiber product by tropical gluing type with an exact component-source lift**. It is not a toric initial form, Newton-polytope label, coordinate policy, dense resultant, virtual relation count, or solver replacement. Those are controls. Survival requires a target-independent family, complete special-to-generic correspondence, source-labelled components rather than aggregate cycle weights, and an inverse whose gluing tree/output is sub-rho.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; `F` is a fixed sign-canonical factor base of size `B=N^beta`, and arity `m` is frozen.
2. The marked addition correspondence has a logarithmic model and degeneration compatible with the finite-field fibers being tested.
3. Basic/minimal stable log maps and their tropical gluing types cover every generic factor-base decomposition with controlled multiplicity and no spurious unmatched components.
4. Evaluation fiber products can be computed implicitly, and every surviving component has a public exact inverse to source indices, signs, and multiplicities.
5. Virtual/cycle multiplicities are not treated as source certificates; all obstruction theory, gluing choices, expansions, exceptional fibers, and generic-fiber lifts are verified.
6. Degeneration construction, tropical types, evaluation joins, source output, relation density, `B+sigma` rows, rank, factor logs, blind descent, candidates, and peak memory are fully charged.

## Semantic fingerprint

`addition_correspondence_degeneration | basic_stable_log_maps | tropical_gluing_types | evaluation_fiber_product | exact_component_source_lift | blind_descent`

The new-operation test is whether logarithmic degeneration turns the dense relation fiber into source-invertible components with a provably smaller complete state space. A cycle-level degeneration formula or a tropical label with no exact lift is relation-only evidence and receives no credit.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H644`, the batched non-Grobner higher-arity decomposition hypothesis whose sparsity and memory costs remain open.
2. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-15`, the corresponding open question for a non-Grobner batched `m in {5,6,8}` sieve on random prime-field curves.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1403`, where projectively complete sign-class filtering reproduces the saturated dense `S5` surface.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1439`, the smallest frozen coordinate-policy gate; a log degeneration must change the source geometry rather than select another coordinate.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1441`, where a replicated five-term coordinate enrichment remains a dense-composition control.

## Closest primary literature

- Kim, Lho, and Ruddat, [The degeneration formula for stable log maps](https://arxiv.org/abs/1803.04210), proves a degeneration formula, including a cycle version, in a basic stable-log-map setting; it does not provide factor-base source atomization.
- Abramovich and Chen, [Stable logarithmic maps to Deligne--Faltings pairs II](https://arxiv.org/abs/1102.4531), develops moduli of stable logarithmic maps for generalized Deligne--Faltings structures without an elliptic scalar decoder.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), provides the neighboring relation equations but no logarithmic component/source inverse.

No checked paper identifies basic stable-log-map gluing components with exact factor-base tuples or proves sub-rho blind descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, the universal marked addition correspondence, log structures, degeneration family, expansion policy, basicness/minimality convention, tropical-type encoding, and generic-lift rule.
2. Prove the generic fiber equals the complete signed addition incidence and compute the normal-crossings special fiber plus its basic stable-log-map strata without enumerating factor-base tuples.
3. For a public output `R`, form the relevant evaluation fiber product, enumerate every gluing type/component, lift it to the generic fiber, apply the exact source inverse, and verify the recovered tuple belongs to `F^m` and sums to `R`.
4. Run the frozen construction on known outputs `R_j=[r_j]P`; retain rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` verified rows have rank `B`.
5. Solve for every factor log and independently verify each equality `[log_P(F_i)]P=F_i`.
6. Draw fresh masks `t`, set `R_t=Q+[t]P`, and apply the identical degeneration, evaluation fiber product, gluing enumeration, generic lift, and exact source verification.
7. Combine verified factor logs for every decomposition to recover candidates for `x+t`, subtract `t mod N` to unmask, and retain all ambiguity branches.
8. Accept only a scalar `x` satisfying `[x]P=Q`; archive virtual-only components, failed lifts, and rejected candidates.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2` and constant-state memory; BSGS has time and memory exponents `1/2`. Let log-degeneration setup time/memory exponents be `d_t,d_m`, tropical/gluing-type count exponent be `g`, factor-base exponent be `beta`, reciprocal relation and target success exponents be `delta,delta_t`, per-type evaluation/lift/source-inverse exponent be `k`, obstruction/virtual-multiplicity resolution exponent be `v`, complete source/candidate output exponent be `o`, target ambiguity exponent be `a`, linear-algebra time/memory exponents be `ell,ell_m`, and `sigma=N^o(1)`. Then

`lambda=max(d_t, g, beta+delta+g+k+v+o, ell, delta_t+g+k+v+o+a, beta)`

and

`mu=max(d_m, g, beta+o, ell_m, v, a)`.

Every expansion, tropical type, automorphism factor, virtual multiplicity, evaluation join, generic lift, rejected component, `B+sigma` row, factor log, and candidate is charged. If the gluing forest or evaluation fiber product has one node per source tuple, its full exponent enters both output and memory. A compact degeneration identity alone does not reduce `lambda`.

## Likely fatal obstruction

Stable-log-map degeneration formulas organize virtual classes and weighted counts, not generally individual finite-field points with endpoint ancestry. Many maps/source tuples can share one tropical gluing type and one evaluation component; the cycle weight aggregates them, so an exact source inverse is absent. Restoring endpoint labels in the evaluation fiber product can reproduce the original dense incidence scheme. Moreover, the number of expansions, contact-order partitions, and gluing trees can grow combinatorially, while lifting each special-fiber component to all generic tuples can make complete output `Theta(B^m)`. The representation may therefore move, rather than remove, the source/output obstruction.

## Proof track

Construct the logarithmic addition family, prove properness and a complete generic/special correspondence, then establish a biconditional between basic gluing components and exact signed factor-base tuples with a constructive generic lift. Bound tropical types, obstruction calculations, evaluation joins, relation density, output, rank, descent, and memory so that `lambda,mu<1/2`.

## Disproof track

Find two distinct source tuples in one gluing component, a virtual component with no pointwise source lift, a generic tuple absent from the special fiber, or a gluing/output lower bound of `N^(1/2)`. Dependence on target-chosen degeneration data, hidden scalar labels, or post-hoc source selection also disproves the hypothesis.

## Positive and negative controls

- Published simple-normal-crossings degeneration examples with independently checkable tropical gluing weights.
- Planted evaluation problems whose components have known unique and multiple source lifts.
- Toric initial degenerations, Newton-polytope labels, and coordinate-policy/Semaev controls matched for dimension and arithmetic work.
- Cycle-count-only output and a forbidden endpoint-labelled fiber product that explicitly stores every tuple.
- Exhaustive signed factor-base tuples on ordinary toy curves, including multiplicities and exceptional fibers.
- Blind masked targets under a frozen degeneration, with complete candidate output and matched rho/BSGS accounting.

## Quantitative promotion and falsification gates

The theorem gate requires complete generic/special coverage, zero virtual-to-point conflation, a constructive component-source inverse, and symbolic `lambda,mu<=0.45`. A future toy preflight requires zero independently verified component, lift, source, sum, factor-log, or blind-descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind targets at each of the two largest sizes; upper 95% bounds for `d_t,d_m,g,v,o,a,lambda,mu` must be at most `0.45`. Falsify as written after one independently reproduced component/source collision, a missing generic tuple, an unresolvable virtual-only component, or a lower 95% bound of at least `0.50` for gluing/output, `lambda`, or `mu`.

## Artifact plan

- Degeneration and component/source theorem: `ideas/artifacts/ECDLP-IDEA-087/log_component_source_lift.md`
- Frozen logarithmic-family specification: `ideas/artifacts/ECDLP-IDEA-087/log_family.yaml`
- Prospective gluing enumerator: `ideas/artifacts/ECDLP-IDEA-087/stable_log_atomizer.sage`
- Independent generic/source verifier: `ideas/artifacts/ECDLP-IDEA-087/verify_log_sources.py`
- Prospective run receipts: `ideas/artifacts/ECDLP-IDEA-087/runs/<run-id>/`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-087/analysis.md`

## Interpretation boundary

This deferred representation proposal is toy, heuristic, model-bound, and novelty-unverified. A correct degeneration formula, tropical gluing type, virtual cycle, valid relation, or toy descent is not a pointwise source decoder, a performance result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-087/log_component_source_lift.md` defining the marked logarithmic degeneration and proving either a pointwise component/source biconditional with complete gluing bounds or the virtual-aggregation no-go.
