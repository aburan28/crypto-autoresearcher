# ECDLP-IDEA-090 — Artin-Schreier linearized-cover norm descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected_source_orientation`
- Evidence scale: `toy` cover/source-orientation analysis only; no experiment or timing was run
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid cover, linearized fiber solution, or norm identity is not an ECDLP break.

## Falsifiable hypothesis

There is a publicly specified ramified Artin-Schreier cover `pi:C->E` on which factor-base membership and relation fibers become linearized additive equations. Smooth low-degree places above a lifted relation target can be factored with exact place provenance; norming those places back to `E` yields source-labelled factor-base relations. If the same fixed cover handles known-scalar relations and masked blind targets with total setup, genus/field arithmetic, collection, rank, descent, output, and memory below rho, it would provide a representation-changing ECDLP descent.

## Mechanism-new operation

The proposed operation is **lift to an Artin-Schreier cover, solve linearized fiber equations there, factor the lifted divisor into smooth source places, and norm exact place sources back to `E`**. Merely rewriting Semaev equations over a cover, choosing another solver, adding a bounded number of branch labels, or norming a relation-only certificate is a duplicate/control. Survival requires a cover operation that creates asymptotically growing source-resolving structure without paying for its degree, genus, field extensions, or a hidden scalar dictionary.

## Assumptions

1. `E(F_q)` has a prime-order subgroup `<P>` of order `N`; the public factor base `F` has size `B=N^(beta+o(1))`.
2. A frozen Artin-Schreier equation `z^p-z=f` (or an explicitly bounded tower) defines `pi:C->E`, with every ramified place, exceptional fiber, and field of definition charged.
3. The lifted factor-base and relation constraints become additive linearized equations whose solutions correspond biconditionally to exact places above signed factor-base tuples.
4. Smooth-place testing and factorization on `C`, including residue-field arithmetic, returns exact source provenance rather than only a norm or relation-validity certificate.
5. The norm map preserves enough orientation to recover signed points on `E` and introduces no unknown prime-to-`p` kernel component.
6. Cover construction, genus, degree, all place sources, `B+sigma` rows, rank, factor logs, masked descent, output, and memory are included in one single-instance cost.

## Semantic fingerprint

