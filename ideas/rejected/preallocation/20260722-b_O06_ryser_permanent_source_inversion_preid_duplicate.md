# Pre-ID duplicate draft — Ryser permanent source inversion

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O06`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_compatibility_matrix_and_exponential_inclusion_exclusion`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a permanent, matching count, or relation is not an ECDLP result.

## Falsifiable hypothesis

A compact endpoint-derived bipartite compatibility matrix has permanent equal to the
number of five-source decompositions, and Ryser inclusion-exclusion plus row/column
restriction yields signed occurrences for complete descent below rho and BSGS.

## Mechanism-new operation

Ryser's formula computes the permanent of a supplied matrix by subset inclusion-exclusion.
It counts only if entries are endpoint-derived without source incidence, the permanent is
biconditional with elliptic equality, and restriction queries replay signed occurrences.

## Assumptions

1. The matrix has sub-rho dimension and can be built without pair/source tables.
2. Perfect matchings correspond exactly to all-strata five-source tuples.
3. Permanent values retain signs, multiplicities, and occurrence ancestry through replay.
4. Witness self-reduction and all zeros fit the online cap.
5. Identical construction supports relation and fresh masked targets.

## Semantic fingerprint

`public_endpoint_compatibility_matrix | Ryser_permanent_inclusion_exclusion | exact_matching_count | signed_matching_to_source_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-396_birkhoff_von_neumann_permutation_source_decomposition_hypothesis.md` — permutation decompositions consume a supplied matrix.
2. `ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md` — matching structure begins from graph edges.
3. `ideas/rejected/ECDLP-IDEA-213_dimer_inverse_spectral_exact_source_router_hypothesis.md` — matching counts lose target-source inversion.
4. `ideas/rejected/preallocation/20260720-d_H06_tutte_randomized_source_matching_preid_duplicate.md` — matching detection is a supplied-graph control.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact existence/replay frontier.

## Closest primary literature

- Ryser, [Combinatorial Mathematics](https://bookstore.ams.org/CAR/14), gives the inclusion-exclusion permanent formula for supplied matrices.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not give a compact matching matrix equivalent to five-way addition.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the baseline.

The operation is distinct, but the transplant merges with supplied matching/determinant
lanes and exponential subset inversion; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, matrix indices/entries, signs, strata, restriction schedule, arithmetic ring, and verifier.
2. Build target-independent endpoint state within `B^(9/4+o(1))`; forbid source edges, pair tables, dense resultants, target caches, and scalar labels.
3. For each known-log target, construct the charged matrix, evaluate restricted permanents, self-reduce a matching to occurrences, and verify the point sum.
4. Collect `max(d_FB+32,1000)` verified independent rows, reach rank `d_FB`, and solve all logs.
5. Reuse frozen state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge matrix construction, `2^n` subsets, arithmetic, zeros, self-reduction, output, densities, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; `q` includes matrix build,
permanent evaluations, and witness restrictions. Promotion requires `lambda,mu<=0.45`,
`B^(9/4)` setup/state and `B^(5/4)` fresh caps. Pollard rho expected time and
BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Matrix edges already encode compatible source pairs, while perfect matching enforces only
pairwise bijection, not the five-way elliptic sum. A faithful matrix materializes source
incidence; Ryser then costs `2^n` in its true dimension. Counts aggregate occurrences.

## Proof track

Prove an endpoint-only sub-rho matrix whose perfect matchings are exactly target tuples,
with charged signed self-reduction and complete descent.

## Disproof track

Find one source-derived entry, a matching not satisfying the target, a valid tuple without
matching, exponential dimension, lost provenance, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy matrix with one labelled perfect matching.
- Negative: same permanent/different matchings, pairwise-compatible false tuples, zeros, repeated signs, and blind targets.
- Baselines: Tutte/Lovasz, explicit matching enumeration, P1553 R4, rho, and BSGS.
- Controls are toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only after exact biconditionality over four sizes/all strata, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one supplied entry, matching/target mismatch, unpaid `2^n` work, cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o06_matrix_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o06_matching_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o06_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects only the elliptic permanent route. Claims remain toy, heuristic,
model-bound, and novelty-unverified; no experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the endpoint matrix-entry formula and either prove perfect-matching/source biconditionality inside the true subset cost or preserve the first false edge or tuple.
