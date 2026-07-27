# Pre-ID duplicate draft — Minesweeper gap-certificate source join

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_indexed_relations_and_certificate_only_output`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a compact gap certificate or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint-derived indexed relations admit Minesweeper gap boxes whose certificate complexity is
sub-rho even when the full source join is large. Certificate-guided seeks find exact signed
tuples or exact emptiness and complete factor logs plus fresh descent below exponent `0.45`.

## Mechanism-new operation

Minesweeper probes supplied indexed relations, learns gap constraints from misses, and seeks
outside the accumulated constraint data structure. It counts only if indexes are endpoint-
derived without source enumeration, gaps certify the elliptic join rather than a supplied table,
and positive tuples replay signed occurrences. A relation-only gap certificate is a control.

## Assumptions

1. Indexed relations and comparison order are public, scalar-blind, and target-independent.
2. Certificate size includes input construction and is sub-rho on fresh targets.
3. Gap learning, comparisons, constraint storage, output, and all-negative cases are charged.
4. Positive/negative semantics are exact on every restriction and exceptional stratum.
5. Positive tuples retain signs, multiplicities, and point labels for descent.

## Semantic fingerprint

`public_endpoint_indexed_relations | Minesweeper_gap_box_learning | exact_join_or_empty_certificate | charged_signed_positive_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — join execution starts from supplied relations.
2. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — certificates do not erase input/provenance costs.
3. `ideas/rejected/ECDLP-IDEA-353_fully_sparse_boolean_product_witness_router_hypothesis.md` — a decision/witness router needs exact source construction.
4. `ideas/rejected/ECDLP-IDEA-404_stone_duality_source_ultrafilter_hypothesis.md` — compact existence certificates lack a source inverse.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence plus replay owner.

## Closest primary literature

- Ngo et al., [Beyond Worst-Case Analysis for Joins with Minesweeper](https://doi.org/10.1145/2594538.2594547), measures supplied indexed instances by comparison certificates.
- Ngo et al., [Worst-Case Optimal Join Algorithms](https://doi.org/10.1145/2213556.2213565), is the worst-case join control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not build sparse indexed relations; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) controls ECDLP cost.

Certificate complexity is relative to a supplied database. The endpoint compiler and signed
inverse remain absent, so the transplant is semantically occupied and novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, relation tries/indexes, variable order, comparison model, gap schema,
   restrictions, strata, provenance, and verifier.
2. Build endpoint-only indexes within `B^(9/4+o(1))`; forbid explicit source tuples, pair
   tables, scalar residues, target caches, and uncharged input comparisons.
3. For each known-log target, learn gaps until an exact tuple or exhaustion, replay signed
   occurrences, and verify each positive elliptic relation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and
   charge index construction, comparisons, gaps, output, failures, and sparse linear algebra.
5. Reuse identical indexes for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge certificate discovery, not only final certificate size, plus rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; comparison/query/workspace `N^q,N^q_m`; rank credit `N^r`; output
`N^o`; certificate ambiguity `N^u`; factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, with input and
certificate discovery charged. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

The indexed relations are exactly the missing source object. A small certificate for a supplied
instance does not make those relations cheap to construct, and a negative gap certificate cannot
replace signed positive occurrence replay for relation rows and target descent.

## Proof track

Construct endpoint-only indexes, prove small discoverable certificates on all targets,
exact restricted semantics, signed replay, and complete sub-rho descent.

## Disproof track

Find a source-bearing index, certificate/input floor, false gap, large discovery path,
certificate-only output, lost sign, cap violation, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy indexed relations with one tuple and compact gap certificate.
- Negative: certificate-small/input-large cases, empty fibres, dense outputs, equal gaps/different
  sources, variable-order changes, repeated signed points, and blind targets.
- Baselines: InsideOut, sparse Boolean witnesses, P1553 R4, rho, and BSGS.
- A small supplied-instance certificate is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only indexes, zero semantic errors at four sizes, charged certificate
  discovery, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied indexes, certificate-only output, one false gap, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p09_index_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p09_gap_certificate_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Minesweeper. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; a certificate is not a scalar recovery.

## Exactly one next executable action

1. Expand the indexed relation constructor and certificate-discovery trace for one target and preserve the first source-input or unsigned-certificate dependency.
