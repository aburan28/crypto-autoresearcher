# Falsification review — SIG-D6-NULL-RECAL-v2 repair

Task `TASK-20260725-711` · Red Team · GOAL-SIG-001 BATCH-002  
Verdict: **PASS** · report id `RT-20260725-711` · no official state change

Inference: requested policy `review-xhigh`; resolved model
`cursor-grok-4.5-high-fast`; fallback `true`; authorization
`AMEND-PATH-001-001`; independent session `true`. Fallback is policy/infra,
not mathematical evidence. Equivalence to `review-xhigh` is not claimed.

## Review basis

Durable producer evidence is the Coordinator snapshot archived by
`TASK-20260725-710` at commit `95c1b4f9a781ae05dbb17b0984e18df388c94589`
(parent `a764af80b18dd53c3c303c992e13314d13034918`), reachable from review
`HEAD` (`518fa95595823e01b696b38e1d47b6b7bccf4191` bind). Dispatch queue
`archive.commit_sha` matches. That commit changes exactly:

- `.../TASK-20260725-709/d6_null_protocol.yaml`
- `.../TASK-20260725-709/protocol_design_note.md`
- `.../archives/TASK-20260725-710/snapshot-receipt.json`

| Path | Queue / receipt digest | Git blob at `95c1b4f9a781` |
|---|---|---|
| `d6_null_protocol.yaml` | `69ebeb7ab5a711f417d223209604752c5683ca99cd5929ea1381bc41a64575e0` | match |
| `protocol_design_note.md` | `21bd1bf7d5d313a58fbf8d475dcbed37378bffdb62dd1fa7e785ba62599807c6` | match |

The receipt still says `pending_post_commit` with null commit metadata; Git
binding is the durable check. Working-tree-only producer edits were not used
as evidence. Pinned `h013_sha256` matches
`experiments/EXP-SIG-005/src/h013_f5_signatures.sage`.

Prior REVISE context (read-only): `RT-20260725-633`, `EV-SIG-009`,
`DEC-20260725-014`.

## Attack

Try to falsify that repaired `CALIB_PASS` can still be claimed without
set-identity support alignment (discharge of OBJ-633-1 / OBJ-633-2).

## Axes

| Axis | Result | Notes |
|---|---|---|
| Equal-\|cols\| / wrong-support still admits CALIB_PASS | **Not falsified** | CG-NCOLS = set equality; CG-SUPPORT-HASH unconditional; secondary not a CALIB_PASS path. |
| D≤5 continuity "or" bypass | **Not falsified** | Explicit (a) AND (b); inclusive-or forbidden. |
| Legacy D6 invalidation | **Not falsified** | Quarantine retained. |
| Auth / no illicit D≥6 reopen | **Not falsified** | `review_only_freeze`; dual Coordinator auth. |
| CTRL-B cross-discharge | **Not falsified** | Explicit non-discharge both ways. |

## Prior blockers — discharged

### OBJ-633-1 — set identity (was blocking) → **DISCHARGED**

v2 hardens every CALIB_PASS path:

1. **CG-NCOLS** — `calibrated_null_cols(D) == sem_cols(D)` as sets; cardinality
   is derived only.
2. **CG-SUPPORT-HASH** — unconditional admission metric (no
   `_pass_if_alignment_used`).
3. **Secondary** — `REJECT-UNTIL-NATIVE-SUPPORT-MATCH` with
   `calib_pass_admissible: false`; set equality if attempted; admission metric
   `secondary_native_match_not_used_as_calib_pass_path`.
4. **CG-SUPPORT-SUBSET** — fail closed if `sem_cols ⊈ null_cols`.

**Mutation re-check:** keep `|null_cols|==|sem_cols|` while supports differ →
`CALIB_FAIL_NCOLS` / `CALIB_FAIL_SUPPORT_HASH`. No remaining CALIB_PASS path.

### OBJ-633-2 — D5 continuity "or" (was blocking) → **DISCHARGED**

`CG-D5-CONTINUITY` requires both (a) unaligned D∈{3,4,5} C5 continuity and
(b) aligned D≤5 null-zero / rank match; inclusive-or of one mode is forbidden.
ALIGN is the mandatory primary construction for any CALIB_PASS path.

Non-blocking OBJ-633-3 / OBJ-633-4 are also closed (subset fail-code;
`package_review_check` label).

## What survives (scope honesty)

- No measurement authorized in BATCH-002; protocol PASS only unlocks later
  executor *scheduling* under a fresh write_scope + separate Coordinator ledger
  measurement authorization.
- `CALIB_PASS` still needs that later authorization before cascade observables;
  H-SIG-001 status unchanged by this card.
- Legacy D6 magnitudes remain quarantined; infra failures stay non-evidence.
- Residuals (non-blocking): empirical `sr_pred` tautology label; n=12 prior
  ENOSPC risk; receipt `pending_post_commit` metadata.

## Baseline / scope

Closest baseline: EXP-SIG-005 T11 boolean_null under C5, now with hard
equal-support-set admission. Pollard-rho / BSGS are out of scope for this
instrument-repair freeze. This PASS is not cascade falsification and not a
birth-law result.

## Verdict

**PASS** — OBJ-633-1 and OBJ-633-2 are discharged. Support-set identity gates
are hard admission on every `CALIB_PASS` path; D5 continuity is AND-conjunct.
Do not treat this as measurement authorization or D≥6 cascade reopen.

## Next concrete action

Ledger-archive this review (`TASK-20260725-712` / `EV-SIG-010` /
`DEC-20260725-028`). Optionally schedule a later calibration executor under a
fresh write_scope only after separate Coordinator measurement authorization.
Keep the D≥6 cascade closed until admitted `CALIB_PASS` run receipts exist.
