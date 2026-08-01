# ECDLP-IDEA-381 — Megiddo–Cole parametric source search

## Status and claim labels

- Class: `algorithmic`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_parametric_comparison_oracle_is_query2p1_and_no_public_monotone_endpoint_order_exists`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; resolving a toy parametric search is not an ECDLP break.

## Falsifiable hypothesis

There is a DLP-free monotone public parameter for endpoint restrictions such that Megiddo–Cole parametric search batches exact relation decisions and identifies a canonical occurrence-labelled source within the fresh-target gate.

## Mechanism-new operation

The screened operation is **simulate a parallel source-selection algorithm at an unknown critical parameter, resolve batched comparisons with exact restricted-existence decisions, and recover the critical source coordinate**. It survives only if the order and comparison oracle are constructed independently of scalar logs and Query2P1.

## Assumptions

1. Prime-order elliptic endpoints admit a public total/monotone parameter compatible with translation and source restrictions.
2. The parallel comparison network is target-independent and compact.
3. Each exact comparison is strictly cheaper than Query2P1 and preserves occurrence labels and all signed strata.
4. Cole-style batching reduces total online work including every negative restriction and verification below `B^(5/4)`.
5. Preprocessing, comparisons, oracle work, output, rank, factor logs, blind descent, bit time, and memory are charged.

## Semantic fingerprint

`public_monotone_endpoint_parameter | parallel_source_comparison_network | Megiddo_Cole_parametric_search | exact_critical_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the complete source and descent path is mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source decision circuit is missing.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation is unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`; shared comparisons/norms did not remove exact source cost.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`; public additive ordering/characters do not compress the prime-order source fibre.

## Closest primary literature

- Megiddo, [Applying parallel computation algorithms in the design of serial algorithms](https://doi.org/10.1145/2157.322410), reduces optimization to comparisons with a supplied decision procedure.
- Cole, [Slowing down sorting networks to obtain faster sorting algorithms](https://doi.org/10.1145/7531.7537), batches comparisons but does not create their oracle or monotone parameter.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives unordered group equations rather than a public monotone source order.

No checked source supplies the required elliptic order or sub-Query2P1 comparison; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, public parameter, comparison network, exact decision oracle, restrictions, masks, and verifier.
2. Build target-independent network/state within `B^(9/4)` without scalar orientation or source tables.
3. On known-log targets, run parametric search, charge every comparison/oracle call, isolate a critical source coordinate through restrictions, recover a tuple, and verify it.
4. Collect at least `B` independent verified rows, charge misses/dependencies, solve factor logs, and verify them independently.
5. Apply the unchanged parameter/network/oracle to fresh scalar-blind `Q+[t]P`, including mask resampling and all negative children.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge network construction, comparisons, exact decisions, restrictions, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state is at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Parametric search accelerates a comparison-driven algorithm after a monotone scalar parameter and an exact decision oracle exist. Generic elliptic points have no DLP-free order respected by group translation; coordinate orders scramble across targets. Worse, the needed comparison asks whether a restricted source fibre exists, which is Query2P1 itself. Batching oracle calls changes call count, not their missing construction. This merges with IDEAs 125, 134, 138, 156, and 199 unless both new operations are proved.

## Proof track

Construct a public translation-compatible parameter and exact subgate comparison oracle, prove source-biconditional self-reduction, and derive complete exponents at most `0.45`.

## Disproof track

Prove any compatible total order yields scalar orientation, exhibit translated coordinate-order reversals, or reduce every comparison to exact restricted Query2P1.

## Positive and negative controls

- Positive: supplied monotone geometric optimization instances with independent decision oracles must reproduce known critical values.
- Negative: random elliptic translations, scalar-blind relabellings, equal comparisons with different singleton sources, all strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 125/134/138/156/199, direct bisection, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with public-order and sub-Query2P1 oracle theorems, exact source lift, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on DLP-derived order, one Query2P1 comparison, one nonmonotone target/restriction, one missed stratum, or either exponent at least `0.50`.
- A fast toy optimization with a supplied oracle is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-381/monotone_parameter_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-381/translation_order_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-381/comparison_oracle_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-381/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic parametric-search route, not parametric search. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; batching comparisons is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-381/monotone_parameter_obligations.md` and test whether any proposed public point order survives one arbitrary group translation.

