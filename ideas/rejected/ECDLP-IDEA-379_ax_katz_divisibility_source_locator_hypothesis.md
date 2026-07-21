# ECDLP-IDEA-379 — Ax–Katz divisibility source locator

## Status and claim labels

- Class: `arithmetic`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_divisibility_is_aggregate_and_does_not_decide_nonempty_restricted_fibres`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run preflight under `review_required`; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct divisibility congruence or valid relation is not an ECDLP break.

## Falsifiable hypothesis

After an endpoint-only polynomial encoding of finite deck membership, Ax–Katz divisibility gives an exact nonempty bit for every restricted relation fibre, enabling charged dyadic bisection to one occurrence-labelled source below the P1553 gates.

## Mechanism-new operation

The screened operation is **encode each restricted fibre as a finite-field zero set, compute or infer its `p`-adic point-count divisibility, and turn that congruence into an exact existence oracle followed by source bisection**. It is new only if divisibility distinguishes zero from every positive allowed count and the polynomial system is constructed without source enumeration.

## Assumptions

1. Finite deck membership and all signed complete-chart conditions admit a low-degree, low-variable endpoint-only polynomial encoding.
2. Ax–Katz valuations separate the empty fibre from every nonempty restricted fibre, including singleton and nonreduced cases.
3. The divisibility receipt is computable within the online gate rather than merely guaranteed after the source variety is supplied.
4. Arbitrary dyadic restrictions preserve the hypotheses and support occurrence-labelled source recovery.
5. Counts/congruences, construction, restrictions, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`restricted_Semaev_fibre | Ax_Katz_p_adic_zero_count_divisibility | exact_nonempty_bit | dyadic_occurrence_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; complete source and target-descent accounting remains mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an exact compact source decision is the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation remains unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; nonlinear full-phase information did not yield exact source recovery.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1420-ZERO-PRODUCT-NO-PROMOTION`; exact zero-product masking retained the full source boundary.

## Closest primary literature

- Ax, [Zeros of polynomials over finite fields](https://doi.org/10.2307/2373163), proves `p`-divisibility bounds for aggregate zero counts under degree/variable hypotheses.
- Katz, [On a theorem of Ax](https://doi.org/10.2307/2373389), sharpens the valuation bound but does not turn it into a point locator.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a low-degree finite-deck indicator encoding.

No checked source proves an exact nonempty bit or point recovery from these valuations; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, five disjoint signed decks, polynomial deck indicators, complete signed charts, restrictions, divisibility rule, masks, and verifier.
2. Build any reusable target-independent coefficients/state within `B^(9/4)` without materializing source tuples.
3. For each known-log target and every dyadic restriction, construct the restricted system, compute a rigorous valuation/congruence receipt, decide exact existence, isolate one tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charge zero/duplicate/dependent fibres, solve factor logs, and verify them independently.
5. Apply the unchanged polynomial/divisibility operation to fresh scalar-blind `Q+[t]P`, charging every restriction, exceptional stratum, and mask rebuild.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge system construction, count/valuation work, restriction replay, exact source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state must be at most `B^(9/4+o(1))`, one complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Ax–Katz controls the valuation of an aggregate number of zeros. Divisibility by `p^k` does not distinguish zero from a positive multiple of `p^k`, and in some parameter ranges it forces the very count signal needed for existence to vanish modulo the available precision. Encoding arbitrary finite decks requires high-degree indicator products or source selectors, while computing an exact count restores dense elimination. This merges with IDEAs 019, 053, 138, 156, and 197 unless a new exact existence theorem is proved.

## Proof track

Give a low-degree deck encoding and prove a valuation gap `v_p(#V)=infinity` exactly for empty fibres and a disjoint finite range for every nonempty restricted fibre, with a subgate computation and source lift.

## Disproof track

Produce empty and nonempty restricted fibres with the same available divisibility receipt, or prove the deck-indicator degrees/variables or exact counting work exceed the frozen gates.

## Positive and negative controls

- Positive: supplied low-degree systems where exact counts and Ax–Katz valuations are independently known.
- Negative: zero versus `p^k` points, singleton fibres, cancelling/singular strata, high-degree deck indicators, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 019/053/138/156/197, exact point counting, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an exact valuation-gap theorem, subgate computation, exact source bisection, `1,000` independent rows, `100` blind descents, frozen state/query gates, and `lambda,mu<=0.45`.
- Falsify on one empty/nonempty receipt collision, one high-degree source indicator, one missed stratum, exact counting at source scale, or either exponent at least `0.50`.
- Correct aggregate divisibility on a toy system is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-379/valuation_gap_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-379/empty_nonempty_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-379/source_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-379/cost_analysis.md`

## Interpretation boundary

This rejects the screened exact-existence inference, not Ax–Katz divisibility. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a point-count congruence is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-379/valuation_gap_obligations.md` and construct the smallest empty/nonempty restricted-fibre pair sharing every proposed Ax–Katz receipt.
