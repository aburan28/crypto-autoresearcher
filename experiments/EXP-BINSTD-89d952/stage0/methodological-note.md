# Methodological note — EXP-BINSTD-89d952 Stage 0

Task `TASK-20261001-e15653`. Observations only. No attack claim.
No rho-competitiveness claim. Amazon Bedrock unused.

## HOLD-T corrections absorbed

From `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-493606.yaml`
(verdict defective / HOLD-T):

1. **Remove /mu.** Per-instance divisor μ=n does not exist (a77711 Lemmas A1/A2;
   KN-FIND-47da4e). Corrected leaf count is `N = 2^{ml}/m!` identical for
   Koblitz-shaped and pseudorandom-shaped arms. Cancelation on the n-target
   orbit system: `n · 2^{ml}/(m! · n) = 2^{ml}/m!`.
2. **Forbid n∈{29,37} as Frobenius-stable measurement cells.** `ord_29(2)=28`,
   `ord_37(2)=36` ⇒ mid-dimension τ-stable V empty.
3. **Instrument replan.** WDSat/CaDiCaL absent; Stage 1 uses pure-Python
   S₄/W₄ from EXP-CERTBIN-e94b27 patterns. CNF-XOR leaf counts are NOT a
   success criterion. Feasibility of S₄ Macaulay at 15 variables is the first
   Stage-1 metric.
4. **Anchor honesty.** IDEA-20260904-b40e6d ~2.8e6 is a **design estimate**,
   labeled unmeasured — not a completed-run anchor.
5. **Primary prediction.** arm_ratio ≈ 1 (shape-blind equality), not the
   source /μ differential. Source /μ is the named falsifiable alternative.
6. **Successor seam.** True m≥4 measurement without symmetry claim routes to
   CERTBIN S₅ extension; this packet does not close that gap.

## certificate.kind vocabulary

Closed set only: `discrete_log | decomposition | key_recovery | none`.
Stage 0 uses `none`. Verified planted finds in Stage 1 may use
`decomposition`. Pure cost/refutation observations use `none`.

## What is NOT claimed

- No break of any curve.
- No competitiveness with Pollard rho.
- No per-instance μ-orbit / canonical-representative constraint (unsound).
- No transfer of toy n=19 costs to deployed n≥131.
