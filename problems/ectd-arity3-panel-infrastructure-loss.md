# EXP-ECTD-0cf008 arity-3 panel: 17 of 20 arms lost to infrastructure

- **Status:** `open`
- **Kind:** implementation gap (runtime dependency and RSS sampling in the supervisor); not a measurement
- **Affected work:** EXP-ECTD-0cf008 and its report `experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/`; GOAL-ECTD-001; H-ECTD-e88346 (`approved`); DEC-20261015-df1003, DEC-20261015-5a1f2c
- **Next action owner:** Coordinator (additive recovery amendment)
- **Last updated:** 2026-10-18

## Problem

We cannot cite the 20-arm native arity-3 relation-yield panel as a comparison of conductor effects: only 3 arms have `output_validated` receipts (P37-floor-u2-native, P29-E2-native, P29-E3-native), so no native/random or transport comparison exists.

## Evidence and uncertainty

- **Observed:** 11 arms `infrastructure_error` with `ModuleNotFoundError: No module named psutil` (no collector result); 2 arms `infrastructure_error` with `cannot read resident memory for process` during verifier-phase RSS sampling (raw outputs kept, no sealed receipt); 4 `u2-transport` arms stuck `waiting_on_dependencies` because their native references have no validated output. The report states the failed attempts were neither overwritten nor imputed.
- **Derived or proved:** not applicable.
- **Missing capability:** a runtime lock and preflight that fail before dispatch. A draft exists: `experiments/EXP-ECTD-0cf008/amendments/recovery-20261016-draft.json` (17-arm additive plan) with `runtime-lock.json`; its `admission_pending` list names the missing Coordinator-approved amendment, handoff, run-id recheck, published archive and executor claim.
- **What this evidence does not establish:** any effect size, null, or weakening of H-ECTD-e88346. The hypothesis text itself says "a failed control or censored arm is not evidence against the hypothesis".

## What would unblock it

- [ ] Coordinator-approved additive amendment binding the exact 17-arm recovery plan with new run ids, failed directories retained.
- [ ] Runtime preflight (psutil present, RSS sampling verified) passing before dispatch.
- [ ] A complete valid panel, then the pre-registered ratio intervals.

## Next discriminating step

- **Action or proof obligation:** finish and approve the recovery amendment; rerun the 17 arms.
- **Inputs and controls:** original specification sha256 6adf8dd0...; the three validated arms stay as they are.
- **Execution limits and stop condition:** the amendment's own limits.
- **Outcomes and next actions:** a complete panel goes to review-evidence; a repeat infrastructure loss is recorded here.
- **Recheck trigger:** amendment approval.

## Resolution and history

2026-10-18: record opened from the owner's index-calculus integrity review. Unresolved.
