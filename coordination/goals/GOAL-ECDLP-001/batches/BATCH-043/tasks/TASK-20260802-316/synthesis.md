# BATCH-043 Coordinator synthesis — TASK-20260802-316

**Goal:** GOAL-ECDLP-001 (active)
**Batch:** BATCH-043
**Amendment under review:** `PA-IT-001-v3-rc43-repair-3`
**Proposal snapshot:** `9f3b2a7ad`
**Review snapshot:** `514239010`
**Red-team verdict:** `REVISE` (`RT-20260802-314`)

## Adopted on the merits

Adopt RT-314 **REVISE**. Do **not** authorize an EXP-IT-001 implementation or
execution batch on `PA-IT-001-v3-rc43-repair-3`.

### Blocking defects retained

1. **RT-314-B1** — Anomalous `C_special_smart = ceil(64·log2 p)` still
   re-inverts `R_xfer < 0.7` at bits 16/18/20/22 against matched rho; only
   bits=24 clears. RT-244-B1 is not closed.
2. **RT-314-B2** — Cost-surface Executor discretion via conflict with spec v3
   quadratic Smart charge and unpinned plant bit size.
3. **RT-314-B3** — Density abscissa silently changed vs spec v3.

Closed as worded: RT-244-B2, M1, M2, M3, and command-surface half of B3.

## Independence

TASK-314 records `independent_session: true` with
`fallback_used: true` (resolved `claude-opus-4-8-thinking`, not live
`gpt-5.6-sol`). Substance is adopted; model-binding debt is recorded.

## Status / non-transitions

- H-IT-001 remains `specified`.
- No EXP-IT-001 run authorized.
- No support / reject / SOTA / closure / breakthrough.
- GOAL-ECDLP-001 remains `active`.

## Knowledge promotion

`not_warranted` — design-review REVISE only; no validated mathematical finding.

## Exact next action

Open a successor batch for one superseding overlay
`PA-IT-001-v3-rc44-repair-4` that (1) recalibrates anomalous Smart charge so
`R_xfer < 0.7` holds at the pinned plant bit under matched rho, with disclosed
constants and a supersession clause over spec v3's quadratic term,
(2) pins anomalous plant bit size and restates matched_rho,
(3) restores or explicitly re-freezes the density abscissa with justification,
then obtain a true independent review-adversarial session before any
implementation or run.
