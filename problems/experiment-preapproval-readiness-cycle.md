# Experiment approval readiness has a circular selector gate

- **Status:** `investigating`
- **Kind:** control-plane implementation and contract mismatch.
- **Affected work:** [AGENTS.md approval rule](../AGENTS.md#approval-is-bounded-by-execution), [the ordinary experiment selector](../tools/newest_experiments.py), [the supervisor plan loader](../tools/experiment_execution.py), [EXP-ICPERF-018b0c](../experiments/EXP-ICPERF-018b0c/specification.yaml), and the separate [supervisor archive-coverage problem](ready-plans-lack-supervisor-archive-coverage.md).
- **Next action owner:** Coordinator for a reviewed read-only preapproval probe and contract correction; then the ICPERF design lane for a complete prospective k11 packet.
- **Last updated:** 2026-10-17

## Problem

The current approval rule requires `tools/newest_experiments.py --experiment <EXP-ID>` to report `execution_state: ready` before an experiment can be approved, while the selector and its plan loader both require an already approved experiment. This makes the stated preapproval test unreachable for every new contract. For `EXP-ICPERF-018b0c`, the bounded 60-bit ordinary-binary k11 solver pilot, the draft is `review_required` with null approval, task and queue bindings, so it cannot be evaluated by the selector before approval. The missing bindings and lawful lane are separate, real prerequisites; removing the circular test alone does not approve this pilot.

## Evidence and uncertainty

- **Observed:** `tools/newest_experiments.py` filters out a specification unless `status == approved`, `approved_by` is nonempty and `frozen is True`, even under `--experiment` or `--include-blocked`. Its `execution_progress()` calls `coverage()`, whose `experiment_execution.load_plan()` requires a frozen plan, nonempty approval/task/queue and an approved or running specification. For the k11 draft, the ordinary selector returns `[]` because it is excluded, not because an implementation check failed.
- **Derived:** For any unapproved specification, the current approval precondition and selector's inclusion condition cannot both hold. The logical cycle does not depend on curve or solver parameters.
- **Observed, distinct gap:** `problems/ready-plans-lack-supervisor-archive-coverage.md` documents approved plans labeled `ready` even though `authorize()` refuses their missing exact run artifacts. A selector-only relaxation would leave this separate safety gap untested.
- **Missing capability:** A reviewed, read-only approvability probe of exact prospective final specification, plan, handoff and queue bytes, including source/input digests, supervisor and trial artifact coverage, execution route and lawful lane, followed by the unchanged postapproval selector and runtime gates. A scoped implementation is under review; it is not an approval or scientific run.
- **What this evidence does not establish:** It does not assess whether the k11 formulas have natural solutions, whether a factor base helps degree of regularity or sparsity, or whether any complete index-calculus cost improves.

## What would unblock it

- [ ] A reviewed contract replaces the impossible preapproval selector test with a separate read-only `approvable: true` probe on exact prospective bytes, retaining `newest_experiments.py --experiment ... == ready` after a committed Coordinator approval and before dispatch.
- [ ] The probe refuses missing approval-decision, task, queue, source/input, raw-bundle, supervisor artifact, execution-route or lawful-lane bindings with specific blockers. A complete synthetic packet passes while the canonical unapproved specification stays excluded and the runner refuses it.
- [ ] The final archived implementation passes focused positive/negative controls and the relevant unchanged selector/runner checks; the postapproval fixture becomes ready only with the exact projected bytes, and a changed bound byte loses readiness.

Meeting these conditions repairs the generic approval gate. It does not make the current k11 draft approvable until its own missing queue, handoff, lane and execution route are complete. Its bounded solver trial and independent result review remain separate obligations.

## Next discriminating step

- **Action or proof obligation:** Archive the Coordinator's prospective tooling decision and test a read-only `tools/experiment_preapproval.py` against a complete synthetic packet and the incomplete `EXP-ICPERF-018b0c` draft.
- **Inputs and controls:** Keep the ordinary selector, plan loader and `authorize()` unchanged. Positive control: a complete preview packet with matching spec/plan/queue/handoff digests, committed source, archive coverage and open lane. Negative controls: missing raw bundle, supervisor file, source hash, queue binding, lane and execution route; require the ordinary selector to exclude the canonical draft throughout.
- **Execution limits and stop condition:** Static checks only; no solver, scientific trial, claim or status transition. Stop if a proposed change makes an unapproved contract selectable or weakens a runtime guard.
- **Outcomes and next actions:** Passing controls support the scoped contract correction, subject to PR review and archive verification. A false positive requires a tighter probe. A valid complete packet refused for a named mechanical reason needs a scoped correction; missing k11 bindings keep that experiment `review_required`.
- **Recheck trigger:** Merge of the governance tooling PR or a changed selector/runtime admission contract.

A planned step is not an experiment result. Apply the existing approval, execution and archival rules before any pilot.

## Resolution and history

2026-10-17: Opened from the mutually exclusive selector and preapproval rule, with `EXP-ICPERF-018b0c` as a concrete affected draft. Unresolved until the exact probe, contract change, controls and archive are reviewed and landed.

## 2026-10-17 additive-repair boundary

The [SNFS repair packet](../coordination/design/SNFS-INSTRUMENT-REPAIR-20261017/README.txt) exercised the current read-only preapproval probe on already-approved E3/D4 instruments with prospective versioned plans. The probe returned approvable:false: it expects an unapproved canonical specification, canonical trial-plan.json routing and input bindings, and a lawful new queue lane. These are exact mechanical gaps; the packet does not claim a passing probe or an approval. A supported repair path must retain the ordinary supervisor guards and reject changed scientific bytes or incomplete artifact coverage.

## SNFS additive continuation, 2026-10-17

A [proposed additive admission extension](../coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/) now exercises transport repair and fresh retry identities in synthetic fixtures. Production admission/selector/supervisor code is unchanged. Its fixture checks do not authorize E3/D4 or G1 execution: exact committed packet bytes, lawful lane/queue ownership, supported additive postapproval selection and truthful Coordinator session authority remain required. This is concrete implementation preparation for the existing obstruction, not resolution or a new scientific result.
