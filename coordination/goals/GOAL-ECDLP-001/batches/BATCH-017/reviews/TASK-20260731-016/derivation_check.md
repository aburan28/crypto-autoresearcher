# TASK-20260731-016 — Derivation / protocol check for EXP-DS-001 v1

**Report:** `RT-20260731-016` (path + task id).
**Reviewed HEAD:** `df613af684f6b878378b6e7696d1ce3ef8975a4c` (TASK-20260731-015 freeze snapshot).
**Question:** Is the frozen H-DS-001 / EXP-DS-001 contract executable and claim-safe before any compute is spent?

## Verdict

**REVISE.** No derivation change is proposed by this reviewer (reviewer does not author repairs). The binding defects are protocol decidability holes in the frozen text, not a mis-transcribed algebraic identity.

## Snapshot binding

| Path | sha256 at `df613af6` | Matches archive table |
|---|---|---|
| `ledger/hypotheses/H-DS-001.yaml` | `6e268e0bffef4727c90a8e67f9806d31a55acb3e8442caae9bcd89831f98bc59` | yes |
| `experiments/EXP-DS-001/specification.yaml` | `c1792bf1733e56f631b04585f50272c9a3342302459daa62a64d1e5fdc4c3889` | yes |

`git merge-base --is-ancestor df613af6 HEAD` succeeds; review HEAD equals the freeze commit.

## What re-derives cleanly

1. **Mechanism sketch.** Half-arity claw rewrite of Semaev membership → charged ratio `R = cost_split / cost_naive` is the stated prediction; end-to-end exponent honesty against matched rho is secondary and correctly caveated (`claim_kind: constant_factor`; E still expected ≳ 1/2 without a surviving HEUR-DS-1 superpolynomial gain).
2. **Null-object obligation.** IDEA-20260731-011 is frozen as `NULL-DS-RANDOM-MULTIHOMOGENEOUS` with planted-bug and honest-rho controls — satisfies inventor-protocol §3 *presence*.
3. **Claim ceiling.** Toy-only; no crypto-scale or asymptotic-support path from this contract alone; H-IC-001 / H-STR-002 quarantined.
4. **Baselines.** Matched Pollard rho (negation) and BSGS are required controls.
5. **D-1 approval routing.** `review_required` / `approved_by: null`; approval only via TASK-20260731-017. No run smuggled.

## Blocking failures (not algebraic)

### B-1 — HEUR-DS-1 is not a pre-registered decidable test

H-DS-001 promises a KS threshold “in EXP-DS-001”. EXP-DS-001 never states a number. The metric allows KS of an intermediate-**degree** CDF against Dickman ρ(u), which does not match the formal claim (smoothness probability ≈ c·ρ(u)). `D` in `u = log D / log B` is not tabulated. TAIL-DS-1’s “extreme outlier” is qualitative. F3 (“KS/tail fail”) is therefore not executable — post-hoc threshold selection would violate target-result-profile A7 / pre-registration.

### B-2 — Structure gate has an unlabeled middle band

When `R < 0.5`:

| `R_null` | Frozen label |
|---|---|
| `>= 0.9` | can meet S1 (with other conjuncts) |
| `< 0.5` | F2 |
| `in [0.5, 0.9)` | **none** |

That middle band is a realistic null-echo outcome and is exactly what a structure-destruction gate must classify. Absence of a disposition makes the IDEA-011 gate incomplete.

## Scope of this check

Pre-execution protocol review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full objection list (B-1, B-2, M-1..M-4, m-1, I-1, I-2).

## Coordinator handoff

On REVISE: TASK-20260731-017 must record `APPROVAL_DETERMINATION: NOT APPROVED`. No Executor runs. This task’s `write_scope` excludes the dispatch queue; Coordinator must mark TASK-016 completed and regenerate the BATCH-017 plan.
