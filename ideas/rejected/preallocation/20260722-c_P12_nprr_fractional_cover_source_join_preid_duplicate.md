# Pre-ID duplicate draft — NPRR fractional-cover source join

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P12`; no canonical ID allocated.
- Disposition: `merged_rejected_worst_case_optimal_join_over_supplied_relations`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; worst-case-optimal join execution or a valid relation is not an ECDLP result.

## Falsifiable hypothesis

The five-role ECDLP source query has a fractional-cover decomposition whose NPRR heavy/light
execution stays inside the frozen setup/query rectangle. Endpoint-derived relations and exact
replay then complete factor logs and 100 fresh descents below exponent `0.45`.

## Mechanism-new operation

NPRR partitions supplied natural-join relations into heavy/light cases and attains the AGM
worst-case output bound. It counts only if every relation is endpoint-derived without source
enumeration, the AGM input/output exponents fit the ECDLP gates, and output tuples replay signed
points. Applying NPRR to materialized source relations is a control.

## Assumptions

1. Relation schemas/tuples are public, scalar-blind, and target-independent.
2. Total input relation size fits `B^(9/4+o(1))` and is not hidden source incidence.
3. Heavy/light partitions, hash/index state, output, and all-negative work are charged.
4. Natural-join tuples are biconditional with elliptic target equality on all strata.
5. Output preserves signs, multiplicities, and point identities for fresh descent.

## Semantic fingerprint

`public_endpoint_natural_join_relations | NPRR_fractional_cover_heavy_light | AGM_bounded_exact_output | charged_signed_tuple_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — exact owner of worst-case multiway join execution.
2. `ideas/artifacts/ECDLP-IDEA-117/fd_width_gate.md` — cites NPRR and records the source/input-width obstruction.
3. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — relation construction and provenance are charged.
4. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — hypergraph relation compression lacks endpoint construction/inverse.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-to-source frontier.

## Closest primary literature

- Ngo et al., [Worst-Case Optimal Join Algorithms](https://doi.org/10.1145/2213556.2213565), attains the AGM bound for supplied natural-join relations.
- Veldhuizen, [Leapfrog Triejoin](https://arxiv.org/abs/1210.0481), is the nearby iterator-based worst-case-optimal control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not create sparse source relations; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) supplies the baseline.

NPRR is already cited in the P1511 width gate and semantically merges with IDEA-325/117.
The transplant is not a survivor and novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, query hypergraph, fractional cover, relations, heavy thresholds,
   restrictions, signed tuple schema, strata, and verifier.
2. Build endpoint-only relations within `B^(9/4+o(1))`; forbid explicit source/pair tables,
   scalar residues, target fitting, dense resultants, and uncharged relation indexes.
3. For each known-log target, execute heavy/light cases, replay signed points from one tuple,
   and verify the elliptic relation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and
   charge relation construction, partitions, output, failures, and sparse linear algebra.
5. Reuse byte-identical relations/state for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge actual AGM inputs/output, endpoint compilation, rank, factor logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; join/workspace `N^q,N^q_m`; rank credit `N^r`; AGM/output
`N^o`; heavy/light ambiguity `N^u`; factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, including every
input relation and output tuple. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

Worst-case optimality is measured after the natural-join relations are supplied. In ECDLP those
relations are the missing source-bearing partial-sum/incidence object, and the AGM output bound can
remain at the full `B^5=N` relation surface. No signed inverse is created by heavy/light partitioning.

## Proof track

Construct sparse endpoint-only relations with a favorable fractional cover, exact all-strata
semantics, signed replay, and complete sub-rho relation/descent exponents.

## Disproof track

Reduce inputs to P1511/IDEA-325, find source-sized relations or AGM output, a false/missed tuple,
lost sign, restriction rebuild, cap violation, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy natural-join relations with known fractional cover and labelled tuple.
- Negative: AGM-tight instances, input-large/output-small cases, empty joins, identical projections/
  different sources, threshold changes, repeated signed points, and blind targets.
- Baselines: IDEA-325, P1511, Leapfrog Triejoin, P1553 R4, rho, and BSGS.
- Worst-case-optimal execution on supplied relations is toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only sparse relations, zero errors at four sizes, favorable charged
  AGM/input exponents, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied/source-sized relations, AGM output floor, one replay error, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p12_relation_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p12_fractional_cover_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This merges with IDEA-325/P1511 and does not reject NPRR. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; join optimality is not an ECDLP breakthrough.

## Exactly one next executable action

1. Compute the actual relation-cardinality and fractional-cover exponents for the proposed schema and preserve the first P1511 input-floor or AGM-output-floor certificate.
