# ECDLP-IDEA-098 — Squarefree Grobner-shelling source lift

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `deferred_theorem_required`
- Top lane: `conservative`
- Evidence scale: semantic/cost screen only; no run; any future degeneration check would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a squarefree initial ideal, shellable complex, valid lifted relation, or correct toy descent is not an ECDLP break.

## Falsifiable hypothesis

For the source-labelled elliptic relation ideal at fixed arity `m`, there is a target-independent weight order whose initial ideal is squarefree and whose Stanley-Reisner facets encode exact signed factor-base source tuples. A shelling or vertex decomposition can enumerate only the accepted facets for an output `R`, and a flat deformation lifts each selected facet to the corresponding finite-field source tuple without traversing the dense relation fiber. The resulting rows, factor-log calibration, and blind target descent have complete time and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **flatly degenerate the labelled relation incidence to a squarefree monomial scheme, read sources from shelling facets, and lift them through the deformation**. The claimed gain comes from replacing nonlinear elimination by a combinatorial complex whose faces retain provenance. A generic Grobner solver, toric initial form without source labels, dense resultant, parameter change, or post-hoc facet label is a control.

The record is deferred behind a theorem gate because neither squarefreeness nor shellability alone compresses the number of components. In a flat degeneration the degree/multiplicity needed to recover the zero-dimensional relation fiber is conserved. The candidate survives only if a target-independent shelling can skip almost all facets while preserving a complete exact source inverse, or if a compressed facet grammar generates accepted source branches with charged output below rho. Without such a theorem, source-biconditional facets enumerate the witness space or store an equivalent dictionary.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; a fixed target-independent factor base `F` has `B=N^beta`, and relation arity `m` is frozen.
2. The complete signed, source-labelled addition ideal `I_R` has a uniform presentation over a public output parameter, including repeated points, signs, points at infinity, and nonreduced fibers.
3. A target-independent weight vector produces a squarefree initial ideal for every accepted output, not only specially planted or generic characteristic-zero examples.
4. Its facets admit a public exact inverse to source indices and a shelling that can skip nonaccepted branches without querying the hidden source tuple.
5. Every selected facet lifts uniquely and exactly through the flat family to an `F_p` relation branch with no unresolved monodromy or residue ambiguity.
6. Grobner-basis construction, coefficient growth, complex size, shelling, facet output, deformation lifting, failures, `B+sigma` rows, rank, factor logs, blind descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`source_labelled_relation_ideal | squarefree_initial_ideal | Stanley_Reisner_facet_shelling | flat_deformation_source_lift | blind_descent`

The operation survives deduplication only if the squarefree degeneration creates a source-invertible object asymptotically smaller than the relation degree. A toric degeneration, generic Grobner backend, or facet list annotated with already known tuples is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H644`, the nearest proposed batched non-Grobner high-arity decomposition sieve and its complete relation-cost obligation.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1051`, where low-degree public-coordinate and row-coefficient identities fail to provide the needed exact relation mechanism.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1259`, the positive widened-generation/selective-control record that requires fresh held-out validation rather than retrospective source selection.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1260`, where frozen Semaev-token and signed-support selectors fail immediately out of sample.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, whose forward/backward state representation becomes dense and supplies the closest composition/output boundary.

## Closest primary literature