`bounded_ramified_AS_cover | linearized_fiber_equations | cover_place_smoothness | exact_place_sources | norm_back_to_E | blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the open representation-changing Prym/Jacobian lane whose admission gate requires a DLP-free projected-smoothness operation.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-054`, which closes only one direct principal-polarization descent through a missing rational isotropic subgroup.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1473`, where a sparse implicit Semaev membership test is exact but endpoint logs and the relation system remain uncompressed.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1474`, where a large known-scalar CM orbit does not yield an invariant sparse deck or cheap endpoint coordinate.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1475`, where frozen character-residual buckets do not concentrate source support enough for rank.

## Closest primary literature

- Brochero Martínez and de Oliveira, [On the number of rational points of Artin-Schreier curves and hypersurfaces](https://arxiv.org/abs/2211.11371), is nearby primary work on explicit Artin-Schreier equations and their rational points; it does not claim an elliptic factor-source decoder or a cheap norm descent.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the elliptic relation-system boundary that lifting must improve rather than merely restate.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic square-root boundary if the cover interface is generically simulable.

No checked source supplies the claimed cover-place/source biconditional or a sub-rho prime-field cover cost. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, `B=N^beta`, the Artin-Schreier cover/tower, branch divisor, relation arity, place-smoothness bound, norm convention, masks, and independent place/source verifier.
2. Lift each known-scalar target `R=[u]P` and the factor-base constraints to `C`; solve the frozen linearized fiber equations, factor the resulting divisor into accepted smooth places, retain each place's exact provenance, norm to signed factor-base points, and verify their sum equals `R`.
3. Repeat without adaptive cover selection until at least `B+sigma` independently accepted, source-labelled rows are retained; log every failed lift, nonsmooth divisor, extension degree, branch exception, kernel ambiguity, and duplicate row.
4. Construct the relation matrix over `Z/NZ`, meet the preregistered full-rank threshold, solve all factor logs, and independently verify every `[log_P(F_i)]P=F_i`.
5. For a blind target `Q=[x]P`, commit a random `r`, lift `T=Q+[r]P` through the same cover and place-smoothness path, and reject any target-dependent branch or parameter choice.
6. Norm an accepted exact place decomposition to `E`, combine verified factor logs, remove any explicitly enumerated bounded kernel ambiguity, unmask `x=(sum_i epsilon_i log_P(F_i))-r mod N`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho takes time `N^(1/2+o(1))` with negligible-table memory; BSGS takes
`N^(1/2+o(1))` time and memory. Let `gamma_exp` be the exponent of explicitly
enumerated sheets/places, `g` the charged genus/field-arithmetic exponent, `s` cover
setup, `beta` factor-base size, `k` lifted fiber/place-factorization cost,
`delta,delta_t` reciprocal relation/descent density exponents, `o` exact source/norm
output, and `ell` rank/factor-log solving. Then
`lambda=max(s,g,gamma_exp,beta+delta+k+o,ell,delta_t+k+o,beta)`, and
`mu=max(beta,mu_cover,mu_places,mu_linear_algebra,o)`. In prime fields `q=p` with
`N asymp p`, an explicit sheet/place enumeration for a degree-`p` Artin–Schreier cover
has `gamma_exp=1`. The algebraic degree alone is not asserted to lower-bound every
implicit algorithm; a compact implicit representation receives credit only after it
supplies exact source labels and charges the operations that recover them.

## Likely fatal obstruction

Artin–Schreier linearization is additive `p`-primary structure. In the prime-field lane,
an explicit degree-`p` sheet/place treatment is `N`-scale; an implicit treatment may be
compact but does not thereby expose individual factor-base sources. In fixed small
characteristic, a bounded cover supplies only bounded sheet/branch data and still leaves
generic factor atoms unresolved. Most decisively, normed place data does not furnish the
prime-to-`p` orientation of the large ECDLP subgroup. Recovering that orientation requires
the missing exact source inverse or a scalar dictionary. The formulation therefore
merges with the occupied cover/torsor/norm lanes; no unconditional lower bound for every
implicit cover algorithm is claimed.

## Proof track

Construct an explicit cover family, prove a biconditional between linearized place factors and signed elliptic factor-base tuples, prove that norm preserves orientation with a DLP-free bounded kernel, and derive `lambda,mu<1/2` including cover degree, genus, fields, `B+sigma` rows, rank, factor logs, and blind descent.

## Disproof track

Show that explicit prime-field sheet/place enumeration has exponent one; show bounded
covers expose only bounded branch data; exhibit distinct elliptic source tuples with the
same normed place data; or show that recovering prime-to-`p` orientation requires an
`N`-scale dictionary or generic DLP.

## Positive and negative controls

- Positive: small-characteristic Artin-Schreier curves with exhaustively enumerated fibers and independently verified normed divisors.
- Positive: planted additive linearized systems whose sheet labels are known to recover their sources.
- Negative: matched unramified or randomly ramified covers of the same degree and genus.
- Negative: fixed-degree covers with factor-base labels permuted while branch support is preserved.
- Negative: Semaev relation solving directly on `E`, charged under the same acceptance and output rules.
- Negative: masked blind targets for which only a norm identity, not exact factor atoms, is exposed.

## Quantitative promotion and falsification gates

No active promotion gate remains. A successor would require an exact
place-to-factor-source biconditional, a DLP-free bounded norm kernel, and complete
charged cover/genus/implicit-recovery exponents below `0.50`. Any later empirical gate
would require at least `B+sigma` accepted rows per preregistered size, full rank, all
factor logs verified, at least 100 masked blind descents, and upper 95% bounds
`lambda<=0.45` and `mu<=0.45`. Falsify the scoped explicit arm if
`gamma_exp>=0.50`; falsify every arm that loses exact signed sources or requires a
scalar-orientation dictionary.

## Artifact plan

- Degree no-go: `ideas/artifacts/ECDLP-IDEA-090/artin_schreier_degree_no_go.md`
- Cover schema: `ideas/artifacts/ECDLP-IDEA-090/cover_schema.yaml`
- Place/source verifier design: `ideas/artifacts/ECDLP-IDEA-090/verify_place_norm_sources.py`
- Cost worksheet: `ideas/artifacts/ECDLP-IDEA-090/cost_model.json`
- Future runs, if separately approved: `ideas/artifacts/ECDLP-IDEA-090/runs/<run-id>/`

## Interpretation boundary

This rejected cover mechanism is toy, heuristic, model-bound, and novelty-unverified. The no-go is scoped to the proposed bounded/growing Artin-Schreier linearized-cover path, not every cover or transfer attack. A correct cover equation, smooth-place factorization, or norm relation is not source-complete rank, blind descent, a better-than-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-090/artin_schreier_degree_no_go.md` separating explicit-sheet from implicit-cover costs and formalizing the missing prime-to-`p` source-orientation inverse.
