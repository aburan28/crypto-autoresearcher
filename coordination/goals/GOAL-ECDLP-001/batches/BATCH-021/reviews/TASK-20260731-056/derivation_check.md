# TASK-20260731-056 — Derivation / protocol check for PA-DS-001-v2-ctrl-theater-repair

**Report:** `RT-20260731-056` (path + task id).
**Reviewed snapshot:** `98fa35db18e49cc65f977392bbbd925990e9a05b` (TASK-20260731-055).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`).
**Prior disposition:** DEC-20260731-012 inconclusive on CTRL-RT025-UNPLANTED (EV-DS-003; RT-20260731-047). Exact next action: BATCH-021 theater repair — PLANT-INDEPENDENT + RHO-CALIB + NULL-SPLIT-COMPOSITION; CI-IDENTITY and SPARSE-P-SUCCESS deferred.
**Session note:** Fresh replacement after `6f4bcb84-4f0d-4cfe-b69f-19fedab9c7fe` failed_infrastructure with zero deliverables. This session did not author the addendum.
**Question:** Is the theater-repair addendum falsifiable, decidable, v2-bound, and free of claim-ceiling / science-metric leaks so TASK-057 may APPROVE?

## Verdict

**PASS.** All five card checklist items hold on the frozen blobs. No new blocking holes. No measurement; no approval issued here.

## Snapshot binding

| Path | sha256 at `98fa35db` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_theater_repair.yaml` | `ae045b81d37c6449b1f5774e5b3e47cc24511c1bb3b9936b0970adc3b4452ab8` | PA-DS-001-v2-ctrl-theater-repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-PLANT-INDEPENDENT.yaml` | `19975ff578fde57e99453aa9a36b3e43cb04eec985c621409c3a2514257d946b` | plant repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-RHO-CALIB.yaml` | `c43d30b7cc90b9d22457e637bff67b884df77ddc7f4131ef282c9708ba7bab6b` | rho repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-NULL-SPLIT-COMPOSITION.yaml` | `483a2432cabb8282ef081568ff22badd6c7d34ffeef9c4e89df03f186356affa` | null-split repair |
| `ledger/decisions/DEC-20260731-014.yaml` | `20f9353438399a7cf959c9742d2527600e166e54af3aafb3c28b93630cc5c253` | opens BATCH-021 theater repair |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in snapshot commit; parent pin matches |

`git merge-base --is-ancestor 98fa35db HEAD` succeeds. `git show --name-only 98fa35db` excludes all `specification*.yaml` blobs.

## Card checklist (PASS only if all hold)

| # | Requirement | Where frozen | Status |
|---|---|---|---|
| 1 | Plant: forbid echo-only / divide-then-echo; require `null_gate_f2_shape` or non-arithmetic FLAG; no synth; no hardcoded `planted_bug_detected` | `CTRL-RT025-PLANT-INDEPENDENT` `method.forbid` + `require_detection_path` + `falsifies_if` | met |
| 2 | Rho: measured ratios that can fail; not hardcoded 1.0 | `CTRL-RT025-RHO-CALIB` `method.measure` + `falsifies_if` | met |
| 3 | Null-split: composition + destroy check `R_null` can go &lt;0.9 (or honest non-falsifiability) | `CTRL-RT025-NULL-SPLIT-COMPOSITION` `method.compose` + `destroy_parameter_check` | met |
| 4 | No full 54-cell; deferred CI-IDENTITY / SPARSE named; no v2 edit | amendment `non_changes`, `deferred_*`; commit path list | met |
| 5 | Toy ceiling; `no_run` until TASK-057; no H-IC-001 / H-STR-002 changes | `claim_ceiling`, `no_run_authorized_until_approval`, DEC-014 | met |

## What still re-derives cleanly

1. Parent v2 remains the immutable APPROVED matrix contract; execution binds to v2 cost identities / backend constraints PLUS the three co-required controls.
2. EV-DS-002 / EV-DS-003 remain immutable prior records; EV-DS-004 (if filed) is the theater-repair package evidence.
3. RC-21 one-cycle cap: this PASS does not open a second cycle; Executor still needs TASK-057 APPROVED.
4. Toy claim ceiling; asymptotic promotion gates remain OPEN; H-DS-001 stays `analyzed`.
5. Deferred CI-IDENTITY and SPARSE-P-SUCCESS are named and explicitly not co-required this batch.

## Blocking defects

None.

## Scope of this check

Pre-execution control-addendum review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full gate ledger.

## Coordinator handoff

On PASS: TASK-20260731-057 should record `APPROVAL_DETERMINATION: APPROVED` and authorize Executor only against `specification.v2.yaml` as narrowed by the three co-required theater-repair controls. Do not open a second amendment cycle (RC-21). This task’s `write_scope` excludes the dispatch queue; Coordinator must mark TASK-056 completed and regenerate the BATCH-021 plan. Leave `_session_6f4bcb84_infrastructure_failed.json` in place.
