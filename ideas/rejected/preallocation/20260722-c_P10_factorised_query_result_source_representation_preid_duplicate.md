# Pre-ID duplicate draft — factorised query-result source representation

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P10`; no canonical ID allocated.
- Disposition: `merged_rejected_factorization_of_supplied_source_result`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a compact factorisation or relation certificate is not an ECDLP result.

## Falsifiable hypothesis

The five-source relation result has low readability even when its flat tuple set is large. An
endpoint-constructible factorised representation using unions and products supports exact
restriction and signed tuple unranking, yielding full factor logs and blind descent below `0.45`.

## Mechanism-new operation

Factorised databases exploit distributivity to represent a supplied query result as nested
unions/products with repeated values shared. It counts only if the factorisation is constructed
directly from endpoints without flat source enumeration, supports subset-stable exact existence,
and unpacks signed occurrences at charged cost. Compressing an already computed result is a control.

## Assumptions

1. The representation is target-independent, scalar-blind, and within the setup cap.
2. Readability and construction cost are bounded on generic prime-field instances.
3. Restrictions do not require expansion or target-specific refactorization.
4. Every selected product path returns signs, multiplicities, and actual factor-base points.
5. The same representation supports relation targets and 100 fresh masks.

## Semantic fingerprint

`public_endpoint_factorised_relation | union_product_shared_representation | exact_subset_stable_existence | charged_signed_path_unranking | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — direct owner of factorized provenance joins and width costs.
2. `ideas/artifacts/ECDLP-IDEA-117/fd_width_gate.md` — formal factorized-database width/input-floor gate.
3. `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md` — explicit supplied-input derivation.
4. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — union/product circuit representation remains source-bearing.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact restriction/replay frontier.

## Closest primary literature

- Olteanu and Závodný, [Factorised Representations of Query Results](https://doi.org/10.1145/2274576.2274607), compresses supplied relational query results via union/product factorisation.
- Ngo et al., [Worst-Case Optimal Join Algorithms](https://doi.org/10.1145/2213556.2213565), is the flat multiway-join control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies an equation system but not a compact source factorisation; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) controls cost.

This is an exact semantic duplicate of the IDEA-117/P1511 factorized provenance lane. The
operation is not a survivor and novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, union/product grammar, variable order, readability measure,
   restrictions, unranking, strata, and verifier.
2. Construct endpoint-only representation within `B^(9/4+o(1))`; forbid flat source tuples,
   pair tables, scalar residues, target fitting, and dense resultants hidden in leaves.
3. For each known-log target, restrict the representation, unrank a signed product path, and
   verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve every factor log, and
   charge construction, readability, restrictions, unranking, output, and sparse linear algebra.
5. Reuse byte-identical representation for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge all leaf/source creation, DAG state, bits, rank, logs, descent, and live memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; restriction/unranking work/workspace `N^q,N^q_m`; rank credit
`N^r`; output/readability `N^o`; ambiguity `N^u`; factor-log time/memory `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`; construction is
never replaced by final representation size. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

Factorisation compresses a result after its source semantics are known. For generic
all-distinct relation fibres, constructing union/product leaves or a source-faithful provenance
DAG recreates the input-width floor already proved in P1511; low output readability alone is insufficient.

## Proof track

Give a direct endpoint constructor with low readability, exact restrictions, signed unranking,
and complete setup/query/memory exponents below rho and BSGS.

## Disproof track

Reduce the constructor to IDEA-117/P1511, find a flat/source-sized leaf set, restriction
expansion, ambiguous unranking, cap violation, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy factorisable relation with compact union/product DAG and labelled tuple.
- Negative: all-distinct high-readability instances, same factorisation/different sources, empty
  restrictions, repeated signed points, flat-expansion checks, and blind targets.
- Baselines: IDEA-117/P1511, decomposable circuits, P1553 R4, rho, and BSGS.
- Compactness after supplied-result construction is toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only with a theorem-level endpoint constructor outside P1511, zero errors at four
  sizes, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on P1511 reduction, source-sized leaves, one replay error, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p10_constructor_reduction_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p10_readability_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p10_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This merges with IDEA-117/P1511 and does not reject factorised databases. Evidence remains toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Map the proposed constructor term-by-term to the P1511 factorized semijoin derivation and preserve the first unmatched endpoint operation or complete the duplicate proof.
