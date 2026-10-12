# Methodological note — HOLD-Q defects absorbed (Stage 0)

Experiment `EXP-BINSTD-cedae5`, task `TASK-20261001-e57118`.
Source idea `IDEA-20260922-c2bbe6`; review
`analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-c2bbe6.yaml`
(verdict `dominated`; agreement: honest toy-tier revision).
Hypothesis `H-BINSTD-fe6b59`. Approval `DEC-20261001-ada211`.

This note is written **before** any Stage 1 scientific run.

## Defects absorbed (observations only; no claim / status change)

1. **`dominated_by` filled.** HOLD-Q required `T ≈ sqrt(2 N B)` with
   ECC2K-130 floors `≥ 2^66.0` at `B=1` vs matched rho `≈ 2^60.809`.
   Stage 0 `dominated-by-pricing.yaml` recomputes the grid
   `{1, 2^10, 2^20, 2^30}` → `{66.0, 71.0, 76.0, 81.0}` and records
   domination. Plain free-leg remains `Θ(N)`. Sharpening cited from
   `IDEA-20260926-1db0e8` without adopting its GTTD form.

2. **Toy tier forced.** Frozen claim is a toy relation-collection
   instrument at `n ≤ 41` (primary cell RC-1 `n=17`). No transfer to
   deployed rows; transfer assumption: **NONE claimed**.

3. **GTTD not adopted.** `KN-LIT-164` / `KN-LIT-92caf4` are cited as kb
   corpus context for the classical double-large-prime variation. This
   EXP does **not** implement GTTD oracle measurement (successor_seam /
   G1 lane; `IMP-gttd-out-of-scope`).

4. **`Z/(4ℓ)` control required.** Stage 3 replicates collision statistics
   in `Z/(4·32603)` with a random matched-size window. Residual
   uniformity is a group-free statement; excess on the curve but not the
   replica is curve structure (blocking control).

5. **Citation provenance.** "Joux–Vitse free-leg" and classical sieve
   large-prime attributions remain **`recalled`** where not independently
   read. Free-leg arithmetic (residual `L=-(P1+P2)`, sign fold via
   `x(L)`, birthday `T^2/(2S)`) is re-derived in Stage 0 /
   implementation rather than trusted from unread detail.
   `recalled→retrieved` upgrades require `verified_by` and an actual read.

## Bound claims (what this EXP may and may not say)

- **May:** report measured combined/full counts, histograms, certificate
  pass rates, `curve_over_generic_ratio`, and comparisons to the
  preregistered modeled curves on RC-1 and the generic replica.
- **Must not:** claim a break, rho-beating on any deployed curve, GTTD
  result, or `F7` advice reuse of the hash table.
- **Timeouts/crashes:** `failed_infrastructure`, never negative math evidence.

## Certificate vocabulary

`certificate.kind ∈ {discrete_log, decomposition, key_recovery, none}`.
Relation-claiming runs use `decomposition` with independent re-sum to `O`.
Stage-0 / metric-only manifests use `none`.

## Stage-5 gate

Optional `n=19` Koblitz sibling runs **only** if Stage 1/3 show
curve-specific residual concentration (`curve/generic` ratio outside
`[0.5, 2]` or excess `>4x`). Otherwise write `stage5/skip-not-triggered.yaml`.
