# Prime63 pilot launcher accepts self-attested approval

- **Status:** `open`
- **Kind:** implementation gap in execution admission
- **Affected work:** [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [TASK-20261017-406ac9](../ledger/handoffs/TASK-20261017-406ac9.yaml), [archived launcher](../research/icperf_prime63_pilot_launcher_20261017/execute.py), and the proposed 27-cell prime63 pilot
- **Next action owner:** Coordinator for a frozen repair handoff; Executor for implementation
- **Last updated:** 2026-10-17

## Problem

The archived launcher cannot establish that a 63-bit prime-field solver call belongs to a committed, approved experiment with a live executor claim. Its `approved_packet` function accepts caller-provided `status: approved` and `selector_execution_state: ready` strings after checking only a local input-manifest digest and a fixed task ID. A caller can make those fields without an approved specification, exact trial plan, archival decision, or published claim. The same check protects the full panel and wide-field worker paths. Thus its engineering validation does not authorize a scientific pilot or an end-to-end speed claim.

The affected prospective panel has six planted positive systems and 21 natural systems: coset, random and small-x arms at m=2 through 8 over the archived prime63 curve. The result is an admission gap under these exact inputs, not a statement about whether any relation exists or how fast the algebraic solver would run.

## Evidence and uncertainty

- **Observed:** [The frozen source](../research/icperf_prime63_pilot_launcher_20261017/execute.py) checks four caller-supplied packet fields in `approved_packet` and calls it from both `--run-approved` and wide `--worker-request`. The [18-file snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/archives/TASK-20261017-406ac9/snapshot-receipt.json) binds those bytes to commit `f86ca214d673ffcfe847e504285ccef3a6ac24a9`. The [engineering validation](../research/icperf_prime63_pilot_launcher_20261017/engineering_validation.json) covers controls and scheduling, with no full-width scientific solver panel.
- **Derived or proved:** Checking caller-controlled strings and a file digest cannot establish an archived approval decision or a current published claim; the required bindings are absent from the predicate.
- **Suspected explanation:** The engineering-only launcher anticipated a later approval packet but did not implement repository admission against the dispatcher. No solver-performance explanation follows.
- **Missing capability:** A prospective launcher must call `tools.experiment_execution.load_plan` and `authorize` against the exact committed plan, source hashes, queue, handoff and live published claim, and check the ordinary experiment selector's `ready` state before scratch creation or worker launch.
- **What this evidence does not establish:** It supplies no degree-of-regularity, relation yield, rank, total runtime, or comparison with matched rho.

## What would unblock it

- [ ] Freeze a corrected launcher at a new path, with a committed frozen specification, source/input closure, exact trial plan, handoff, queue, and Coordinator decision; a read-only `experiment_preapproval.py --packet` probe for those exact prospective bytes returns `approvable: true` before approval.
- [ ] After approval and archival, `newest_experiments.py --experiment <ID> --json` reports `execution_state: ready`, and each full-width parent and child entry point independently rechecks `load_plan` and `authorize` with the claimed owner and epoch before any scratch/output creation or Sage spawn.
- [ ] Negative tests for forged approval strings, wrong decision or plan/specification/source hash, missing or expired claim, wrong owner/epoch, and `review_required` selector prove zero worker spawn and zero run output. Positive admission uses a real published claim and independently checked archive receipt.

Those conditions permit a bounded scientific pilot to be dispatched under the normal `run` route. They do not by themselves measure relation yield, certify target work, or establish an index-calculus speedup.

## Next discriminating step

- **Action or proof obligation:** Write and independently inspect the prospective admission repair, preserving the archived source bytes.
- **Inputs and controls:** Reuse the 27 archived prime63 systems and hashes; compare admission behavior against the frozen self-attested check; use the negative cases above and a genuine ready-selector/live-claim positive case.
- **Execution limits and stop condition:** Engineering validation only until the exact protocol passes preapproval and later ordinary selector admission. Stop before any full-width solver call if a binding is missing.
- **Outcomes and next actions:** Passing all admission tests permits protocol approval and `/run`; a failed negative case requires repair; missing selector or claim is an infrastructure/protocol impediment to record, not a solver outcome.
- **Recheck trigger:** Corrected source and its independent admission test receipt land in a content-first archive.

## Resolution and history

- 2026-10-17: Created after the prime63 engineering source and separate snapshot receipt were archived. The frozen bytes remain unchanged. **Unresolved.**
