# ECDLP-IDEA-174 — Harder-Narasimhan quiver source filtration

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_quiver_factor_backend`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and prospective theorem only; zero runs
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: any finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a filtration, stable factor, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Public endpoint equations can be compiled into a framed quiver representation whose unique Harder-Narasimhan filtration has stable graded factors if and only if they are the exact signed factor-base points of a source tuple. An exact inverse from those factors would yield complete relations, factor logs, and masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **endpoint-to-framed-quiver compilation followed by pre-source unique Harder-Narasimhan filtration and stable-factor inversion**. The obstruction removed would be source-fiber enumeration: stability strata would expose point atoms before a tuple is known. This is not a Hall-algebra or module backend applied after sources are materialized. It is mechanism-new only if the factor biconditional and inverse hold without encoding the incidence matrix or enumerating `B^m` refinements.

Independent operation-level review found that the required compiler and point inverse are
not supplied, so HN filtration is a representation/backend substitution for the
endpoint-to-quiver and simple-factor lane already rejected in IDEA-093, with additional
overlap with IDEA-072/127/169. HN quotients are semistable; extracting stable factors
requires a noncanonical Jordan-Hölder refinement unless a new point-biconditional theorem
is proved. The current record is therefore merged/rejected.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, quiver, framing, stability weight, masks, and verifier are frozen.
2. The endpoint representation is constructed without a source tuple, scalar orientation, or relation table.
3. Its unique HN factors correspond biconditionally to exact signed factor-base points on every declared stratum.
4. Factor isomorphism types can be inverted to point identities, signs, and multiplicities with bounded ambiguity.
5. Compilation, filtration, refinement, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_endpoint_equations | framed_quiver_representation | unique_HN_filtration | stable_factor_point_biconditional | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank representation control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the materialized product/source-cost boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the structured zero-output no-promotion result.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the nearest complete source-extraction gate.

## Closest primary literature

- Reineke, [The Harder-Narasimhan system in quantum groups and cohomology of quiver moduli](https://arxiv.org/abs/math/0204059), develops HN recursion for quiver representations; it does not give an elliptic endpoint/source inverse.
- King, [Moduli of representations of finite dimensional algebras](https://doi.org/10.1093/qmath/45.4.515), supplies the stability framework for representation moduli; it does not identify stable factors with factor-base points.

Both primary URLs were checked. Neither supplies the claimed compiler, biconditional, or sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze quiver vertices/arrows, framing, dimension vector, stability weight, factor base, masks, and verifier.
2. Compile each known endpoint `R_j=[r_j]P` into its framed representation without source advice.
3. Compute the unique HN filtration, invert every stable graded factor to signed factor-base points, and assemble all tuples.
4. Verify tuples; preserve unstable strata, isomorphic-factor collisions, multiplicities, misses, ambiguity, infinity, and output.
5. Collect rank `B`, solve the relation matrix, and independently verify every factor-base logarithm.
6. Apply the identical compiler and filtration to fresh masked targets `Q+[t]P`.
7. Substitute verified logs, remove masks, retain every candidate, and verify `[x]P=Q`.
8. Charge compilation, HN computation, factor refinement/inversion, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup be `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, compilation/filtration/inversion `N^q,N^q_m`, output and ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are complete time and peak-memory exponents; all quiver matrices, HN refinements, factor dictionaries, branches, and source output are charged.

## Likely fatal obstruction

The framed representation may merely embed the original elliptic incidence problem. HN factors are isomorphism types, not point identities; refining them to signed points can require a source dictionary or `B^m` choices. Thus uniqueness of the filtration need not orient or unrank the source tuple.

## Proof track

Give an endpoint-only compiler, prove unique all-strata HN existence, the stable-factor/point biconditional and exact inverse, and derive complete `lambda,mu<=0.45` without materialized incidence.

## Disproof track

Reduce compilation to the original source fiber, exhibit distinct point tuples with isomorphic graded factors, require a `B^m` refinement, expose hidden scalar orientation, or derive an exponent at least `0.5`.

## Positive and negative controls

- Quivers with planted stable factors and supplied source labels.
- Unframed, semistable, and repeated-isomorphism-type controls.
- Hall/module backends operating on already materialized source tuples.
- Exhaustive toy fibers, direct enumeration, rho, BSGS, and blind-target verification.

## Quantitative promotion and falsification gates

This version is merged/rejected at the supplied-representation/source-inverse gate. Reopening under a new ID requires an operation distinct from the IDEA-093 quiver-factor lane, exact biconditional recall and precision `1.0` on every declared stratum, zero hidden source labels, and symbolic `lambda,mu<=0.45`. One lost/false point, unresolved Jordan-Hölder or isomorphism collision, `B^m` refinement, or either exponent at least `0.5` falsifies this version.

## Artifact plan

- Prospective compiler theorem: `ideas/artifacts/ECDLP-IDEA-174/hn_compiler_theorem.md`
- Prospective representation fixtures: `ideas/artifacts/ECDLP-IDEA-174/quiver_fixtures.json`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-174/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-174/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-174_hn_quiver_filtration_preflight.yaml`

All research-artifact paths are ID-owned and prospective; the retired contract is unapproved and permits zero runs. No artifact, contract run, or experiment exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified, zero-run evidence. Finite checks are toy and projections heuristic and model-bound. Correct HN filtration or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-174/hn_compiler_theorem.md` specifying the endpoint compiler and proving or refuting the stable-factor/point biconditional before implementation.
