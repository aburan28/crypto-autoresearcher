# ECDLP-IDEA-350 — Translation-catalog fractional-cascading source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_ordered_3sum_backend_requires_scalar_order_or_B3_translation_catalogs`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired review_required preflight; execution prohibited`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; exact lookup or one valid tuple is not an ECDLP break.

## Falsifiable hypothesis

Source-labelled pair-sum catalogs admit a public DLP-free order under which every required elliptic translation has at most `B^(1/4+o(1))` monotone runs, so fractional-cascading bridges return exact five-source relations within the P1553 setup and fresh-target gates.

## Mechanism-new operation

The screened operation is **order pair-sum catalogs, connect them by fractional-cascading bridges, and reuse one exact-complement search across target translations while retaining source labels**. It is distinct only if the order and bridge graph are constructed from public curve coordinates, not scalar logs, and translation remains low-run on every required deck. Otherwise it is an ordered-search backend for the existing three-sum/source-fibre problem.

Minimum-interface correction: bridges need not retain every witness or multiplicity. A target-labelled, subset-stable exact complement-existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged catalog queries, suffices to recover one tuple.

## Assumptions

1. A public total order on `E(F_p)` is compatible with all required translations without computing discrete logarithms.
2. Every target and fifth-source translation decomposes into at most `B^(1/4+o(1))` monotone catalog runs.
3. Restricted bridges preserve exact zero-versus-nonzero across signs, overlaps, singularities, and infinity, so bisection recovers one labelled tuple.
4. The catalog graph is target-independent and supports identical scalar-blind masked-target queries.
5. Catalog construction, bridges, misses, source output, rank, factor logs, verification, and memory are fully charged.

## Semantic fingerprint

`source_labelled_pair_sum_catalogs | public_DLP_free_order | low_run_translation_catalog_graph | fractional_cascading_exact_complement_search | subset_stable_exact_restriction_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; exact pair advice avoids triple storage only by paying cubic target or batch traffic.
2. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; a sorted triple/complement stream exactly matches dictionary-backed five-sum MITM but is not a speedup.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the public source-resolving partition or circuit, not lookup after it is built, is the open operation.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; a public arithmetic source-fibre generator and transposed target batching remain above the complete gate.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; exact source terminals retain one record per witness when a lookup router preserves ancestry.

## Closest primary literature

- Chazelle and Guibas, [Fractional cascading I](https://doi.org/10.1007/BF01840440), accelerates searches through an already ordered graph of catalogs; it does not construct a translation-compatible elliptic order or reduce the number of catalogs.
- Gold and Sharir, [Improved bounds for 3SUM, k-SUM, and linear degeneracy](https://arxiv.org/abs/1512.05279), uses ordered real pair sums and specialized batching, not a finite-elliptic-group source reporter.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than the required order, bridges, or source inverse.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, five signed coloured factor decks, public order, pair catalogs, bridge graph, overlap policy, masks, and verifier.
2. Build target-independent source-labelled pair-sum catalogs without scalar indices.
3. For known-log targets, query restricted exact complements, bisect to one signed tuple, and replay it by direct group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply the identical catalogs and translation routine to fresh scalar-blind `Q+[t]P` targets.
6. Substitute factor logs, remove `t`, retain all ambiguities, and verify `[x]P=Q`.
7. Charge ordering, catalogs, bridges, runs, misses, output, rank, logs, descent, verification, bit time, and bit memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup and state must be at most `B^(9/4+o(1))`; one fresh target must be at most `B^(5/4+o(1))`; complete promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Fractional cascading saves repeated logarithmic searches only after related ordered catalogs exist. A scalar-compatible order is DLP-derived, while ordinary coordinate orders are generically scrambled by elliptic translations into source-sized runs. Materializing per-translation catalogs or bridges restores `B^3` traffic. Thus the operation does not remove P1553's missing restriction-aware exact decision/source reporter.

## Proof track

Construct a public order and bridge graph, prove subset-stable exact complement decisions and charged bisection on every stratum, and derive complete `lambda,mu<=0.45`.

## Disproof track

Exhibit one translation with source-sized run count, prove every compatible order yields scalar orientation, or show bridge construction/materialization costs at least `B^3`.

## Positive and negative controls

- Positive: ordered integer catalogs with planted bounded-run translations and exact source labels.
- Negative: random prime-order curve decks, independently permuted labels, coordinate-order translations, and the P1435 sorted-join baseline.
- Baselines: IDEAs 134/143/344, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a DLP-free order, subset-stable zero-error complement decisions plus charged bisection, at most `B^(1/4+o(1))` runs, 1,000 independent rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one false complement, one DLP-derived key, one source-sized run family, `B^3` catalog traffic, or either exponent at least `0.50`.
- A faster binary search, exact complement, or valid toy tuple is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-350/translation_order_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-350/run_count_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-350/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-350/cost_analysis.md`

## Interpretation boundary

This rejects the proposed ordered-catalog route, not fractional cascading or every data structure. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Correct lookup or one relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-350/translation_order_obligations.md` and derive whether any public coordinate order keeps all required elliptic translations within `B^(1/4+o(1))` monotone runs.
