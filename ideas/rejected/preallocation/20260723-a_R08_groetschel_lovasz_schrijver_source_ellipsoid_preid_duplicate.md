# Pre-ID duplicate draft — Grötschel–Lovász–Schrijver source ellipsoid

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R08`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_separation_oracle`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; separation correctness, a relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, signed source occurrences are integral points of an
endpoint-defined convex body with a public sub-rho separation oracle. Ellipsoid localization
finds an exact occurrence for relations and 100 fresh blind targets, with complete time and
memory exponents at most `0.45`.

## Mechanism-new operation

The ellipsoid method repeatedly queries a separation oracle for a supplied convex body and cuts
away infeasible volume. It counts only if the body and oracle are compiled from public endpoints
without source incidence, and the final point exactly replays signs, multiplicities, and
occurrences. An oracle that answers source feasibility is Query2P1 in another interface.

## Assumptions

1. The endpoint source hull has polynomial dimension and bounded encoding length.
2. A complete separation oracle is public, scalar-blind, and subcap on arbitrary restrictions.
3. Convex feasibility is equivalent to integer source existence with no relaxation gap.
4. Localization and rounding return a unique exact signed occurrence.
5. Target-independent body data is reused unchanged for fresh masked targets.

## Semantic fingerprint

`public_endpoint_source_convex_body | ellipsoid_separation_cuts | exact_integral_feasible_source | charged_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-b_J04_collins_cad_endpoint_cell_source_section_preid_duplicate.md` — exact cell decisions still require a source-aware predicate.
2. `ideas/rejected/preallocation/20260719-d_D07_benders_source_cut_generation_preid_duplicate.md` — cuts depend on a supplied source formulation and subproblem oracle.
3. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — refinement counterexamples do not construct the missing source semantics.
4. `ideas/rejected/preallocation/20260719-d_D09_frank_wolfe_source_convex_hull_preid_duplicate.md` — convex-hull optimization begins after source vertices exist.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay remain the owner.

## Closest primary literature

- Grötschel, Lovász, and Schrijver, [The Ellipsoid Method and Its Consequences in Combinatorial Optimization](https://doi.org/10.1007/BF02579273), derives optimization consequences from supplied separation access.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not supply the required separation oracle.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls the generic comparison.

The endpoint separation oracle and integrality theorem remain unproved; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, body encoding, bounding ellipsoid, separation oracle, precision, rounding, restrictions, strata, and verifier.
2. Build target-independent body data inside `B^(9/4+o(1))`, excluding source vertices, scalar labels, and decomposition calls.
3. For known-log targets, localize with exact cuts, recover a signed occurrence, and verify the elliptic sum.
4. Gather at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and every factor log.
5. Reuse identical state for 100 fresh masked targets, recover sources, subtract masks, and verify each scalar.
6. Charge body/oracle construction, every cut, bit precision, rounding, failures, replay, rank, logs, bit operations, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; separation/localization work `N^q,N^q_m`; rank credit `N^r`;
output `N^o`; ambiguity `N^u`; and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS remain exponent `0.50`.

## Likely fatal obstruction

The separation oracle must distinguish restrictions containing a source from empty ones, which
is the missing exact predicate. Convex hull membership can also be feasible when no integer
source exists; enforcing integrality or extracting a vertex restores source enumeration.

## Proof track

Prove endpoint-only body and complete separation, zero integrality gap on every restriction,
bounded bit complexity, and exact signed vertex recovery through blind descent.

## Disproof track

Find one source-aware cut, fractional feasible empty fibre, exponential facet/precision cost,
rounding ambiguity, restriction rebuild, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied integral toy polytopes with planted labelled source vertices.
- Negative: fractional hull points without sources, equal cuts with different vertices, empty
  fibres, exceptional strata, adversarial thin bodies, and blind targets.
- Baselines: Benders, CEGAR, P1553 R4, rho, and BSGS.
- Separation-oracle correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with compactness, exact separation and integrality theorems, zero four-size/all-
  strata errors, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-aware oracle call, fractional false positive, cap violation, replay
  failure, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r08_separation_oracle_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r08_integrality_gap_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r08_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not the ellipsoid method. Correct cuts and valid rows remain toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Expand the proposed separation oracle for one restricted toy endpoint and preserve its first source-feasibility subcall or prove exact source-blind separation and integral replay.
