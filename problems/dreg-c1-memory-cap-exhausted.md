# GOAL-DREG-001 item C1 stopped on its memory cap; no d_reg measurement exists

- **Status:** `open`
- **Kind:** resource limit (separate from any mathematical result)
- **Affected work:** GOAL-DREG-001 BATCH-006 item C1 (n=15, D=6 completion-criterion rung); [DEC-20260828-653923](../ledger/decisions/DEC-20260828-653923.yaml); `coordination/goals/GOAL-DREG-001/batches/BATCH-006/tasks/TASK-20260828-955d56/`; H-DREG-001 (`inconclusive`, DEC-20260717-002)
- **Next action owner:** Executor under TASK-20261005-821d86; Coordinator to review
- **Last updated:** 2026-10-18

## Problem

We cannot cite item C1 as a result about the degree of regularity because all six required (seed, arm) runs ended `failed_infrastructure` / `resource_exhaustion` before the rank kernel was invoked, so no rank exists for any of them.

The lane contract fixed `memory_gb: 8`. The prepare phase alone peaked at 11.73 GiB (sem) and 12.22 GiB (null) for seed 2026, 46.6% and 52.75% above the cap. The completion criterion (n in {12, 15, 18}, at least 3 seeds, with the semi-regular null control) is still not met.

## Evidence and uncertainty

- **Observed:** 0 of 6 runs `completed_valid`; independent Validator VAL-20260828-001 `passed` on all five joints, with RSS confirmed from three sources independent of the manifest prose. The goal's `next_action` already says this is "never a negative result about d_reg (AGENTS.md rule 5)".
- **Derived or proved:** not established; the rank-computation phase memory is unmeasured and is likely larger than the prepare phase.
- **Suspected explanation:** the n=15, D=6 system exceeds an 8 GiB floor in prepare; unconfirmed for the rank phase.
- **Missing capability:** a lane contract with a memory budget above the measured prepare peak, or a lower-memory prepare path.
- **What this evidence does not establish:** anything about d_reg at n=15, for or against H-DREG-001. It must not be counted as a negative or as a weakening.

## What would unblock it

- [x] A new lane contract with a higher floor: DEC-20261005-8d23bb raised `memory_gb` from 8 to 16 GiB and carded the retry as TASK-20261005-821d86 (`ledger/handoffs/TASK-20261005-821d86.yaml`). Whether 16 GiB covers the unmeasured rank phase is not known.
- [ ] All six (seed, arm) runs `completed_valid`, with the semi-regular null control, and an independent replay of at least one rank.

## Next discriminating step

- **Action or proof obligation:** execute TASK-20261005-821d86 (option (a) of DEC-20260828-653923 NA-1). As of `origin/main` f279a4918c no run output for it is committed.
- **Inputs and controls:** same n=15, D=6 instances and seeds; same null control.
- **Execution limits and stop condition:** the existing lane-contract rules.
- **Outcomes and next actions:** completed_valid ranks feed the existing evidence path; a second resource stop is recorded here again and not read as a result.
- **Recheck trigger:** a Coordinator lane-contract revision.

## Resolution and history

2026-10-18: record opened from the owner's index-calculus integrity review (infrastructure ground cited as a result). Unresolved.
