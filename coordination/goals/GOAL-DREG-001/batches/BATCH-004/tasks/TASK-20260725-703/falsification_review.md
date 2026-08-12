# Falsification review — CTRL-B repair freeze

Task `TASK-20260725-703` · Red Team · GOAL-DREG-001 BATCH-004  
Verdict: **PASS** · report id `RT-20260725-703` · no official state change

Inference: requested policy `review-xhigh`; resolved model
`cursor-grok-4.5-high-fast`; fallback `true`; authorization
`AMEND-PATH-001-001`; independent session `true`. Fallback is policy/infra,
not mathematical evidence.

## Review basis

Durable producer evidence is the Coordinator snapshot archived by
`TASK-20260725-702` at commit `8f4f1d605038ce8eaf6bbdda9673a0f4ff3fde83`
(parent `85a585f98a17161a4e697301c562d99eb5c8072c`), reachable from review
`HEAD`. That commit changes exactly:

- `.../TASK-20260725-701/ctrl_b_protocol.yaml`
- `.../TASK-20260725-701/protocol_design_note.md`
- `.../archives/TASK-20260725-702/snapshot-receipt.json`

Producer SHA-256 values match the receipt
(`44a0b0c9…` / `2febbf7e…`). The receipt still says
`pending_post_commit` with null commit metadata; Git binding is the durable
check. Working-tree-only producer edits were not used as evidence.

Prior REVISE context: `RT-20260725-691`, `DEC-20260725-023`. CTRL-A system
hashes in `identity_pins` were cross-checked against committed
`support_confound_probe.json` (`sem_hash` / `null_hash` match).

## Disposition of OBJ-691-1..3

| Objection / control | Status | Notes |
|---|---|---|
| OBJ-691-1 / CTRL-Q-MACHINE | **Discharged** | Q1–Q4 are `closed_boolean` under `CTRL-B-Q-MACHINE-v1` on named fields; D5 series pinned; Q4 N/A before admission. |
| OBJ-691-2 / CTRL-AUTH-SPLIT | **Discharged** | Split labels + design-note table; protocol PASS → schedule executor only. |
| OBJ-691-3 / CTRL-SUPPORT-HASH | **Discharged** | `deleted_ncols`, set equality, degree hist, support/deletion rebuild digests beside `ncols==174035`. |
| OBJ-691-4 / scope guard | Preserved | `always_not_claimed` keeps protocol PASS ≠ d_reg / ≠ pin / ≠ H-DREG status. |

## Falsification axes (repair)

| Axis | Result | Notes |
|---|---|---|
| Quarantine predicates not machine-checkable | **Not falsified** | Prior hole closed at protocol level; checker script still to be path-pinned in executor card (RES-703-1). |
| Authorization wording ambiguous | **Not falsified** | Split gates remove structural-admission-at-protocol-PASS misread. |
| ncols-only admission allows wrong support | **Not falsified** | Wrong-16016-column mutation fails set/hash admission metrics. |

## What this PASS does *not* authorize

- No rank measurement in BATCH-004.
- No exact `deficit_genuine` value.
- No d_reg asymptotics, sub-rho, or rehabilitation of raw 17947.
- No H-DREG-001 shared-ledger status change.

Honest pre-measurement degree-axis observable remains the pinned D5
support-matched series (1322 / 1862 / 1999).

## Residual non-blocking

1. **RES-703-1** — Implement `CTRL-B-Q-MACHINE-v1` as a path-pinned checker in
   the executor card before evaluating `quarantine_predicates_Q1_Q4_hold` on
   live EV/DEC.
2. **RES-703-2** — When implementing Q1, keep structural-field `pass_iff_all`
   strict; do not let the allowlist OR on `raw_headline_status` weaken those
   clauses.

## Baseline / scope

Pure rank control (`certificate.kind=none`). No Pollard-rho/BSGS path opened.
Any later positive genuine deficit remains wrong-sign for an H-DREG-001 WIN
reading. This review does not measure rank.

## Verdict

**PASS** — OBJ-691-1..3 discharged on committed snapshot `8f4f1d605038`.
Protocol is repair-complete for thin red-team re-check; measurement still
requires a later admitted executor receipt.

## Next concrete action

Ledger-archive this review (`TASK-20260725-704`), then open a fresh executor
write_scope for chunked CTRL-B with admission metrics and checker
implementation enforced. Until then keep raw 17947 quarantined.
