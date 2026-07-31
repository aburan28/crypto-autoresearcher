# Falsification review — SIG-D6-NULL-RECAL-v1

Task `TASK-20260725-633` · Red Team · GOAL-SIG-001 BATCH-001  
Verdict: **REVISE** · report id `RT-20260725-633` · no official state change

Inference: requested policy `review-xhigh`; resolved model
`cursor-grok-4.5-high-fast`; fallback `true`; authorization
`AMEND-PATH-001-001`; independent session `true`. Fallback is policy/infra,
not mathematical evidence.

## Review basis

Durable producer evidence is the Coordinator snapshot archived by
`TASK-20260725-632` at commit `91d10c79cec061d4e76f8522d73c09a804d81492`
(parent `e8832002a122e75c4be6a711295b91d5b3e1cf61`), reachable from review
`HEAD`. That commit changes exactly:

- `.../TASK-20260725-631/d6_null_protocol.yaml`
- `.../TASK-20260725-631/protocol_design_note.md`
- `.../archives/TASK-20260725-632/snapshot-receipt.json`

Producer SHA-256 values match the receipt
(`03873abd…` / `e1d05d78…`). The receipt still says
`pending_post_commit` with null commit metadata; Git binding is the durable
check. Working-tree-only producer edits were not used as evidence.

Pinned instrument `h013_sha256` matches
`experiments/EXP-SIG-005/src/h013_f5_signatures.sage` in the worktree.
Prior ledger context (read-only): `EV-SIG-005`, `DEC-20260720-001`,
`KN-FIND-027`, `GOAL-SIG-001.yaml`; RUN-k D6 numbers cross-checked.

## Axes

| Axis | Result | Notes |
|---|---|---|
| Legacy D6 baseline invalidation | **Not falsified** | `LEGACY-T11-D6-SHARED-SRPRED` + quarantine of RUN-h magnitudes matches EV/DEC/KN-FIND-027. |
| Unequal-*ncols* gate vs RUN-k | **Not falsified** | CG-NCOLS native clause cites 31180≠29332. |
| Equal *support* completeness | **Falsified** | Definition requires identical sets; CG-NCOLS checks counts; support-hash optional; secondary is count-match. |
| Auth / no illicit D≥6 reopen | **Not falsified** | `review_only_freeze`; dual Coordinator auth; CALIB_PASS ≠ cascade. |
| D≤5 continuity verifiability | **Falsified (ambiguity)** | "unaligned **or** aligned" can be satisfied by one mode. |
| CTRL-B cross-discharge | **Not falsified** | Explicit non-discharge both ways. |

## Blocking objections

### OBJ-633-1 — ncols-only vs set identity (blocking)

`definition.statement` requires identical Macaulay column *sets*, but
`CG-NCOLS` only machine-checks equal cardinalities. The sole set/hash gate
(`CG-SUPPORT-HASH`) is admission-optional via
`CG-SUPPORT-HASH_pass_if_alignment_used`. Secondary
`REJECT-UNTIL-NCOLS-MATCH` searches equal native counts only and is not barred
from a CALIB_PASS path once count/residual gates pass.

**Cheapest mutation:** keep `|null_cols|==|sem_cols|` (or delete the wrong
`|null\\sem|` columns) while `null_cols ≠ sem_cols` as sets. That is the
ncols-only hole already closed for DREG CTRL-B.

**Required repair:** unconditional support-set equality (+ hashes) on every
CALIB_PASS path; rewrite CG-NCOLS to sets; close or strengthen secondary.

### OBJ-633-2 — CG-D5-CONTINUITY "or" (blocking)

Literal "unaligned or aligned" allows preserving only the historical unaligned
D≤5 C5 while an ALIGN repair regresses aligned D≤5 zeros.

**Required repair:** require **both** unaligned D≤5 continuity **and**
aligned D≤5 null-zero/rank match when ALIGN is used.

## What survives (not blockers)

- No measurement authorized in BATCH-001; protocol PASS only schedules a later
  executor under fresh write_scope + separate Coordinator ledger auth.
- CALIB_PASS still needs another Coordinator authorization before cascade
  observables; H-SIG-001 status unchanged by this card.
- Legacy D6 magnitudes remain quarantined; infra failures stay non-evidence.
- Non-blocking residuals: empirical `sr_pred` tautology (already labeled);
  n=12 null D6 prior ENOSPC risk; receipt `pending_post_commit` metadata.

## Baseline / scope

Closest baseline: EXP-SIG-005 T11 boolean_null under C5. Pollard-rho / BSGS
are out of scope for this instrument-repair freeze. This REVISE is not cascade
falsification and not a birth-law result.

## Verdict

**REVISE** — do not schedule calibration execution on this freeze. Repair
OBJ-633-1 and OBJ-633-2, snapshot again, and re-dispatch independent red-team.

## Next concrete action

Ledger-archive this review (`TASK-20260725-634`), open a producer repair
write_scope for unconditional support-set/hash admission and D5 dual-mode
continuity, then re-review. Keep D≥6 cascade closed until a later
`CALIB_PASS` + Coordinator measurement authorization.