- Knutson and Miller, [Grobner geometry of Schubert polynomials](https://arxiv.org/abs/math/0110058), proves squarefree Stanley-Reisner initial ideals and shellability for structured Schubert determinantal ideals; it gives no such degeneration for generic elliptic relation fibers.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation ideals but not a squarefree source-preserving degeneration.
- Amadori et al., [Discrete logarithm in prime fields using algebraic geometry](https://eprint.iacr.org/2017/609), gives a nearby prime-field relation-solving context and does not establish a shelling-based source lift.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked primary source proves a target-uniform squarefree degeneration whose facets compress and invert generic prime-field elliptic source tuples. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, signed source variables, the universal relation ideal, term/weight order, initial-ideal convention, shelling rule, deformation parameter, lift normalization, and exceptional-fiber policy.
2. Construct and verify the squarefree initial ideal without expanding `F^m`; build its Stanley-Reisner complex and certify every claimed facet and shelling step.
3. For a public output `R`, identify accepted facets, lift each through the flat family, invert it to exact signed members of `F`, and independently verify the elliptic sum equals `R`.
4. Apply the frozen procedure to known random outputs `R_j=[r_j]P`; retain verified rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms and independently verify `[log_P(F_i)]P=F_i` for every factor-base point.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and run the identical degeneration, shelling, facet selection, deformation lift, source inverse, and exact sum verification.
7. Substitute verified factor logs, subtract `t mod N`, retain every ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Preserve nonsquarefree fibers, omitted facets, failed lifts, duplicate sources, rejected candidates, and all intermediate sizes.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` and constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; weight/Grobner setup time and memory be `N^g,N^gm`; total complex/facet-state build work and resident state be bounded by `N^f`; relation and target success probabilities be `N^-delta,N^-delta_t`; shelling, lift, and source-inverse work per returned facet be `N^k`; emitted facet/source and target-ambiguity counts per successful fiber be `N^o,N^u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(g,f,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(gm,f,beta+o,ell_m,u)`.

These are the fully charged time and peak-memory exponents. All Grobner polynomials,
coefficients, monomials, faces, facets, shelling state, lift paths, failed fibers,
`B+sigma` rows, source tuples, and candidate output are charged. Flatness preserves degree,
so a facet or lift state per relation branch enters `f` or `o` even if the monomial
generators are short. A valid initial ideal earns no speed claim unless both `lambda` and
`mu` are below `1/2`.

## Likely fatal obstruction

Squarefree degeneration can make intersection combinatorics transparent, but it does not lower the flat family's degree. If every relation branch must be recoverable and each facet carries exact provenance, at least the accepted branch count appears as facets, lift paths, or annotations. A shelling orders those facets; it does not answer a target query without traversing them. If several branches share a facet, the deformation lift must split them and recover the same dense multiplicity. Moreover, the elliptic relation ideals are not Schubert determinantal ideals, so a uniform squarefree initial ideal may not exist at all.

## Proof track

Give a target-uniform Grobner degeneration, prove squarefreeness and shellability over the relevant finite fields, prove a biconditional facet-to-source inverse with unique exact lifting, and bound the complete complex, facet search, lift output, relation collection, factor-log solve, blind descent, and memory by exponents below `1/2`.

## Disproof track

Exhibit one accepted fiber with no squarefree initial ideal under the frozen order, prove that source-biconditional facets are at least the relation degree, find distinct source branches sharing a facet/lift, or lower-bound shelling/lift output by `N^(1/2)`. Any target-specific order selected after seeing sources or a tuple-indexed facet annotation also disproves the mechanism.

## Positive and negative controls

- Schubert determinantal ideals with published squarefree shellable initial complexes.
- Planted zero-dimensional ideals whose squarefree facets and deformation lifts have known exact source labels.
- The same ideals under a nonsquarefree order and a generic Grobner solver matched for arithmetic work.
- Toric degeneration and dense-resultant controls with identical source/output accounting.
- Exhaustive ordinary toy-curve relation ideals, including repeated roots, sign symmetries, and nonreduced fibers.
- Blind masked targets under a frozen weight order, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

The theorem gate requires a target-uniform squarefree initial ideal, an exact facet/source biconditional, a proof that accepted-facet navigation does not enumerate the full relation degree, and symbolic `g,gm,f,o,u,lambda,mu<=0.45` without a tuple-indexed complex. A later toy preflight requires zero independently verified facet/lift/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind descents at each of the two largest sizes. Falsify after one reproduced source collision, one accepted fiber outside the frozen squarefree family, or a lower 95% bound `>=0.50` for facet count, lift output, complete time, or memory.

## Artifact plan

- Squarefree/source theorem gate: `ideas/artifacts/ECDLP-IDEA-098/squarefree_source_gate.md`
- Compressed-navigator representation gate: `ideas/artifacts/ECDLP-IDEA-098/compressed_navigator_gate_v1.md`
- Natural serial recursive-S3 grammar specification: `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_grammar_spec_v1.yaml`
- Local-separator operator trichotomy: `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_local_separator_trichotomy_v1.md`
- Finite-field router candidate/removal receipt: `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_field_router_candidate_v1.md`
- Prospective independent R1-R5 audit: `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r5_independent_audit.md`
- Frozen ideal and weight specification: `ideas/artifacts/ECDLP-IDEA-098/degeneration_spec.yaml`
- Prospective Grobner/shelling prototype: `ideas/artifacts/ECDLP-IDEA-098/squarefree_shelling.sage`
- Independent source/lift verifier: `ideas/artifacts/ECDLP-IDEA-098/verify_shelling_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-098/analysis.md`
- Any future receipts: `ideas/artifacts/ECDLP-IDEA-098/runs/<run-id>/`

## Interpretation boundary

This deferred conservative proposal is toy, heuristic, model-bound, and novelty-unverified. The output-degree argument is the likely obstruction, not a proved universal no-go for every structured squarefree degeneration. A correct Grobner basis, flat family, squarefree initial ideal, shelling, lifted relation, or toy scalar is not evidence of source compression, a below-rho algorithm, or a breakthrough.

## Exactly one next executable action

The completed theorem, representation screen, serial grammar, local-operator
trichotomy, and sparse-factor-map removal are preserved under the IDEA-098
artifact root as non-run producer evidence.

1. Independently review the P1515 R1-R5 chain into `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r5_independent_audit.md` and either freeze one mechanism-new successor with an explicit target-routing recurrence or recommend `deferred_no_candidate_operation`; do not authorize the planned P1515 contract or a solver search from the sparse factor-map identity.
