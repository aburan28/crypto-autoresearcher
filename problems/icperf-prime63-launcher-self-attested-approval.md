# Prime63 pilot launcher accepts self-attested approval

- **Status:** `open`
- **Kind:** implementation gap in execution admission
- **Affected work:** [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [TASK-20261017-406ac9](../ledger/handoffs/TASK-20261017-406ac9.yaml), [original launcher](../research/icperf_prime63_pilot_launcher_20261017/execute.py), [admission repair](../research/icperf_prime63_admission_fix_20261017/execute.py), and the proposed 27-cell prime63 pilot
- **Next action owner:** Coordinator for an additive runnable protocol and repair handoff; Executor for implementation
- **Last updated:** 2026-10-17

## Problem

The original launcher cannot establish that a 63-bit prime-field solver call belongs to a committed, approved experiment with a live executor claim. Its `approved_packet` function accepts caller-provided `status: approved` and `selector_execution_state: ready` strings after checking only a local input-manifest digest and a fixed task ID. A caller can make those fields without an approved specification, exact trial plan, archival decision, or published claim. The archived engineering repair replaces these strings with repository authorization, but its additional requirement that the ordinary selector remain `ready` inside both parent and child conflicts with the standard supervisor's in-flight state. Thus neither source is presently an admitted scientific pilot.

The affected prospective panel has six planted positive systems and 21 natural systems: coset, random and small-x arms at m=2 through 8 over the archived prime63 curve. The result is an admission gap under these exact inputs, not a statement about whether any relation exists or how fast the algebraic solver would run.

## Evidence and uncertainty

- **Observed:** [The frozen source](../research/icperf_prime63_pilot_launcher_20261017/execute.py) checks four caller-supplied packet fields in `approved_packet` and calls it from both `--run-approved` and wide `--worker-request`. The [18-file snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/archives/TASK-20261017-406ac9/snapshot-receipt.json) binds those bytes to commit `f86ca214d673ffcfe847e504285ccef3a6ac24a9`. The [engineering validation](../research/icperf_prime63_pilot_launcher_20261017/engineering_validation.json) covers controls and scheduling, with no full-width scientific solver panel.
- **Observed:** The [repair validation](../research/icperf_prime63_admission_fix_20261017/validation.json) reports nine passing engineering tests, including 20 fail-closed parent/child cases, but its positive 27-call path mocks approval and selector state. The [repair snapshot](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/archives/TASK-20261017-cf438c/snapshot-receipt.json) fixes those bytes at `bf43515cffaf7618a974ebf5f032619d1c920931`. In the actual supervisor, [`execute_trial`](../tools/experiment_execution.py) creates the run directory before spawning its driver; [`trial_state`](../tools/experiment_execution.py) calls that in-flight directory `needs_reconciliation`, and [`execution_progress`](../tools/newest_experiments.py) then has no `planned` trial for a one-trial plan. The repair's [`admit`](../research/icperf_prime63_admission_fix_20261017/execute.py) rejects anything except selector `ready`, including the authorized in-flight parent and child.
- **Derived or proved:** Checking caller-controlled strings and a file digest cannot establish an archived approval decision or a current published claim. For a single-trial standard plan, the supervisor creates its run directory before launcher admission; by the cited state functions, the selector cannot remain `ready` during that run. This is a code-path implication, not an observed full-width attempt.
- **Suspected explanation:** The first launcher anticipated a later approval packet; the repair treated the selector's pre-dispatch `ready` state as a state that persists during execution. No solver-performance explanation follows.
- **Missing capability:** A prospective driver must use the standard supervisor's run-directory and claim bindings, check the ordinary selector `ready` before dispatch, and independently recheck `load_plan` and `authorize` in its parent and child without mistaking a bound in-flight trial for a stale or unauthorized one.
- **What this evidence does not establish:** It supplies no degree-of-regularity, relation yield, rank, total runtime, or comparison with matched rho.

## What would unblock it

- [ ] Freeze an additive driver/launcher at a new path with committed specification, source/input closure, exact trial plan, handoff, queue, and Coordinator decision; read-only `experiment_preapproval.py --packet` returns `approvable: true` on the exact prospective bytes before approval.
- [ ] After approval and archival, `newest_experiments.py --experiment <ID> --json` reports `execution_state: ready` **before dispatch**. Under the real standard supervisor, both parent and child independently recheck `load_plan` and `authorize` with the live owner/epoch and exact in-flight run binding before scratch/output creation or Sage spawn. One complete positive admission control succeeds without weakening pre-dispatch readiness.
- [ ] Retain forged approval, changed hash, expired/absent claim, wrong owner/epoch and `review_required` negative controls with zero task output or Sage spawn; independently verify the new positive receipt and the prior archived controls.

Those conditions permit a bounded scientific pilot to be dispatched under the normal `run` route. They do not by themselves measure relation yield, certify target work, or establish an index-calculus speedup.

## Next discriminating step

- **Action or proof obligation:** Implement a successor admission path against a real standard-supervisor fixture with one planned trial, then obtain a live-claim positive receipt on an approved bounded protocol.
- **Inputs and controls:** Reuse the archived 27-system hashes; compare selector state before and after run-directory creation; inject stale run directories, forged launch metadata, wrong owner/epoch, changed plan/source and expired claims. Check parent and child separately.
- **Execution limits and stop condition:** Engineering fixtures make no full-width solver call. Stop before Sage if any authority or binding fails; a later approved pilot retains the frozen 300-second per-cell, 8 GiB and four-hour guards.
- **Outcomes and next actions:** A real in-flight positive plus all negative refusals permits the bounded pilot; positive refusal requires another repair; false acceptance blocks dispatch; infrastructure failure remains an access/runtime outcome.
- **Recheck trigger:** Additive successor source, exact preapproval packet, and a real bound in-flight admission receipt are archived.

## Resolution and history

- 2026-10-17: Created after the prime63 engineering source and separate snapshot receipt were archived. The frozen bytes remain unchanged. **Unresolved.**
- 2026-10-17: The additive repair passed its recorded mocked controls and was snapshotted, but code-path review found the selector-in-flight mismatch above. The repair remains immutable; the next design must test the real supervisor ordering. **Unresolved.**
