# TASK-20260731-042 — Derivation / protocol check for PA-DS-001-v2-ctrl-unplanted

**Report:** `RT-20260731-042` (path + task id).
**Reviewed snapshot:** `cac4d8b459a44f1561d3f47835562824f7767765` (TASK-20260731-041).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`).
**Prior disposition:** DEC-20260731-018 inconclusive; RT-20260731-038; next_action CTRL-RT025-UNPLANTED (+ live plant).
**Question:** Is the control addendum falsifiable, decidable, v2-bound, and free of claim-ceiling / science-metric leaks so TASK-043 may APPROVE?

## Verdict

**PASS.** DEC-009 next_action is protocol-encoded. No new blocking holes. Residuals R-1 / R-2 are non-blocking. No measurement; no approval issued here.

## Snapshot binding

| Path | sha256 at `cac4d8b4` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_unplanted.yaml` | `2c9ab2e1422185b5e1426380e9d4142d09b6f3c57611156127dbf18184827ea0` | PA-DS-001-v2-ctrl-unplanted |
| `experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml` | `c85cc14cf4d5f1a2a693b84756b28fa0abc08f0e8a5a246701f442e97fda060c` | control protocol |
| `ledger/decisions/DEC-20260731-019.yaml` | `b76b7f915cf5625ada84e9e933bfd9919c592e9cd2eb1ec0f4d563820097189e` | opens BATCH-020 |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in snapshot commit; parent pin matches |

`git merge-base --is-ancestor cac4d8b4 HEAD` succeeds. Snapshot path list excludes all specification*.yaml blobs.

## DEC-009 next_action checklist

| Requirement | Where frozen | Status |
|---|---|---|
| Cell bits=20, B=64, m=4, seed=101 | `scope.cells` | met |
| Unplanted uniform (or sparse + success-prob accounting) | `target_mode` | met |
| Same backend id | `backend.must_match_planted_package_id` = `ds001-v2-point-sum-membership+charged-units-v1` | met |
| `smoothness_abort=false` | top-level field | met |
| `relations_target=200` or honest resource stop | `relations_target` + `resource_stop` | met |
| Live /4 plant, no synthetic known-answer | `companion_live_plant` | met |
| No full 54-cell / no v1 / no H-IC/H-STR edits | `scope`, `non_changes`, `does_not_modify_hypotheses` | met |
| No S1_met / asymptotic from control alone | `claim_ceiling`, `confirmatory_status` | met |

## What still re-derives cleanly

1. Parent v2 cost identities used by reference (yield-charged wall × ρ_gop / max(n_usable,1)).
2. R-1 remains binding on the unplanted cell (R&lt;0.5 ∧ R_null&lt;0.9 ⇒ F2_eligible).
3. EV-DS-002 planted package is not superseded; control is a separate run package.
4. RC-20 one-cycle cap: this PASS does not open a second cycle; Executor still needs TASK-043 APPROVED.
5. Toy claim ceiling; RT038-B1–B7 + M1 still bind later interpretation.

## Non-blocking residual (R-1)

Live /4 must be a **companion detection path** (`live_plant_report.json`) and must **not** rewrite primary unplanted R in `R_cell.json`. Implied by companion naming, separate artifacts, packaging AND-conjuncts, and parent CTRL-NULL-PLANT / driver pattern. Not REVISE-forcing under RC-20.

## Scope of this check

Pre-execution control-addendum review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full gate ledger.

## Coordinator handoff

On PASS: TASK-20260731-043 should record `APPROVAL_DETERMINATION: APPROVED` and authorize Executor only against `specification.v2.yaml` as narrowed by `controls/CTRL-RT025-UNPLANTED.yaml`. Do not open a second amendment cycle (RC-20). This task’s `write_scope` excludes the dispatch queue; Coordinator must mark TASK-042 completed and regenerate the BATCH-020 plan.
